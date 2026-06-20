import re

class RuntimeResolver:
    def __init__(self):
        self.rules = {
            "port_collision": {
                "patterns": [r"address already in use", r"port \d+ already in use", r"bind failed"],
                "fix": "lru_port=$(lsof -t -i :8000); [ -n \"$lru_port\" ] && kill -9 $lru_port",
                "explanation": "The network interface socket is blocked by a ghost background process thread."
            },
            "database_refused": {
                "patterns": [r"connection refused", r"is the server running on host", r"cant connect to local mysql"],
                "fix": "sudo systemctl start postgresql # Or verify docker-compose background container maps",
                "explanation": "The target infrastructure database engine is not currently running or listening on host loops."
            }
        }

    def resolve(self, raw_log: str) -> dict:
        """Scans logs for execution-layer server environment blocks."""
        for issue, meta in self.rules.items():
            for pattern in meta["patterns"]:
                if re.search(pattern, raw_log):
                    return {
                        "status": "runtime_fault_detected",
                        "issue_type": issue,
                        "command": meta["fix"],
                        "explanation": meta["explanation"]
                    }
        return None
