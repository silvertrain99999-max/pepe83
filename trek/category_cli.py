import argparse
import json
from pathlib import Path

from workflow import load_tree, next_category, queue, set_state, summary, validate_tree


def main() -> int:
    p = argparse.ArgumentParser(description="TREK 카테고리 Top-down 관리")
    p.add_argument("tree")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("summary")
    q = sub.add_parser("queue")
    q.add_argument("--root", default="gear")
    n = sub.add_parser("next")
    n.add_argument("--root", default="gear")
    s = sub.add_parser("set")
    s.add_argument("category_id")
    s.add_argument("--scope", choices=("sell_now", "explore", "exclude", "undecided"))
    s.add_argument("--status", choices=("not_started", "in_progress", "blocked", "complete", "excluded"))
    s.add_argument("--evidence")
    s.add_argument("--output")
    args = p.parse_args()
    tree = load_tree(args.tree)
    errors = validate_tree(tree)
    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        return 1
    if args.command == "summary":
        result = summary(tree)
    elif args.command == "queue":
        result = queue(tree, args.root)
    elif args.command == "next":
        result = next_category(tree, args.root)
    else:
        updated = set_state(tree, args.category_id, scope=args.scope,
                            status=args.status, evidence=args.evidence)
        target = Path(args.output or args.tree)
        target.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
        result = {"saved": str(target), "next": next_category(updated, "gear")}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

