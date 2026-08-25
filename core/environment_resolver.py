import re

class EnvironmentResolver:
    def __init__(self):
        self.module_pkg_map = {
            "yaml": "pyyaml",
            "cv2": "opencv-python",
            "sklearn": "scikit-learn",
            "pil": "Pillow",
            "bs4": "beautifulsoup4",
            "docx": "python-docx",
            "pptx": "python-pptx",
            "fitz": "PyMuPDF",
            "usb": "pyusb",
            "serial": "pyserial"
        }

    def resolve(self, raw_log: str) -> dict:
        """Scans logs for execution pathway routing and environmental variable gaps."""
        # 1. Dynamic check for missing environment variable / KeyError
        key_match = re.search(r"KeyError:\s*['\"]([A-Za-z0-9_]+)['\"]", raw_log, re.IGNORECASE)
        if not key_match:
            key_match = re.search(r"([A-Za-z0-9_]+_KEY|[A-Za-z0-9_]+_TOKEN|[A-Za-z0-9_]+_SECRET)", raw_log)

        if key_match:
            env_var = key_match.group(1).upper()
            return {
                "status": "environment_fault_detected",
                "issue_type": "missing_env_token",
                "command": f"export {env_var}='your_{env_var.lower()}_here' # Or populate your .env file",
                "explanation": f"The application runtime framework failed to find the mandatory secret access credential '{env_var}'."
            }

        # 2. Dynamic check for ModuleNotFoundError / No module named
        mod_match = re.search(r"No module named\s*['\"]([A-Za-z0-9_\-\.]+)['\"]", raw_log, re.IGNORECASE)
        if mod_match:
            raw_mod = mod_match.group(1).split(".")[0].lower()
            pkg_name = self.module_pkg_map.get(raw_mod, raw_mod)
            return {
                "status": "environment_fault_detected",
                "issue_type": "missing_module",
                "command": f"pip install {pkg_name}",
                "explanation": f"The Python module '{raw_mod}' is not installed in the active environment. Install it via '{pkg_name}'."
            }

        if "environment" in raw_log.lower() or "local env" in raw_log.lower():
            return {
                "status": "environment_fault_detected",
                "issue_type": "env_configuration_error",
                "command": "source venv/bin/activate && pip install -r requirements.txt",
                "explanation": "Environment path configuration issue detected. Re-activate virtual environment or reinstall dependencies."
            }

        return None
