#!/usr/bin/env python3
'''Exercise the actual patched nxdk SDL USB callbacks and Back-event handoff.

Build Xbox first, or pass --driver-source path/to/SDL_xboxjoystick.c.
The host fixture substitutes USB/SDL/kernel services, not controller logic.
'''
from pathlib import Path
import argparse
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--driver-source", type=Path)
args = parser.parse_args()
if args.driver_source:
    driver = args.driver_source
else:
    cache = (root / "build-xbox/CMakeCache.txt").read_text()
    match = re.search(r"^SDL3Wrapper_SOURCE_DIR:[^=]+=(.+)$", cache, re.M)
    if not match:
        raise SystemExit("Build Xbox first or provide --driver-source")
    driver = Path(match[1]) / "nxdk_glue/joystick/SDL_xboxjoystick.c"
text = driver.read_text()

def function(name):
    # Extract a definition (skip its prototype); all tested code comes from SDL.
    match = re.search(r"^static [^\n]+\b" + name + r"\([^;]*?\)\s*\{", text, re.M)
    if not match:
        return ""
    start = match.start()
    brace = text.index("{", match.start())
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end] + "\n"

def definition(name):
    match = re.search(r"typedef struct " + name + r"\b.*?}\s*[^;]+;", text, re.S)
    assert match, name
    return match[0] + "\n"

parts = [definition("_XINPUT_GAMEPAD"), definition("joystick_hwdata")]
functions = [function(n) for n in ["clear_input_data", "parse_input_data", "int_read_callback", "disconnect_callback", "SDL_XBOX_JoystickUpdate", "SDL_XBOX_JoystickClose"]]
assert all(functions[i] for i in range(1, len(functions)))
constants = "\n".join(line for line in text.splitlines() if line.startswith("#define XINPUT_GAMEPAD_") or line.startswith("#define BUTTON_DEADZONE"))
fixture = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8; typedef uint16_t Uint16; typedef uint32_t Uint32;
typedef uint64_t Uint64; typedef int16_t Sint16; typedef int32_t Sint32;
typedef int KIRQL;
#define MAX_PACKET_SIZE 32
#define XID_TYPE_GAMECONTROLLER 1
#define USBH_OK 0
#define SDL_memcpy memcpy
#define SDL_memset memset
#define SDL_free free
#define SDL_arraysize(x) (sizeof(x)/sizeof((x)[0]))
#define JOY_DBGMSG(...) ((void)0)
enum {SDL_GAMEPAD_BUTTON_SOUTH,SDL_GAMEPAD_BUTTON_EAST,SDL_GAMEPAD_BUTTON_WEST,SDL_GAMEPAD_BUTTON_NORTH,
 SDL_GAMEPAD_BUTTON_BACK,SDL_GAMEPAD_BUTTON_GUIDE,SDL_GAMEPAD_BUTTON_START,SDL_GAMEPAD_BUTTON_LEFT_STICK,
 SDL_GAMEPAD_BUTTON_RIGHT_STICK,SDL_GAMEPAD_BUTTON_LEFT_SHOULDER,SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER};
enum {SDL_GAMEPAD_AXIS_LEFTX,SDL_GAMEPAD_AXIS_LEFTY,SDL_GAMEPAD_AXIS_RIGHTX,SDL_GAMEPAD_AXIS_RIGHTY,
 SDL_GAMEPAD_AXIS_LEFT_TRIGGER,SDL_GAMEPAD_AXIS_RIGHT_TRIGGER};
enum {SDL_HAT_CENTERED=0,SDL_HAT_UP=1,SDL_HAT_RIGHT=2,SDL_HAT_DOWN=4,SDL_HAT_LEFT=8};
typedef struct xid_dev { struct {int bType;} xid_desc; void *user_data; uint32_t uid;} xid_dev_t;
typedef struct {void *context; int status; Uint32 xfer_len; Uint8 *buff; int bIsTransferDone;} UTR_T;
'''
fixture += constants + "\n" + "\n".join(parts)
fixture += r'''
typedef struct {joystick_hwdata *hwdata; bool buttons[11]; struct {Sint16 value;} axes[6];
 Uint8 hats[1]; int id;} SDL_Joystick;
static int irq, rearms, retries, rumble_calls, fail_rearm;
static void (*on_lower)(void);
static KIRQL KeRaiseIrqlToDpcLevel(void) {int old=irq;irq=1;return old;}
static void KfLowerIrql(KIRQL old) {irq=old;if(on_lower){void(*f)(void)=on_lower;on_lower=NULL;f();}}
static int usbh_int_xfer(UTR_T *u) {assert(irq==1 && u->xfer_len==0 && u->bIsTransferDone==0);rearms++;return fail_rearm?-1:USBH_OK;}
static int usbh_xid_read(xid_dev_t *d,int ep,void *cb) {assert(d && cb && ep==0 && !irq);retries++;return USBH_OK;}
static int usbh_xid_rumble(xid_dev_t *d,int a,int b) {assert(d);rumble_calls++;return 0;}
static Uint64 SDL_GetTicksNS(void) {return 1;}
extern void queue_back(int id);
extern int consume_back(void);
extern void connect_pad(int id);
extern void remove_pad(int id);
static int downs, ups;
static void SDL_SendJoystickButton(Uint64 ts,SDL_Joystick *j,int button,bool down) {
 if(j->buttons[button]==down)return;
 j->buttons[button]=down;
 if(button==SDL_GAMEPAD_BUTTON_BACK){if(down){downs++;queue_back(j->id);}else ups++;}
}
static void SDL_SendJoystickHat(Uint64 ts,SDL_Joystick *j,int i,int hat){j->hats[i]=hat;}
static void SDL_SendJoystickAxis(Uint64 ts,SDL_Joystick *j,int i,int value){j->axes[i].value=value;}
typedef struct controller_connection_event {uint32_t uid;bool connected;} controller_connection_event_t;
static controller_connection_event_t uid_event_queue[8];
static int uid_event_queue_index;
static int SDL_GetAtomicInt(int *v){return *v;}
static bool SDL_CompareAndSwapAtomicInt(int *v,int old,int n){if(*v!=old)return false;*v=n;return true;}
'''
fixture += "\n".join(functions)
fixture += r'''
static void complete(UTR_T *u) {int old=irq;irq=1;int_read_callback(u);assert(irq==1);irq=old;}
static UTR_T report(SDL_Joystick *j,Uint8 *bytes,int len) {
 UTR_T u={.context=j->hwdata->xid_dev,.status=0,.xfer_len=len,.buff=bytes,.bIsTransferDone=1};
 complete(&u);return u;
}
static SDL_Joystick pad(int id) {
 SDL_Joystick j={0};j.id=id;j.hwdata=calloc(1,sizeof(*j.hwdata));
 j.hwdata->xid_dev=calloc(1,sizeof(xid_dev_t));j.hwdata->xid_dev->xid_desc.bType=XID_TYPE_GAMECONTROLLER;
 j.hwdata->xid_dev->uid=id;connect_pad(id);return j;
}
static SDL_Joystick *injected_pad;
static void inject_neutral(void){Uint8 n[20]={0,20};report(injected_pad,n,20);}
void run_driver_tests(void) {
 Uint8 n[20]={0,20},b[20]={0,20,0x20},a[20]={0,20,0,0,255};
 SDL_Joystick j=pad(11);j.hwdata->xid_dev->user_data=&j;
 int start=rearms;UTR_T u=report(&j,b,20);assert(rearms==start+1 && !u.bIsTransferDone);
 report(&j,n,20);assert(!j.hwdata->raw_data[2]);
 SDL_XBOX_JoystickUpdate(&j);assert(downs==1 && ups==1 && !j.buttons[SDL_GAMEPAD_BUTTON_BACK]);
 assert(consume_back() && !consume_back());
 // Repeated neutral or held packets cannot create repeated menu requests.
 int d=downs;SDL_XBOX_JoystickUpdate(&j);assert(downs==d && !consume_back());
 report(&j,b,20);SDL_XBOX_JoystickUpdate(&j);assert(j.buttons[SDL_GAMEPAD_BUTTON_BACK] && consume_back());
 for(int i=0;i<20;i++)report(&j,b,20);
 d=downs;SDL_XBOX_JoystickUpdate(&j);assert(downs==d && !consume_back());
 report(&j,n,20);report(&j,b,20);report(&j,n,20);SDL_XBOX_JoystickUpdate(&j);
 assert(downs==d+1 && !j.buttons[SDL_GAMEPAD_BUTTON_BACK] && consume_back() && !consume_back());
 // Gameplay and confirmation remain live, including complete A taps.
 report(&j,a,20);report(&j,n,20);SDL_XBOX_JoystickUpdate(&j);
 assert(!j.buttons[SDL_GAMEPAD_BUTTON_SOUTH] && !consume_back());
 // A completion just after the protected snapshot survives for the next update.
 report(&j,b,20);injected_pad=&j;on_lower=inject_neutral;SDL_XBOX_JoystickUpdate(&j);
 assert(j.hwdata->new_data && j.buttons[SDL_GAMEPAD_BUTTON_BACK] && consume_back());
 SDL_XBOX_JoystickUpdate(&j);assert(!j.buttons[SDL_GAMEPAD_BUTTON_BACK] && !consume_back());
 // Every truncated allocation is genuinely short; ASan detects speculative reads.
 for(int len=0;len<20;len++) {
  report(&j,b,20);Uint8 *short_data=malloc(len?len:1);memcpy(short_data,n,len);
  report(&j,short_data,len);free(short_data);SDL_XBOX_JoystickUpdate(&j);
  assert(!j.buttons[SDL_GAMEPAD_BUTTON_BACK] && !consume_back());
 }
 Uint8 bad[20]={1,20,0x20};report(&j,b,20);report(&j,bad,20);SDL_XBOX_JoystickUpdate(&j);assert(!consume_back());
 bad[0]=0;bad[1]=19;report(&j,b,20);report(&j,bad,20);SDL_XBOX_JoystickUpdate(&j);assert(!consume_back());
 // USB errors and failed rearming release old state, with retries only on main.
 report(&j,b,20);u=(UTR_T){.context=j.hwdata->xid_dev,.status=-1,.bIsTransferDone=1};
 start=rearms;complete(&u);assert(rearms==start);start=retries;
 SDL_XBOX_JoystickUpdate(&j);assert(retries==start+1 && !j.buttons[SDL_GAMEPAD_BUTTON_BACK] && !consume_back());
 fail_rearm=1;u=report(&j,b,20);assert(u.bIsTransferDone);SDL_XBOX_JoystickUpdate(&j);assert(!consume_back());fail_rearm=0;
 // A different active pad must not erase a real reserved menu request.
 SDL_Joystick other=pad(12);other.hwdata->xid_dev->user_data=&other;
 report(&j,b,20);report(&j,n,20);report(&other,a,20);SDL_XBOX_JoystickUpdate(&j);SDL_XBOX_JoystickUpdate(&other);assert(consume_back());
 // The USB stack frees xid_dev before SDL removal/close: no stale pointer use.
 xid_dev_t *gone=j.hwdata->xid_dev;disconnect_callback(gone,0);
 assert(!gone->user_data && !j.hwdata->xid_dev);remove_pad(j.id);free(gone);
 start=retries;SDL_XBOX_JoystickUpdate(&j);assert(retries==start && !consume_back());SDL_XBOX_JoystickClose(&j);assert(!j.hwdata);
 // Closing a still-attached pad also makes a later completion inert.
 gone=other.hwdata->xid_dev;SDL_XBOX_JoystickClose(&other);assert(!gone->user_data && !other.hwdata);
 start=rearms;u=(UTR_T){.context=gone,.status=0,.buff=b,.xfer_len=20};complete(&u);assert(rearms==start);free(gone);remove_pad(other.id);
 assert(!irq);puts("PASS: actual SDL USB read rearm, complete Back taps, live gameplay, snapshot race, invalid/error release, retry and disconnect/close lifetime");
}
'''
cpp = r'''
#include "xbox_back_press.hpp"
#include <cassert>
#include <cstdio>
static XboxSDLInput::BackPresses taps;
extern "C" void queue_back(int id){taps.press(id);}
extern "C" int consume_back(){return taps.consume();}
extern "C" void connect_pad(int id){taps.connect(id);}
extern "C" void remove_pad(int id){taps.disconnect(id);}
extern "C" void run_driver_tests();
int main() {
 assert(!taps.consume());taps.press(0);taps.press(99);assert(!taps.consume());
 for(int i=1;i<=4;i++)taps.connect(i);
 taps.press(1);taps.press(1);assert(taps.consume()&&!taps.consume());
 taps.press(2);taps.press(4);taps.disconnect(2);assert(taps.consume()&&!taps.consume());
 taps.press(3);taps.disconnect(3);taps.connect(3);assert(!taps.consume());
 taps.press(4);taps.clear();assert(!taps.consume());
 run_driver_tests();puts("PASS: four-pad SDL Back event handoff, one-shot consumption, removal/reconnect and cleanup");
}
'''
with tempfile.TemporaryDirectory(prefix="xbox-sdl-controller-") as directory:
    work = Path(directory)
    (work / "driver.c").write_text(fixture)
    (work / "event.cpp").write_text(cpp)
    common = ["-g", "-O1", "-fno-omit-frame-pointer", "-fsanitize=address,undefined"]
    subprocess.run(["clang", "-std=c11", *common, "-c", str(work / "driver.c"), "-o", str(work / "driver.o")], check=True)
    subprocess.run(["clang++", "-std=c++17", *common, "-I", str(root / "include/windowing/sdl3"), str(work / "event.cpp"), str(work / "driver.o"), "-o", str(work / "test")], check=True)
    subprocess.run([str(work / "test")], check=True)
