# Copyright (C) 2018 Jeff Stevens
# This software is licensed under the GNU GPL v3 https://www.gnu.org/licenses/gpl-3.0.html

# LOG_LEVEL = 0  Disables logging.
# LOG_LEVEL = 1  Logs a one line summary each time a card is load balanced.
# LOG_LEVEL = 2  Logs additional detailed information about each step of the load balancing process.
LOG_LEVEL = 0

import sys
import anki
import datetime
from aqt import mw
from aqt import gui_hooks
from anki.scheduler.v2 import Scheduler as V2Scheduler


def log_info(message):
    if LOG_LEVEL >= 1:
        sys.stdout.write(message)


def log_debug(message):
    if LOG_LEVEL >= 2:
        sys.stdout.write(message)


def load_balanced_ivl(card, ivl):
    """Return the (largest) interval that has the least number of cards and falls within the 'fuzz'"""
    orig_ivl = int(ivl)
    min_ivl, max_ivl = V2Scheduler._fuzzIvlRange(V2Scheduler,orig_ivl)
    min_num_cards = 18446744073709551616        # Maximum number of rows in an sqlite table?
    best_ivl = 1
    for check_ivl in range(min_ivl, max_ivl + 1):
        num_cards = card.col.db.scalar("""select count() from cards where due = ? and queue = 2""",
                                       card.col.sched.today + check_ivl)
        if num_cards <= min_num_cards:
            best_ivl = check_ivl
            log_debug("> ")
            min_num_cards = num_cards
        else:
            log_debug("  ")
        log_debug("check_ivl {0:<4} num_cards {1:<4} best_ivl {2:<4}\n".format(check_ivl, num_cards, best_ivl))
    log_info("{0:<28} orig_ivl {1:<4} min_ivl {2:<4} max_ivl {3:<4} best_ivl {4:<4}\n"
             .format(str(datetime.datetime.now()), orig_ivl, min_ivl, max_ivl, best_ivl))
    return best_ivl

def adjust_ivl(self,
              card,
              ease):
    assert card is not None
    card.ivl = load_balanced_ivl(card, card.ivl)

gui_hooks.reviewer_did_answer_card.append(adjust_ivl)
