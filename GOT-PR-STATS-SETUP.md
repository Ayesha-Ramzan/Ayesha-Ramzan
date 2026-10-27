# GOT merged PR stats

The GOT repository is private, so public profile-stat services cannot read its pull requests. The profile uses `.github/workflows/update-got-pr-stats.yml` to fetch merged PRs securely and update `got-pr-stats.svg`.

Add a repository secret named `GOT_REPO_TOKEN` with a fine-grained GitHub token that has read-only **Pull requests** and **Metadata** access to:

`gobind-trades/Gobind-trades-Admin-dashboard-`

Then run **Actions → Update GOT PR stats → Run workflow** once. The workflow refreshes the card daily afterward.
