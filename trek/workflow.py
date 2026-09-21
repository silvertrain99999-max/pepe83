"""TREK 카테고리 Top-down 작업 흐름."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterator

STATUSES = {"not_started", "in_progress", "blocked", "complete", "excluded"}
SCOPES = {"sell_now", "explore", "exclude", "undecided"}


def load_tree(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def walk(nodes: list[dict[str, Any]], depth: int = 0) -> Iterator[tuple[dict[str, Any], int]]:
    for node in nodes:
        yield node, depth
        yield from walk(node.get("children", []), depth + 1)


def leaves(nodes: list[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    for node, _ in walk(nodes):
        if not node.get("children"):
            yield node


def validate_tree(tree: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    for node, _ in walk(tree.get("roots", [])):
        node_id = node.get("id")
        if not node_id or node_id in ids:
            errors.append(f"카테고리 ID 누락 또는 중복: {node_id}")
        ids.add(node_id)
        if node.get("status") not in STATUSES:
            errors.append(f"{node_id}: 잘못된 status")
        if node.get("scope") not in SCOPES:
            errors.append(f"{node_id}: 잘못된 scope")
        if node.get("scope") == "exclude" and node.get("status") != "excluded":
            errors.append(f"{node_id}: scope=exclude이면 status=excluded여야 합니다")
        if node.get("status") == "complete" and not node.get("evidence"):
            errors.append(f"{node_id}: 완료 근거 경로가 필요합니다")
    return errors


def find(tree: dict[str, Any], category_id: str) -> dict[str, Any] | None:
    return next((n for n, _ in walk(tree.get("roots", [])) if n.get("id") == category_id), None)


def queue(tree: dict[str, Any], root_id: str = "gear") -> list[dict[str, str]]:
    """사용자가 scope를 결정한 잎만 원래 카테고리 순서로 반환한다."""
    root = find(tree, root_id)
    if not root:
        raise KeyError(root_id)
    return [{"id": n["id"], "name": n["name"], "scope": n["scope"], "status": n["status"]}
            for n in leaves([root]) if n["scope"] in {"sell_now", "explore"} and n["status"] != "excluded"]


def next_category(tree: dict[str, Any], root_id: str = "gear") -> dict[str, str] | None:
    """완료 전 건너뛰지 않고 첫 미완료 카테고리를 반환한다."""
    return next((item for item in queue(tree, root_id) if item["status"] != "complete"), None)


def set_state(tree: dict[str, Any], category_id: str, *, scope: str | None = None,
              status: str | None = None, evidence: str | None = None) -> dict[str, Any]:
    result = deepcopy(tree)
    node = find(result, category_id)
    if not node:
        raise KeyError(category_id)
    if scope is not None:
        if scope not in SCOPES:
            raise ValueError(scope)
        node["scope"] = scope
        if scope == "exclude":
            node["status"] = "excluded"
    if status is not None:
        if status not in STATUSES:
            raise ValueError(status)
        if status == "complete" and not (evidence or node.get("evidence")):
            raise ValueError("완료에는 evidence가 필요합니다")
        node["status"] = status
    if evidence is not None:
        node["evidence"] = evidence
    return result


def summary(tree: dict[str, Any]) -> dict[str, Any]:
    all_leaves = list(leaves(tree.get("roots", [])))
    counts = {status: sum(n["status"] == status for n in all_leaves) for status in STATUSES}
    scopes = {scope: sum(n["scope"] == scope for n in all_leaves) for scope in SCOPES}
    return {"leaf_count": len(all_leaves), "status": counts, "scope": scopes,
            "next": next_category(tree, "gear")}

