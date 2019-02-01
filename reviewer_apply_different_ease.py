# -*- coding: utf-8 -*-
from __future__ import unicode_literals


"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

some code reused from anki - anki/sched.py which is
     Copyright: Damien Elmes <anki@ichi2.net>

changes: copyright 2018 ijgnord
"""

# To view the ease value of the current and prior card during reviews use the add-on
# Extended Card Stats During Review, https://ankiweb.net/shared/info/1008566916

# in the user interface the ease value has three digits: 250 means 2.5 the prior interval
# Anki internally saves 250 as 2500. 
# only use this add-on if you know the implications of changing the ease factor.
# only use this after carefully reading https://apps.ankiweb.net/docs/manual.html#reviews
# it's not enough to read some random guide from internet that tells you that Anki 
# needs to be optimized. There are some really bad ideas out there.
# This add-on doesn't validate the user input. If you want to change more than the 
# numbers make sure to follow basic Python syntax. Errors here might permanently ruin
# the scheduling of your cards and permanently damage your collection.

####BEGIN USER CONFIG####
AGAIN = lambda fct: max(1300, fct - 200)
HARD  = lambda fct: max(1300, fct - 150)
GOOD  = lambda fct: max(1300, fct)
EASY  = lambda fct: max(1300, fct + 150)

# Example of some insane settings
# I wouldn't use a value that's lower than 1300 because who knows if this might
# break Anki in the future.
# AGAIN = lambda fct: max(1100, fct - 1400)
# HARD  = lambda fct: max(1800, fct - 650)
# GOOD  = lambda fct: max(1800, int(fct*1.1))
# EASY  = lambda fct: max(2200, fct + 370)
####END USER CONFIG######


from anki.hooks import wrap
from anki.sched import Scheduler


def default_ease_changes(fct, ease):
    if ease == 1:
        return max(1300, fct - 200)
    elif ease == 2:
        return max(1300, fct - 150)
    elif ease == 3:
        return max(1300, fct)
    elif ease == 4:
        return max(1300, fct + 150)   


def apply_custom_ease(fct,ease):
    if ease == 1: return AGAIN(fct)
    if ease == 2: return HARD(fct)
    if ease == 3: return GOOD(fct)
    if ease == 4: return EASY(fct)


def try_to_apply_custom_ease(fct,ease):
    try:
        nfct = apply_custom_ease(fct,ease)
    except:
        nfct = default_ease_changes(fct,ease)
    else:
        #minimal input validation
        if not isinstance(nfct,int):
            nfct = default_ease_changes(fct,ease)
        #since Anki multiplies the initial ease by 10 and it only changes
        #the easy by +200/-150/+150 the ease set by Anki is always divisible by 10
        #make sure that the same is true for ease value set by this add-on
        nfct = (nfct//10)*10   # "/" doesn't suffice for Python3 see e.g. https://stackoverflow.com/q/19507808
    return nfct


def adjustedRescheduleLapse(self, card, _old):
    fct = card.factor
    out = _old(self,card)
    card.factor = try_to_apply_custom_ease(fct,1)
    return out
Scheduler._rescheduleLapse = wrap(Scheduler._rescheduleLapse, adjustedRescheduleLapse, "around")



def adjustedRescheduleRev(self, card, ease, _old):
    fct = card.factor
    _old(self, card, ease)
    if self._resched(card):
        card.factor = try_to_apply_custom_ease(fct,ease)
Scheduler._rescheduleRev = wrap(Scheduler._rescheduleRev, adjustedRescheduleRev, "around")
