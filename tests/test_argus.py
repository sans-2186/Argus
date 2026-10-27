"""
Automated Unit & Integration Tests for ARGUS (`tests/test_argus.py`)
Compatible with both `pytest` and `python3 -m unittest discover -s tests`.
Verifies:
1. Authentic data manifest & schema completeness (no missing URLs, periods, or units).
2. Deterministic financial calculations (YoY/QoQ %, basis points, DSO, SBC restatement math).
3. Deterministic 4-category classification rules:
   - Verified numerical mismatch
   - Potential narrative–metric divergence
   - No identified discrepancy
   - Insufficient evidence
4. AI/Concept-Aware Semantic Matching vs. Exact Keyword Baseline evaluation metrics.
"""

import os
import sys
import unittest

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import argus_engine as ae


class TestArgusCalculationsAndRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ae.load_argus_data(os.path.join(PROJECT_ROOT, "data"))

    def test_source_manifest_integrity(self):
        """Verify all sources have authentic URLs, publication dates, reporting periods, and extracted metrics."""
        sources = self.data["manifest"]["sources"]
        self.assertGreaterEqual(len(sources), 6)
        for src in sources:
            self.assertTrue(src["url"].startswith("https://"))
            self.assertTrue(len(src["publication_date"]) == 10)
            self.assertTrue(len(src["reporting_period"]) > 0)
            self.assertGreater(len(src["extracted_metrics"]), 0)

    def test_financial_metrics_completeness_and_units(self):
        """Verify every financial metric period has source attribution, period, and explicit units."""
        metrics = self.data["metrics"]
        self.assertEqual(len(metrics), 6)
        periods = [m["period"] for m in metrics]
        self.assertEqual(periods, ["Q1 FY26", "Q2 FY26", "Q3 FY26", "Q4 FY26", "Q1 FY27", "Q2 FY27"])
        for row in metrics:
            self.assertIn("millions", row["units"])
            self.assertTrue(row["source_url"].startswith("https://"))
            self.assertGreater(row["revenue_m"], 0)
            self.assertGreater(row["data_center_rev_m"], 0)

    def test_deterministic_percentage_and_bps_calculations(self):
        """Verify exact deterministic arithmetic on NVIDIA reported figures."""
        # FY26 GAAP OpEx YoY: $23,076M vs $16,405M -> +40.66%
        fy26_opex_yoy = ae.calculate_pct_change(16405.0, 23076.0)
        self.assertAlmostEqual(fy26_opex_yoy, 40.66, places=2)

        # Q2 FY27 Revenue QoQ: $96,221M vs $81,615M -> +17.90%
        q2_rev_qoq = ae.calculate_pct_change(81615.0, 96221.0)
        self.assertAlmostEqual(q2_rev_qoq, 17.90, places=2)

        # Q2 FY27 Operating Cash Flow QoQ: $24,077M vs $50,344M -> -52.175% -> -52.18%
        q2_ocf_qoq = ae.calculate_pct_change(50344.0, 24077.0)
        self.assertAlmostEqual(q2_ocf_qoq, -52.18, places=2)

        # Q3 FY27 Guided Gross Margin compression: 74.0% vs 75.0% -> -100 bps
        gm_bps = ae.calculate_bps_change(75.0, 74.0)
        self.assertEqual(gm_bps, -100)

        # DSO expansion in Q2 FY27: AR $63,059M / Rev $96,221M * 91 days = 59.64 days
        dso_q1 = ae.calculate_dso(40710.0, 81615.0, 91)
        dso_q2 = ae.calculate_dso(63059.0, 96221.0, 91)
        self.assertAlmostEqual(dso_q1, 45.39, places=2)
        self.assertAlmostEqual(dso_q2, 59.64, places=2)
        self.assertGreater(dso_q2 - dso_q1, 14.0)

    def test_four_classification_categories(self):
        """Verify deterministic rules properly classify all 4 required competition finding categories."""
        # 1. Verified numerical mismatch (Q4 FY26 Non-GAAP OpEx restatement $5,102M vs $6,666M)
        cat1, msg1 = ae.classify_finding_deterministic(
            comparison_type="direct_numerical_or_ceiling",
            baseline_value=5102.0,
            reported_value=6666.0,
            tolerance_pct=1.5,
        )
        self.assertEqual(cat1, ae.CATEGORY_MISMATCH)
        self.assertIn("RULE_NUMERICAL_MISMATCH", msg1)

        # 2. Potential narrative-metric divergence (Revenue +17.9% QoQ vs OCF -52.18% QoQ)
        cat2, msg2 = ae.classify_finding_deterministic(
            comparison_type="narrative_vs_metric_trajectory",
            baseline_value=17.90,
            reported_value=17.90,
            narrative_direction="positive",
            secondary_metric_delta_pct=-52.18,
        )
        self.assertEqual(cat2, ae.CATEGORY_DIVERGENCE)
        self.assertIn("RULE_NARRATIVE_DIVERGENCE", msg2)

        # 3. No identified discrepancy (Shareholder return $26,000M narrative vs $25,779M cash outflow)
        cat3, msg3 = ae.classify_finding_deterministic(
            comparison_type="direct_numerical_or_ceiling",
            baseline_value=26000.0,
            reported_value=25779.0,
            tolerance_pct=1.5,
        )
        self.assertEqual(cat3, ae.CATEGORY_NO_DISCREPANCY)
        self.assertIn("RULE_NO_DISCREPANCY", msg3)

        # 4. Insufficient evidence (Missing Hyperscale vs ACIE dollar breakdown in Q2 FY27 release)
        cat4, msg4 = ae.classify_finding_deterministic(
            comparison_type="direct_numerical_or_ceiling",
            baseline_value=None,
            reported_value=89000.0,
        )
        self.assertEqual(cat4, ae.CATEGORY_INSUFFICIENT)
        self.assertIn("RULE_INSUFFICIENT_EVIDENCE", msg4)

    def test_all_four_categories_present_in_dataset(self):
        """Ensure the curated NVIDIA findings cover all 4 required categories."""
        categories_found = {c["category"] for c in self.data["comparisons"]}
        for required_cat in ae.VALID_CATEGORIES:
            self.assertIn(required_cat, categories_found)

    def test_semantic_vs_keyword_benchmark(self):
        """Verify semantic matching outperforms keyword matching in both Precision and Recall on the labeled test set."""
        bench = ae.evaluate_matching_benchmark(
            self.data["eval_dataset"],
            semantic_threshold=0.50,
            keyword_threshold=0.22,
        )
        sem = bench["semantic_metrics"]
        kw = bench["keyword_metrics"]

        self.assertEqual(bench["total_pairs"], 12)
        self.assertGreater(sem["precision"], kw["precision"])
        self.assertGreater(sem["recall"], kw["recall"])
        self.assertGreater(sem["f1"], kw["f1"])
        self.assertLess(sem["fp"], kw["fp"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
