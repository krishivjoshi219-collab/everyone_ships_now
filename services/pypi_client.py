import requests
from functools import lru_cache

class PyPIClient:  
    def __init__(self):
        self.base_url = "https://pypi.org/pypi"

    @lru_cache(maxsize=128)
    def fetch_all_releases(self, package_name: str) -> dict:
        clean_name = package_name.strip().lower()
        target_url = f"{self.base_url}/{clean_name}/json"
        
        response_template = {
            "valid": False,
            "package": clean_name,
            "all_releases": [],
            "latest_stable": "",
            "reason": ""
        }

        try:
            # Using connection/read timeout configuration
            response = requests.get(target_url, timeout=(3, 5))
            
            if response.status_code == 200:
                data = response.json()
                response_template["valid"] = True
                response_template["latest_stable"] = data.get("info", {}).get("version", "")
                releases_dict = data.get("releases", {})
                response_template["all_releases"] = list(releases_dict.keys())
                return response_template
            elif response.status_code == 404:
                response_template["reason"] = "Package missing from official PyPI index."
                return response_template
            else:
                response_template["reason"] = f"PyPI Registry Error ({response.status_code})"
                return response_template
                
        except requests.RequestException as e:
            response_template["reason"] = f"Connection error: {e}"
            return response_template
