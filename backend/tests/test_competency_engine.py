def get_level_from_accuracy(accuracy: float) -> int:
    """
    Deterministic accuracy-to-proficiency mapping.

    0–20%   -> Level 1
    21–40%  -> Level 2
    41–60%  -> Level 3
    61–80%  -> Level 4
    81–100% -> Level 5
    """
    if accuracy <= 20:
        return 1
    elif accuracy <= 40:
        return 2
    elif accuracy <= 60:
        return 3
    elif accuracy <= 80:
        return 4
    else:
        return 5


def calculate_gap(required_level: int, current_level: int) -> int:
    """Required level - current level, never below zero."""
    return max(required_level - current_level, 0)


def calculate_priority(
    gap: int,
    is_critical: bool,
    organizational_priority: int,
) -> int:
    """
    Priority formula:

    (Gap × 2) + Criticality Weight + Organizational Priority

    Critical -> 2
    Non-critical -> 0
    """
    criticality_weight = 2 if is_critical else 0

    return (
        (gap * 2)
        + criticality_weight
        + organizational_priority
    )


def test_beginner_level():
    assert get_level_from_accuracy(0) == 1
    assert get_level_from_accuracy(20) == 1


def test_basic_level():
    assert get_level_from_accuracy(21) == 2
    assert get_level_from_accuracy(40) == 2


def test_intermediate_level():
    assert get_level_from_accuracy(41) == 3
    assert get_level_from_accuracy(60) == 3


def test_advanced_level():
    assert get_level_from_accuracy(61) == 4
    assert get_level_from_accuracy(80) == 4


def test_expert_level():
    assert get_level_from_accuracy(81) == 5
    assert get_level_from_accuracy(100) == 5


def test_skill_gap():
    assert calculate_gap(4, 1) == 3
    assert calculate_gap(4, 4) == 0
    assert calculate_gap(3, 5) == 0


def test_critical_high_priority():
    assert calculate_priority(
        gap=3,
        is_critical=True,
        organizational_priority=3,
    ) == 11


def test_non_critical_normal_priority():
    assert calculate_priority(
        gap=2,
        is_critical=False,
        organizational_priority=1,
    ) == 5


def test_priority_ordering():
    high = calculate_priority(
        gap=3,
        is_critical=True,
        organizational_priority=3,
    )

    low = calculate_priority(
        gap=1,
        is_critical=False,
        organizational_priority=1,
    )

    assert high > low