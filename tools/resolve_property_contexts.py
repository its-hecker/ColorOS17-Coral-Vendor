#!/usr/bin/env python3
"""Prepare reviewed ColorOS property_contexts candidates against Pixel vendor.

A binary ColorOS first-boot failure can come from duplicate property context keys.
This tool NEVER edits the installed Pixel vendor or source donor. It writes a
candidate replacement for a donor system_ext/product contexts file only when
a collision is exact, vendor definitions are unambiguous, and a report is saved.
Platform (plat) collisions and missing inputs are hard blockers.
"""
import argparse
import json
import sys
from pathlib import Path

SYSTEM_PATHS = (
    ("platform", "system/etc/selinux/plat_property_contexts"),
    ("system_ext", "system_ext/etc/selinux/system_ext_property_contexts"),
    ("product", "product/etc/selinux/product_property_contexts"),
)
VENDOR_PATHS = (
    "etc/selinux/vendor_property_contexts",
    "odm/etc/selinux/odm_property_contexts",
)
SAFE_TO_PROPOSE = {"system_ext", "product"}
MATCH = {"exact", "prefix"}


def parse_entry(line):
    fields = line.split("#", 1)[0].split()
    if len(fields) < 2:
        return None
    selector = fields[2] if len(fields) >= 3 and fields[2] in MATCH else "prefix"
    value_type = fields[3] if len(fields) >= 4 and fields[2] in MATCH else (
        fields[2] if len(fields) >= 3 and fields[2] not in MATCH else None)
    return (fields[0], selector), (fields[1], value_type)


def gather_vendor(vendor_root):
    entries = {}
    present = []
    for rel in VENDOR_PATHS:
        file = vendor_root / rel
        if not file.is_file():
            continue
        present.append(rel)
        for line in file.read_text(errors="replace").splitlines():
            entry = parse_entry(line)
            if entry:
                key, value = entry
                entries.setdefault(key, set()).add(value)
    return entries, present


def reconcile(donor_root, vendor_root):
    vendor, present = gather_vendor(vendor_root)
    if not present:
        raise ValueError("No vendor property_contexts: supply the assembled Pixel vendor image")
    report = {"vendor_sources": present, "removed_candidates": [],
              "blocked": [], "unmodified": [], "file_outputs": {}}
    for area, rel in SYSTEM_PATHS:
        file = donor_root / rel
        if not file.exists():
            report["blocked"].append({"area": area, "path": rel, "reason": "missing donor contexts"})
            continue
        kept = []
        changed = 0
        for index, line in enumerate(file.read_text(errors="replace").splitlines(keepends=True), 1):
            entry = parse_entry(line)
            if entry is None:
                kept.append(line)
                continue
            key, value = entry
            candidates = vendor.get(key)
            if not candidates or candidates == {value}:
                kept.append(line)
                continue
            record = {"area": area, "file": rel, "line": index, "property": key[0],
                      "selector": key[1], "donor_context": value, "vendor_contexts":
                      sorted([list(v) for v in candidates], key=str)}
            if area not in SAFE_TO_PROPOSE:
                report["blocked"].append({**record, "reason": "platform conflict needs review"})
                kept.append(line)
            elif len(candidates) != 1:
                report["blocked"].append({**record, "reason": "ambiguous vendor definitions"})
                kept.append(line)
            else:
                report["removed_candidates"].append(record)
                changed += 1
        report["file_outputs"][rel] = {"content": "".join(kept),
                                       "changed": bool(changed), "rows_removed": changed}
    return report


def main():
    p = argparse.ArgumentParser(description="ColorOS property-context collision candidate generator")
    p.add_argument("--donor-root", type=Path, required=True,
                   help="READ-ONLY extracted ColorOS system tree")
    p.add_argument("--vendor-root", type=Path, required=True,
                   help="READ-ONLY assembled Pixel vendor image mount root")
    p.add_argument("--output", type=Path, required=True,
                   help="Separate directory for candidate files + JSON report")
    p.add_argument("--strict", action="store_true", help="Fail on unresolved collisions")
    a = p.parse_args()
    donor, vendor, out = (x.expanduser().resolve() for x in
                          (a.donor_root, a.vendor_root, a.output))
    if out == donor or out == vendor or donor in out.parents or vendor in out.parents:
        p.error("Output must not be inside either source tree")
    report = reconcile(donor, vendor)
    out.mkdir(parents=True, exist_ok=True)
    for rel, candidate in report.pop("file_outputs").items():
        if candidate["changed"]:
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(candidate["content"])
            report["unmodified"].append({"file": rel, "status": "candidate generated",
                                         "removed": candidate["rows_removed"]})
        else:
            report["unmodified"].append({"file": rel, "status": "no changes"})
    report["status"] = "BLOCKED" if report["blocked"] else "CANDIDATE_ONLY"
    report["warning"] = ("Generated files are NOT installed automatically; "
                         "validate on a reconstructed, signed image with AVB intact.")
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if a.strict and report["blocked"]:
        raise SystemExit(2)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        raise SystemExit(2)
