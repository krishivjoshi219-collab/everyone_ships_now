import re

class SystemResolver:
    def __init__(self):
        # Explicit real-world system failures
        self.rules = {
            "missing_gcc": {
                "patterns": [r"gcc: command not found", r"error: command 'gcc' failed"],
                "fix": "sudo apt-get update && sudo apt-get install -y build-essential python3-dev",
                "explanation": "The native C/C++ compiler toolchain is missing from the host machine operating system layer."
            },
            "missing_openssl": {
                "patterns": [r"openssl/ssl\.h", r"cannot find -lssl"],
                "fix": "sudo apt-get install -y libssl-dev libffi-dev",
                "explanation": "Cryptographic system development libraries are missing, causing Python binary wheels compilation blocks."
            },
            "missing_wheel_build": {
                "patterns": [r"Failed building wheel for", r"Failed to build wheels"],
                "fix": "pip install --upgrade pip setuptools wheel",
                "explanation": "The local environment environment packaging utilities are outdated and cannot execute source compilation."
            }
        }

    def resolve(self, raw_log: str) -> dict:
        """Scans logs for lower-level native operating system flaws."""
        for issue, meta in self.rules.items():
            for pattern in meta["patterns"]:
                if re.search(pattern, raw_log):
                    return {
                        "status": "system_fault_detected",
                        "issue_type": issue,
                        "command": meta["fix"],
                        "explanation": meta["explanation"]
                    }
        return None
