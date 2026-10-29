"""Backward-compatible employee profile fields; never return password hashes."""
import re


def profile(record):
    r = dict(record)
    parts = str(r.get('name', '')).strip().split(' ', 1)
    r.setdefault('firstName', parts[0] if parts else '')
    r.setdefault('lastName', parts[1] if len(parts) > 1 else '')
    # Existing accounts keep their email as their initial username until edited.
    r.setdefault('username', str(r.get('email', '')).strip().lower())
    r.setdefault('phone', '')
    r.setdefault('position', '')
    return r


def username(value):
    value = str(value or '').strip().lower()
    if not re.fullmatch(r'[a-z0-9][a-z0-9._@+\-]{2,99}', value):
        raise ValueError('Uživatelské jméno: 3–100 znaků bez diakritiky a mezer (písmena, číslice, . _ @ + -).')
    return value
