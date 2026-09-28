(function(root) {
  "use strict";
  const hasMaxAward = entry => typeof entry.max_award_amount === "number" &&
    Number.isFinite(entry.max_award_amount) && entry.max_award_amount >= 0 &&
    typeof entry.max_award_currency === "string" && /^[A-Z]{3,10}$/.test(entry.max_award_currency);
  function compareMaxAward(a,b,direction="desc") {
    const aKnown=hasMaxAward(a), bKnown=hasMaxAward(b);
    if(aKnown!==bKnown) return aKnown?-1:1;
    const tie=()=>String(a.name||"").localeCompare(String(b.name||""));
    if(!aKnown) return tie();
    // Values in different currencies are not comparable without a dated FX rate.
    const currency=a.max_award_currency.localeCompare(b.max_award_currency);
    return currency || (direction==="desc"?-1:1)*(a.max_award_amount-b.max_award_amount) || tie();
  }
  function maxAwardLabel(entry) {
    if(!hasMaxAward(entry)) return "Not verified";
    return `${entry.max_award_currency} ${new Intl.NumberFormat("en-US",{maximumFractionDigits:2}).format(entry.max_award_amount)}`;
  }
  const api={hasMaxAward,compareMaxAward,maxAwardLabel};
  if(typeof module==="object"&&module.exports) module.exports=api;
  else root.CatalogRewards=api;
})(typeof window==="undefined"?globalThis:window);
