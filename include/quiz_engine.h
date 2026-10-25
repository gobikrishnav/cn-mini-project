#ifndef QUIZ_ENGINE_H
#define QUIZ_ENGINE_H

#include "common.h"
#include "ip_calc.h"

typedef struct {
    int total_questions;
    int correct_answers;
    int current_streak;
    int best_streak;
} quiz_session_t;

void quiz_session_init(quiz_session_t *session);
void run_interactive_quiz(quiz_session_t *session);

#endif /* QUIZ_ENGINE_H */
