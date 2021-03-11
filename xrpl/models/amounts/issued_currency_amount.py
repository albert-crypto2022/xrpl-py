"""
Specifies an amount in an issued currency.

See https://xrpl.org/currency-formats.html#issued-currency-amounts.
"""
from dataclasses import dataclass

from xrpl.models.base_model import REQUIRED
from xrpl.models.currencies.issued_currency import IssuedCurrency
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class IssuedCurrencyAmount(IssuedCurrency):
    """
    Specifies an amount in an issued currency.

    See https://xrpl.org/currency-formats.html#issued-currency-amounts.
    """

    value: str = REQUIRED  # type: ignore
