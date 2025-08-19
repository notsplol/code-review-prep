from __future__ import annotations
from typing import Dict, List


# helpers

CODE_EXTS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rb",
    ".php",
    ".cs",
    ".cpp",
    ".c",
    ".rs",
    ".kt",
    ".m",
    ".swift",
}
TEST_DIR_TOKENS = {"tests", "__tests__", "spec", "test"}
TEST_FILE_TOKENS = {"test_", "_test", ".spec.", ".spec_", ".spec-"}
DOC_EXTS = {".md", ".rst", ".adoc"}
CONFIG_EXTS = {
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".env",
    ".properties",
}
DEPENDENCY_FILES = {
    "requirements.txt",
    "poetry.lock",
    "pyproject.toml",
    "Pipfile",
    "Pipfile.lock",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "Gemfile",
    "Gemfile.lock",
}
SENSITIVE_AREAS = {
    "auth": ("auth", "authentication", "oauth", "jwt"),
    "payments": ("payment", "payments", "billing", "stripe", "paypal"),
    "database": (
        "db",
        "database",
        "models",
        "migrations",
        "repository",
        "queries",
        "dao",
        "prisma",
        "sequelize",
    ),
    "api": ("api", "endpoints", "controller", "router"),
    "config": ("config", "settings", "secrets", ".env"),
}


def _ext(path: str) -> str:
    dot = path.rfind(".")
    return path[dot:].lower() if dot != -1 else ""


def _is_test_file(path: str) -> bool:
    lower = path.lower()
    if any(t in lower.split("/") for t in TEST_DIR_TOKENS):
        return True
    return any(tok in lower for tok in TEST_FILE_TOKENS)


def _is_code_file(path: str) -> bool:
    return _ext(path) in CODE_EXTS


def _is_doc_file(path: str) -> bool:
    return _ext(path) in DOC_EXTS


def _is_config_file(path: str) -> bool:
    return _ext(path) in CONFIG_EXTS or any(
        tok in path.lower() for tok in ("config", "settings")
    )


def _is_dependency_file(path: str) -> bool:
    return path.split("/")[-1] in DEPENDENCY_FILES


def _touches_sensitive_area(path: str) -> List[str]:
    lower = path.lower()
    hits = []
    for area, tokens in SENSITIVE_AREAS.items():
        if any(tok in lower for tok in tokens):
            hits.append(area)
    return hits


# main


class ChangeCategorizer:
    """
    Consumes diff_data from BranchAnalyzer and produces:
      - categories: dict of categorized changes
      - risks: structured risk assessment
      - suggestions: suggested reviewers &
                     checklist items (lightweight heuristics)
    """

    def categorize_changes(self, diff_data: List[Dict]) -> Dict[str, List[Dict]]:
        categories = {
            "added": [],
            "modified": [],
            "deleted": [],
            "tests": [],
            "docs": [],
            "config": [],
            "dependencies": [],
            "code": [],
            "other": [],
        }

        for f in diff_data:
            path = f["file"]
            status = f.get("status", "M")
            placed_specific = False

            if _is_test_file(path):
                categories["tests"].append(f)
                placed_specific = True
            elif _is_doc_file(path):
                categories["docs"].append(f)
                placed_specific = True
            elif _is_dependency_file(path):
                categories["dependencies"].append(f)
                placed_specific = True
            elif _is_config_file(path):
                categories["config"].append(f)
                placed_specific = True
            elif _is_code_file(path):
                categories["code"].append(f)
                placed_specific = True

            if not placed_specific:
                categories["other"].append(f)

            # status
            if status in ("A", "added"):
                categories["added"].append(f)
            elif status in ("M", "modified"):
                categories["modified"].append(f)
            elif status in ("D", "deleted"):
                categories["deleted"].append(f)

        return categories

    def assess_risks(self, diff_data: List[Dict]) -> Dict:
        risks = {
            "large_changes": [],
            "sensitive_areas": {},
            "missing_tests": [],
            "new_dependencies": [],
            "focus_areas": [],
            "estimate_minutes": 0,
        }

        total_add = sum(f.get("additions", 0) for f in diff_data)
        total_del = sum(f.get("deletions", 0) for f in diff_data)
        total_files = len(diff_data)

        # large file changes
        for f in diff_data:
            churn = f.get("additions", 0) + f.get("deletions", 0)
            if churn >= 100:
                risks["large_changes"].append({**f, "churn": churn})

        # sensitive changes
        sensitive_map: Dict[str, List[Dict]] = {}
        for f in diff_data:
            areas = _touches_sensitive_area(f["file"])
            for a in areas:
                sensitive_map.setdefault(a, []).append(f)
        risks["sensitive_areas"] = sensitive_map

        # dependencies
        risks["new_dependencies"] = [
            f for f in diff_data if _is_dependency_file(f["file"])
        ]

        # missing tests: touched code but no tests changed at all
        touched_code = any(
            _is_code_file(f["file"]) for f in diff_data if f.get("status") != "D"
        )
        touched_tests = any(
            _is_test_file(f["file"]) for f in diff_data if f.get("status") != "D"
        )
        if touched_code and not touched_tests:
            # add top 3 most changed code files as examples
            code_sorted = sorted(
                [f for f in diff_data if _is_code_file(f["file"])],
                key=lambda x: (x.get("additions", 0) + x.get("deletions", 0)),
                reverse=True,
            )
            risks["missing_tests"] = code_sorted[:3]

        focus = []
        focus.extend(risks["large_changes"])
        for files in sensitive_map.values():
            focus.extend(files)

        seen = set()
        focus_unique = []
        for f in sorted(
            focus,
            key=lambda x: x.get("additions", 0) + x.get("deletions", 0),
            reverse=True,
        ):
            if f["file"] in seen:
                continue
            seen.add(f["file"])
            focus_unique.append(f)
        risks["focus_areas"] = focus_unique[:5]

        # base 3 min + 1 min per file + (total LOC changed / 50)
        estimate = 3 + total_files * 1 + int((total_add + total_del) / 50)
        risks["estimate_minutes"] = max(5, min(60, estimate))

        return risks

    def suggest_reviewers(self, diff_data: List[Dict]) -> List[str]:
        """
        Lightweight heuristic: suggest owners by directory names.
        If later you integrate `git blame`, wire it here.
        """
        owners = set()
        for f in diff_data:
            parts = f["file"].split("/")
            if len(parts) > 1:
                # directory 'payments' -> reviewer '@payments'
                owners.add("@" + parts[0].replace("_", "-"))
        # stable, small list
        suggestions = sorted(list(owners))[:4]
        return suggestions

    def checklist(self, risks: Dict) -> List[str]:
        items = [
            "Verify error handling on modified critical paths",
            "Check test coverage for changed code",
            "Ensure docs/config updated if behavior changed",
        ]
        if risks["sensitive_areas"].get("database"):
            items.append("Confirm DB query performance and indexes")
            items.append("Review migration safety and rollback")
        if risks["sensitive_areas"].get("auth"):
            items.append("Validate auth flows, scopes, token handling")
        if risks["sensitive_areas"].get("payments"):
            items.append("Check payment flow idempotency and retries")
        if risks["new_dependencies"]:
            items.append("Review new dependencies for security/licensing")
        if risks["large_changes"]:
            items.append("Consider splitting oversized files/functions")
        return items
