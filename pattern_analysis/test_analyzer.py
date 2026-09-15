import tempfile
import unittest
from pathlib import Path

try:
    from .analyzer import (
        analyse_and_store_report,
        analyse_report,
        get_all_analyses,
        get_analysis_by_id,
        init_db,
    )
except ImportError:
    from analyzer import (
        analyse_and_store_report,
        analyse_report,
        get_all_analyses,
        get_analysis_by_id,
        init_db,
    )



class TestPatternAnalyser(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        self.db_path = (
            Path(self.temp_directory.name)
            / "test_sif.db"
        )

        init_db(self.db_path)

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_basic_pattern_detection(self):

        report = """
        Worker was working at height in the plant.
        No fall protection was used.
        """

        result = analyse_report(report)

        self.assertEqual(
            result["activity"],
            "Working at Height",
        )

        self.assertEqual(
            result["location"],
            "Plant",
        )

        self.assertEqual(
            result["barrier_failure"],
            "Fall Protection Failure",
        )

        self.assertTrue(
            result["sif_potential"]
        )

    def test_null_handling(self):

        result = analyse_report(None)

        self.assertFalse(
            result["sif_potential"]
        )

        self.assertEqual(
            result["confidence"],
            0.0,
        )

        self.assertEqual(
            result["status"],
            "empty_report",
        )

    def test_sqlite_storage(self):

        result = analyse_and_store_report(
            report_id="TEST-001",
            report_text="""
            Crane lifting operation at construction site.
            No PPE was used.
            """,
            db_path=self.db_path,
        )

        self.assertTrue(
            result["stored"]
        )

        analysis_id = result["analysis_id"]

        stored = get_analysis_by_id(
            analysis_id,
            self.db_path,
        )

        self.assertIsNotNone(stored)

        self.assertEqual(
            stored["report_id"],
            "TEST-001",
        )

    def test_multiple_records_do_not_overwrite(self):

        analyse_and_store_report(
            report_id="TEST-001",
            report_text="Worker was lifting a suspended load.",
            db_path=self.db_path,
        )

        analyse_and_store_report(
            report_id="TEST-002",
            report_text="Vehicle was travelling on the road.",
            db_path=self.db_path,
        )

        records = get_all_analyses(
            self.db_path
        )

        self.assertEqual(
            len(records),
            2,
        )

        report_ids = {
            record["report_id"]
            for record in records
        }

        self.assertEqual(
            report_ids,
            {"TEST-001", "TEST-002"},
        )

    def test_empty_report_is_not_stored(self):

        result = analyse_and_store_report(
            report_id="EMPTY-001",
            report_text="",
            db_path=self.db_path,
        )

        self.assertFalse(
            result["stored"]
        )

        records = get_all_analyses(
            self.db_path
        )

        self.assertEqual(
            len(records),
            0,
        )

    def test_offshore_keyword_collision(self):
        # 1. Generic work platform should NOT produce Offshore
        scaffold_report = "Worker was working at height without proper fall protection and nearly fell from the platform."
        scaffold_result = analyse_report(scaffold_report)
        self.assertNotEqual(scaffold_result["location"], "Offshore")

        # 2. Genuine offshore platform report SHOULD produce Offshore
        offshore_report = "Worker was on an offshore platform during maintenance."
        offshore_result = analyse_report(offshore_report)
        self.assertEqual(offshore_result["location"], "Offshore")


if __name__ == "__main__":
    unittest.main()