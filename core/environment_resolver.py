import re

class EnvironmentResolver:
    def __init__(self):
        self.rules = {
            "venv_not_active": {
                "patterns": [r"ModuleNotFoundError: No module named", r"No module named"],
                "fix": "source venv/bin/activate && pip install -r requirements.txt",
                "explanation": "The required package is likely installed globally or inside an inactive isolated environment shell path."
            },
            "missing_env_token": {
                "patterns": [r"KeyError:\s*'([A-Z0-9_]+_KEY)'", r"Environment Variable missing"],
                "fix": "export OPENAI_API_KEY='your_master_key_here' # Or populate your secure .env config map",
                "explanation": "The application runtime framework failed to find the mandatory secret access credentials."
            }
        }

    def resolve(self, raw_log: str) -> dict:
        """Scans logs for execution pathway routing and environmental variable gaps."""
        for issue, meta in self.rules.items():
            for pattern in meta["patterns"]:
                if re.search(pattern, raw_log):
                    return {
                        "status": "environment_fault_detected",
                        "issue_type": issue,
                        "command": meta["fix"],
                        "explanation": meta["explanation"]
                    }
        return None
