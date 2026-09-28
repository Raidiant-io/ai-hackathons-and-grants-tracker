const {test} = require('node:test');
const assert = require('node:assert/strict');
const {compareMaxAward, maxAwardLabel} = require('./dist/catalog-rewards.js');

test('max award sorts numeric per-entry amounts, not the advertised prize pool', () => {
  const entries = [
    {name:'Small winner', reward:'$1 million prize pool', max_award_amount:900, max_award_currency:'USD'},
    {name:'Large winner', reward:'Small program', max_award_amount:12000, max_award_currency:'USD'},
    {name:'Middle winner', max_award_amount:2500.5, max_award_currency:'USD'},
  ];
  assert.deepEqual([...entries].sort((a,b)=>compareMaxAward(a,b,'desc')).map(e=>e.name), ['Large winner','Middle winner','Small winner']);
  assert.deepEqual([...entries].sort((a,b)=>compareMaxAward(a,b,'asc')).map(e=>e.name), ['Small winner','Middle winner','Large winner']);
});

test('unknowns stay last in either direction; zero is not unknown', () => {
  const entries = [
    {name:'Unknown', reward:'$1 billion'},
    {name:'Invalid string', max_award_amount:'50000', max_award_currency:'USD'},
    {name:'No currency', max_award_amount:50000},
    {name:'Zero', max_award_amount:0, max_award_currency:'USD'},
    {name:'Known', max_award_amount:10, max_award_currency:'USD'},
  ];
  for (const direction of ['asc','desc']) {
    const sorted = [...entries].sort((a,b)=>compareMaxAward(a,b,direction));
    assert.deepEqual(new Set(sorted.slice(0,2).map(e=>e.name)), new Set(['Known','Zero']));
    assert.equal(maxAwardLabel(sorted[2]), 'Not verified');
  }
  assert.equal(maxAwardLabel(entries[0]), 'Not verified');
  assert.equal(maxAwardLabel(entries[3]), 'USD 0');
});

test('currencies remain separate groups rather than pretending to convert their values', () => {
  const entries = [
    {name:'Dollars', max_award_amount:500000, max_award_currency:'USD'},
    {name:'Euro small', max_award_amount:50, max_award_currency:'EUR'},
    {name:'Euro large', max_award_amount:2000, max_award_currency:'EUR'},
  ];
  assert.deepEqual(entries.sort((a,b)=>compareMaxAward(a,b,'desc')).map(e=>e.name), ['Euro large','Euro small','Dollars']);
  assert.equal(maxAwardLabel(entries[1]), 'EUR 50');
});
