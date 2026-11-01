#!/usr/bin/env python3
"""Exercise actual typed-op executor cases and compiler emitters with sanitizers."""
from pathlib import Path
import re
import subprocess
import tempfile
root = Path(__file__).resolve().parents[1]
header = (root/'include/runtime/bytecode.hpp').read_text()
executor = (root/'source/runtime/bytecode_executor.cpp').read_text()
operators = (root/'source/runtime/blocks/operators.cpp').read_text()
def enum(name):
    start = header.index('enum class '+name)
    return header[start:header.index('};',start)+2]
cases = executor[executor.index('            SE_CASE(NumAdd)'):executor.index('            SE_CASE(CallNative)')]
emitters = operators[operators.index('// Typed arithmetic and logic'):]
assert int(re.search(r'bytecodeCacheVersion = (\d+)',header)[1]) >= 2
with tempfile.TemporaryDirectory(prefix='typed-bytecode-') as tmp:
    tmp = Path(tmp)
    (tmp/'test.cpp').write_text(r'''
#include <cassert>
#include <cmath>
#include <cstdint>
#include <limits>
#include <string>
#include <utility>
#include <vector>
'''+enum('BytecodeOp')+'\n'+enum('BytecodeStackKind')+r'''
struct Thread {std::vector<double> numberStack;std::vector<bool> boolStack;unsigned pc=0;};
#define SE_CASE(name) case BytecodeOp::name:
#define SE_NEXT() return
void execute(BytecodeOp op, Thread &thread) { switch(op) {
'''+cases+r'''
default:assert(false);
}}
struct Compiler {
std::vector<std::pair<std::string,BytecodeStackKind>> inputs;
std::vector<BytecodeOp> code;
unsigned here(){return code.size();}
void compileInput(void*,const char*name,BytecodeStackKind kind){inputs.emplace_back(name,kind);}
void emit(BytecodeOp op){code.push_back(op);}
};
#define SCRATCH_BYTECODE_BLOCK(ns,name) bool emit_##name(Compiler &compiler,void *block,unsigned &outFirstInstr)
'''+emitters+r'''
int main(){
    const double values[]={0.,-0.,1.,-3.,1.5,1e300,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()};
    for (double a:values) for(double b:values) for(int op=0;op<4;++op) {
        Thread t;t.numberStack={123.5,a,b};
        const BytecodeOp code[]={BytecodeOp::NumAdd,BytecodeOp::NumSubtract,BytecodeOp::NumMultiply,BytecodeOp::NumDivide};
        double expected=op==0?a+b:op==1?a-b:op==2?a*b:a/b;
        execute(code[op],t);
        assert(t.pc==1&&t.numberStack.size()==2&&t.numberStack[0]==123.5);
        double result=t.numberStack.back();
        if(std::isnan(expected))assert(std::isnan(result));else assert(result==expected);
        if(expected==0)assert(std::signbit(result)==std::signbit(expected));
    }
    for(bool a:{false,true})for(bool b:{false,true}) {
        for(auto op:{BytecodeOp::BooleanAnd,BytecodeOp::BooleanOr}) {
            Thread t;t.boolStack={true,a,b};execute(op,t);
            assert(t.pc==1&&t.boolStack.size()==2&&t.boolStack[0]);
            assert(t.boolStack.back()==(op==BytecodeOp::BooleanAnd?(a&&b):(a||b)));
        }
        Thread t;t.boolStack={true,a};execute(BytecodeOp::BooleanNot,t);
        assert(t.pc==1&&t.boolStack.size()==2&&t.boolStack.back()==!a);
    }
    using Emitter=bool(*)(Compiler&,void*,unsigned&);
    const Emitter functions[]={emit_add,emit_subtract,emit_multiply,emit_divide,emit_and,emit_or,emit_not};
    const BytecodeOp codes[]={BytecodeOp::NumAdd,BytecodeOp::NumSubtract,BytecodeOp::NumMultiply,BytecodeOp::NumDivide,BytecodeOp::BooleanAnd,BytecodeOp::BooleanOr,BytecodeOp::BooleanNot};
    for(int i=0;i<7;++i) {
        Compiler c;unsigned first=999;assert(functions[i](c,nullptr,first));
        assert(first==0&&c.code==std::vector<BytecodeOp>{codes[i]});
        assert(c.inputs.size()==(i==6?1:2));
        assert(c.inputs[0].first==(i<4?"NUM1":i==6?"OPERAND":"OPERAND1"));
        for(auto &input:c.inputs)assert(input.second==(i<4?BytecodeStackKind::Number:BytecodeStackKind::Boolean));
        if(i!=6)assert(c.inputs[1].first==(i<4?"NUM2":"OPERAND2"));
    }
}
''')
    subprocess.run(['c++','-std=c++17','-O2','-fsanitize=address,undefined',str(tmp/'test.cpp'),'-o',str(tmp/'test')],check=True)
    subprocess.run([str(tmp/'test')],check=True)
print('PASS: typed-op stacks, operand order, IEEE edge cases, boolean truth tables, emitters and cache version')
