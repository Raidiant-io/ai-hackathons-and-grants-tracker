# AI Hackathons & Grants Tracker

A local-first explorer for verified software-building opportunities: hackathons,
competitions, grants, and bounties. Includes a sortable table, responsive cards,
deadline calendar, search, category filters, and an expired/archived toggle.

## Run locally

Requires Python 3.10+. Node 20+ is optional for npm shortcuts and filter tests.

```sh
npm start
# Or, without Node:
python3 -m http.server 8766 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8766/. Reuse an existing healthy server; do not stop an
unrelated service occupying the port. Opening `dist/index.html` directly also
works. No build, dependencies or cloud service is required to run locally.

## GitHub Pages

Live app: https://raidiant-io.github.io/ai-hackathons-and-grants-tracker/

`.github/workflows/pages.yml` tests the app and deploys only `dist/` after changes
to that folder reach `main`. It also supports manual workflow dispatch. Relative
asset paths work under the repository's Pages URL. Private posting inputs never
reach the deployment artifact.

After a scheduled catalog sync, review and commit just `dist/opportunities.json`
and `dist/opportunities.js`, push to `main`, and confirm the Pages deployment
and live catalog match. Preserve unrelated/staged changes; do not force-push to
resolve conflicts. Publishing failures do not justify reposting Discord messages.

## Location filters

- **Remote** is the default: confirmed reward access without required travel.
- **In person** includes physical and hybrid participation anywhere. A country
  dropdown lists destinations present in the full catalog, including archives.
- **Format not stated** keeps incomplete historical participation details distinct.
- **All locations** displays every accepted normal catalog entry.

Country selection applies only to In person. The table and calendar share all
filters; Clear filters returns to Remote. Missing countries appear as Not stated,
not guessed from city names. Multi-country events match each stated destination.

Our current research prioritizes remote opportunities and only selects new
in-person events in Chile/Europe. That is a discovery preference, not an app
restriction. See [the research policy](docs/research-policy.md).

## Catalog and sync

`dist/opportunities.json` is the public catalog. The equivalent
`dist/opportunities.js` renders it at runtime, including when opened from a local
file where browsers block JSON fetches. No entries are hard-coded in HTML.
`dist/catalog-filters.js` owns generic participation/country matching.

After posting verified entries through the existing private Discord workflow
and writing the scan report, sync from external inputs:

```sh
python3 sync_catalog.py \
  --registry /path/to/private/posted_opportunities.json \
  --batches-dir /path/to/private/saved-batches \
  --report /path/to/report-2026-09-28.md
```

The script only reads the registry. Saved batches enrich accepted entries;
the report refreshes open/archived status. Unaccepted, failed-to-post and watchlist
items are excluded. Accepted evidence-backed trust warnings appear separately;
previous normal entries with later warnings leave the normal table. Warnings
are cautions, not findings of fraud.

Existing local automation can still use the original adjacent-folder defaults;
fresh clones should pass explicit paths. The latest public catalog is checked in
so anyone can run the app without private posting inputs.

Verify the JSON/JS agree, all accepted identities appear once, and catalog/warning
counts match posting history. If a server is running, verify it loads the refreshed
catalog; otherwise report updated-on-disk status. Local failures never justify
reposting accepted Discord messages.

Archive status comes from the latest verified report. Known date-only cutoffs
also archive after that UTC date ends; confirm exact timezones with the organizer.

## Related checks

```sh
npm run test:filters        # Generic participation/country behavior
npm run test:participation  # Conservative location metadata
npm run test:catalog        # Private inputs → public catalog/companion script
```

UI wiring is additionally verified in the local browser. The repository does not
include webhook credentials, private registries/batches, or dormant hosting
metadata. Keep such inputs outside this repository.
