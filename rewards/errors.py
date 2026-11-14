"""Errors raised by the rewards pilot. All of them inherit from RewardsError."""
from __future__ import annotations


class RewardsError(Exception):
    """Base class for every rewards error."""


class ForbiddenRuleError(RewardsError):
    """A rule would reward trading, trade counts, balances, portfolios or investment returns."""


class UnknownRuleError(RewardsError):
    """The rule is not one of the pilot rules."""


class NotFoundError(RewardsError):
    """An employer, member or redemption id does not exist."""


class NotEligibleError(RewardsError):
    """The member is not enrolled, or not employed, on the date given."""


class RedemptionError(RewardsError):
    """A redemption request or status change was refused."""


class BelowMinimumError(RedemptionError):
    """Fewer points than the catalog minimum for that redemption type."""


class InsufficientPointsError(RedemptionError):
    """More points than the member's balance."""


class PoolExhaustedError(RedemptionError):
    """The USD value is more than the employer's remaining reward pool."""


class RedemptionDisabledError(RedemptionError):
    """The redemption type exists but is switched off (for example invest_deposit)."""


class PrivacyError(RewardsError):
    """Something that looks like an email address or phone number was about to be stored or exported."""
