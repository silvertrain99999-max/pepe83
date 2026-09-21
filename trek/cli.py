import argparse
import json
from pathlib import Path

from catalog import CatalogError, build_plan, load, validate


def main() -> int:
    parser = argparse.ArgumentParser(description="TREK SKU 원장 검증 및 채널 반영안 생성")
    parser.add_argument("catalog")
    parser.add_argument("--channel", choices=("smartstore", "cafe24"))
    parser.add_argument("--output")
    args = parser.parse_args()
    data = load(args.catalog)
    errors = validate(data)
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        return 1
    result = {"valid": True}
    if args.channel:
        result["channel"] = args.channel
        result["plans"] = build_plan(data, args.channel)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

