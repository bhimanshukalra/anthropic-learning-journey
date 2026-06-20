# Existing test — passed into context so CI test-gen doesn't duplicate this scenario.
# (Note what's NOT covered yet: average([]) — the empty-list edge case.)

from app.calculator import average


def test_average_basic():
    assert average([2, 4, 6]) == 4
