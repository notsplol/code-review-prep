from git import Repo
from pathlib import Path

class BranchAnalyzer:
    def __init__(self, repo_path="."):
        self.repo = Repo(Path(repo_path).resolve())

    def get_changed_files(self, branch_name: str):
        """
        Similar to diff. Returns list of changed files between main and branch_name.
        Each entry: {
            'file': str,
            'status': 'A' | 'M' | 'D',
            'additions': int,
            'deletions': int
        }
        """
        #branch existance step
        if branch_name not in [head.name for head in self.repo.heads]:
            raise ValueError(f"Branch '{branch_name}' does not exist.")

        main_branch = "main"
        diff = self.repo.git.diff(
            f"{main_branch}..{branch_name}", "--numstat", "--name-status"
        )

        changed_files = []
        for line in diff.splitlines():
            parts = line.strip().split("\t")
            if len(parts) < 3:
                continue

            #first two columns = additions & deletions, third = file path
            additions, deletions, file_path = parts[:3]
            additions = int(additions) if additions.isdigit() else 0
            deletions = int(deletions) if deletions.isdigit() else 0

            #get status (Added/Modified/Deleted)
            status_output = self.repo.git.diff(
                f"{main_branch}..{branch_name}", "--name-status"
            )
            status_map = {
                f.split("\t")[1]: f.split("\t")[0] for f in status_output.splitlines()
            }
            status = status_map.get(file_path, "M")

            changed_files.append({
                "file": file_path,
                "status": status,
                "additions": additions,
                "deletions": deletions,
            })

        return changed_files

