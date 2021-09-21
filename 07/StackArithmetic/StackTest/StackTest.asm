@14
0;JMP
@SP
A=M-1
M=0
@R13
A=M
0;JMP
@SP
A=M-1
M=-1
@R13
A=M
0;JMP
//          push constant 17
@17
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 17
@17
D=A
@SP
AM=M+1
A=A-1
M=D
//          eq
@39
D=A
@R13
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@8
D;JEQ
@2
0;JMP
//          push constant 17
@17
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 16
@16
D=A
@SP
AM=M+1
A=A-1
M=D
//          eq
@64
D=A
@R13
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@8
D;JEQ
@2
0;JMP
//          push constant 16
@16
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 17
@17
D=A
@SP
AM=M+1
A=A-1
M=D
//          eq
@89
D=A
@R13
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@8
D;JEQ
@2
0;JMP
//          push constant 892
@892
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 891
@891
D=A
@SP
AM=M+1
A=A-1
M=D
//          lt
@114
D=A
@R13
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@8
D;JLT
@2
0;JMP
//          push constant 891
@891
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 892
@892
D=A
@SP
AM=M+1
A=A-1
M=D
//          lt
@139
D=A
@R13
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@8
D;JLT
@2
0;JMP
//          push constant 891
@891
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 891
@891
D=A
@SP
AM=M+1
A=A-1
M=D
//          lt
@164
D=A
@R13
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@8
D;JLT
@2
0;JMP
//          push constant 32767
@32767
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 32766
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
//          gt
@189
D=A
@R13
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@8
D;JGT
@2
0;JMP
//          push constant 32766
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 32767
@32767
D=A
@SP
AM=M+1
A=A-1
M=D
//          gt
@214
D=A
@R13
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@8
D;JGT
@2
0;JMP
//          push constant 32766
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 32766
@32766
D=A
@SP
AM=M+1
A=A-1
M=D
//          gt
@239
D=A
@R13
M=D
@SP
AM=M-1
D=M
A=A-1
D=M-D
@8
D;JGT
@2
0;JMP
//          push constant 57
@57
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 31
@31
D=A
@SP
AM=M+1
A=A-1
M=D
//          push constant 53
@53
D=A
@SP
AM=M+1
A=A-1
M=D
//          add
@SP
AM=M-1
D=M
A=A-1
M=M+D
//          push constant 112
@112
D=A
@SP
AM=M+1
A=A-1
M=D
//          sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
//          neg
@SP
A=M-1
M=-M
//          and
@SP
AM=M-1
D=M
A=A-1
M=M&D
//          push constant 82
@82
D=A
@SP
AM=M+1
A=A-1
M=D
//          or
@SP
AM=M-1
D=M
A=A-1
M=M|D
//          not
@SP
A=M-1
M=!M
