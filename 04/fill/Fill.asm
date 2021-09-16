// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should reMAIN fully black as long as the key is pressed. 
// When no key is pressed, the program WHITE_SCREEN the screen, i.e. writes
// "white" in every pixel;
// the screen should reMAIN fully clear as long as no key is pressed.

// Put your code here.
// ------ MAIN -----
(MAIN)
    @KBD
    D = M
    @BLACK_SCREEN
    D; JGT
    @WHITE_SCREEN
    0; JMP

// ------ black screen -----
(BLACK_SCREEN)
    // setup
    @8192
    D = A
    @SCREEN
    D = D + A
    @addressCounter
    M = D

    (BLACK_SCREEN_LOOP)
        @addressCounter
        A = M
        M = -1
        @addressCounter
        M = M - 1
        D = M

        @SCREEN
        D = D - A
        @BLACK_SCREEN_LOOP
        D; JGE
        @MAIN
        0; JMP

// ------ white screen -----
(WHITE_SCREEN)
    // setup
    @8192
    D = A
    @SCREEN
    D = D + A
    @addressCounter
    M = D

    (WHITE_SCREEN_LOOP)
        @addressCounter
        A = M
        M = 0
        @addressCounter
        M = M - 1
        D = M

        @SCREEN
        D = D - A
        @WHITE_SCREEN_LOOP
        D; JGE
        @MAIN
        0; JMP
