"""SRAM shared category reference CLI. No network or store mutations."""
import json
import argparse
from pathlib import Path

def load():
    return json.loads(Path(__file__).with_name("categories.json").read_text(encoding="utf-8-sig"))

def main():
    parser = argparse.ArgumentParser(description="SRAM common category reference")
    parser.add_argument("--code", help="Exact category code")
    args = parser.parse_args()
    data = load()
    rows = data["categories"]
    assert len({r["code"] for r in rows}) == len(rows), "Duplicate category codes"
    if args.code:
        rows = [r for r in rows if r["code"] == args.code]
        if not rows:
            parser.error("Unknown category code")
    print(json.dumps(rows, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

