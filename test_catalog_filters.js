const test = require("node:test");
const assert = require("node:assert/strict");
const {matchesParticipation, countryOptions} = require("./dist/catalog-filters.js");

test("remote reward access excludes required foreign finales and ignores stale country selection", () => {
  assert.equal(matchesParticipation({participation_mode:"hybrid", remote_eligible:true, attendance_required:true}, "remote"), false);
  assert.equal(matchesParticipation({participation_mode:"remote", remote_eligible:true}, "remote", "Japan"), true);
});
test("in-person filters have no research-geography restriction and support multiple countries", () => {
  const entry = {participation_mode:"hybrid", attendance_countries:["Japan", "Canada"]};
  assert.equal(matchesParticipation(entry, "in_person"), true);
  assert.equal(matchesParticipation(entry, "in_person", "Japan"), true);
  assert.equal(matchesParticipation(entry, "in_person", "Canada"), true);
  assert.equal(matchesParticipation(entry, "in_person", "Chile"), false);
});
test("unresolved physical countries stay discoverable without implying remote participation", () => {
  const physical = {participation_mode:"in_person"};
  const unknown = {participation_mode:"not_stated"};
  assert.equal(matchesParticipation(physical, "in_person", "Not stated"), true);
  assert.equal(matchesParticipation(unknown, "in_person"), false);
  assert.equal(matchesParticipation(unknown, "remote"), false);
  assert.equal(matchesParticipation(unknown, "not_stated"), true);
  assert.equal(matchesParticipation(physical, "all"), true);
});
test("country options are stable, unique, catalog-driven and physical-only", () => {
  const entries = [
    {participation_mode:"in_person", attendance_countries:["Japan", "Japan"]},
    {participation_mode:"hybrid", attendance_countries:["Canada", "Chile"]},
    {participation_mode:"remote", attendance_countries:["France"]},
    {participation_mode:"in_person", attendance_countries:[]}
  ];
  assert.deepEqual(countryOptions(entries), ["Canada", "Chile", "Japan", "Not stated"]);
});
