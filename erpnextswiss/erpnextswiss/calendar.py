# -*- coding: utf-8 -*-
# Copyright (c) 2023-2026, libracore and Contributors
# License: GNU General Public License v3. See license.txt
#
# Swiss public holidays, computed deterministically (no network, stdlib only).
#
# This used to scrape feiertagskalender.ch, which now returns HTTP 403 to
# non-browser requests, so the import silently produced an empty list. The
# holidays are fixed rules, so we compute them instead -- offline and reliably.
#
# The whitelisted signature and return shape are unchanged, so
# public/js/holiday_list.js keeps working as-is:
#
#   parse_holidays(region, year) -> [{'date': 'DD.MM.YYYY', 'description': str}, ...]
#
# Execute manually:
#   $ bench execute erpnextswiss.erpnextswiss.calendar.parse_holidays \
#         --kwargs "{'region': 'GL', 'year': '2026'}"

from datetime import date, timedelta

import frappe

# --- date helpers -----------------------------------------------------------

def _easter(year):
    """Gregorian Easter Sunday (Anonymous Gregorian algorithm / Meeus)."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _first_weekday(year, month, weekday):
    """First <weekday> (Mon=0 .. Sun=6) in the given month."""
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7)


def _nth_weekday(year, month, weekday, n):
    """n-th <weekday> (Mon=0 .. Sun=6) in the given month (n >= 1)."""
    return _first_weekday(year, month, weekday) + timedelta(weeks=n - 1)


# --- holiday definitions ----------------------------------------------------

def _holiday_dates(year):
    """Map holiday key -> (German description, datetime.date) for the given year."""
    easter = _easter(year)
    return {
        'neujahr':            ("Neujahr",              date(year, 1, 1)),
        'berchtoldstag':      ("Berchtoldstag",        date(year, 1, 2)),
        'drei_koenige':       ("Heilige Drei Könige",  date(year, 1, 6)),
        'josefstag':          ("Josefstag",            date(year, 3, 19)),
        'naefelser_fahrt':    ("Näfelser Fahrt",       _first_weekday(year, 4, 3)),   # 1st Thursday in April
        'karfreitag':         ("Karfreitag",           easter - timedelta(days=2)),
        'ostermontag':        ("Ostermontag",          easter + timedelta(days=1)),
        'tag_der_arbeit':     ("Tag der Arbeit",       date(year, 5, 1)),
        'auffahrt':           ("Auffahrt",             easter + timedelta(days=39)),
        'pfingstmontag':      ("Pfingstmontag",        easter + timedelta(days=50)),
        'fronleichnam':       ("Fronleichnam",         easter + timedelta(days=60)),
        'bundesfeier':        ("Bundesfeier",          date(year, 8, 1)),
        'mariae_himmelfahrt': ("Mariä Himmelfahrt",    date(year, 8, 15)),
        'bettag':             ("Eidg. Bettag",         _nth_weekday(year, 9, 6, 3)),   # 3rd Sunday in Sept
        'allerheiligen':      ("Allerheiligen",        date(year, 11, 1)),
        'mariae_empfaengnis': ("Mariä Empfängnis",     date(year, 12, 8)),
        'weihnachten':        ("Weihnachten",          date(year, 12, 25)),
        'stephanstag':        ("Stephanstag",          date(year, 12, 26)),
    }


# Holidays observed in every canton.
NATIONAL = ['neujahr', 'auffahrt', 'bundesfeier', 'weihnachten']

# Additional official public holidays per canton (on top of NATIONAL). Keys are
# the 26 canton codes (unchanged from the previous REGIONS mapping) so
# holiday_list.js keeps working. Based on the standard cantonal public-holiday
# table; regional (commune-level only) holidays are intentionally omitted.
#
# Note: "Eidg. Bettag" (3rd Sunday of September) is computed above but is not
# part of the default cantonal sets -- it falls on a Sunday and the reference
# lists (e.g. GL) do not carry it. Add 'bettag' to a canton below if required.
REGIONS = {
    'AG': ['berchtoldstag', 'karfreitag', 'ostermontag', 'pfingstmontag', 'stephanstag'],
    'AR': ['karfreitag', 'ostermontag', 'pfingstmontag', 'stephanstag'],
    'AI': ['karfreitag', 'ostermontag', 'pfingstmontag', 'fronleichnam', 'mariae_himmelfahrt',
           'allerheiligen', 'mariae_empfaengnis', 'stephanstag'],
    'BL': ['karfreitag', 'ostermontag', 'tag_der_arbeit', 'pfingstmontag', 'stephanstag'],
    'BS': ['karfreitag', 'ostermontag', 'tag_der_arbeit', 'pfingstmontag', 'stephanstag'],
    'BE': ['berchtoldstag', 'karfreitag', 'ostermontag', 'pfingstmontag', 'stephanstag'],
    'FR': ['karfreitag', 'ostermontag', 'pfingstmontag', 'fronleichnam', 'allerheiligen'],
    'GE': ['karfreitag', 'ostermontag', 'pfingstmontag'],
    'GL': ['naefelser_fahrt', 'karfreitag', 'ostermontag', 'pfingstmontag', 'stephanstag'],
    'GR': ['karfreitag', 'ostermontag', 'pfingstmontag', 'stephanstag'],
    'JU': ['berchtoldstag', 'karfreitag', 'ostermontag', 'tag_der_arbeit', 'pfingstmontag',
           'fronleichnam', 'mariae_himmelfahrt', 'allerheiligen'],
    'LU': ['karfreitag', 'ostermontag', 'pfingstmontag', 'fronleichnam', 'mariae_himmelfahrt',
           'allerheiligen', 'mariae_empfaengnis', 'stephanstag'],
    'NE': ['berchtoldstag', 'karfreitag', 'ostermontag', 'tag_der_arbeit', 'pfingstmontag'],
    'NW': ['josefstag', 'karfreitag', 'ostermontag', 'pfingstmontag', 'fronleichnam',
           'mariae_himmelfahrt', 'allerheiligen', 'mariae_empfaengnis', 'stephanstag'],
    'OW': ['karfreitag', 'ostermontag', 'pfingstmontag', 'fronleichnam', 'mariae_himmelfahrt',
           'allerheiligen', 'mariae_empfaengnis', 'stephanstag'],
    'SH': ['berchtoldstag', 'karfreitag', 'ostermontag', 'tag_der_arbeit', 'pfingstmontag', 'stephanstag'],
    'SZ': ['drei_koenige', 'josefstag', 'karfreitag', 'ostermontag', 'pfingstmontag', 'fronleichnam',
           'mariae_himmelfahrt', 'allerheiligen', 'mariae_empfaengnis', 'stephanstag'],
    'SO': ['berchtoldstag', 'karfreitag', 'ostermontag', 'tag_der_arbeit', 'pfingstmontag',
           'fronleichnam', 'allerheiligen'],
    'SG': ['karfreitag', 'ostermontag', 'pfingstmontag', 'fronleichnam', 'allerheiligen',
           'mariae_empfaengnis', 'stephanstag'],
    'TI': ['drei_koenige', 'josefstag', 'ostermontag', 'tag_der_arbeit', 'pfingstmontag', 'fronleichnam',
           'mariae_himmelfahrt', 'allerheiligen', 'mariae_empfaengnis', 'stephanstag'],   # no Karfreitag
    'TG': ['berchtoldstag', 'karfreitag', 'ostermontag', 'tag_der_arbeit', 'pfingstmontag', 'stephanstag'],
    'UR': ['drei_koenige', 'josefstag', 'karfreitag', 'ostermontag', 'pfingstmontag', 'fronleichnam',
           'mariae_himmelfahrt', 'allerheiligen', 'mariae_empfaengnis', 'stephanstag'],
    'VD': ['berchtoldstag', 'karfreitag', 'ostermontag', 'pfingstmontag'],
    'VS': ['josefstag', 'fronleichnam', 'mariae_himmelfahrt', 'allerheiligen', 'mariae_empfaengnis'],
    'ZG': ['karfreitag', 'ostermontag', 'pfingstmontag', 'fronleichnam', 'mariae_himmelfahrt',
           'allerheiligen', 'mariae_empfaengnis', 'stephanstag'],
    'ZH': ['berchtoldstag', 'karfreitag', 'ostermontag', 'tag_der_arbeit', 'pfingstmontag', 'stephanstag'],
}


@frappe.whitelist()
def parse_holidays(region, year):
    """Return the public holidays for a Swiss canton and year, computed offline.

    :param region: canton code (e.g. 'GL', 'ZH', ...)
    :param year:   year as int or string
    :returns:      [{'date': 'DD.MM.YYYY', 'description': str}, ...] sorted by date
    """
    year = int(year)
    region = (region or "").strip().upper()

    definitions = _holiday_dates(year)

    # NATIONAL first, then the canton-specific set; de-duplicate, keep known keys.
    keys = []
    for key in NATIONAL + REGIONS.get(region, []):
        if key not in keys and key in definitions:
            keys.append(key)

    holidays = sorted((definitions[key] for key in keys), key=lambda item: item[1])
    return [{'date': d.strftime('%d.%m.%Y'), 'description': description} for description, d in holidays]
