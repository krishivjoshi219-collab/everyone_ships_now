import re

class ScoutParser:
    def __init__(self):
        pass

    def extract_all(self, raw_log: str) -> dict:
        """
        Scans raw terminal dumps line-by-line to isolate constraints.
        Supports classic inline formats and modern multi-line backtracking logs.
        """
        # Data structure keys mapped exactly to match core/detective.py expectations
        data = {
            "requirements": [],
            "installed": []
        }

        for line in raw_log.splitlines():
            line_clean = line.strip()

            # ─── ENGINE 1: CLASSIC INLINE DETECTOR ───
            # Format: "requires numpy<1.24,>=1.22, but you have numpy 1.26.0"
            if "requires" in line_clean.lower() and "but you have" in line_clean.lower():
                match = re.search(
                    r"requires\s+([a-zA-Z0-9_\-]+)\s*([<>=!,\d\.\-]+).*?but\s+you\s+have\s+\1\s+([\d\.]+)", 
                    line_clean, 
                    re.IGNORECASE
                )
                if match:
                    pkg = match.group(1).strip().lower()
                    specs = match.group(2).strip().replace(" ", "")
                    ver = match.group(3).strip()
                    
                    data["requirements"].append({"package": pkg, "specifiers": specs})
                    data["installed"].append({"package": pkg, "version": ver})

            # ─── ENGINE 2: MODERN MULTI-LINE DEPENDENCY DETECTOR ───
            # Format: "tensorflow-cpu 2.12.0 depends on numpy<1.24 and >=1.22"
            elif "depends on" in line_clean.lower():
                match = re.search(r"depends\s+on\s+([a-zA-Z0-9_\-]+)\s*(.*)", line_clean, re.IGNORECASE)
                if match:
                    pkg = match.group(1).strip().lower()
                    raw_specs = match.group(2).strip()
                    
                    # Core Translation: Swap pip's literal text 'and' to standard commas
                    clean_specs = raw_specs.replace("and", ",").replace(" ", "")
                    data["requirements"].append({"package": pkg, "specifiers": clean_specs})

            # ─── ENGINE 3: MODERN MULTI-LINE INSTALLED/REQUESTED DETECTOR ───
            # Format: "The user requested numpy==1.26.0"
            elif "user requested" in line_clean.lower():
                match = re.search(r"user\s+requested\s+([a-zA-Z0-9_\-]+)==([\d\.]+)", line_clean, re.IGNORECASE)
                if match:
                    pkg = match.group(1).strip().lower()
                    ver = match.group(2).strip()
                    data["installed"].append({"package": pkg, "version": ver})

        return data

    def extract_constraints(self, raw_log: str) -> dict:
        """Maintains backward-compatible functional reference links."""
        return self.extract_all(raw_log)

# ==========================================
# ⚡ ISOLATED PARSER SANITY TEST DRILL
# ==========================================
if __name__ == "__main__":
    print("🕵️ [Scout Parser] Running multi-line extraction check...")
    parser = ScoutParser()

    # Testing the real-world backtracking block generated inside your env
    organic_test_log = """
    The conflict is caused by:
        The user requested numpy==1.26.0
        tensorflow-cpu 2.12.0 depends on numpy<1.24 and >=1.22
    """

    extracted_payload = parser.extract_all(organic_test_log)
    print("\n📦 Parsed Data Output:")
    print("=" * 50)
    print(f"Requirements Mapped: {extracted_payload['requirements']}")
    print(f"Installed Targets:   {extracted_payload['installed']}")
