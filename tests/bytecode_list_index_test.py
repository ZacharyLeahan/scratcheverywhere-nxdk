#!/usr/bin/env python3
"""Compare actual VM list operations with their pre-optimization behavior."""
from pathlib import Path
import subprocess
import tempfile
import sys
root = Path(__file__).resolve().parents[1]
cache = root / 'build-xbox/.cache/catalog'
json_include = next(cache.glob('*/src/include/nlohmann/json.hpp')).parents[1]
expected_include = next(cache.glob('*/src/include/nonstd/expected.hpp')).parents[1]
ryu = next(cache.glob('*/src/ryu/d2s.c')).parents[1]
executor = (root/'source/runtime/bytecode_executor.cpp').read_text()
resolver = executor[executor.index('size_t resolveListIndex('):executor.index('bool valuesEqual(')]
cases = executor[executor.index('            SE_CASE(DeleteFromList)'):executor.index('            SE_CASE(ItemNumOfList)')]
benchmark = '--benchmark' in sys.argv
with tempfile.TemporaryDirectory(prefix='bytecode-list-index-') as tmp:
    tmp = Path(tmp)
    (tmp/'se_export.hpp').write_text('#pragma once\n#define SE_EXPORT\n')
    (tmp/'os.hpp').write_text('#pragma once\n')
    (tmp/'renderer.hpp').write_text("""#pragma once
 enum class Renderers { SDL1, SDL2, SDL3, Xbox, NV2A, GX2, OpenGL, OpenGLCore, GDI, D3D9, Headless };
 namespace Render { inline Renderers currentRenderer = Renderers::Headless; }
""")
    (tmp/'log.hpp').write_text("""#pragma once
#include <string>
namespace Log { inline void logCritical(std::string, bool) {} }
""")
    (tmp/'test.cpp').write_text(r'''
#include "value.hpp"
#include <chrono>
#include <iostream>
#include <limits>
#include <string_view>
struct TrackedValue : Value {
    using Value::Value;
    TrackedValue() = default;
    TrackedValue(const Value &v) : Value(v) {}
    inline static size_t formats=0, views=0;
    std::string asString() const { ++formats; return Value::asString(); }
    std::string_view asStringView() const { ++views; return Value::asStringView(); }
};
static size_t rng=0, randomCalls=0;
uint64_t fastRandomBelow(uint64_t size) { ++randomCalls; return ++rng % size; }
// Reference behavior, including its existing Value conversions and keyword case rules.
size_t referenceIndex(const TrackedValue &v, size_t size) {
    if(!size) return size;
    const auto text=v.asString();
    if(text=="last") return size-1;
    if(text=="random" || text=="any") return fastRandomBelow(size);
    const double n=v.get<double>();
    if(!std::isfinite(n)) return size;
    const double i=std::floor(n)-1;
    return i<0 || i>=double(size) ? size : size_t(i);
}
#define Value TrackedValue
'''+resolver+r'''
struct List { std::vector<Value> items; };
struct Thread { List *list; std::vector<Value> valueStack; unsigned pc=0; };
enum class BytecodeStackKind { Value };
enum class BytecodeOp { DeleteFromList, DeleteAllOfList, InsertInList, ReplaceInList, ItemOfList };
struct Instruction { unsigned a=0; };
List *listAt(Thread &thread, unsigned) { return thread.list; }
Value popValue(Thread &thread, BytecodeStackKind) { auto v=std::move(thread.valueStack.back()); thread.valueStack.pop_back(); return v; }
constexpr unsigned MAX_LIST_ITEMS=200000;
#define SE_CASE(name) case BytecodeOp::name:
#define SE_NEXT() return
void execute(BytecodeOp op, Thread &thread) { Instruction instr; switch(op) {
'''+cases+r'''
}}
void referenceExecute(BytecodeOp op, Thread &t) {
    Value index=t.valueStack.back(); t.valueStack.pop_back();
    List *list=t.list;
    if(op==BytecodeOp::ItemOfList) {
        Value result;
        if(list && !list->items.empty()) {
            const auto i=referenceIndex(index,list->items.size());
            if(i<list->items.size()) result=list->items[i];
        }
        t.valueStack.push_back(result);
    } else if(op==BytecodeOp::DeleteFromList) {
        if(list) {
            const auto text=index.asString();
            if(text=="all") list->items.clear();
            else if(text=="last" && !list->items.empty()) list->items.pop_back();
            else if((text=="random" || text=="any") && !list->items.empty())
                list->items.erase(list->items.begin()+fastRandomBelow(list->items.size()));
            else {
                const double d=index.get<double>();
                const double i=std::floor(d)-1;
                if(std::isfinite(d) && i>=0 && i<double(list->items.size()))
                    list->items.erase(list->items.begin()+size_t(i));
            }
        }
    } else {
        Value item=t.valueStack.back(); t.valueStack.pop_back();
        if(list && op==BytecodeOp::ReplaceInList && !list->items.empty()) {
            const auto i=referenceIndex(index,list->items.size());
            if(i<list->items.size()) list->items[i]=item;
        } else if(list && op==BytecodeOp::InsertInList) {
            const auto text=index.asString();
            size_t pos=list->items.size()+1;
            if(text=="last") pos=list->items.size();
            else if(text=="random" || text=="any") pos=fastRandomBelow(list->items.size()+1);
            else {
                const double d=index.get<double>(), i=std::floor(d)-1;
                if(std::isfinite(d) && i>=0 && i<=double(list->items.size())) pos=size_t(i);
            }
            if(pos<=list->items.size()) {
                list->items.insert(list->items.begin()+pos,item);
                if(list->items.size()>MAX_LIST_ITEMS) list->items.pop_back();
            }
        }
    }
    ++t.pc;
}
void same(const std::vector<Value> &a,const std::vector<Value> &b) {
    assert(a.size()==b.size());
    for(size_t i=0;i<a.size();++i) assert(a[i].getTag()==b[i].getTag() && a[i].asString()==b[i].asString());
}
int main(int argc,char**) {
    std::vector<Value> values;
    for(double n : {-1e300,-2.,-0.,0.,.5,1.,1.999,2.,3.,4.,200000.,200001.,1e300,
        std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}) values.emplace_back(n);
    for(const char *s : {"last","random","any","all","LAST","Random"," last","last ",""," ","1","1.99","3","4","200000","NaN","Infinity","0x2","0b10","0o2","\xc2\xa0" "2\xe3\x80\x80","garbage"}) values.emplace_back(std::string(s));
    values.emplace_back(true); values.emplace_back(false); values.emplace_back(Undefined{});
    values.emplace_back(Color{0,0,0,0}); values.emplace_back(Color{0,0,100,0});
    for(const auto &v:values) for(size_t size : {0u,1u,2u,4096u,200000u}) for(size_t seed : {0u,13u,100u}) {
        rng=seed; randomCalls=0; const auto expected=referenceIndex(v,size); const auto calls=randomCalls;
        rng=seed; randomCalls=0; const auto actual=resolveListIndex(v,size);
        assert(actual==expected && randomCalls==calls);
    }
    for(const auto &v:values) for(int count : {-1,0,1,3,200000})
    for(auto op : {BytecodeOp::DeleteFromList,BytecodeOp::InsertInList,BytecodeOp::ReplaceInList,BytecodeOp::ItemOfList}) {
        List original;
        for(int i=0;i<count;++i) original.items.emplace_back(i+10);
        List a=original,b=original;
        Thread t1{count<0?nullptr:&a}, t2{count<0?nullptr:&b};
        t1.valueStack.emplace_back(12345); // preserved caller stack
        if(op==BytecodeOp::InsertInList || op==BytecodeOp::ReplaceInList) t1.valueStack.emplace_back(999);
        t1.valueStack.push_back(v); t2.valueStack=t1.valueStack;
        rng=7; randomCalls=0; referenceExecute(op,t1); const auto calls=randomCalls;
        rng=7; randomCalls=0; execute(op,t2); assert(randomCalls==calls);
        assert(t1.pc==t2.pc); same(a.items,b.items); same(t1.valueStack,t2.valueStack);
    }
    TrackedValue::formats=0;
    for(const auto &v:values) resolveListIndex(v,1000);
    assert(TrackedValue::formats==0);
    std::cout<<"PASS: numeric/string/boolean/color indices, missing lists, empty lists, bounds, insertion cap, RNG calls and VM stacks; zero index formatting\n";
    if(argc>1) {
        std::vector<Value> indices;
        for(int i=1;i<=4096;++i) indices.emplace_back(i);
        size_t sums[2]={};
        for(int trial=0;trial<3;++trial) for(int kind=0;kind<2;++kind) {
            TrackedValue::formats=0;
            const auto begin=std::chrono::steady_clock::now();
            size_t sum=0;
            for(int i=0;i<1000000;++i) sum+=kind?resolveListIndex(indices[i%4096],4096):referenceIndex(indices[i%4096],4096);
            const auto us=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-begin).count();
            sums[kind]=sum;
            std::cout<<"BENCH trial="<<trial<<" optimized="<<kind<<" lookups=1000000 us="<<us<<" formats="<<TrackedValue::formats<<" checksum="<<sum<<"\n";
        }
        assert(sums[0]==sums[1]);
    }
}
#undef Value
''')
    subprocess.run(['cc','-O2','-I'+str(ryu),'-c',str(ryu/'ryu/d2s.c'),'-o',str(tmp/'d2s.o')],check=True)
    includes = [tmp,root/'include',root/'include/runtime',json_include,expected_include,ryu]
    command = ['c++','-std=c++17','-O2','-include','vector']
    if not benchmark: command += ['-fsanitize=address,undefined']
    command += ['-I'+str(p) for p in includes]
    subprocess.run(command+[str(tmp/'test.cpp'),str(root/'source/runtime/value.cpp'),str(root/'source/runtime/math.cpp'),str(tmp/'d2s.o'),'-o',str(tmp/'test')],check=True)
    subprocess.run([str(tmp/'test')] + (['--benchmark'] if benchmark else []),check=True)
