"""Fetch a bounded, provenance-preserving public subset for Phase 3 intake."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.phase3_export import existing_sample_ids, export_record, source_group
from src.data.sources import create_source


def _existing_metadata(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
        except json.JSONDecodeError:
            continue
    return rows


def _write_reports(report_dir: Path, summary: dict, inspection: dict) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "fetch_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    rows = ["# Phase 3 public-dataset fetch", "", f"**Status:** {summary['status']}", "", "## Counts", "", f"- Requested: {summary['requested']['real']} REAL, {summary['requested']['synthetic']} SYNTHETIC.", f"- Exported in this run: {summary['exported']['real']} REAL, {summary['exported']['synthetic']} SYNTHETIC.", f"- Available locally from this source after run: {summary['available_after_run']['real']} REAL, {summary['available_after_run']['synthetic']} SYNTHETIC.", f"- Skipped duplicates: {summary['skipped_duplicates']}.", f"- Rejected invalid audio: {summary['rejected_invalid_audio']}.", f"- Speakers: {summary['speaker_count']}; source groups: {summary['source_group_count']}; languages: {summary['language_count']}.", f"- Total exported duration: {summary['total_duration_hours']:.4f} hours.", "", "## Runtime schema", "", "```json", json.dumps(inspection, indent=2, ensure_ascii=False), "```", ""]
    (report_dir / "fetch_summary.md").write_text("\n".join(rows), encoding="utf-8")
    source = ["# Phase 3 dataset sources", "", "## InTheWild", "", "- Repository: `SpeechAntiSpoofingBenchmarks/InTheWild`", "- Source URL: https://huggingface.co/datasets/SpeechAntiSpoofingBenchmarks/InTheWild", "- Source split: `test`", "- License: **LICENSE_REVIEW_REQUIRED** (runtime source field was empty).", "- Intended use: bounded research/prototype intake for deepfake-audio research; verify source-card and institutional terms before deployment.", "- Limitations: English-only; generator family is not consistently documented; do not represent its source split as an independent benchmark after training.", "", "## ASVspoof", "", "- Dataset/track: ASVspoof 2019 Logical Access (LA), evaluation partition.", "- Mirror: `SpeechAntiSpoofingBenchmarks/ASVspoof2019_LA`", "- Source URL: https://huggingface.co/datasets/SpeechAntiSpoofingBenchmarks/ASVspoof2019_LA", "- Original protocol: https://www.asvspoof.org/index2019.html", "- Labels: runtime-inspected protocol-backed `bonafide -> 0` and `spoof -> 1`.", "- License: **ODC-By 1.0 declared by the public mirror; LICENSE_REVIEW_REQUIRED for this project's intended use.**", "- Access method: bounded deterministic streaming export, not a full source mirror download.", "- Limitations: the selected evaluation mirror exposes speaker IDs but no system/attack family; do not use it as a final independent benchmark after training.", "", "## Local intake totals", ""]
    for dataset, counts in sorted(summary.get("all_source_counts", {}).items()):
        source.append(f"- {dataset}: {counts['real']} REAL, {counts['synthetic']} SYNTHETIC exported files.")
    source.append("")
    (report_dir / "dataset_sources.md").write_text("\n".join(source), encoding="utf-8")


def _source_counts(rows: list[dict]) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        if row.get("voiceguard_label") not in (0, 1):
            continue
        dataset = str(row.get("source_dataset") or "undocumented")
        counts[dataset]["real" if int(row["voiceguard_label"]) == 0 else "synthetic"] += 1
    return {name: {"real": values["real"], "synthetic": values["synthetic"]} for name, values in sorted(counts.items())}


def _metadata_group(row: dict) -> str:
    value = row.get("speaker_id") or row.get("original_path_or_reference") or row.get("sample_id")
    dataset = row.get("source_dataset") or "unknown_source"
    return hashlib.sha256(f"{dataset}:{value}".encode("utf-8")).hexdigest()[:12]


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a bounded public deepfake-audio subset for VoiceGuard Phase 3.")
    parser.add_argument("--dataset", default="inthewild", choices=["inthewild", "asvspoof"])
    parser.add_argument("--real-count", type=int, default=1000)
    parser.add_argument("--synthetic-count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--shuffle-buffer", type=int, default=64, help="Bounded streaming shuffle buffer; lower values reduce initial audio prefetch.")
    parser.add_argument("--workers", type=int, default=1, help="Concurrent selected-audio exports; metadata writes remain atomic.")
    parser.add_argument("--output-root", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--streaming", action=argparse.BooleanOptionalAction, default=True, help="Use Hugging Face streaming (default: true).")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.real_count < 0 or args.synthetic_count < 0 or args.real_count + args.synthetic_count == 0 or args.shuffle_buffer < 2 or args.workers < 1:
        parser.error("real-count and synthetic-count must be non-negative and at least one must be positive")

    source = create_source(args.dataset)
    inspection = source.inspect(streaming=args.streaming)
    print("DATASET_SCHEMA")
    print(json.dumps(inspection, indent=2, ensure_ascii=False))
    output_root = args.output_root.resolve()
    metadata_path = output_root / "phase3_metadata.jsonl"
    prior = _existing_metadata(metadata_path)
    source_name = str(getattr(source, "source_dataset", "InTheWild"))
    source_prior = [row for row in prior if str(row.get("source_dataset")) == source_name]
    known_ids = existing_sample_ids(metadata_path)
    target = {0: args.real_count, 1: args.synthetic_count}
    labels = {0: "real", 1: "synthetic"}
    existing = Counter(int(row.get("voiceguard_label")) for row in source_prior if row.get("voiceguard_label") in (0, 1))
    local_groups = {label: {str(row.get("speaker_id")) for row in source_prior if row.get("voiceguard_label") == label and row.get("speaker_id")} for label in target}
    groups = {label: set(values) for label, values in local_groups.items()}
    speakers = {str(row.get("speaker_id")) for row in source_prior if row.get("speaker_id")}
    exported = Counter()
    skipped = Counter()
    rejected = Counter()
    durations = []
    max_per_group = {label: max(5, math.ceil(count / 20)) for label, count in target.items()}
    group_selected = defaultdict(Counter)
    for row in source_prior:
        label = row.get("voiceguard_label")
        if label in target and row.get("speaker_id"):
            group_selected[int(label)][_metadata_group(row)] += 1
    needed = {label: max(0, target[label] - existing[label]) for label in target}
    # On a resumable deterministic run, early pages can consist entirely of
    # already-exported records. Account for the existing source-local subset
    # while retaining a hard bounded scan.
    scan_limit = max(500, sum(needed.values()) * 30, sum(existing.values()) * 6)
    scanned = 0
    started = time()
    exported_rows: list[dict] = []
    parallel = args.workers > 1 and not args.dry_run
    futures: list[tuple[int, object]] = []

    def handle_result(label: int, state: str, metadata: dict | None, decrement_needed: bool) -> None:
        if state in {"exported", "would_export"}:
            exported[label] += 1
            if metadata and metadata.get("speaker_id"):
                speakers.add(str(metadata["speaker_id"]))
            if metadata:
                exported_rows.append(metadata)
                durations.append(float(metadata["duration_seconds"]))
            if decrement_needed and not args.dry_run:
                needed[label] -= 1
        elif state == "duplicate":
            skipped["duplicate"] += 1
        elif state == "invalid_audio":
            rejected["invalid_audio"] += 1
        else:
            rejected[state] += 1
    if args.dry_run:
        iterator = source.iter_records(args.seed, buffer_size=args.shuffle_buffer)
    elif any(needed.values()):
        # Keep streaming bounded: a very large shuffle buffer can prefetch a
        # substantial portion of a multi-gigabyte audio repository before the
        # first local WAV is emitted.
        iterator = source.iter_records(args.seed, buffer_size=args.shuffle_buffer)
    else:
        iterator = ()
    executor = ThreadPoolExecutor(max_workers=args.workers) if parallel else None
    try:
        for record in iterator:
            scanned += 1
            label = record.voiceguard_label
            if label not in target or (args.dry_run and exported[label] >= target[label]) or (not args.dry_run and needed[label] <= 0):
                if scanned >= scan_limit:
                    break
                continue
            if record.sample_id in known_ids:
                skipped["duplicate"] += 1
                if scanned >= scan_limit:
                    break
                continue
            group = source_group(record)
            if group_selected[label][group] >= max_per_group[label]:
                skipped["diversity_cap"] += 1
                if scanned >= scan_limit:
                    break
                continue
            group_selected[label][group] += 1
            groups[label].add(group)
            if parallel:
                futures.append((label, executor.submit(export_record, record, output_root, metadata_path, known_ids)))
                needed[label] -= 1
            else:
                state, metadata = export_record(record, output_root, metadata_path, known_ids, dry_run=args.dry_run)
                handle_result(label, state, metadata, decrement_needed=True)
            if args.dry_run and exported[0] >= args.real_count and exported[1] >= args.synthetic_count:
                break
            if not args.dry_run and not any(needed.values()):
                break
            if scanned >= scan_limit:
                break
    finally:
        if executor is not None:
            executor.shutdown(wait=True)
    for label, future in futures:
        state, metadata = future.result()
        handle_result(label, state, metadata, decrement_needed=False)
    available = {label: existing[label] + exported[label] for label in target}
    summary = {
        "status": "DRY_RUN" if args.dry_run else ("COMPLETE" if all(available[label] >= target[label] for label in target) else "PARTIAL"),
        "dataset": args.dataset,
        "source_dataset": source_name,
        "seed": args.seed,
        "shuffle_buffer": args.shuffle_buffer,
        "workers": args.workers,
        "streaming": args.streaming,
        "dry_run": args.dry_run,
        "output_root": output_root.as_posix(),
        "metadata_path": metadata_path.as_posix(),
        "requested": {"real": args.real_count, "synthetic": args.synthetic_count},
        "already_present_before_run": {"real": existing[0], "synthetic": existing[1]},
        "exported": {"real": exported[0], "synthetic": exported[1]},
        "available_after_run": {"real": available[0], "synthetic": available[1]},
        "skipped_duplicates": skipped["duplicate"],
        "skipped_diversity_cap": skipped["diversity_cap"],
        "rejected_invalid_audio": rejected["invalid_audio"],
        "other_rejections": {key: value for key, value in rejected.items() if key != "invalid_audio"},
        "source_group_count": len(groups[0] | groups[1]),
        "speaker_count": len(speakers),
        "language_count": 1 if exported or source_prior else 0,
        "total_duration_hours": sum(durations) / 3600,
        "scanned_candidates": scanned,
        "scan_limit": scan_limit,
        "elapsed_seconds": round(time() - started, 3),
        "all_source_counts": _source_counts(prior + exported_rows),
    }
    _write_reports(ROOT / "reports" / "phase3", summary, inspection)
    print("FETCH_SUMMARY")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if args.dry_run or summary["status"] == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
