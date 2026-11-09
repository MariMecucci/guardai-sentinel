import unittest
from sentinel.service import analyze_code
from sentinel.static import scan_code, validate_source


class SourceValidationTests(unittest.TestCase):
    def test_unsupported_extension(self):
        with self.assertRaises(ValueError):
            validate_source("hidden.exe", "print('hi')")

    def test_empty_input(self):
        with self.assertRaises(ValueError):
            validate_source("file.py", " \n")

    def test_long_file(self):
        with self.assertRaises(ValueError):
            validate_source("x.py", "a" * 30_001)

    def test_too_many_lines(self):
        with self.assertRaises(ValueError):
            validate_source("x.sql", "SELECT 1;\n" * 601)

    def test_nul(self):
        with self.assertRaises(ValueError):
            validate_source("x.py", "a=1\x00")

    def test_case_insensitive_extension(self):
        self.assertEqual(validate_source("sample.PY", "a=1"), "python")


class ScannerTests(unittest.TestCase):
    def test_python_sql_fstring(self):
        report = scan_code("a.py", "query = f\"SELECT * FROM users WHERE id='{user}'\"\n")
        self.assertEqual(report.findings[0].rule_id, "PY-SQL-001")

    def test_python_concat(self):
        report = scan_code("a.py", "query = 'SELECT * FROM users WHERE id=' + user")
        self.assertEqual(len(report.findings), 1)

    def test_python_safe_parameter(self):
        report = scan_code("a.py", "cursor.execute('SELECT * FROM users WHERE id=?', (id,))")
        self.assertEqual(report.findings, [])

    def test_python_direct_execute_fstring(self):
        r = scan_code("a.py", "cursor.execute(f'SELECT * FROM users WHERE id={user}')")
        self.assertEqual(r.findings[0].line, 1)

    def test_subprocess_shell(self):
        r = scan_code("a.py", "import subprocess\nsubprocess.run(command, shell=True)")
        self.assertEqual(r.findings[0].rule_id, "PY-SHELL-002")

    def test_safe_subprocess(self):
        r = scan_code("a.py", "import subprocess\nsubprocess.run(['echo', 'hello'], shell=False)")
        self.assertEqual(len(r.findings), 0)

    def test_sql_template(self):
        r = scan_code("q.sql", "SELECT * FROM users WHERE email = '${user_email}';")
        self.assertEqual(r.findings[0].rule_id, "SQL-TEMPLATE-001")

    def test_sql_parameter(self):
        r = scan_code("q.sql", "SELECT * FROM users WHERE email = ?;")
        self.assertEqual(len(r.findings), 0)

    def test_syntax_error_is_warning_not_false_clean(self):
        r = scan_code("a.py", "def oops(\n")
        self.assertTrue(any("sintaxe" in w for w in r.warnings))

    def test_result_json_structure(self):
        r = analyze_code("x.py", "query = f'SELECT * FROM clients WHERE id={id}'").to_dict()
        self.assertEqual(r["finding_count"], 1)
        self.assertEqual(r["language"], "python")
        self.assertTrue(r["disclaimer"])
        self.assertIsNone(r["model"])

    def test_does_not_execute_input(self):
        r = scan_code("x.py", "raise RuntimeError('should not execute')")
        self.assertEqual(r.findings, [])

    def test_unconfigured_gemini_requires_key(self):
        import os
        from unittest.mock import patch
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with self.assertRaises(ValueError):
                analyze_code("x.py", "a=1", use_ai=True)


if __name__ == "__main__":
    unittest.main()
