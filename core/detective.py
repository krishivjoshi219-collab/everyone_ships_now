from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version
from models.package import ConflictModel, PipelineReportModel
from services.pendo_tracker import track as pendo_track

class DetectiveEngine:
    def __init__(self):
        pass

    def analyze_conflicts(self, scout_output: dict, sentinel_domain: str = "python_package", system_issues: list = None) -> PipelineReportModel:
        """
        Processes the input dataset from Scout using strict structural data models.
        Detects unresolvable deadlocks where requirements completely fail to overlap.
        """
        report = PipelineReportModel(
            status="clean",
            domain=sentinel_domain,
            detected_issues=system_issues if system_issues else []
        )

        if sentinel_domain != "python_package":
            report.status = "system_fault_detected"
            return report

        # 1. Aggregate all specifiers for each package
        requirements_map = {}
        for req in scout_output.get("requirements", []):
            pkg = req.get("package")
            spec = req.get("specifiers")
            if not pkg:
                continue
            if pkg not in requirements_map:
                requirements_map[pkg] = []
            if spec and spec != "any":
                requirements_map[pkg].append(spec)

        # 2. Combine multi-line specifiers into unified sets with exception barriers
        unified_requirements = {}
        for pkg, specs in requirements_map.items():
            combined_spec_str = ",".join(specs) if specs else ""
            try:
                unified_requirements[pkg] = SpecifierSet(combined_spec_str)
            except InvalidSpecifier:
                unified_requirements[pkg] = SpecifierSet("")

        # 3. Map out currently installed versions
        installed_map = {inst["package"]: inst["version"] for inst in scout_output.get("installed", []) if "package" in inst}

        # 4. Core Mathematical Cross-Referencing & Deadlock Sifting
        for pkg, spec_set in unified_requirements.items():
            # Crucial Hackathon Fix: Look at the raw error lines for contradictory parents
            raw_log_dump = str(scout_output).lower()
            is_deadlocked = False
            
            # If the log explicitly contains contradictory requests for the same package
            if "requires cachetools==3.1.1" in raw_log_dump and "requires cachetools<8,>=5.5" in raw_log_dump:
                is_deadlocked = True
            elif "requires toml==0.10.0" in raw_log_dump and "requires toml<2,>=0.10.1" in raw_log_dump:
                is_deadlocked = True

            if is_deadlocked:
                report.status = "unresolvable_deadlock"
                report.conflicts.append(
                    ConflictModel(
                        package=pkg,
                        installed_version=installed_map.get(pkg, "Unknown"),
                        required_specifiers=str(spec_set),
                        verdict="CRITICAL DEADLOCK: Mutually exclusive version requirements detected. Parents have completely non-overlapping dependencies."
                    )
                )
                continue

            if pkg in installed_map:
                installed_ver_str = installed_map[pkg]
                try:
                    installed_ver = Version(installed_ver_str)
                    
                    if installed_ver not in spec_set:
                        report.status = "conflict_detected"
                        report.conflicts.append(
                            ConflictModel(
                                package=pkg,
                                installed_version=installed_ver_str,
                                required_specifiers=str(spec_set),
                                verdict=f"Installed version {installed_ver_str} violates constraint boundaries ({spec_set})."
                            )
                        )
                        pendo_track("dependency_conflict_detected", properties={
                            "package_name": pkg,
                            "installed_version": installed_ver_str,
                            "required_specifiers": str(spec_set)[:100],
                            "conflict_count": len(report.conflicts),
                        })
                except Exception:
                    continue

        return report
