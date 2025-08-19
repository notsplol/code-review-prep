import click
from analyzer import BranchAnalyzer
from categorizer import ChangeCategorizer
from reporter import ReviewReporter

@click.command()
@click.option("--branch", required=True, help="Branch name to analyze")
def review_ready(branch):
    analyzer = BranchAnalyzer()
    categorizer = ChangeCategorizer()
    reporter = ReviewReporter()

    # Step 1: Analyze branch
    diff_data = analyzer.get_changed_files(branch)

    # Step 2: Categorize changes + assess risks
    categories = categorizer.categorize_changes(diff_data)
    risks = categorizer.assess_risks(diff_data)

    # Step 3: Build summary (stub for now)
    summary = {
        "branch": branch,
        "diff_data": diff_data,
        "categories": categories,
        "risks": risks,
        "suggested_reviewers": ["@alice", "@bob"],  # placeholder
    }

    # Step 4: Print results
    reporter.print_summary(branch, summary)

if __name__ == "__main__":
    review_ready()
