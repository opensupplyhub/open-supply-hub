import re
from typing import Optional

from contricleaner.lib.helpers.clean import clean

# A material name change should fire on the core name, not on legal-form or
# formatting variation (e.g. "M/S. Foo Ltd." vs "Foo Limited" is not a rename).
PREFIXES = {"m s", "ms", "messrs", "messsrs"}
SUFFIX_TOKENS = {
    "ltd", "limited", "inc", "incorporated", "llc", "llp", "plc", "pvt",
    "private", "co", "company", "corp", "corporation", "gmbh", "sa", "sarl",
    "srl", "pte", "bhd", "sdn", "ag", "bv", "nv", "as", "oy", "ab", "spa",
    "kg", "jsc",
}


def normalize(name: Optional[str]) -> Optional[str]:
    if name is None:
        return None
    c = clean(name)
    if not c:
        return None
    c = c.replace(".", " ").replace("(", " ").replace(")", " ")
    c = re.sub(" +", " ", c).strip()
    for p in sorted(PREFIXES, key=len, reverse=True):
        if c == p or c.startswith(p + " "):
            c = c[len(p):].strip()
            break
    tokens = c.split(" ")
    while len(tokens) > 1 and tokens[-1] in SUFFIX_TOKENS:
        tokens.pop()
    return " ".join(tokens).strip() or None


def name_changed(prev: Optional[str], cur: Optional[str]) -> bool:
    """Whether prev -> cur is a material name change (core name differs),
    as opposed to formatting, punctuation, or legal-suffix variation."""
    normalized_prev, normalized_cur = normalize(prev), normalize(cur)
    return (
        normalized_prev is not None
        and normalized_cur is not None
        and normalized_prev != normalized_cur
    )
