from rich.console import Console
from rich.table import Table

console = Console()

class ReviewReporter:
    def __init__(self):
        pass

    def print_summary(self, branch_name: str, summary: dict):
        """
        Pretty-print review summary to console.
        """
        raise NotImplementedError

    def format_checklist(self, items: list):
        """
        Return formatted checklist string.
        """
        raise NotImplementedError
