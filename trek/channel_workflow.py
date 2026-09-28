"""TREK 채널 상품관리의 저장·검증 절차."""
from __future__ import annotations

from dataclasses import dataclass, replace


STAGES = (
    "not_checked",
    "matched",
    "edited",
    "saved",
    "reverified",
)

SMARTSTORE_SEARCH_DEFAULTS = {
    "registration_period": "all",
    "sales_status": "all",
    "search_order": ("product_number", "sku", "exact_product_name"),
}

CHANNELS = {"smartstore", "cafe24"}


@dataclass(frozen=True)
class ChannelTask:
    sku: str
    channel: str
    stage: str = "not_checked"
    product_number: str = ""
    evidence: str = ""


def advance(task: ChannelTask, next_stage: str, *, evidence: str = "") -> ChannelTask:
    """단계를 순서대로만 진행하며 재검증에 근거를 요구한다."""
    if task.channel not in CHANNELS:
        raise ValueError(f"지원하지 않는 채널: {task.channel}")
    if next_stage not in STAGES:
        raise ValueError(f"지원하지 않는 단계: {next_stage}")
    current = STAGES.index(task.stage)
    target = STAGES.index(next_stage)
    if target != current + 1:
        raise ValueError(f"단계는 순서대로 진행해야 합니다: {task.stage} -> {next_stage}")
    if next_stage == "matched" and not task.product_number:
        raise ValueError("상품 매칭에는 채널 상품번호가 필요합니다")
    if next_stage == "reverified" and not evidence:
        raise ValueError("재검증에는 재접속 확인 근거가 필요합니다")
    return replace(task, stage=next_stage, evidence=evidence or task.evidence)


def is_complete(task: ChannelTask) -> bool:
    """저장 후 재접속 검증까지 끝난 경우만 완료로 판단한다."""
    return task.stage == "reverified" and bool(task.evidence)


def product_complete(tasks: list[ChannelTask]) -> bool:
    """카페24와 스마트스토어 양쪽이 모두 재검증되어야 상품 완료다."""
    by_channel = {task.channel: task for task in tasks}
    return CHANNELS <= by_channel.keys() and all(is_complete(by_channel[c]) for c in CHANNELS)

