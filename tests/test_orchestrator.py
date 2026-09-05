import unittest
import json
import os
import subprocess
from core.sentinel import SentinelGuard
from core.scout import ScoutParser
from core.detective import DetectiveEngine
from core.healer import HealerEngine
from core.system_resolver import SystemResolver
from core.environment_resolver import EnvironmentResolver
from core.runtime_resolver import RuntimeResolver
from core.auditor import CodeAuditor
from core.watcher import SandboxWatcher
from services.pdf_generator import PDFReportEngine
from app import BankaiOrchestrator

class TestSentinelGuard(unittest.TestCase):
    def setUp(self):
        self.sentinel = SentinelGuard()

    def test_detect_signals_matrix(self):
        log = "gcc: command not found\nKeyError: 'OPENAI_API_KEY'\nrequires numpy<1.24"
        signals = self.sentinel.detect_signals_matrix(log)
        self.assertTrue(signals["system"])
        self.assertTrue(signals["environment"])
        self.assertTrue(signals["dependency"])

class TestScoutParser(unittest.TestCase):
    def setUp(self):
        self.scout = ScoutParser()

    def test_extract_all_inline(self):
        log = "ERROR: requires numpy<1.24,>=1.22, but you have numpy 1.26.0"
        extracted = self.scout.extract_all(log)
        self.assertEqual(len(extracted["requirements"]), 1)
        self.assertEqual(extracted["requirements"][0]["package"], "numpy")
        self.assertEqual(extracted["installed"][0]["version"], "1.26.0")

class TestDetectiveEngine(unittest.TestCase):
    def setUp(self):
        self.detective = DetectiveEngine()

    def test_analyze_conflicts(self):
        scout_payload = {
            "requirements": [{"package": "numpy", "specifiers": "<1.24,>=1.22"}],
            "installed": [{"package": "numpy", "version": "1.26.0"}]
        }
        report = self.detective.analyze_conflicts(scout_payload)
        self.assertEqual(report.status, "conflict_detected")
        self.assertEqual(len(report.conflicts), 1)

    def test_deadlock_detection(self):
        scout_payload = {
            "requirements": [
                {"package": "cachetools", "specifiers": "==3.1.1"},
                {"package": "cachetools", "specifiers": "<8,>=5.5"}
            ],
            "installed": [{"package": "cachetools", "version": "3.1.1"}]
        }
        report = self.detective.analyze_conflicts(scout_payload)
        self.assertEqual(report.status, "unresolvable_deadlock")

class TestHealerEngine(unittest.TestCase):
    def setUp(self):
        self.healer = HealerEngine()

    def test_compute_safe_version(self):
        specs = "<1.24,>=1.22"
        releases = ["1.21.0", "1.22.0", "1.23.5", "1.24.0", "1.25.0"]
        recommended = self.healer.compute_safe_version(specs, releases)
        self.assertEqual(recommended, "1.23.5")

class TestResolvers(unittest.TestCase):
    def test_system_resolver(self):
        res = SystemResolver().resolve("gcc: command not found")
        self.assertIsNotNone(res)
        self.assertIn("apt-get install", res["command"])

    def test_environment_resolver_keyerror(self):
        res = EnvironmentResolver().resolve("KeyError: 'OPENAI_API_KEY'")
        self.assertIsNotNone(res)
        self.assertIn("OPENAI_API_KEY", res["command"])

    def test_environment_resolver_module_mapping(self):
        res = EnvironmentResolver().resolve("ModuleNotFoundError: No module named 'yaml'")
        self.assertIsNotNone(res)
        self.assertIn("pip install pyyaml", res["command"])

    def test_environment_resolver_extended_mapping(self):
        res_cv2 = EnvironmentResolver().resolve("ModuleNotFoundError: No module named 'cv2'")
        self.assertIsNotNone(res_cv2)
        self.assertIn("pip install opencv-python", res_cv2["command"])

        res_sklearn = EnvironmentResolver().resolve("ModuleNotFoundError: No module named 'sklearn'")
        self.assertIsNotNone(res_sklearn)
        self.assertIn("pip install scikit-learn", res_sklearn["command"])

    def test_runtime_resolver(self):
        res = RuntimeResolver().resolve("address already in use on port 8000")
        self.assertIsNotNone(res)
        self.assertIn("lsof", res["command"])

from unittest.mock import patch, MagicMock

class TestAuditorAndWatcher(unittest.TestCase):
    def test_code_auditor_fallback(self):
        auditor = CodeAuditor()
        res = auditor.fetch_gemini_insights("some crash log", [])
        self.assertIn("explanation", res)
        self.assertIn("pre_thinking", res)

    @patch("groq.Groq")
    def test_code_auditor_groq_rate_limit_fallback(self, mock_groq_cls):
        mock_client = MagicMock()
        mock_groq_cls.return_value = mock_client

        mock_choice = MagicMock()
        mock_choice.message.content = "[EXPLANATION]: Fallback succeeded after rate limit\n---\n[PRE-THINKING]: Risks clear"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client.chat.completions.create.side_effect = [
            Exception("429 Rate limit exceeded"),
            mock_response
        ]

        auditor = CodeAuditor()
        with self.assertLogs("core.auditor", level="WARNING") as cm:
            res = auditor.fetch_gemini_insights(
                "some crash log",
                [],
                provider="groq",
                groq_api_key="fake_groq_key"
            )

        self.assertTrue(any("Groq candidate" in log and "429 Rate limit exceeded" in log for log in cm.output))
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        self.assertEqual(res["explanation"], "Fallback succeeded after rate limit")

    def test_sandbox_watcher(self):
        watcher = SandboxWatcher(max_cpu_seconds=1.0)
        self.assertTrue(watcher.register_api_call_event())

class TestPDFReportEngine(unittest.TestCase):
    def test_pdf_generation(self):
        engine = PDFReportEngine()
        payload = {
            "analysis_id": "TEST-1234",
            "detected_domains": ["📦 Package Dependency"],
            "recovery_order_stack": [{"step": 1, "target": "Patch", "command": "pip install numpy", "explanation": "Fix"}],
            "metrics": {"confidence_percentage": 90, "verification_checklist": ["✓ Check passed"]},
            "ai_insights": {"explanation": "Test explanation", "pre_thinking": "Test prethinking"}
        }
        pdf_bytes = engine.generate_executive_report(payload)
        self.assertTrue(isinstance(pdf_bytes, bytes))
        self.assertTrue(len(pdf_bytes) > 0)

class TestBankaiOrchestrator(unittest.TestCase):
    def test_full_diagnosis(self):
        orchestrator = BankaiOrchestrator()
        log = "ERROR: requires numpy<1.24,>=1.22, but you have numpy 1.26.0"
        res = orchestrator.run_full_diagnosis(log)
        self.assertIn("analysis_id", res)
        self.assertTrue(res["metrics"]["confidence_percentage"] > 0)

    def test_snapshot_export_import(self):
        orchestrator = BankaiOrchestrator()
        log = "ERROR: requires numpy<1.24,>=1.22, but you have numpy 1.26.0"
        payload = orchestrator.run_full_diagnosis(log)
        snapshot_json = orchestrator.export_snapshot(payload)
        self.assertIsInstance(snapshot_json, str)
        imported_payload = orchestrator.import_snapshot(snapshot_json)
        self.assertEqual(imported_payload["analysis_id"], payload["analysis_id"])

class TestCLIRunner(unittest.TestCase):
    def test_cli_execution(self):
        cmd = ["python3", "cli.py", "sample_logs/dependency_conflict.txt", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("analysis_id", data)

if __name__ == "__main__":
    unittest.main()
