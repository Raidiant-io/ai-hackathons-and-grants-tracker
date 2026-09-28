# Builder Funding Radar participation policy

Prioritize remote software-building opportunities. Include opportunities with
required physical attendance only in Chile or Europe (geographic Europe, not
only the EU; include the UK, Switzerland and other European countries).

Verify the full reward-bearing journey: building, judging, pitches, finalist
events and prize collection. An online application or qualifier does not make
an opportunity remote. Worldwide eligibility does not establish its format.
Keep residency, incorporation and jurisdiction restrictions separate from
attendance format and visible even for remote grants.

- **Remote:** a solo developer or team can complete the qualifying journey and
  receive the advertised reward without required travel. Optional local events
  are allowed and clearly labelled.
- **In person:** required attendance in Chile or Europe. State city/country,
  travel requirements and whether costs are covered or not stated.
- **Hybrid:** identify each required physical stage. Include required travel
  only in Chile or Europe. An optional in-person component with verified full
  remote prize access can appear in the Remote group, labelled hybrid/optional.
- **Not stated:** unresolved participation format, physical destination or
  remote prize access goes on the report watchlist, not in a new Discord batch.
  Do not infer missing format or call uncertainty a trust concern.

Apply this scope to discovery, qualification, Top 5 ranking, reports, normal
Discord messages and timely trust warnings. Explore remote sources first;
search separately for worthwhile Chilean and European in-person events.
Exclude required travel elsewhere, including foreign finales after online
builds. Preserve old Discord history; do not delete or repost existing entries.

For newly verified batch records, save these fields alongside the existing
required fields (and retain them in the site's catalog):

- `participation_mode`: `remote`, `in_person`, `hybrid`, or `not_stated`.
- `remote_eligible`: boolean or null; true only for confirmed complete remote
  participation with reward access and no required physical attendance.
- `attendance_required`: boolean or null; include required finalist travel.
- `attendance_region`: `Chile`, `Europe`, `Other`, or `Not stated` for the
  physical component; not the organizer's headquarters or eligible residence.
- `participation_note`: short factual attendance, travel and eligibility caveat.
- `participation_evidence_url`: primary rules/FAQ/application evidence.
- `attendance_countries`: array of verified physical destination country names;
  empty when unspecified or no physical component. Include multiple destinations
  when applicable. Country names are not residence/eligibility restrictions.

Send new normal messages remote-first, followed by Chile/Europe in-person and
hybrid entries, then any eligible trust warning list. Include the format and
city/country in the existing location field so Discord readers see it.

Within each existing report section (`Open now`, `Upcoming application windows`
and `Rolling or no-deadline grants`), separate Remote from In person / Hybrid —
Chile & Europe using third-level headings; keep the established table columns
and sort within each group by the first deadline a new entrant must meet.
Document geographic-scope removals separately from expired or untrustworthy
entries. Preserve second-level headings used by the catalog synchronizer.

The website is a generic catalog explorer, not a research-scope gate. It defaults
to Remote in table and calendar. In person exposes a catalog-driven country
selector for all destinations, including accepted historical entries outside
the current research scope. All locations includes every normal catalog entry.
Insufficient format evidence stays under Format not stated, and unspecified
physical countries remain selectable as Not stated. Keep the Chile/Europe
preference in discovery and delivery policy, not hard-coded in the app filters.
