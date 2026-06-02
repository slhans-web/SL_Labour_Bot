import unittest
import calculators

class TestCalculators(unittest.TestCase):
    def test_epf_etf_no_allowance(self):
        basic = 50000.0
        res = calculators.calculate_epf_etf(basic)
        self.assertEqual(res["total_earnings"], 50000.0)
        self.assertEqual(res["epf_employee"], 4000.0)    # 8% of 50k
        self.assertEqual(res["epf_employer"], 6000.0)    # 12% of 50k
        self.assertEqual(res["etf_employer"], 1500.0)    # 3% of 50k
        self.assertEqual(res["net_salary_base"], 46000.0) # 50k - 4k

    def test_epf_etf_with_allowance(self):
        basic = 60000.0
        allowance = 10000.0
        res = calculators.calculate_epf_etf(basic, allowance)
        self.assertEqual(res["total_earnings"], 70000.0)
        self.assertEqual(res["epf_employee"], 5600.0)    # 8% of 70k
        self.assertEqual(res["epf_employer"], 8400.0)    # 12% of 70k
        self.assertEqual(res["etf_employer"], 2100.0)    # 3% of 70k

    def test_gratuity_eligible(self):
        basic = 80000.0
        years = 6
        res = calculators.calculate_gratuity(basic, years)
        self.assertTrue(res["eligible"])
        self.assertEqual(res["gratuity_amount"], 240000.0) # (80k / 2) * 6

    def test_gratuity_not_eligible(self):
        basic = 80000.0
        years = 4
        res = calculators.calculate_gratuity(basic, years)
        self.assertFalse(res["eligible"])
        self.assertEqual(res["gratuity_amount"], 0.0)

    def test_overtime(self):
        basic = 60000.0
        hours = 10.0
        res = calculators.calculate_overtime(basic, hours)
        self.assertEqual(res["hourly_rate"], 250.0)       # 60000 / 240
        self.assertEqual(res["ot_hourly_rate"], 375.0)    # 250 * 1.5
        self.assertEqual(res["ot_pay"], 3750.0)          # 375 * 10
        self.assertEqual(res["total_pay"], 63750.0)      # 60k + 3750

if __name__ == "__main__":
    unittest.main()
