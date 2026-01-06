"""Tests for stfwb.utils.coverage module."""

from stfwb.utils.coverage import Coverage
from stfwb.core.types import CoverageUnit


def test_coverage_percentage_zero_total():
    cov = Coverage(unit=CoverageUnit.FRAGMENTS, covered=0, total=0, gaps=[])
    assert cov.percentage == 0.0
    # By definition here, 0/0 is considered complete
    assert cov.is_complete is True
    d = cov.to_dict()
    assert d["unit"] == CoverageUnit.FRAGMENTS.value
    assert d["covered"] == 0 and d["total"] == 0 and d["percentage"] == 0.0


def test_coverage_percentage_and_dict():
    cov = Coverage(unit=CoverageUnit.SECTIONS, covered=3, total=5, gaps=["s1", "s2"])
    assert cov.percentage == 60.0
    assert cov.is_complete is False
    d = cov.to_dict()
    assert d == {
        "unit": CoverageUnit.SECTIONS.value,
        "covered": 3,
        "total": 5,
        "percentage": 60.0,
        "gaps": ["s1", "s2"],
    }
