"""Additional Project tests to cover from_dict path."""

from stfwb.core.project import Project


def test_project_from_dict_roundtrip():
    p = Project(name="p", target_uri="u")  # pyright: ignore[reportCallIssue]
    d = p.to_dict()
    p2 = Project.from_dict(d)
    assert p2.name == "p"
    assert p2.target_uri == "u"
    assert p2.is_valid()
