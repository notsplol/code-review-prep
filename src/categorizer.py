class ChangeCategorizer:
    def __init__(self):
        pass

    def categorize_changes(self, diff_data: list):
        """
        Input: list of file diffs from BranchAnalyzer
        Output: dictionary of all the categorized changes
        Example:
        {
            'new_features': [...],
            'bug_fixes': [...],
            'refactoring': [...],
            'config_changes': [...],
            'tests': [...],
            'dependencies': [...]
        }
        """
        raise NotImplementedError

    def assess_risks(self, diff_data: list):
        """
        Make highlights for potential risks:
        - Large diffs
        - Sensitive file changes (db, auth, payments)
        - New dependencies added
        """
        raise NotImplementedError
