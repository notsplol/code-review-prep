import pytest
from categorizer import ChangeCategorizer


def test_categorize_changes():
    data = [
        {"file": "src/foo.py", "status": "M", "additions": 10, "deletions": 2},
        {"file": "tests/test_foo.py", "status": "A", "additions": 5, "deletions": 0},
        {"file": "README.md", "status": "M", "additions": 1, "deletions": 0},
    ]
    cat = ChangeCategorizer()
    categories = cat.categorize_changes(data)
    assert len(categories["code"]) == 1
    assert len(categories["tests"]) == 1
    assert len(categories["docs"]) == 1


def test_risk_assessment():
    data = [
        {"file": "src/large.py", "status": "M", "additions": 150, "deletions": 60},
        {"file": "src/foo.py", "status": "M", "additions": 10, "deletions": 2},
    ]
    cat = ChangeCategorizer()
    risks = cat.assess_risks(data)
    assert "large_changes" in risks
    assert len(risks["large_changes"]) == 1
