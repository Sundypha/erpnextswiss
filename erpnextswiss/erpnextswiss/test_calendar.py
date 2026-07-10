# -*- coding: utf-8 -*-
# Copyright (c) 2026, libracore and Contributors
# License: GNU General Public License v3. See license.txt
#
# Unit tests for the deterministic (offline) Swiss holiday computation.
# Run with:  bench --site <site> run-tests --module erpnextswiss.erpnextswiss.test_calendar

import unittest
from datetime import date

from erpnextswiss.erpnextswiss.calendar import _easter, parse_holidays


class TestSwissHolidays(unittest.TestCase):
    def test_gl_2026_exact(self):
        # Acceptance: Glarus 2026 -- incl. the canton-specific "Näfelser Fahrt"
        # (first Thursday in April) -- computed with NO network call.
        self.assertEqual(
            parse_holidays('GL', '2026'),
            [
                {'date': '01.01.2026', 'description': 'Neujahr'},
                {'date': '02.04.2026', 'description': 'Näfelser Fahrt'},
                {'date': '03.04.2026', 'description': 'Karfreitag'},
                {'date': '06.04.2026', 'description': 'Ostermontag'},
                {'date': '14.05.2026', 'description': 'Auffahrt'},
                {'date': '25.05.2026', 'description': 'Pfingstmontag'},
                {'date': '01.08.2026', 'description': 'Bundesfeier'},
                {'date': '25.12.2026', 'description': 'Weihnachten'},
                {'date': '26.12.2026', 'description': 'Stephanstag'},
            ],
        )

    def test_easter_2026(self):
        self.assertEqual(_easter(2026), date(2026, 4, 5))

    def test_year_accepts_int_and_str(self):
        self.assertEqual(parse_holidays('GL', 2026), parse_holidays('GL', '2026'))

    def test_result_is_sorted_by_date(self):
        for region in ('ZH', 'GL', 'TI', 'VS'):
            result = parse_holidays(region, '2026')
            self.assertTrue(result)
            keys = [(h['date'][6:10], h['date'][3:5], h['date'][0:2]) for h in result]
            self.assertEqual(keys, sorted(keys), region)

    def test_ticino_has_no_karfreitag(self):
        descriptions = [h['description'] for h in parse_holidays('TI', '2026')]
        self.assertNotIn('Karfreitag', descriptions)

    def test_unknown_region_returns_national_only(self):
        self.assertEqual(
            [h['description'] for h in parse_holidays('XX', '2026')],
            ['Neujahr', 'Auffahrt', 'Bundesfeier', 'Weihnachten'],
        )


if __name__ == '__main__':
    unittest.main()
