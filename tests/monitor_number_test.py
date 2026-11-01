#!/usr/bin/env python3
"""Exercise actual monitor formatting and Ryu with normal and Xbox math flags.

Configure a build first, or pass --ryu-source pointing at RyuJS's src folder.
No game assets or alternate number formatter are used by this regression.
"""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--ryu-source', type=Path)
args = parser.parse_args()
ryu = args.ryu_source
if ryu is None:
    for commands in sorted(root.glob('build*/compile_commands.json')):
        for item in json.loads(commands.read_text()):
            source = Path(item['file'])
            if source.name == 'd2s.c' and source.parent.name == 'ryu' and source.exists():
                ryu = source.parent.parent
                break
        if ryu is not None:
            break
if ryu is None or not (ryu / 'ryu/d2s.c').exists():
    parser.error('Configure a build with RyuJS, or pass --ryu-source PATH/TO/src')

renderer = (root / 'source/renderer.cpp').read_text()
formatter = renderer[renderer.index('std::string Render::getVariableValueString('):
                     renderer.index('std::string Render::getListValueString(')]
math = (root / 'source/runtime/math.cpp').read_text()
to_string = math[math.index('std::string Math::toString(double number)'):
                 math.index('double Math::degreesToRadians(')]
preamble = r'''
#include <cmath>
#include <iostream>
#include <limits>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>
#include "ryu/d2s.h"
// Only the Value accessors consumed by this presentation function are stubbed.
// Both actual formatting functions and the configured RyuJS source are linked.
struct Value {
    enum Kind { Number, String, Undefined } kind;
    double number = 0;
    std::string text;
    static Value numeric(double n) { return {Number, n, ""}; }
    static Value string(std::string s) { return {String, 0, std::move(s)}; }
    bool isDouble() const { return kind == Number; }
    bool isUndefined() const { return kind == Undefined; }
    template<class T> T get() const {
        if constexpr (std::is_same_v<T, double>) return number;
        else return text;
    }
};
namespace Math { std::string toString(double); }
namespace Render { std::string getVariableValueString(Value); }
'''
checks = r'''
int main() {
    const std::vector<std::pair<double, std::string>> cases = {
        {0.1, "0.1"}, {0.2, "0.2"}, {0.3, "0.3"}, {58.4, "58.4"},
        {0.0, "0"}, {-0.0, "0"}, {-0.2, "-0.2"},
        {1.2345674, "1.234567"}, {1.2345676, "1.234568"},
        {-1.2345674, "-1.234567"}, {-1.2345676, "-1.234568"},
        {0.0000004, "0"}, {-0.0000004, "0"}, {0.0000006, "0.000001"},
        {-0.0000006, "-0.000001"}, {1.9999996, "2"}, {-1.9999996, "-2"},
        // Exact values observed entering the formatter in the Xbox guest.
        // The JSON loader's pre-existing conversion error is separate from
        // the display rounding; do not change these underlying numbers.
        {0x1.9999999999998p-4, "0.1"}, {0x1.9999999999998p-3, "0.2"},
        {-0x1.9999999999998p-3, "-0.2"},
        {0x1.fffffffffffedp+32, "8589934591.999982"},
        {0x1.1ccf385ebc98cp+1023, "1.0000000000000471e+308"},
        {100000000.0, "100000000"}, {8589934591.0, "8589934591"},
        {1e308, "1e+308"}, {-1e308, "-1e+308"},
        {std::numeric_limits<double>::infinity(), "Infinity"},
        {-std::numeric_limits<double>::infinity(), "-Infinity"},
        {std::numeric_limits<double>::quiet_NaN(), "NaN"},
    };
    for (const auto &[number, expected] : cases) {
        const auto actual = Render::getVariableValueString(Value::numeric(number));
        if (actual != expected) {
            std::cerr << "FAIL: monitor " << Math::toString(number)
                      << " -> " << actual << "; expected " << expected << '\n';
            return 1;
        }
    }
    // These representable values cannot change when rounded to six decimals.
    for (double n : {8589934592.0, 8589934592.000002, -8589934592.000002,
                     9007199254740991.0, std::numeric_limits<double>::max()}) {
        if (Render::getVariableValueString(Value::numeric(n)) != Math::toString(n)) return 2;
    }
    for (const auto *s : {"00012", "0.20000000000000001", "1e-7", "text", ""}) {
        if (Render::getVariableValueString(Value::string(s)) != s) return 3;
    }
    if (!Render::getVariableValueString({Value::Undefined}).empty()) return 4;
    std::cout << "PASS: actual numeric monitor rounding, large/nonfinite values, strings and undefined\n";
}
'''
with tempfile.TemporaryDirectory(prefix='monitor-numbers-') as directory:
    directory = Path(directory)
    obj = directory / 'ryu.o'
    subprocess.run(['cc', '-std=c11', '-O1', '-I' + str(ryu), '-c',
                    str(ryu / 'ryu/d2s.c'), '-o', str(obj)], check=True)
    source = directory / 'test.cpp'
    source.write_text(preamble + to_string + formatter + checks)
    for name, flags in [('normal', []), ('xbox-fast-math', ['-ffast-math', '-fno-finite-math-only'])]:
        binary = directory / name
        subprocess.run(['c++', '-std=c++17', '-O1', *flags, '-I' + str(ryu),
                        str(source), str(obj), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
    # Reject the old implementation under the exact problematic flags. The
    # first decimal case fails, so overflow handling cannot mask this check.
    baseline = '''std::string Render::getVariableValueString(Value value) {
        if (value.isDouble()) return Math::toString(std::round(value.get<double>() * 1e6) / 1e6);
        if (value.isUndefined()) return "";
        return value.get<std::string>();
    }\n'''
    source.write_text(preamble + to_string + baseline + checks)
    binary = directory / 'old-format-negative-control'
    subprocess.run(['c++', '-std=c++17', '-O1', '-ffast-math', '-fno-finite-math-only',
                    '-I' + str(ryu), str(source), str(obj), '-o', str(binary)], check=True)
    old = subprocess.run([str(binary)], capture_output=True, text=True)
    assert old.returncode == 1 and '0.09999999999999999' in old.stderr, old.stderr
    print('PASS: old reciprocal-math formatter rejected by the same decimal assertion')
