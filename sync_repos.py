#!/usr/bin/env python3
"""Reads GitHub repo facts and the latest workflow run for each repo in
config/repos.json and writes data/repos.json for the dashboard.
Standard library only. Needs GH_TOKEN (Actions provides one automatically)."""
import json, os, sys, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = os.environ.get("GH_TOKEN", "")


def api(path):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "mmt-hub-sync")
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    with open(os.path.join(ROOT, "config", "repos.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    owner, out = cfg["owner"], []
    for c in cfg["repos"]:
        name = c["name"]
        item = {
            "name": name, "url": f"https://github.com/{owner}/{name}",
            "status": c.get("status", "Active"), "language": "Other",
            "stars": 0, "issues": 0, "updated": "",
            "description": c.get("description", ""),
            "live": f"https://{owner}.github.io/{name}/",
            "sync_minutes": c.get("sync_minutes"),
            "last_run": "", "conclusion": "", "error": "",
        }
        try:
            r = api(f"/repos/{owner}/{name}")
            item["language"] = r.get("language") or "Other"
            item["stars"] = r.get("stargazers_count", 0)
            item["issues"] = r.get("open_issues_count", 0)
            item["updated"] = (r.get("pushed_at") or "")[:10]
            if not item["description"]:
                item["description"] = r.get("description") or ""
            if r.get("homepage"):
                item["live"] = r["homepage"]
        except urllib.error.HTTPError as e:
            item["error"] = f"repo: HTTP {e.code}"
        except Exception as e:
            item["error"] = f"repo: {e}"
        try:
            runs = api(f"/repos/{owner}/{name}/actions/runs?status=completed&per_page=1")
            if runs.get("workflow_runs"):
                run = runs["workflow_runs"][0]
                item["last_run"] = run.get("updated_at", "")
                item["conclusion"] = run.get("conclusion") or ""
        except Exception as e:
            item["error"] = (item["error"] + " runs: " + str(e)).strip()
        out.append(item)

    path = os.path.join(ROOT, "data", "repos.json")
    new = {"repos": out}
    try:
        with open(path, encoding="utf-8") as f:
            if json.load(f) == new:
                print("No changes.")
                return
    except Exception:
        pass
    with open(path, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=2)
    print(f"Wrote {len(out)} repos.")
    if all(i["error"] for i in out):
        sys.exit("Every repo failed. Check GH_TOKEN and repo names.")


if __name__ == "__main__":
    main()
