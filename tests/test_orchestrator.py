import unittest
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

    def test_runtime_resolver(self):
        res = RuntimeResolver().resolve("address already in use on port 8000")
        self.assertIsNotNone(res)
        self.assertIn("lsof", res["command"])

class TestAuditorAndWatcher(unittest.TestCase):
    def test_code_auditor_fallback(self):
        auditor = CodeAuditor()
        res = auditor.fetch_gemini_insights("some crash log", [])
        self.assertIn("explanation", res)
        self.assertIn("pre_thinking", res)

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

if __name__ == "__main__":
    unittest.main()
