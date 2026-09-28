"""Explicit per-entry award assessments; never parse an advertised prize pool."""

import math
import re
from datetime import date
from urllib.parse import urlparse

AWARD_FIELDS = (
    'max_award_amount', 'max_award_currency', 'max_award_kind',
    'max_award_basis', 'max_award_evidence_url', 'max_award_verified_at',
)


def normalize_award(record: dict) -> dict:
    result = {field: record.get(field) for field in AWARD_FIELDS}
    amount = result['max_award_amount']
    currency = result['max_award_currency']
    evidence = urlparse(str(result['max_award_evidence_url'] or ''))
    checked = result['max_award_verified_at']
    valid_date = isinstance(checked, str) and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', checked))
    if valid_date:
        try:
            date.fromisoformat(checked)
        except ValueError:
            valid_date = False
    if amount is None:
        if 'max_award_amount' in record and (not valid_date or not result['max_award_basis']):
            raise ValueError('An unresolved award assessment needs a reason and valid date')
        result.update(max_award_currency=None, max_award_kind=None, max_award_evidence_url=None)
        return result
    if (type(amount) not in (int, float) or not math.isfinite(amount) or amount < 0
            or not isinstance(currency, str) or not re.fullmatch(r'[A-Z]{3,10}', currency)
            or result['max_award_kind'] not in ('cash', 'credits', 'crypto', 'mixed', 'in_kind')
            or not isinstance(result['max_award_basis'], str) or not result['max_award_basis'].strip()
            or evidence.scheme not in ('https', 'http') or not evidence.netloc or not valid_date):
        raise ValueError('Per-entry award needs a finite numeric amount, currency, kind, basis, evidence URL and valid assessment date')
    return result


def select_award(*assessments: dict) -> dict:
    """Newest assessment wins atomically, including explicit unknowns; ties use last input."""
    candidates = [item for item in assessments if 'max_award_amount' in item]
    chosen = max(enumerate(candidates), key=lambda pair: (pair[1].get('max_award_verified_at') or '', pair[0]))[1] if candidates else {}
    return normalize_award(chosen)
