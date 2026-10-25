#ifndef COMMON_H
#define COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <time.h>

#ifdef _WIN32
    #include <windows.h>
    #include <conio.h>
#else
    #include <unistd.h>
    #include <termios.h>
#endif

/* ANSI Terminal Color Codes */
#define ANSI_RESET        "\x1b[0m"
#define ANSI_BOLD         "\x1b[1m"
#define ANSI_DIM          "\x1b[2m"
#define ANSI_UNDERLINE    "\x1b[4m"

/* Standard Foreground Colors */
#define ANSI_FG_BLACK     "\x1b[30m"
#define ANSI_FG_RED       "\x1b[31m"
#define ANSI_FG_GREEN     "\x1b[32m"
#define ANSI_FG_YELLOW    "\x1b[33m"
#define ANSI_FG_BLUE      "\x1b[34m"
#define ANSI_FG_MAGENTA   "\x1b[35m"
#define ANSI_FG_CYAN      "\x1b[36m"
#define ANSI_FG_WHITE     "\x1b[37m"

/* Bright Foreground Colors */
#define ANSI_FG_BRIGHT_BLACK   "\x1b[90m"
#define ANSI_FG_BRIGHT_RED     "\x1b[91m"
#define ANSI_FG_BRIGHT_GREEN   "\x1b[92m"
#define ANSI_FG_BRIGHT_YELLOW  "\x1b[93m"
#define ANSI_FG_BRIGHT_BLUE    "\x1b[94m"
#define ANSI_FG_BRIGHT_MAGENTA "\x1b[95m"
#define ANSI_FG_BRIGHT_CYAN    "\x1b[96m"
#define ANSI_FG_BRIGHT_WHITE   "\x1b[97m"

/* Background Colors */
#define ANSI_BG_DARK_BLUE  "\x1b[48;5;18m"
#define ANSI_BG_CYAN       "\x1b[46m"
#define ANSI_BG_BLUE       "\x1b[44m"
#define ANSI_BG_RED        "\x1b[41m"
#define ANSI_BG_GREEN      "\x1b[42m"
#define ANSI_BG_DARK_GRAY  "\x1b[48;5;236m"

/* Unicode Box Drawing Characters (UTF-8) */
#define BOX_H           "─"
#define BOX_V           "│"
#define BOX_TL          "┌"
#define BOX_TR          "┐"
#define BOX_BL          "└"
#define BOX_BR          "┘"
#define BOX_T_DOWN      "┬"
#define BOX_T_UP        "┴"
#define BOX_T_RIGHT     "├"
#define BOX_T_LEFT      "┤"
#define BOX_CROSS       "┼"

/* Double Line Box Drawing */
#define DBOX_H          "═"
#define DBOX_V          "║"
#define DBOX_TL         "╔"
#define DBOX_TR         "╗"
#define DBOX_BL         "╚"
#define DBOX_BR         "╝"
#define DBOX_T_DOWN     "╦"
#define DBOX_T_UP       "╩"
#define DBOX_T_RIGHT    "╠"
#define DBOX_T_LEFT     "╣"
#define DBOX_CROSS      "╬"

/* Status Symbols */
#define SYM_BULLET      "●"
#define SYM_CHECK       "✔"
#define SYM_CROSS       "✘"
#define SYM_ARROW       "➔"
#define SYM_TRIANGLE    "►"

#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))

#endif /* COMMON_H */
