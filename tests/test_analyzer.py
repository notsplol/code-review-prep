from analyzer import BranchAnalyzer


def test_dummy_diff(monkeypatch):
    def fake_get_changed_files(self, branch_name, base_branch="main"):
        return [
            {"file": "src/foo.py", "status": "M", "additions": 10, "deletions": 2},
            {
                "file": "tests/test_foo.py",
                "status": "A",
                "additions": 5,
                "deletions": 0,
            },
        ]

    monkeypatch.setattr(BranchAnalyzer, "get_changed_files", fake_get_changed_files)

    analyzer = BranchAnalyzer()
    diff = analyzer.get_changed_files("feature/fake")
    assert len(diff) == 2
    assert diff[0]["file"] == "src/foo.py"
