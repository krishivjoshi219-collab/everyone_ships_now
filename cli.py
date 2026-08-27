#!/usr/bin/env python3
"""
DependenceDoc CLI - Terminal Diagnostics Interface
Execute environment restoration analysis directly from your terminal.
"""

import sys
import os
import argparse
import json
from app import BankaiOrchestrator

def main():
    parser = argparse.ArgumentParser(
        description="DependenceDoc Terminal CLI - Environment Recovery & Dependency Crash Diagnosis Tool"
    )
    parser.add_argument(
        "log_file",
        nargs="?",
        default=None,
        help="Path to file containing terminal crash dump / log. Reads from STDIN if not provided."
    )
    parser.add_argument(
        "-f", "--file",
        dest="file_flag",
        help="Path to terminal crash log file (alternative to positional argument)."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw diagnostic payload in JSON format."
    )
    parser.add_argument(
        "--export-script",
        dest="export_script",
        metavar="OUTPUT_SH",
        help="Export generated recovery commands directly into a shell script file."
    )
    parser.add_argument(
        "--gemini-key",
        dest="gemini_key",
        default="",
        help="Optional Gemini API key for enhanced AI root cause insights."
    )

    args = parser.parse_args()

    # Determine input log content source
    log_path = args.log_file or args.file_flag
    if log_path and log_path != "-":
        if not os.path.exists(log_path):
            print(f"Error: Log file '{log_path}' not found.", file=sys.stderr)
            sys.exit(1)
        with open(log_path, "r", encoding="utf-8") as f:
            raw_log = f.read()
    else:
        if not sys.stdin.isatty():
            raw_log = sys.stdin.read()
        elif log_path == "-":
            raw_log = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(0)

    if not raw_log.strip():
        print("Error: Empty log provided.", file=sys.stderr)
        sys.exit(1)

    orchestrator = BankaiOrchestrator()
    payload = orchestrator.run_full_diagnosis(raw_log, gemini_api_key=args.gemini_key)

    if args.json:
        # JSON output helper (convert dataclass/objects if any)
        clean_payload = dict(payload)
        clean_payload.pop("raw_dataclass", None)
        print(json.dumps(clean_payload, indent=2, default=str))
    else:
        print("\n🩺 DEPENDENCE DOC DIAGNOSTIC SUMMARY")
        print("=" * 60)
        print(f"Analysis ID:        {payload.get('analysis_id')}")
        print(f"Detected Domains:   {', '.join(payload.get('detected_domains', []))}")
        print(f"Confidence Score:   {payload.get('metrics', {}).get('confidence_percentage')}%")
        print(f"Side-Effect Risk:   {payload.get('metrics', {}).get('risk_badge')}")

        insights = payload.get("ai_insights", {})
        if insights.get("explanation"):
            print("\n🧠 ROOT CAUSE ANALYSIS:")
            print(insights["explanation"])

        print("\n🛠️ RECOMMENDED RECOVERY COMMANDS:")
        recovery_stack = payload.get("recovery_order_stack", [])
        if not recovery_stack:
            print("  ✓ No commands required. Environment looks clean.")
        else:
            for step in recovery_stack:
                print(f"  Step {step.get('step')}: {step.get('target')}")
                print(f"    Explanation: {step.get('explanation')}")
                print(f"    Command:     {step.get('command')}\n")

    if args.export_script:
        recovery_stack = payload.get("recovery_order_stack", [])
        script_content = "#!/bin/bash\nset -e\n# DependenceDoc Automated Recovery Script\n\n"
        for step in recovery_stack:
            script_content += f"echo '==> Step {step.get('step')}: {step.get('target')}'\n"
            script_content += f"{step.get('command', '')}\n\n"

        with open(args.export_script, "w", encoding="utf-8") as f:
            f.write(script_content)
        os.chmod(args.export_script, 0o755)
        print(f"\n✅ Recovery script exported to '{args.export_script}'")

if __name__ == "__main__":
    main()
