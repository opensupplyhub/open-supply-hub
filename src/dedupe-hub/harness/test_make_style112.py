"""Tests for make_style112: the new file copies the reference's class mix and similarity spread, and only uses training-half pairs."""
import random
import unittest

import make_style112 as ms


def rec(name, country="tr"):
    """A cleaned record with a name, an address and a country."""
    return {"name": name, "address": "1 main st", "country": country}


def ex(left, right):
    """One training example in dedupe's training.json shape."""
    return {"__class__": "tuple", "__value__": [left, right]}


def row(i, label, left, right, train=True):
    """One labeled pair the way load_pairs returns it."""
    return {"match_id": str(i), "label": label, "left": left, "right": right, "train": train,
            "country": left["country"], "confidence": 0.5}


class Profile(unittest.TestCase):
    """Measuring a reference training file."""

    def test_match_share_and_cross_country_share(self):
        """Two matches and two non-matches, one non-match across countries: share 0.5 and cross 0.5."""
        t = {"match": [ex(rec("acme"), rec("acme")), ex(rec("beta"), rec("beta"))],
             "distinct": [ex(rec("acme"), rec("zzzz")), ex(rec("acme"), rec("zzzz", "mx"))]}
        p = ms.profile(t)
        self.assertEqual((p["match_share"], p["distinct"]["cross"]), (0.5, 0.5))

    def test_identical_names_land_in_the_top_bin(self):
        """A pair of identical names has similarity 1, which must fall in the last bin."""
        self.assertEqual(ms.bin_of(1.0), len(ms.BIN_EDGES) - 2)


class Quotas(unittest.TestCase):
    """Turning shares into whole slots."""

    def test_sums_to_n(self):
        """Whatever the shares, the slots add up to exactly n."""
        self.assertEqual(sum(ms.quotas([0.28, 0.2, 0.25, 0.27], 348)), 348)


class Build(unittest.TestCase):
    """Building a file from labeled rows."""

    def setUp(self):
        """Forty matches and forty rejections in two countries, plus rows in the evaluation half."""
        self.rows = []
        for i in range(40):
            c = "tr" if i % 2 else "mx"
            self.rows.append(row(i, 1, rec("factory %d ltd" % i, c), rec("factory %d limited" % i, c)))
            self.rows.append(row(100 + i, 0, rec("plant %d" % i, c), rec("plant %d north" % i, c)))
            self.rows.append(row(200 + i, 1, rec("eval %d" % i, c), rec("eval %d" % i, c), train=False))
        self.ref = ms.profile({"match": [ex(rec("abc"), rec("abc"))] * 4,
                               "distinct": [ex(rec("abc"), rec("xyz", "mx"))] * 3 + [ex(rec("abcdef"), rec("abcdeg"))] * 3})

    def test_sizes_and_cross_country_share(self):
        """The file has the requested total, the reference's match share, and made cross-country non-matches."""
        t, ids, report = ms.build(self.rows, self.ref, 20, 1.0, random.Random(1))
        self.assertEqual((len(t["match"]), len(t["distinct"])), (8, 12))
        self.assertGreater(report["made"]["cross"], 0)

    def test_evaluation_half_is_never_used(self):
        """No selected id belongs to a row outside the training half."""
        _, ids, _ = ms.build(self.rows, self.ref, 20, 1.0, random.Random(1))
        self.assertFalse(ids & {str(200 + i) for i in range(40)})

    def test_boosted_country_gets_more_and_limited_country_less(self):
        """A boosted country supplies more real matches than before, and a limited one at most its cap."""
        plain, _, _ = ms.build(self.rows, self.ref, 20, 0.3, random.Random(1))
        t, _, _ = ms.build(self.rows, self.ref, 20, 0.3, random.Random(1), boost=["tr"], boost_cap=0.8, limit=["mx"], limit_cap=0.1)
        count = lambda tr, c: sum(1 for e in tr["match"] if e["__value__"][0]["country"] == c)  # noqa: E731
        self.assertGreater(count(t, "tr"), count(plain, "tr"))
        self.assertLessEqual(count(t, "mx"), 1)


if __name__ == "__main__":
    unittest.main()
