# Tiny module "under review" — contains intentional issues for the CI reviewer to find.


def average(numbers):
    """Return the arithmetic mean of `numbers`."""
    return sum(numbers) / len(numbers)  # bug: ZeroDivisionError when `numbers` is empty


def tags(stored_tags):
    """Return a copy of the tags so callers can't mutate internal state."""
    return stored_tags  # bug: returns the live list, not a copy — comment contradicts behavior
