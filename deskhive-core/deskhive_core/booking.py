"""Booking rules: local naive datetimes and half-open intervals [start, end)."""

import logging
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

logger = logging.getLogger(__name__)


class InvalidBookingError(ValueError):
    """The requested interval is invalid."""


class BookingConflictError(ValueError):
    """The requested space is already booked for part of this interval."""


def validate_booking(start: datetime, end: datetime) -> None:
    """Require positive duration <= 12 hours. Aware datetimes are out of scope."""
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        raise InvalidBookingError("start and end must be datetime objects")
    if start.utcoffset() is not None or end.utcoffset() is not None:
        raise InvalidBookingError("Use local naive datetimes in this exercise")
    duration = end - start
    if duration <= timedelta(0) or duration > timedelta(hours=12):
        logger.warning("Rejected booking interval: %s -> %s", start, end)
        raise InvalidBookingError("Duration must be positive and at most 12 hours")


def positive_rate(value) -> Decimal:
    """Return a finite positive decimal rate without binary-float arithmetic."""
    try:
        rate = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Hourly rate must be a positive number") from exc
    if not rate.is_finite() or rate <= 0:
        raise ValueError("Hourly rate must be finite and greater than zero")
    return rate


def compute_price(hourly_rate, start: datetime, end: datetime) -> Decimal:
    """Round duration UP to the next half hour, then money to cents (HALF_UP)."""
    validate_booking(start, end)
    rate = positive_rate(hourly_rate)
    duration = end - start
    half_hour = timedelta(minutes=30)
    units = -(-duration // half_hour)  # ceiling: round UP to the next half hour
    return (rate * Decimal(units) / Decimal(2)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def overlaps(a_start: datetime, a_end: datetime,
             b_start: datetime, b_end: datetime) -> bool:
    """Adjacent valid bookings do not conflict; containment does conflict."""
    validate_booking(a_start, a_end)
    validate_booking(b_start, b_end)
    return a_start < b_end and b_start < a_end


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start = datetime(2030, 1, 15, 10)
    end = datetime(2030, 1, 15, 11, 30)
    print("90 minutes at EUR 20/hour:", compute_price("20", start, end))
    print("Adjacent intervals overlap:", overlaps(start, end, end, end + timedelta(hours=1)))
    try:
        validate_booking(end, start)
    except InvalidBookingError as exc:
        print("Invalid interval rejected:", exc)
