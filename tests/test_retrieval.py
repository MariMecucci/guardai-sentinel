"""BM25 retrieval / provenance smoke tests (all offline)."""
import unittest
from sentinel.models import Finding
from sentinel.retrieval import load_passages, retrieve_passages, grounding_passage_context
from sentinel.evaluate_retrieval import score_cases
from sentinel.service import analyze_code

def finding(rule_id):
    return Finding(rule_id=rule_id, title="synthetic", severity="low", line=1,
                   evidence="synthetic", why="synthetic", remediation="synthetic")

class RetrievalTests(unittest.TestCase):
    def test_corpus_has_unique_versioned_https_citations(self):
        passages = load_passages()
        self.assertEqual(len(passages), len({p.id for p in passages}))
        self.assertTrue(all(p.source_url.startswith("https://") and p.source_version for p in passages))

    def test_sql_retrieval_excludes_shell_sources(self):
        retrieved = retrieve_passages([finding("PY-SQL-001")], limit=5)
        self.assertTrue(retrieved)
        self.assertTrue(all("PY-SQL-001" in p.rule_ids for p in retrieved))
        self.assertIn("OWASP-SQLI-PARAM-v1", [p.id for p in retrieved])

    def test_shell_retrieval_excludes_sql_sources(self):
        retrieved = retrieve_passages([finding("PY-SHELL-002")], limit=5)
        self.assertEqual({p.source_id for p in retrieved}, {"CWE-78", "PYTHON-SUBPROCESS"})

    def test_unknown_and_safe_rules_abstain(self):
        self.assertEqual(retrieve_passages([]), [])
        self.assertEqual(retrieve_passages([finding("FUTURE-RULE")]), [])
        self.assertEqual(retrieve_passages([finding("PY-SQL-001")], limit=0), [])

    def test_context_identifiers_and_no_context_fallback(self):
        retrieved = retrieve_passages([finding("PY-SQL-001")])
        context = grounding_passage_context(retrieved)
        self.assertIn(retrieved[0].id, context)
        self.assertIn("RESUMO EDITORIAL", context)
        self.assertIn("Nenhum trecho", grounding_passage_context([]))

    def test_retrieval_reproducible(self):
        first = [p.id for p in retrieve_passages([finding("PY-SQL-001")])]
        second = [p.id for p in retrieve_passages([finding("PY-SQL-001")])]
        self.assertEqual(first, second)

    def test_analysis_report_includes_passage_provenance(self):
        report = analyze_code("example.py", 'q = f"SELECT * FROM users WHERE id={user_id}"').to_dict()
        self.assertTrue(report["retrieved_passages"])
        self.assertIn("source_version", report["retrieved_passages"][0])

    def test_fixture_reports_full_recall_when_k_covers_all(self):
        evaluation = score_cases()
        self.assertEqual(len(evaluation["cases"]), 5)
        self.assertEqual(evaluation["mean_recall_at_k"], 1.0)

if __name__ == "__main__":
    unittest.main()
