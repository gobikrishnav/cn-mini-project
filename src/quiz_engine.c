#include "quiz_engine.h"

void quiz_session_init(quiz_session_t *session) {
    if (!session) return;
    session->total_questions = 0;
    session->correct_answers = 0;
    session->current_streak = 0;
    session->best_streak = 0;
}

static void shuffle_options(char options[4][64], int *correct_idx) {
    int orig_correct = *correct_idx;
    for (int i = 3; i > 0; i--) {
        int j = rand() % (i + 1);
        if (i != j) {
            char temp[64];
            strncpy(temp, options[i], sizeof(temp));
            strncpy(options[i], options[j], sizeof(options[i]));
            strncpy(options[j], temp, sizeof(options[j]));

            if (orig_correct == i) orig_correct = j;
            else if (orig_correct == j) orig_correct = i;
        }
    }
    *correct_idx = orig_correct;
}

void run_interactive_quiz(quiz_session_t *session) {
    if (!session) return;

    srand((unsigned int)time(NULL));

    while (1) {
        printf("\033[2J\033[H");
        printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_YELLOW "╔══════════════════════════════════════════════════════════════════════════╗" ANSI_RESET "\n");
        printf("  " ANSI_BOLD ANSI_FG_BRIGHT_YELLOW "║           COMPUTER NETWORKS VIVA & EXAM SUBNETTING TRAINER               ║" ANSI_RESET "\n");
        printf("  " ANSI_BOLD ANSI_FG_BRIGHT_YELLOW "╚══════════════════════════════════════════════════════════════════════════╝" ANSI_RESET "\n");

        double accuracy = session->total_questions > 0 ?
            ((double)session->correct_answers / session->total_questions) * 100.0 : 0.0;

        printf("  " ANSI_FG_BRIGHT_WHITE "Score: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%d" ANSI_RESET "/"
               ANSI_BOLD ANSI_FG_WHITE "%d" ANSI_RESET " (%.1f%%) | "
               "Streak: " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "%d" ANSI_RESET " | "
               "Best Streak: " ANSI_BOLD ANSI_FG_BRIGHT_MAGENTA "%d" ANSI_RESET " | [Press 'Q' to Exit]\n",
               session->correct_answers, session->total_questions, accuracy,
               session->current_streak, session->best_streak);
        printf("  " ANSI_FG_BRIGHT_BLACK "──────────────────────────────────────────────────────────────────────────" ANSI_RESET "\n\n");

        int qtype = rand() % 4;
        char question_text[256];
        char explanation[512];
        char options[4][64];
        int correct_idx = 0;

        if (qtype == 0) {
            /* Subnet Mask from CIDR */
            int cidr = 20 + (rand() % 10); /* 20 to 29 */
            ipv4_t mask = cidr_to_mask(cidr);
            char mask_str[16];
            ipv4_to_str(mask, mask_str, sizeof(mask_str));

            snprintf(question_text, sizeof(question_text),
                     "What is the standard subnet mask for prefix length /%d ?", cidr);

            snprintf(options[0], sizeof(options[0]), "%s", mask_str);

            /* Generate distractors */
            ipv4_t d1 = cidr_to_mask(cidr > 20 ? cidr - 1 : 28);
            ipv4_t d2 = cidr_to_mask(cidr < 29 ? cidr + 1 : 21);
            ipv4_t d3 = (mask & 0xFFFFFF00) | 224;
            char s1[16], s2[16], s3[16];
            ipv4_to_str(d1, s1, sizeof(s1));
            ipv4_to_str(d2, s2, sizeof(s2));
            ipv4_to_str(d3, s3, sizeof(s3));

            snprintf(options[1], sizeof(options[1]), "%s", s1);
            snprintf(options[2], sizeof(options[2]), "%s", s2);
            snprintf(options[3], sizeof(options[3]), "%s", s3);

            snprintf(explanation, sizeof(explanation),
                     "Prefix /%d has %d network bits (1s) and %d host bits (0s). In decimal notation: %s.",
                     cidr, cidr, 32 - cidr, mask_str);
        } else if (qtype == 1) {
            /* Usable Host Count */
            int cidr = 23 + (rand() % 7); /* 23 to 29 */
            int host_bits = 32 - cidr;
            uint64_t usable = (1ULL << host_bits) - 2;

            snprintf(question_text, sizeof(question_text),
                     "How many usable host IP addresses can be assigned in a /%d subnet?", cidr);

            snprintf(options[0], sizeof(options[0]), "%llu hosts", (unsigned long long)usable);
            snprintf(options[1], sizeof(options[1]), "%llu hosts", (unsigned long long)(usable + 2)); /* Total IPs without subtracting 2 */
            snprintf(options[2], sizeof(options[2]), "%llu hosts", (unsigned long long)(usable * 2));
            snprintf(options[3], sizeof(options[3]), "%llu hosts", (unsigned long long)(usable > 4 ? usable / 2 : 14));

            snprintf(explanation, sizeof(explanation),
                     "Formula: Usable Hosts = 2^(32 - CIDR) - 2 = 2^%d - 2 = %llu - 2 = %llu hosts. "
                     "(Network and Broadcast addresses cannot be assigned to hosts).",
                     host_bits, (unsigned long long)(usable + 2), (unsigned long long)usable);
        } else if (qtype == 2) {
            /* Network Address calculation */
            int cidr = 24 + (rand() % 6); /* 24 to 29 */
            ipv4_t base = 0xC0A80A00; /* 192.168.10.0 */
            int offset = rand() % 250;
            ipv4_t test_ip = base + offset;
            ipv4_t net = test_ip & cidr_to_mask(cidr);

            char ip_str[16], net_str[16];
            ipv4_to_str(test_ip, ip_str, sizeof(ip_str));
            ipv4_to_str(net, net_str, sizeof(net_str));

            snprintf(question_text, sizeof(question_text),
                     "What is the Network Address for the host IP %s/%d ?", ip_str, cidr);

            snprintf(options[0], sizeof(options[0]), "%s", net_str);

            /* Distractors */
            char d1[16], d2[16], d3[16];
            ipv4_to_str(net + 1, d1, sizeof(d1));
            ipv4_to_str(net | calculate_wildcard(cidr_to_mask(cidr)), d2, sizeof(d2));
            ipv4_to_str(base, d3, sizeof(d3));

            snprintf(options[1], sizeof(options[1]), "%s", d1);
            snprintf(options[2], sizeof(options[2]), "%s", d2);
            snprintf(options[3], sizeof(options[3]), "%s", d3);

            snprintf(explanation, sizeof(explanation),
                     "Perform bitwise AND between IP (%s) and Mask (%s) to zero out all host bits, giving %s.",
                     ip_str, cidr_to_mask(cidr) ? "matching prefix" : "", net_str);
        } else {
            /* Broadcast Address calculation */
            int cidr = 25 + (rand() % 4); /* 25 to 28 */
            ipv4_t base = 0x0A320100; /* 10.50.1.0 */
            int offset = rand() % 250;
            ipv4_t test_ip = base + offset;
            ipv4_t net = test_ip & cidr_to_mask(cidr);
            ipv4_t bcast = net | calculate_wildcard(cidr_to_mask(cidr));

            char ip_str[16], bcast_str[16];
            ipv4_to_str(test_ip, ip_str, sizeof(ip_str));
            ipv4_to_str(bcast, bcast_str, sizeof(bcast_str));

            snprintf(question_text, sizeof(question_text),
                     "What is the Directed Broadcast address for %s/%d ?", ip_str, cidr);

            snprintf(options[0], sizeof(options[0]), "%s", bcast_str);

            char d1[16], d2[16], d3[16];
            ipv4_to_str(bcast - 1, d1, sizeof(d1));
            ipv4_to_str(net, d2, sizeof(d2));
            ipv4_to_str(0x0A3201FF, d3, sizeof(d3));

            snprintf(options[1], sizeof(options[1]), "%s", d1);
            snprintf(options[2], sizeof(options[2]), "%s", d2);
            snprintf(options[3], sizeof(options[3]), "%s", d3);

            snprintf(explanation, sizeof(explanation),
                     "Broadcast address has all host bits set to '1': Network ID OR Wildcard Mask = %s.",
                     bcast_str);
        }

        shuffle_options(options, &correct_idx);

        printf("  " ANSI_BOLD ANSI_FG_BRIGHT_WHITE "Question %d:" ANSI_RESET " %s\n\n",
               session->total_questions + 1, question_text);

        for (int i = 0; i < 4; i++) {
            printf("    " ANSI_BOLD ANSI_FG_CYAN "[%c]" ANSI_RESET " %s\n",
                   'A' + i, options[i]);
        }

        printf("\n  " ANSI_FG_WHITE "Enter your choice (A/B/C/D) or 'Q' to quit: " ANSI_RESET);
        char input[32];
        if (!fgets(input, sizeof(input), stdin)) break;

        char choice = (char)toupper((unsigned char)input[0]);
        if (choice == 'Q') {
            break;
        }

        int user_choice_idx = choice - 'A';
        session->total_questions++;

        if (user_choice_idx == correct_idx) {
            session->correct_answers++;
            session->current_streak++;
            if (session->current_streak > session->best_streak) {
                session->best_streak = session->current_streak;
            }
            printf("\n  " ANSI_BG_GREEN ANSI_FG_BRIGHT_WHITE " ✔ CORRECT! WELL DONE! " ANSI_RESET "\n");
        } else {
            session->current_streak = 0;
            printf("\n  " ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " ✘ INCORRECT! " ANSI_RESET "\n");
            printf("  Correct answer is: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "[%c] %s" ANSI_RESET "\n",
                   'A' + correct_idx, options[correct_idx]);
        }

        printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "Explanation:" ANSI_RESET " %s\n\n", explanation);
        printf("  " ANSI_FG_BRIGHT_BLACK "Press ENTER to continue to next question..." ANSI_RESET);
        getchar();
    }
}
