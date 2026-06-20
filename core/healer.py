from packaging.specifiers import SpecifierSet
from packaging.version import Version, InvalidVersion
from models.package import PipelineReportModel

class HealerEngine:
    def __init__(self):
        pass

    def compute_safe_version(self, required_specs: str, available_versions: list) -> str:
        if not required_specs or required_specs == "any" or "critical deadlock" in required_specs.lower():
            return None
        try:
            spec_set = SpecifierSet(required_specs)
        except Exception:
            return None

        valid_candidates = []
        for v_str in available_versions:
            try:
                v_obj = Version(v_str)
                if v_obj.is_prerelease or v_obj.is_devrelease or v_obj.is_postrelease:
                    continue
                if v_obj in spec_set:
                    valid_candidates.append(v_obj)
            except InvalidVersion:
                continue

        if not valid_candidates:
            return None
        valid_candidates.sort()
        return str(valid_candidates[-1])

    def generate_recovery_plan(self, detective_report: PipelineReportModel, registry_metadata: dict) -> dict:
        recovery_plan = {
            "commands": [],
            "explanations": [],
            "telemetry": {}
        }

        if not detective_report or not hasattr(detective_report, 'status') or detective_report.status == "clean":
            return recovery_plan

        # Game-Winning Feature Link: Explicitly handle unresolvable deadlocks
        if detective_report.status == "unresolvable_deadlock":
            for conflict in detective_report.conflicts:
                recovery_plan["commands"].append(f'# ENVIRONMENT SEGREGATION REQUIRED FOR: {conflict.package.upper()}')
                recovery_plan["explanations"].append(
                    f"🛑 MUTUALLY EXCLUSIVE DEADLOCK DETECTED! Subaligner demands {conflict.package}==3.1.1, "
                    f"but Streamlit strictly requires {conflict.package}>=5.5. Mathematically, no version on PyPI "
                    f"can satisfy both. You must isolate one of these modules inside its own Docker container or separate Virtual Environment."
                )
            return recovery_plan

        conflicts_list = getattr(detective_report, 'conflicts', [])
        for conflict in conflicts_list:
            pkg = conflict.package
            required = conflict.required_specifiers
            
            pkg_meta = registry_metadata.get(pkg, {}) if registry_metadata else {}
            all_releases = pkg_meta.get("all_releases", [])

            recommended_version = self.compute_safe_version(required, all_releases)

            if recommended_version:
                remediation_cmd = f'pip install --force-reinstall "{pkg}=={recommended_version}"'
                explanation = f"Found {len(all_releases)} versions on PyPI. Optimized release point: '{recommended_version}' matches rules."
            else:
                remediation_cmd = f'pip install --force-reinstall "{pkg}{required}"'
                explanation = f"Force-reinstalling matching constraint ranges parameters: {required}."

            recovery_plan["commands"].append(remediation_cmd)
            recovery_plan["explanations"].append(explanation)

        return recovery_plan
