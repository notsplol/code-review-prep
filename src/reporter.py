from __future__ import annotations
from typing import Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

console = Console()


class ReviewReporter:
    def __init__(self):
        pass

    def _sum_stats(self, diff_data: List[Dict]) -> Dict[str, int]:
        return {
            "files": len(diff_data),
            "additions": sum(f.get("additions", 0) for f in diff_data),
            "deletions": sum(f.get("deletions", 0) for f in diff_data),
        }

    def _render_focus(self, focus: List[Dict]) -> Table:
        t = Table(show_header=True, header_style="bold")
        t.add_column("File", overflow="fold")
        t.add_column("Status", width=9)
        t.add_column("+", justify="right")
        t.add_column("-", justify="right")
        for f in focus:
            t.add_row(
                f["file"],
                f.get("status", "?"),
                str(f.get("additions", 0)),
                str(f.get("deletions", 0)),
            )
        return t

    def _render_categories(self, categories: Dict[str, List[Dict]]) -> Table:
        t = Table(show_header=True, header_style="bold")
        t.add_column("Category")
        t.add_column("Count", justify="right")
        t.add_row("Added", str(len(categories.get("added", []))))
        t.add_row("Modified", str(len(categories.get("modified", []))))
        t.add_row("Deleted", str(len(categories.get("deleted", []))))
        t.add_row("Code files", str(len(categories.get("code", []))))
        t.add_row("Tests", str(len(categories.get("tests", []))))
        t.add_row("Docs", str(len(categories.get("docs", []))))
        t.add_row("Config", str(len(categories.get("config", []))))
        t.add_row("Dependencies", str(len(categories.get("dependencies", []))))
        return t

    def _render_checklist(self, items: List[str]) -> Text:
        txt = Text()
        for it in items:
            txt.append("□ ")
            txt.append(it + "\n")
        return txt

    def print_summary(self, branch_name: str, summary: Dict):
        diff_data = summary["diff_data"]
        stats = self._sum_stats(diff_data)
        risks = summary["risks"]
        categories = summary["categories"]

        console.print()
        console.print(
            Panel.fit(f"[bold]📋 Review Summary for [cyan]{branch_name}[/cyan][/bold]")
        )

        console.print(Rule())

        # Overview
        overview = Table(show_header=False)
        overview.add_row("📊 Files changed", str(stats["files"]))
        overview.add_row("➕ Additions", str(stats["additions"]))
        overview.add_row("➖ Deletions", str(stats["deletions"]))
        overview.add_row("⏱️ Est. review time", f"{risks['estimate_minutes']} minutes")
        console.print(overview)

        console.print()
        console.print(
            Panel(
                self._render_categories(categories),
                title="Change Overview",
                expand=False,
            )
        )

        if risks["focus_areas"]:
            console.print()
            console.print(
                Panel(
                    self._render_focus(risks["focus_areas"]),
                    title="🔍 Review Focus Areas",
                    expand=False,
                )
            )

        concerns: List[str] = []
        if risks["large_changes"]:
            concerns.append(
                f"{len(risks['large_changes'])} large files changed (≥100 LOC churn)"
            )
        if risks["new_dependencies"]:
            concerns.append("New/updated dependencies detected")
        sens = risks["sensitive_areas"]
        if sens:
            areas_list = ", ".join(k for k, v in sens.items() if v)
            if areas_list:
                concerns.append(f"Sensitive areas touched: {areas_list}")
        if risks["missing_tests"]:
            concerns.append("No tests changed while code changed")

        if concerns:
            concerns_table = Table(show_header=False)
            for c in concerns:
                concerns_table.add_row(f"• {c}")
            console.print()
            console.print(
                Panel(concerns_table, title="⚠️ Potential Concerns", expand=False)
            )

        checklist_items = summary.get("checklist", [])
        if checklist_items:
            console.print()
            console.print(
                Panel(
                    self._render_checklist(checklist_items),
                    title="✅ Checklist for Reviewer",
                    expand=False,
                )
            )

        console.print()
