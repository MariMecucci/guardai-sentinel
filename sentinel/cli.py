"""CLI: python -m sentinel.cli examples/vulnerable_login.py"""
import argparse
import json
from pathlib import Path
from .service import analyze_code


def main() -> None:
    p = argparse.ArgumentParser(description="GuardAI Sentinel — static security checks")
    p.add_argument("file", type=Path)
    args = p.parse_args()
    data = args.file.read_text(encoding="utf-8")
    report = analyze_code(args.file.name, data)
    print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
