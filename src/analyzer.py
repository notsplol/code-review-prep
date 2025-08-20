from git import Repo
from pathlib import Path


class BranchAnalyzer:
    def __init__(self, repo_path: str = "."):
        self.repo = Repo(Path(repo_path).resolve())

    def get_changed_files(self, branch_name: str, base_branch: str = "main"):
        """
        Returns a list of changed files between `base_branch` and `branch_name`.

        Each entry:
        {'file': str, 'status': A|M|D, 'additions': int, 'deletions': int}
        """

        def _resolve_ref(name: str) -> str:
            
            local_heads = [h.name for h in self.repo.heads]
            if name in local_heads:
                return name

            
            try:
                origin = self.repo.remotes.origin
                origin_refs = [r.name for r in origin.refs]
            except Exception:
                origin_refs = []

            if f"origin/{name}" in origin_refs:
                return f"origin/{name}"

            
            try:
                self.repo.commit(name)
                return name
            except Exception:
                raise ValueError(
                    f"Branch or ref '{name}' does not exist " "locally or on origin"
                )

        base_ref = _resolve_ref(base_branch)
        target_ref = _resolve_ref(branch_name)

        # get status map from name-status
        name_status = self.repo.git.diff(f"{base_ref}..{target_ref}", "--name-status")
        status_map = {}
        for ln in name_status.splitlines():
            parts = ln.split("\t")
            if len(parts) >= 2:
                status_map[parts[1]] = parts[0]

        # parse additions and deletions from numstat
        numstat = self.repo.git.diff(f"{base_ref}..{target_ref}", "--numstat")
        changed_files = []
        for line in numstat.splitlines():
            parts = line.strip().split("\t")
            if len(parts) < 3:
                continue

            additions, deletions, file_path = parts[:3]
            additions = int(additions) if additions.isdigit() else 0
            deletions = int(deletions) if deletions.isdigit() else 0
            status = status_map.get(file_path, "M")
            changed_files.append(
                {
                    "file": file_path,
                    "status": status,
                    "additions": additions,
                    "deletions": deletions,
                }
            )

        return changed_files
