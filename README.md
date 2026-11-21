# MMT Business Corporation Hub

A static dashboard of the MMT repositories. A GitHub Action reads each repo
(stars, issues, language, last push, last workflow run) every 15 minutes and
writes `data/repos.json`. `index.html` reads that file and flags each repo as
fresh, stale or failing from its last sync run.

## Setup

1. Create a new GitHub repo (for example `mmt-hub`) and upload everything in this folder.
2. Settings > Pages > Deploy from a branch > `main` / `(root)`.
3. Actions tab > "Sync repo data" > Run workflow. Open `https://<username>.github.io/<repo>/`.
4. If any of your repos are private, add a repository secret named `GH_PAT`
   (a fine-grained token with read access to Contents, Metadata and Actions on those repos).

## Change the repo list

Edit `config/repos.json`. `sync_minutes` is how often that repo's own sync runs;
a repo is marked stale when its last run is older than 3x that interval plus 15 minutes.
Leave it `null` to show only the last sync time.

## Notes

- GitHub can delay scheduled runs and pauses them after 60 days without repo activity.
- No secrets are stored in the page or in `data/repos.json`.
