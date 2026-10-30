"""Tests for check_pairs.py: columns, statuses, upload grouping, pick-one coverage and the warnings."""
import csv
import os
import sys
import tempfile
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # the harness folder
sys.path[:0] = [_ROOT] + [os.path.join(_ROOT, d) for d in sorted(os.listdir(_ROOT))
                          if os.path.isdir(os.path.join(_ROOT, d)) and not d.startswith(("_", "."))]
import check_pairs as cp  # noqa: E402


def write_pairs(rows, columns=cp.REQUIRED):
    """Write rows (dicts) to a temporary CSV with the given columns and return its path."""
    f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
    w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    f.close()
    return f.name


def pair(match_id, name, status, fac="Some Factory", country="tr"):
    """One pair row: an upload called `name` in `country` against a facility, with a moderator status."""
    return {"match_id": str(match_id), "status": status, "confidence": "0.5", "item_clean_name": name,
            "item_name": name, "item_clean_address": "1 main st", "item_address": "1 main st",
            "item_country": country, "fac_name": fac, "fac_address": "1 main st", "fac_country": country}


class Columns(unittest.TestCase):
    """The file must have every column the harness reads."""

    def test_missing_columns_are_named(self):
        """A file without fac_country reports it and stops before grouping."""
        cols = [c for c in cp.REQUIRED if c != "fac_country"]
        path = write_pairs([pair(1, "a", "CONFIRMED")], columns=cols)
        self.assertEqual(cp.check(path)["missing_columns"], ["fac_country"])


class Uploads(unittest.TestCase):
    """Pairs group into uploads by cleaned name, address and country."""

    def test_counts_usable_new_and_ambiguous(self):
        """One upload with one confirmed candidate, one with none, one with two confirmed (left out)."""
        rows = [pair(1, "alpha ltd", "CONFIRMED"), pair(2, "alpha ltd", "REJECTED"),
                pair(3, "beta ltd", "REJECTED"),
                pair(4, "gamma ltd", "CONFIRMED"), pair(5, "gamma ltd", "CONFIRMED")]
        up = cp.check(write_pairs(rows))["uploads"]
        self.assertEqual((up["total"], up["usable"], up["with_match"], up["new"], up["ambiguous_left_out"]),
                         (3, 2, 1, 1, 1))

    def test_same_name_in_two_countries_is_two_uploads(self):
        """The country is part of the upload key."""
        rows = [pair(1, "alpha ltd", "CONFIRMED", country="tr"), pair(2, "alpha ltd", "CONFIRMED", country="bd")]
        self.assertEqual(cp.check(write_pairs(rows))["uploads"]["total"], 2)


class Warnings(unittest.TestCase):
    """What the report warns about."""

    def test_sample_of_single_pairs_is_flagged(self):
        """Every upload has one candidate: the file looks like a pair sample, not whole uploads."""
        rows = [pair(i, f"upload {i}", "CONFIRMED" if i % 2 else "REJECTED") for i in range(20)]
        warnings = cp.check(write_pairs(rows), min_uploads=1)["warnings"]
        self.assertTrue(any("single candidate" in w for w in warnings))

    def test_too_few_usable_uploads_is_flagged(self):
        """Below --min-uploads the report says upload-level results will be thin."""
        rows = [pair(1, "alpha ltd", "CONFIRMED"), pair(2, "alpha ltd", "REJECTED")]
        warnings = cp.check(write_pairs(rows), min_uploads=1000)["warnings"]
        self.assertTrue(any("usable uploads" in w for w in warnings))

    def test_odd_status_and_repeated_ids_are_flagged(self):
        """A status other than CONFIRMED or REJECTED, and a repeated match_id, are both reported."""
        rows = [pair(1, "alpha ltd", "CONFIRMED"), pair(1, "alpha ltd", "PENDING"), pair(2, "alpha ltd", "REJECTED")]
        report = cp.check(write_pairs(rows), min_uploads=1)
        text = " ".join(report["warnings"])
        self.assertIn("PENDING", text)
        self.assertEqual(report["duplicate_match_ids"], 1)

    def test_a_good_file_has_no_warnings(self):
        """Whole uploads with several candidates each, enough of them: no warnings."""
        rows = []
        for u in range(5):
            rows += [pair(u * 10, f"upload {u}", "CONFIRMED"), pair(u * 10 + 1, f"upload {u}", "REJECTED"),
                     pair(u * 10 + 2, f"upload {u}", "REJECTED")]
        self.assertEqual(cp.check(write_pairs(rows), min_uploads=3)["warnings"], [])


class Flags(unittest.TestCase):
    """Pick-one flags are checked against the pairs file."""

    def write_flags(self, ids):
        """Write a pick_one_flags.csv holding the given match ids and return its path."""
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
        f.write("match_id,pick_one\n" + "".join(f"{i},true\n" for i in ids))
        f.close()
        return f.name

    def test_coverage_counts_flagged_rejections(self):
        """A flag on a rejected pair counts; a flag on a confirmed pair is reported as odd."""
        rows = [pair(1, "alpha ltd", "CONFIRMED"), pair(2, "alpha ltd", "REJECTED"), pair(3, "beta ltd", "REJECTED")]
        report = cp.check(write_pairs(rows), self.write_flags([2, 1]), min_uploads=1)
        self.assertEqual(report["flags"], {"flagged": 2, "in_pairs": 2, "rejected_in_pairs": 2, "flagged_rejected": 1})
        self.assertTrue(any("not rejected pairs" in w for w in report["warnings"]))

    def test_flags_from_another_file_are_flagged(self):
        """Flags none of whose ids are in the pairs file are reported as probably belonging elsewhere."""
        rows = [pair(1, "alpha ltd", "REJECTED")]
        report = cp.check(write_pairs(rows), self.write_flags([100, 200, 300]), min_uploads=1)
        self.assertTrue(any("different file" in w for w in report["warnings"]))

    def test_a_flags_file_covering_more_than_the_pairs_is_fine(self):
        """Flags for ids the pairs file does not hold are normal when some overlap exists: no 'different file' warning."""
        rows = [pair(1, "alpha ltd", "REJECTED"), pair(2, "alpha ltd", "CONFIRMED")]
        report = cp.check(write_pairs(rows), self.write_flags([1, 100, 200, 300]), min_uploads=1)
        self.assertFalse(any("different file" in w for w in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
