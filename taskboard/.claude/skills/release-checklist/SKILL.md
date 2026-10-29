---
name: release-checklist
description: Checklist before releasing a new version. Use when the user asks to prepare a release, bump version, tag a release, or check if a branch is ready to ship.
---

# Release checklist

Work through each step in order and report pass/fail for each:

1. **Branch**: confirm we are on `main` (or the release branch) and it is up to date with remote.
2. **Tests**: run the test suite (`npm test` / `pytest` — use whatever the repo uses). Stop if anything fails.
3. **Lint/build**: run lint and a production build.
4. **Migrations**: list any new DB migrations since the last tag (`git diff <last-tag>..HEAD --name-only | grep migrations`). Flag them.
5. **Changelog**: draft CHANGELOG entries from commits since the last tag, grouped into Added / Changed / Fixed.
6. **Version**: propose the next version using semver, with a reason.
7. **Summary**: end with a table of all steps and a clear READY / NOT READY verdict.

Never push tags or publish without explicit confirmation from the user.
