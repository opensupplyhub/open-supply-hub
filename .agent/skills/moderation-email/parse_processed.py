#!/usr/bin/env python3
"""Parse a ~PROCESSED workbook dump (Drive MCP output) into structured JSON.

One call replaces the exploratory parsing passes: identifies the tables,
finds the moderator-tagged table (header contains `error`), extracts tagged
rows, resolves duplicate pairs (letters, row-number refs, or free-text
annotations), detects tab pruning vs the original table, and looks up
missing pair partners in the original table.

Usage:
    python3 parse_processed.py <dump-file> [--csv tagged.csv]

<dump-file> may be the raw markdown or the MCP tool-result JSON
({"fileContent": ...}). Output: JSON on stdout.
"""
import csv
import json
import re
import sys


def load(path: str) -> str:
    text = open(path).read()
    try:
        obj = json.loads(text)
        return obj["fileContent"] if isinstance(obj, dict) else text
    except (json.JSONDecodeError, KeyError):
        return text


def cells(row: str) -> list:
    return [c.strip().replace("\\", "") for c in row.strip().strip("|").split("|")]


def is_separator(cs: list) -> bool:
    return all(not c or set(c) <= set(":- ") for c in cs)


def split_tables(src: str) -> list:
    tables, cur = [], []
    for ln in src.split("\n"):
        if ln.strip().startswith("|"):
            cur.append(ln)
        else:
            if cur:
                tables.append(cur)
                cur = []
    if cur:
        tables.append(cur)
    parsed = []
    for t in tables:
        rows = [cells(r) for r in t]
        rows = [r for r in rows if not is_separator(r)]
        if rows:
            parsed.append(rows)
    return parsed


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    path = sys.argv[1]
    csv_out = None
    if "--csv" in sys.argv:
        csv_out = sys.argv[sys.argv.index("--csv") + 1]

    tables = split_tables(load(path))
    tagged_table = original_table = None
    for rows in tables:
        hdr = [h.lower() for h in rows[0]]
        if "error" in hdr and ("country" in hdr or "name" in hdr):
            tagged_table = rows
        elif "country" in hdr and "name" in hdr and "error" not in hdr:
            if original_table is None or len(rows) > len(original_table):
                original_table = rows

    result = {"tables": len(tables)}
    if tagged_table is None:
        result["error"] = "no table with an `error` column found — do not invent tags"
        print(json.dumps(result, indent=1))
        return

    hdr = [h.lower() for h in tagged_table[0]]
    err_i = hdr.index("error")
    dup_i = hdr.index("duplicate_pair_id") if "duplicate_pair_id" in hdr else None
    data = tagged_table[1:]

    def field(r, name, default=""):
        return r[hdr.index(name)] if name in hdr and len(r) > hdr.index(name) else default

    tagged = []
    for i, r in enumerate(data, start=2):
        err = r[err_i] if len(r) > err_i else ""
        dup = r[dup_i] if dup_i is not None and len(r) > dup_i else ""
        if err or dup:
            tagged.append({
                "rn": i,
                "os_hub_row": i - 1,  # list page currently displays row_index+1 (OSDEV-2724 regression; PR #1167 restores +2 → page will equal rn after deploy)
                "country": field(r, "country"),
                "name": field(r, "name"),
                "address": field(r, "address"),
                "sector_product_type": field(r, "sector_product_type"),
                "facility_type_processing_type": field(r, "facility_type_processing_type"),
                "number_of_workers": field(r, "number_of_workers"),
                "parent_company": field(r, "parent_company"),
                "error": err,
                "duplicate_pair_id": dup,
            })

    # Duplicate pair resolution
    pairs, notes = {}, []
    for t in tagged:
        pid = t["duplicate_pair_id"]
        tags = t["error"]
        if pid and not re.fullmatch(r"[A-Za-z]|\d{1,4}", pid):
            notes.append({"rn": t["rn"], "annotation": pid})
            pid = ""
        if pid or "dupe_" in tags:
            key = pid or f"unpaired-{t['rn']}"
            pairs.setdefault(key, []).append(t["rn"])
    # merge row-number pair refs: pid "210" on rn 86 means pair (86, 210)
    resolved = []
    seen = set()
    for key, rns in pairs.items():
        members = set(rns)
        if re.fullmatch(r"\d{1,4}", key):
            members.add(int(key))
        members = sorted(members)
        fs = frozenset(members)
        if fs in seen:
            continue
        seen.add(fs)
        entry = {"pair": key, "rows": members}
        # find partners not in the tagged data (pruned) via the original table
        missing = [m for m in members if m - 2 >= len(data) or m < 2]
        for m in members:
            if 2 <= m < len(data) + 2:
                row_tags = next((t["error"] for t in tagged if t["rn"] == m), "")
                if m in [t["rn"] for t in tagged] and not row_tags:
                    pass
        if len(members) == 1 and original_table:
            # unpaired dupe tag: search original table for same normalized name
            me = next(t for t in tagged if t["rn"] == members[0])
            target = norm(me["name"])
            for j, orow in enumerate(original_table[1:], start=2):
                if j != members[0] and norm(orow[1] if len(orow) > 1 else "") == target:
                    entry["partner_in_original"] = {
                        "rn": j, "name": orow[1],
                        "address": orow[2] if len(orow) > 2 else "",
                        "number_of_workers": orow[5] if len(orow) > 5 else "",
                    }
                    break
        if missing and original_table:
            entry["partners_from_original"] = []
            for m in missing:
                if m - 2 < len(original_table) - 1:
                    orow = original_table[1:][m - 2]
                    entry["partners_from_original"].append({
                        "rn": m, "name": orow[1] if len(orow) > 1 else "",
                        "address": orow[2] if len(orow) > 2 else "",
                        "number_of_workers": orow[5] if len(orow) > 5 else "",
                    })
        resolved.append(entry)

    # Merge entries whose row-sets overlap (a dupe_remove row shows up both
    # in its letter/row-ref pair and as an unpaired entry).
    merged = []
    for e in resolved:
        home = next((m for m in merged if set(m["rows"]) & set(e["rows"])
                     or set(m["rows"]) & {p_["rn"] for p_ in
                     ([e.get("partner_in_original")] if e.get("partner_in_original") else [])}), None)
        if home:
            home["rows"] = sorted(set(home["rows"]) | set(e["rows"]))
            for k in ("partner_in_original", "partners_from_original"):
                if e.get(k) and not home.get(k):
                    home[k] = e[k]
        else:
            merged.append(e)
    resolved = merged

    result.update({
        "data_rows_in_tagged_tab": len(data),
        "data_rows_in_original_tab": len(original_table) - 1 if original_table else None,
        "pruned": bool(original_table) and (len(original_table) - 1) != len(data),
        "tagged_count": len(tagged),
        "ratio_pct": round(100 * len(tagged) / len(data), 1) if data else None,
        "tagged": tagged,
        "duplicate_pairs": resolved,
        "pair_annotations": notes,
    })
    print(json.dumps(result, indent=1, ensure_ascii=False))

    if csv_out:
        with open(csv_out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["rn", "country", "name", "address", "error", "duplicate_pair_id"])
            for t in tagged:
                w.writerow([t["rn"], t["country"], t["name"], t["address"],
                            t["error"], t["duplicate_pair_id"]])


if __name__ == "__main__":
    main()
