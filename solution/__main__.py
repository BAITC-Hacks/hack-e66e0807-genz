"""Batch entry point: python -m solution --data … --out …."""
import argparse
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Calculate explainable AML hypotheses locally.")
    parser.add_argument("--data", type=Path, default=Path("data"),
                        help="directory with nodes, edges and transactions parquet files")
    parser.add_argument("--out", type=Path, default=Path("output"),
                        help="directory for three CSV exports and report.json")
    args = parser.parse_args(argv)
    for name in ("nodes.parquet", "edges.parquet", "transactions.parquet"):
        if not (args.data / name).is_file():
            parser.error(f"Missing input file: {args.data / name}")
    from solution.pipeline import run_pipeline
    try:
        report = run_pipeline(args.data, args.out)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Calculation failed: {exc}\n")
    meta = report["meta"]
    print(f"Created {args.out}: {meta['n_nodes']} nodes, {meta['n_edges']} edges, "
          f"{meta['n_transactions']} transactions in {meta['elapsed_seconds']:.3f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
