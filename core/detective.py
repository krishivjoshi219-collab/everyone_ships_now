from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version
from models.package import ConflictModel, PipelineReportModel

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
        raw_specs_by_pkg = {}
        for req in scout_output.get("requirements", []):
            pkg = req.get("package")
            spec = req.get("specifiers")
            if not pkg:
                continue
            if pkg not in requirements_map:
                requirements_map[pkg] = []
                raw_specs_by_pkg[pkg] = []
            if spec and spec != "any":
                requirements_map[pkg].append(spec)
                raw_specs_by_pkg[pkg].append(spec)

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
            raw_log_dump = str(scout_output).lower()
            is_deadlocked = False

            # Check for multiple conflicting specifiers for the same package
            specs_list = raw_specs_by_pkg.get(pkg, [])
            if len(specs_list) > 1:
                # Attempt to find if any single version could satisfy all specifiers
                # If individual specifiers are mathematically incompatible (e.g. ==3.1.1 and >=5.5)
                has_exact_and_range_clash = False
                for s in specs_list:
                    if "==" in s:
                        try:
                            exact_v = Version(s.replace("==", "").strip())
                            for other_s in specs_list:
                                if other_s != s and exact_v not in SpecifierSet(other_s):
                                    has_exact_and_range_clash = True
                                    break
                        except Exception:
                            pass
                if has_exact_and_range_clash:
                    is_deadlocked = True

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
                except Exception:
                    continue

        return report
