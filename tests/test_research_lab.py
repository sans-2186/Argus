"""Tests for research_lab.py (pure Python; runs under pytest or unittest)."""

import copy
import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import argus_engine as ae
import research_lab as rl


class TestResearchLab(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = ae.load_argus_data(os.path.join(PROJECT_ROOT, "data"))
        cls.comps = cls.data["comparisons"]

    def ids(self, question):
        return [r["finding"]["comparison_id"] for r in rl.run_research_review(self.comps, question)]

    def test_all_leads_returns_every_record(self):
        self.assertEqual(self.ids(rl.Q_ALL), [c["comparison_id"] for c in self.comps])

    def test_narrative_filter_uses_categories(self):
        for r in rl.run_research_review(self.comps, rl.Q_NARRATIVE):
            self.assertIn(r["finding"]["category"], (ae.CATEGORY_DIVERGENCE, ae.CATEGORY_NO_DISCREPANCY))
        self.assertIn("CMP-NVDA-003", self.ids(rl.Q_NARRATIVE))
        self.assertNotIn("CMP-NVDA-001", self.ids(rl.Q_NARRATIVE))

    def test_guidance_and_accounting_filters(self):
        self.assertIn("CMP-NVDA-001", self.ids(rl.Q_GUIDANCE))
        self.assertEqual(self.ids(rl.Q_ACCOUNTING), ["CMP-NVDA-002"])

    def test_evidence_gaps_flags_missing_records(self):
        gap_ids = self.ids(rl.Q_GAPS)
        self.assertIn("CMP-NVDA-007", gap_ids)  # insufficient + null values
        self.assertIn("CMP-NVDA-005", gap_ids)  # empty contrary_evidence list
        self.assertNotIn("CMP-NVDA-003", gap_ids)  # all lists populated

    def test_unknown_question_raises(self):
        with self.assertRaises(ValueError):
            rl.run_research_review(self.comps, "nope")

    def test_safe_pct_change_zero_and_missing(self):
        self.assertIsNone(rl.safe_pct_change(0, 5))
        self.assertIsNone(rl.safe_pct_change(None, 5))
        self.assertIsNone(rl.safe_pct_change(5, None))
        self.assertAlmostEqual(rl.safe_pct_change(16405.0, 23076.0), 40.66, places=2)
        self.assertIn("n/a", rl.format_pct(None))

    def test_empty_contrary_evidence_is_described_as_missing_record(self):
        c = next(x for x in self.comps if x["comparison_id"] == "CMP-NVDA-005")
        self.assertEqual(c["evidence_assessment"]["contrary_evidence"], [])
        v = rl.challenge_view(c, rl.CH_CONTRARY)
        self.assertEqual(v["items"], [])
        self.assertIn("missing recorded evidence", v["note"])
        self.assertIn("not proof", v["note"])

    def test_every_challenge_works_for_every_record(self):
        for c in self.comps:
            for ch in rl.CHALLENGES:
                v = rl.challenge_view(c, ch)
                self.assertTrue(v["items"] or v["note"])

    def test_calculation_view_handles_null_baseline(self):
        c = next(x for x in self.comps if x["comparison_id"] == "CMP-NVDA-007")
        v = rl.challenge_view(c, rl.CH_CALC)
        self.assertIn("n/a", v["note"])

    def test_brief_contains_required_sections_for_all_records(self):
        for c in self.comps:
            for ch in rl.CHALLENGES:
                md = rl.build_research_brief(c, rl.Q_ALL, ch, generated_on="2026-10-26")
                self.assertIn(c["comparison_id"], md)
                self.assertIn(c["category"], md)
                self.assertIn(c["statement_origin"]["exact_excerpt"], md)
                self.assertIn(c["follow_up_statement"]["exact_excerpt"], md)
                self.assertIn(c["statement_origin"]["publication_date"], md)
                self.assertIn(c["metric_verification"]["calculated_delta"], md)
                self.assertIn("## Source URLs", md)
                self.assertIn("## Limitations", md)
                self.assertIn(c["statement_origin"]["source_url"], md)
                self.assertIn("does not retrieve", md)

    def test_brief_empty_evidence_not_stated_as_absence(self):
        c = next(x for x in self.comps if x["comparison_id"] == "CMP-NVDA-005")
        md = rl.build_research_brief(c, rl.Q_GAPS, rl.CH_CONTRARY)
        self.assertIn("missing recorded evidence", md)

    def test_brief_survives_missing_fields(self):
        c = copy.deepcopy(self.comps[0])
        c["statement_origin"]["source_url"] = ""
        c["metric_verification"]["python_formula"] = ""
        c["evidence_assessment"] = {}
        md = rl.build_research_brief(c, rl.Q_ALL, rl.CH_UNCERTAINTY)
        self.assertIn("No limitations statement recorded", md)
        self.assertIn("# no formula recorded", md)

    def test_data_not_mutated(self):
        before = copy.deepcopy(self.comps)
        rl.run_research_review(self.comps, rl.Q_GAPS)
        rl.build_research_brief(self.comps[0], rl.Q_ALL, rl.CH_CALC)
        self.assertEqual(before, self.comps)

    def test_escape_helpers(self):
        self.assertEqual(rl.md_safe("$5M and $6M"), "\\$5M and \\$6M")
        self.assertNotIn("$", rl.html_safe("<b>$5M</b>"))
        self.assertIn("&lt;b&gt;", rl.html_safe("<b>"))

    def test_engine_status_message(self):
        self.assertEqual(
            ae.ENGINE_STATUS_MESSAGE,
            "Local concept-aware matching active. No live Gemini inference is being performed in this workflow.",
        )
        _, meta = ae.compute_semantic_similarity_score("operating cash flow", "accounts receivable")
        self.assertNotIn("Embedding", meta["engine_mode"])
        self.assertNotIn("Vector", meta["engine_mode"])


if __name__ == "__main__":
    unittest.main()
