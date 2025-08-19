import sys
import click
from analyzer import BranchAnalyzer
from categorizer import ChangeCategorizer
from reporter import ReviewReporter


@click.command()
@click.option("--branch", required=True, help="Feature branch name to compare against main")
@click.option("--base", default="main", show_default=True, help="Base branch to compare from")
def review_ready(branch: str, base: str):
    """
    Analyze branch diffs, categorize changes, assess risks, and print a review-ready summary.
    """
    analyzer = BranchAnalyzer()
    categorizer = ChangeCategorizer()
    reporter = ReviewReporter()

   #step 1
    try:
        diff_data = analyzer.get_changed_files(branch, base)
    except Exception as e:
        click.echo(f"[error] Failed to compute diff: {e}", err=True)
        sys.exit(1)

    if not diff_data:
        click.echo("No differences found between base and branch.")
        sys.exit(0)

    #step 2
    categories = categorizer.categorize_changes(diff_data)
    risks = categorizer.assess_risks(diff_data)
    suggested_reviewers = categorizer.suggest_reviewers(diff_data)
    checklist = categorizer.checklist(risks)

    #step 3
    summary = {
        "branch": branch,
        "diff_data": diff_data,
        "categories": categories,
        "risks": risks,
        "suggested_reviewers": suggested_reviewers,
        "checklist": checklist,
    }

    #step 4
    reporter.print_summary(branch, summary)


if __name__ == "__main__":
    review_ready()
