# AI Hackathons & Grants Tracker

Local-first static app in `dist/`. Run with `npm start`; no hosted publishing.
Keep the table, calendar, sorting, and archive toggle working together.

## Catalog contract

Remote is the default. In person filters any verified physical destination via
the country selector. Missing formats/countries stay explicitly unstated.
The UI must not enforce personal research geography; before changing discovery
or delivery, read `docs/research-policy.md` for that separate policy.

`sync_catalog.py` reads external private inputs and writes public JSON plus its
equivalent companion JS. Only accepted Discord records belong in the catalog;
evidence-backed warnings remain separate. It must never modify posting history.
No credentials, private registry, posting batches, local machine paths, hosting
metadata or Discord message identifiers belong in Git or the public catalog.

## Verification

Run the related command for each changed boundary: `npm run test:filters` for
`dist/catalog-filters.js`, `npm run test:participation` for `participation.py`,
and `npm run test:catalog` for sync/serialization. Verify UI wiring in the local
browser after HTML changes; test both table and calendar and reset behavior.
Python unittest has no native changed-path selector, so select these documented
test classes explicitly instead of adding a custom test-selection tool.

Use this file as the canonical agent guidance; equivalent agent-instruction
filenames must be symlinks rather than duplicate content.
