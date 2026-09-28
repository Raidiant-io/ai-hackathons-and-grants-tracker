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

## Per-entry award

For every researched normal entry, collect a separate ceiling for a single
project/proposal/report submitted by one eligible solo entrant or team of up to
five, before taxes. Keep `reward` as the advertised pool/bundle description.
Record these fields in the saved Discord candidate batch, including explicit
nulls when the ceiling is unresolved; the site synchronizer preserves them:

- `max_award_amount`: JSON number or null, never formatted text.
- `max_award_currency`: currency code (e.g. USD, EUR, GBP, USDC) or null.
- `max_award_kind`: cash, credits, crypto, mixed, or in_kind; null if unresolved.
- `max_award_basis`: short calculation, scope, restrictions and uncertainty.
- `max_award_evidence_url`: primary rules/prize/funding page, or null if unresolved.
- `max_award_verified_at`: assessment date as YYYY-MM-DD.

Read the individual prize amounts and prize-stacking rules. For mutually exclusive
prizes use the largest eligible award. Sum only amounts that the same entry can
win together, in the same currency, with official evidence of stacking. Count a
team award once, not once per member. Apply any verified per-member caps using
the maximum eligible team size up to five. Exclude student-only rewards and
separate applications, renewals, unrelated tracks and registration/build credits
from a winning entry's ceiling. Explain conditional bonuses, milestone payouts
and restricted award categories in the basis.

Use organizer-stated nominal values for credits or equipment; label them noncash.
Keep unpriced perks in reward details without assigning a guessed value. A typical
grant range, aggregate fund or unsupported stacking claim cannot establish a
ceiling: amount/currency/kind stay null, with the reason in the basis. Unknown
does not mean zero. Do not parse a number out of the reward description or infer
missing denominations, payout types, eligibility or prize compatibility.

The site sorts numeric ceilings within currency groups without FX conversion;
unverified entries stay last in both directions. `data/max-awards.json` contains
public evidence-backed backfills for already accepted entries. Newer saved
assessments supersede these atomically, including an explicit unknown assessment
that clears a former amount. Only registry-accepted entries reach the catalog;
backfills never create new entries or trigger Discord reposts. Complete this step
when each candidate has either a sourced numeric ceiling with basis/date or an
explicit unresolved assessment. Include this distinction in scan reporting.
