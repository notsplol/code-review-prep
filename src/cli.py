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

    #step 1
    diff_data = analyzer.get_changed_files(branch)

    #step 2
    categories = categorizer.categorize_changes(diff_data)
    risks = categorizer.assess_risks(diff_data)

    #step 3
    summary = {
        "branch": branch,
        "diff_data": diff_data,
        "categories": categories,
        "risks": risks,
        "suggested_reviewers": ["@alice", "@bob"],
    }

    #step 4
    reporter.print_summary(branch, summary)

if __name__ == "__main__":
    review_ready()
