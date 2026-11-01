#!/usr/bin/env python3
"""Check real Value conversions against uncached parsing, including slot reuse."""
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
cache = root / 'build-xbox/.cache/catalog'
json_include = next(cache.glob('*/src/include/nlohmann/json.hpp')).parents[1]
expected_include = next(cache.glob('*/src/include/nonstd/expected.hpp')).parents[1]
ryu = next(cache.glob('*/src/ryu/d2s.c')).parents[1]
with tempfile.TemporaryDirectory(prefix='value-numeric-cache-') as tmp:
    tmp = Path(tmp)
    (tmp/'se_export.hpp').write_text('#pragma once\n#define SE_EXPORT\n')
    (tmp/'os.hpp').write_text('#pragma once\n')
    (tmp/'renderer.hpp').write_text('''#pragma once
 enum class Renderers { SDL1, SDL2, SDL3, Xbox, NV2A, GX2, OpenGL, OpenGLCore, GDI, D3D9, Headless };
 namespace Render { inline Renderers currentRenderer = Renderers::Headless; }
''')
    (tmp/'log.hpp').write_text('''#pragma once
#include <string>
namespace Log { inline void logCritical(std::string, bool) {} }
''')
    (tmp/'test.cpp').write_text(r'''
#include "value.hpp"
#include <cmath>
#include <iostream>
#include <limits>
void check(const std::string &text) {
    Value a(text), copy(a);
    const auto expected = Math::parseNumber(text);
    for (int i=0;i<100;++i) {
        assert(a.isNumeric()==expected.has_value());
        double n=expected.value_or(0);
        assert(a.asDouble()==n);
        assert(copy.asDouble()==n);
        if (n==0) assert(std::signbit(a.asDouble())==std::signbit(n));
    }
}
int main() {
    for (const auto *text : {"", " ", "\t", "0", "-0", "+1", "01", "1.25", "1e12", "1e-8", "0xFF", "0b101", "0o17", "Infinity", "-Infinity", "NaN", "hello", "1.2.3", "123junk", " 42 ", "\xc2\xa0-2\xe3\x80\x80"}) check(text);
    for(int i=0;i<1000;++i) { check(std::to_string(i)); check("bad"+std::to_string(i)); }
    for (double n : {0.,-0.,1.,-3.,1.25,1e20}) {
        Value numeric(n), text(Math::toString(n));
        assert(numeric==text && text==numeric);
        assert(!(numeric<text) && !(numeric>text));
    }
    assert(Value(true)==Value(std::string("1")));
    assert(Value(false)==Value(std::string("0")));
    assert(!(Value(0)==Value(std::string(""))));
    assert(!(Value(0)==Value(std::string(" "))));
    assert(!(Value(0)==Value(std::string("\t"))));
    assert(Value(std::string("APPLE"))==Value(std::string("apple")));
    assert(!(Value(std::numeric_limits<double>::quiet_NaN())==Value(0)));
    assert(Value(std::numeric_limits<double>::infinity())==Value(std::string("Infinity")));
    std::cout<<"PASS: numeric cache, invalid input, Unicode whitespace, pool reuse, copies, mixed comparisons\n";
}
''')
    subprocess.run(['cc','-O2','-I'+str(ryu),'-c',str(ryu/'ryu/d2s.c'),'-o',str(tmp/'d2s.o')],check=True)
    includes = [tmp,root/'include',root/'include/runtime',json_include,expected_include,ryu]
    command = ['c++','-std=c++17','-O2','-include','vector','-fsanitize=address,undefined'] + ['-I'+str(p) for p in includes]
    subprocess.run(command+[str(tmp/'test.cpp'),str(root/'source/runtime/value.cpp'),str(root/'source/runtime/math.cpp'),str(tmp/'d2s.o'),'-o',str(tmp/'test')],check=True)
    subprocess.run([str(tmp/'test')],check=True)
