/* Shared by the browser and focused Node tests; no research geography baked in. */
(function (root) {
  const hasRemote = entry => entry.remote_eligible === true && entry.attendance_required !== true;
  const hasInPerson = entry => ["in_person", "hybrid"].includes(entry.participation_mode);
  const countriesFor = entry => Array.isArray(entry.attendance_countries)
    ? [...new Set(entry.attendance_countries.filter(value => typeof value === "string" && value.trim()).map(value => value.trim()))]
    : [];
  function countryOptions(entries) {
    const physical = entries.filter(hasInPerson);
    const options = [...new Set(physical.flatMap(countriesFor))].sort((a, b) => a.localeCompare(b));
    if (physical.some(entry => !countriesFor(entry).length)) options.push("Not stated");
    return options;
  }
  function matchesParticipation(entry, format = "remote", country = "all") {
    if (format === "remote") return hasRemote(entry);
    if (format === "not_stated") return !entry.participation_mode || entry.participation_mode === "not_stated";
    if (format === "all") return true;
    if (format !== "in_person" || !hasInPerson(entry)) return false;
    const countries = countriesFor(entry);
    return country === "all" || (country === "Not stated" ? !countries.length : countries.includes(country));
  }
  const api = {hasRemote, hasInPerson, countriesFor, countryOptions, matchesParticipation};
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.CatalogFilters = api;
})(typeof window === "undefined" ? globalThis : window);
