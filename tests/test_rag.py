"""Offline grounding tests: no Gemini requests and no network."""
import unittest
from sentinel.models import Finding
from sentinel.rag import build_grounding_context, retrieve_for_findings
from sentinel.service import analyze_code

def finding(rule_id):
    return Finding(rule_id=rule_id, title="synthetic", severity="medium",
                   line=1, evidence="synthetic", why="synthetic", remediation="synthetic")

class GroundingTests(unittest.TestCase):
    def test_sql_references_are_retrieved(self):
        refs = retrieve_for_findings([finding("PY-SQL-001")])
        self.assertEqual([x.id for x in refs], ["OWASP-SQLI-PREVENTION", "CWE-89"])
        self.assertIn("prepared statements", build_grounding_context(refs))
    def test_shell_references_are_retrieved(self):
        refs = retrieve_for_findings([finding("PY-SHELL-002")])
        self.assertEqual([x.id for x in refs], ["PYTHON-SUBPROCESS", "CWE-78"])
    def test_duplicates_and_limit(self):
        refs = retrieve_for_findings([finding("PY-SQL-001"), finding("SQL-TEMPLATE-001"),
                                      finding("PY-SHELL-002")], limit=3)
        self.assertEqual(len(refs), 3)
        self.assertEqual(len({x.id for x in refs}), 3)
    def test_unknown_rule_and_empty_findings_do_not_hallucinate_sources(self):
        self.assertEqual(retrieve_for_findings([finding("UNKNOWN")]), [])
        self.assertEqual(retrieve_for_findings([]), [])
        self.assertIn("Nenhuma referência", build_grounding_context([]))
    def test_limit_zero(self):
        self.assertEqual(retrieve_for_findings([finding("PY-SQL-001")], limit=0), [])

    def test_service_report_contains_grounded_sources(self):
        source = 'query = f"SELECT * FROM users WHERE name={username}"'
        report = analyze_code("synthetic.py", source).to_dict()
        self.assertGreater(report["finding_count"], 0)
        ids = [r["id"] for r in report["grounding_references"]]
        self.assertIn("CWE-89", ids)
        self.assertIsNone(report["ai_summary"])

    def test_safe_sample_does_not_claim_sources(self):
        source = "cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))"
        report = analyze_code("synthetic.py", source).to_dict()
        self.assertEqual(report["grounding_references"], [])

if __name__ == "__main__":
    unittest.main()
