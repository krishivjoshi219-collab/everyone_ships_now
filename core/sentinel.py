class SentinelGuard:
    def __init__(self):
        pass

    def detect_signals_matrix(self, raw_log: str) -> dict:
        """
        Surgically extracts parallel problem vectors present in the log.
        Returns a clean boolean map for multi-domain routing.
        """
        log_lower = raw_log.lower()
        return {
            "system": any(sig in log_lower for sig in ["gcc", "openssl", "failed building wheel", "libssl"]),
            "environment": any(sig in log_lower for sig in ["modulenotfounderror", "no module named"]),
            "runtime": any(sig in log_lower for sig in ["keyerror", "database_url", "connection refused", "already in use"]),
            "dependency": any(sig in log_lower for sig in ["requires", "conflict", "incompatible", "version constraint"])
        }
