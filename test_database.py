import unittest
import os
import sqlite3
import database
import config

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Override DB_FILE to run on a test database
        config.DB_FILE = "test_labor_data.db"
        database.DB_FILE = "test_labor_data.db"
        # Initialize
        database.init_db()

    def tearDown(self):
        # Remove test database
        if os.path.exists("test_labor_data.db"):
            os.remove("test_labor_data.db")

    def test_seeding_and_counts(self):
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM wages_boards")
        self.assertGreater(cursor.fetchone()[0], 0)
        
        cursor.execute("SELECT COUNT(*) FROM labor_offices")
        self.assertGreater(cursor.fetchone()[0], 0)
        
        cursor.execute("SELECT COUNT(*) FROM faq")
        self.assertGreater(cursor.fetchone()[0], 0)
        
        conn.close()

    def test_get_all_wages_boards(self):
        boards = database.get_all_wages_boards()
        self.assertTrue(len(boards) > 0)
        self.assertEqual(boards[0]["trade_name_en"], "Security Services Trade")

    def test_save_and_retrieve_history(self):
        user_id = 999999
        username = "test_officer"
        database.save_calculation(
            user_id=user_id,
            username=username,
            calc_type="EPF/ETF",
            inputs_dict={"basic": 50000, "allowances": 0},
            results_dict={"epf_employee": 4000, "epf_employer": 6000}
        )
        
        history = database.get_user_history(user_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["calc_type"], "EPF/ETF")
        self.assertEqual(history[0]["inputs"]["basic"], 50000)
        self.assertEqual(history[0]["results"]["epf_employee"], 4000)

    def test_search_faq(self):
        results = database.search_faqs("EPF")
        self.assertTrue(len(results) > 0)

if __name__ == "__main__":
    unittest.main()
