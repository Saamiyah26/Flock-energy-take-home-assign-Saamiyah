import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "REFIT_RAW_081116"
PLOT_DIR = ROOT / "house1_quality_plots"
REPORT_DIR = ROOT / "house1_quality_reports"

POWER_COLUMNS = [
    "Aggregate",
    "Appliance1",
    "Appliance2",
    "Appliance3",
    "Appliance4",
    "Appliance5",
    "Appliance6",
    "Appliance7",
    "Appliance8",
    "Appliance9",
]

# Map the raw generic names used in the REFIT files into the common short labels used in the assignment.
RAW_COLUMNNAMES = {
    "Aggregate": "Aggregate",
    "Appliance1": "Appliance1",
    "Appliance2": "Appliance2",
    "Appliance3": "Appliance3",
    "Appliance4": "Appliance4",
    "Appliance5": "Appliance5",
    "Appliance6": "Appliance6",
    "Appliance7": "Appliance7",
    "Appliance8": "Appliance8",
    "Appliance9": "Appliance9",
}


def numeric_series(series):
    return pd.to_numeric(series, errors="coerce")


def first_nonempty(df, name):
    return df.loc[:, name].copy() if name in df.columns else pd.Series([np.nan] * len(df), index=df.index)


def build_datasets_from_raw():
    part1 = pd.read_csv(RAW_DIR / "RAW_House1_Part1.csv")
    part2 = pd.read_csv(RAW_DIR / "RAW_House1_Part2.csv")

    for df in (part1, part2):
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
        df["Unix"] = pd.to_numeric(df["Unix"], errors="coerce")

    data1_early = part1[
        (part1["Time"] >= "2013-10-09 14:06:17") & (part1["Time"] <= "2014-06-27 23:59:50")
    ].copy()
    data2a_part1 = part1[
        (part1["Time"] >= "2014-06-28 00:00:04") & (part1["Time"] <= "2014-10-01 01:27:07")
    ].copy()
    data2b_part2 = part2[
        (part2["Time"] >= "2014-06-28 00:00:05") & (part2["Time"] <= "2014-10-01 23:59:59")
    ].copy()
    data3_late = part2[
        (part2["Time"] >= "2014-10-02 00:00:07") & (part2["Time"] <= "2015-07-10 11:56:32")
    ].copy()
    return {
        "data1_early": data1_early,
        "data2a_part1": data2a_part1,
        "data2b_part2": data2b_part2,
        "data3_late": data3_late,
    }


def get_datasets():
    candidates = [
        ("data1_early", globals().get("data1_early")),
        ("data2a_part1", globals().get("data2a_part1")),
        ("data2b_part2", globals().get("data2b_part2")),
        ("data3_late", globals().get("data3_late")),
    ]
    if all(df is not None for _, df in candidates):
        return {name: df.copy() for name, df in candidates}

    # Fallback for notebooks where the split DataFrames are names Data1/Data2A/Data2B/Data3.
    temp = {}
    if "Data1" in globals():
        temp["data1_early"] = globals()["Data1"].copy()
    if "Data2A" in globals():
        temp["data2a_part1"] = globals()["Data2A"].copy()
    if "Data2B" in globals():
        temp["data2b_part2"] = globals()["Data2B"].copy()
    if "Data3" in globals():
        temp["data3_late"] = globals()["Data3"].copy()
    if len(temp) == 4:
        return temp

    return build_datasets_from_raw()


def check_time_validation(df):
    result = {}
    if "Time" not in df.columns:
        return {"invalid_timestamp_count": 0, "missing_timestamp_count": 0, "chronologically_ordered": None, "out_of_order_transitions": 0, "zero_unix_count": 0, "invalid_unix_count": 0, "examples": []}

    parsed = pd.to_datetime(df["Time"], errors="coerce")
    result["invalid_timestamp_count"] = int(parsed.isna().sum())
    result["missing_timestamp_count"] = int(df["Time"].isna().sum())
    result["chronologically_ordered"] = bool(parsed.is_monotonic_increasing)
    result["out_of_order_transitions"] = int(parsed.diff().fillna(pd.Timedelta(0)).lt(pd.Timedelta(0)).sum())

    if "Unix" in df.columns:
        unix = pd.to_numeric(df["Unix"], errors="coerce")
        result["zero_unix_count"] = int((unix == 0).sum())
        result["invalid_unix_count"] = int(unix.isna().sum())
        time_epoch = parsed.map(lambda x: x.timestamp() if pd.notna(x) else np.nan)
        mismatch_idx = ((~unix.isna()) & (~pd.isna(time_epoch)) & (np.abs(unix - time_epoch) > 5)).to_numpy()
        result["mismatch_examples"] = df.loc[mismatch_idx, ["Time", "Unix"]].head(10).to_dict("records")
    else:
        result["zero_unix_count"] = 0
        result["invalid_unix_count"] = 0
        result["mismatch_examples"] = []
    return result


def check_duplicate_analysis(df):
    result = {}
    result["exact_duplicate_rows"] = int(df.duplicated(keep=False).sum())
    if "Time" in df.columns:
        repeated = df["Time"].duplicated(keep=False)
        result["repeated_timestamps"] = int(repeated.sum())
        groups = df.groupby("Time").size()
        repeated_groups = groups[groups > 1]
        result["distinct_repeated_timestamp_count"] = int(repeated_groups.shape[0])
        result["group_size_distribution"] = repeated_groups.value_counts().sort_index().to_dict()
        repeated_examples = df[repeated].sort_values("Time")
        result["repeated_timestamp_examples"] = repeated_examples.head(10).to_dict("records")

        conflicting = []
        for time_value, g in df.groupby("Time"):
            if len(g) <= 1:
                continue
            if "Aggregate" in g.columns:
                agg_values = g["Aggregate"].dropna().unique()
                if len(agg_values) > 1:
                    conflicting.append({"Time": str(time_value), "Aggregate_values": [float(v) for v in agg_values]})
            app_conflict = False
            app_values = {}
            for c in ["Appliance1", "Appliance2", "Appliance3", "Appliance4", "Appliance5", "Appliance6", "Appliance7", "Appliance8", "Appliance9"]:
                if c in g.columns:
                    vals = g[c].dropna().unique()
                    if len(vals) > 1:
                        app_conflict = True
                        app_values[c] = [float(v) for v in vals]
            if app_conflict:
                conflicting.append({"Time": str(time_value), "Appliance_conflicts": app_values})
        result["conflicting_duplicate_groups"] = conflicting[:10]
    else:
        result["repeated_timestamps"] = 0
        result["distinct_repeated_timestamp_count"] = 0
        result["group_size_distribution"] = {}
        result["repeated_timestamp_examples"] = []
        result["conflicting_duplicate_groups"] = []
    return result


def check_missing_data(df):
    summary = {}
    for col in df.columns:
        s = df[col]
        numeric = pd.to_numeric(s, errors="coerce")
        summary[col] = {
            "missing_count": int(s.isna().sum()),
            "missing_pct": float(s.isna().mean() * 100.0) if len(s) else 0.0,
            "zero_count": int((numeric == 0).sum()),
            "zero_pct": float((numeric == 0).mean() * 100.0) if len(s) else 0.0,
        }
    return summary


def check_missing_periods(df):
    out = {}
    for col in df.columns:
        if "Time" not in df.columns:
            continue
        s = df[col]
        if not s.empty:
            missing = s.isna()
            if missing.any():
                starts = missing & (~missing.shift(fill_value=False))
                ends = missing & (~missing.shift(fill_value=False, periods=-1))
                runs = []
                for start_idx, end_idx in zip(starts[starts].index, ends[ends].index):
                    runs.append((start_idx, end_idx))
                out[col] = runs[:10]
            else:
                out[col] = []
    return out


def find_long_gaps(df):
    if "Time" not in df.columns:
        return []
    times = pd.to_datetime(df["Time"], errors="coerce").dropna().sort_values()
    if len(times) < 2:
        return []
    diffs = times.diff().dropna()
    long = diffs[diffs > pd.Timedelta(minutes=30)].sort_values(ascending=False)
    gaps = []
    for pos, (ts, delta) in enumerate(long.items()):
        if pd.isna(ts) or delta is pd.NaT:
            continue
        idx = times.index.get_loc(ts) if ts in times.index else None
        if idx is None:
            continue
        start = None if idx == 0 else times.iloc[idx - 1]
        end = times.iloc[idx]
        if start is not None:
            gaps.append({
                "dataset": df.name,
                "start_time": str(start),
                "end_time": str(end),
                "duration_seconds": float(delta.total_seconds()),
                "duration_minutes": float(delta.total_seconds() / 60.0),
                "duration_hours": float(delta.total_seconds() / 3600.0),
                "duration_days": float(delta.total_seconds() / 86400.0),
            })
    return gaps[:20]


def check_aggregate_consistency(df):
    result = {}
    for col in ["Aggregate"] + [f"Appliance{i}" for i in range(1, 10)]:
        if col not in df.columns:
            continue
    if "Aggregate" not in df.columns:
        return result

    agg = numeric_series(df["Aggregate"])
    app_cols = [c for c in df.columns if c.startswith("Appliance")]
    app_sum = pd.concat([numeric_series(df[c]) for c in app_cols], axis=1).sum(axis=1)
    result["aggregate_zero_nonzero_appliance_rows"] = int(((agg == 0) & (app_sum > 0)).sum())
    result["aggregate_lower_than_appliance_sum"] = int((agg < app_sum).sum())
    result["aggregate_equal_appliance_sum"] = int((agg == app_sum).sum())
    result["aggregate_exceeds_appliance_sum"] = int((agg > app_sum).sum())
    result["aggregate_minus_appsum_summary"] = (agg - app_sum).describe().to_dict()
    result["individual_appliance_exceeds_aggregate_count"] = int(
        df[[c for c in app_cols if c in df.columns]].apply(lambda col: numeric_series(col).gt(agg)).any(axis=1).sum()
    )
    examples = df.loc[(agg == 0) & (app_sum > 0), ["Time", "Aggregate", *app_cols]].head(10).to_dict("records")
    result["inconsistency_examples"] = examples
    return result


def check_sampling_interval(df):
    result = {}
    if "Time" not in df.columns:
        return result
    dt = pd.to_datetime(df["Time"], errors="coerce").dropna()
    if len(dt) < 2:
        return {
            "original_order": {
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "p25": None,
                "p75": None,
                "zero": 0,
                "negative": 0,
                "shorter_than_1s": 0,
                "gt_60s": 0,
                "gt_5min": 0,
                "gt_30min": 0,
                "gt_1h": 0,
                "gt_24h": 0,
            },
            "sorted_order": {
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "p25": None,
                "p75": None,
                "zero": 0,
                "negative": 0,
                "shorter_than_1s": 0,
                "gt_60s": 0,
                "gt_5min": 0,
                "gt_30min": 0,
                "gt_1h": 0,
                "gt_24h": 0,
            },
        }
    def stats_for(series):
        deltas = series.diff().dropna()
        if deltas.empty:
            return {
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "p25": None,
                "p75": None,
                "zero": 0,
                "negative": 0,
                "shorter_than_1s": 0,
                "gt_60s": 0,
                "gt_5min": 0,
                "gt_30min": 0,
                "gt_1h": 0,
                "gt_24h": 0,
            }
        secs = deltas.dt.total_seconds()
        return {
            "min": float(secs.min()),
            "max": float(secs.max()),
            "mean": float(secs.mean()),
            "median": float(secs.median()),
            "p25": float(secs.quantile(0.25)),
            "p75": float(secs.quantile(0.75)),
            "zero": int((secs == 0).sum()),
            "negative": int((secs < 0).sum()),
            "shorter_than_1s": int((secs < 1).sum()),
            "gt_60s": int((secs > 60).sum()),
            "gt_5min": int((secs > 300).sum()),
            "gt_30min": int((secs > 1800).sum()),
            "gt_1h": int((secs > 3600).sum()),
            "gt_24h": int((secs > 86400).sum()),
        }

    result["original_order"] = stats_for(pd.to_datetime(df["Time"], errors="coerce").dropna())
    result["sorted_order"] = stats_for(pd.to_datetime(df["Time"], errors="coerce").dropna().sort_values())
    return result


def check_extreme_values(df):
    summary = {}
    for col in ["Aggregate"] + [f"Appliance{i}" for i in range(1, 10)]:
        if col not in df.columns:
            continue
        s = numeric_series(df[col])
        threshold = 10000 if col == "Aggregate" else 5000
        summary[col] = {
            "min": float(s.min()) if s.notna().any() else np.nan,
            "max": float(s.max()) if s.notna().any() else np.nan,
            "mean": float(s.mean()) if s.notna().any() else np.nan,
            "median": float(s.median()) if s.notna().any() else np.nan,
            "std": float(s.std()) if s.notna().any() else np.nan,
            "negative_count": int((s < 0).sum()),
            "zero_count": int((s == 0).sum()),
            "threshold_count": int((s > threshold).sum()),
            "threshold_pct": float((s > threshold).mean() * 100.0) if s.notna().any() else 0.0,
            "top_10": s.nlargest(10).to_dict(),
            "suspicious_values": [
                {"index": int(i), "timestamp": str(df.loc[int(i), "Time"]), "value": float(v)}
                for i, v in s[s > threshold].head(10).items()
                if "Time" in df.columns and i in df.index
            ],
        }
    return summary


def check_invalid_numeric(df):
    result = {}
    for col in ["Aggregate"] + [f"Appliance{i}" for i in range(1, 10)]:
        if col not in df.columns:
            continue
        s = df[col]
        numeric = pd.to_numeric(s, errors="coerce")
        result[col] = {
            "positive_inf": int(np.isposinf(numeric.to_numpy()).sum()),
            "negative_inf": int(np.isneginf(numeric.to_numpy()).sum()),
            "negative_readings": int((numeric < 0).sum()),
            "contains_non_numeric_strings": bool(s.map(lambda x: isinstance(x, str) and not x.strip().lower() in {"nan", "none", ""} and not pd.to_numeric(x, errors="coerce") == x if False else False)).sum() if False else False,
        }
    return result


def dataset_summary(name, df):
    time_info = check_time_validation(df)
    dup_info = check_duplicate_analysis(df)
    missing_info = check_missing_data(df)
    interval_info = check_sampling_interval(df)
    aggregate_info = check_aggregate_consistency(df)
    extremes = check_extreme_values(df)
    invalid = check_invalid_numeric(df)
    return {
        "name": name,
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "first_timestamp": pd.to_datetime(df["Time"], errors="coerce").min() if "Time" in df.columns else None,
        "last_timestamp": pd.to_datetime(df["Time"], errors="coerce").max() if "Time" in df.columns else None,
        "time_validation": time_info,
        "duplicates": dup_info,
        "missing_data": missing_info,
        "intervals": interval_info,
        "aggregate_consistency": aggregate_info,
        "extreme_values": extremes,
        "invalid_numeric": invalid,
        "missing_periods": check_missing_periods(df),
    }


def make_plots(name, df, plot_dir):
    plot_dir.mkdir(exist_ok=True, parents=True)
    title_name = name.replace("_", " ").title()

    if "Time" in df.columns and "Aggregate" in df.columns:
        fig, ax = plt.subplots(figsize=(12, 4))
        sample = df[["Time", "Aggregate"]].dropna(subset=["Time", "Aggregate"]).copy()
        sample = sample.sort_values("Time")
        if len(sample) > 20000:
            sample = sample.iloc[:: max(1, len(sample) // 20000)]
        ax.plot(sample["Time"], sample["Aggregate"], alpha=0.7)
        ax.set_title(f"{title_name}: Aggregate power over time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Watts")
        fig.tight_layout()
        fig.savefig(plot_dir / f"{name}_aggregate.png", dpi=180)
        plt.close(fig)

    if "Time" in df.columns:
        app_cols = [c for c in df.columns if c.startswith("Appliance")]
        if app_cols:
            fig, ax = plt.subplots(figsize=(12, 5))
            sample = df[["Time"] + app_cols].dropna(subset=["Time"]).copy()
            sample = sample.sort_values("Time")
            if len(sample) > 20000:
                sample = sample.iloc[:: max(1, len(sample) // 20000)]
            for c in app_cols[:3]:
                if c in sample.columns:
                    ax.plot(sample["Time"], numeric_series(sample[c]), alpha=0.7, label=c)
            ax.legend(loc="upper right")
            ax.set_title(f"{title_name}: Appliance power over time")
            ax.set_xlabel("Time")
            ax.set_ylabel("Watts")
            fig.tight_layout()
            fig.savefig(plot_dir / f"{name}_appliances.png", dpi=180)
            plt.close(fig)

    # Missing value distribution
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    if any(c in df.columns for c in POWER_COLUMNS):
        cols = [c for c in POWER_COLUMNS if c in df.columns]
        missing = df[cols].isna().mean().sort_values(ascending=False)
        zero = df[cols].apply(lambda col: (numeric_series(col) == 0).mean()).sort_values(ascending=False)
        missing.plot(kind="bar", ax=axes[0], title=f"{title_name}: missing value rate")
        zero.plot(kind="bar", ax=axes[1], title=f"{title_name}: zero value rate")
    fig.tight_layout()
    fig.savefig(plot_dir / f"{name}_missing_zero.png", dpi=180)
    plt.close(fig)

    # Interval distribution
    if "Time" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        t = pd.to_datetime(df["Time"], errors="coerce").dropna().sort_values()
        diffs = t.diff().dropna().dt.total_seconds()
        if not diffs.empty:
            diffs.hist(bins=50, ax=ax)
        ax.set_title(f"{title_name}: interval distribution")
        ax.set_xlabel("Seconds")
        ax.set_ylabel("Count")
        fig.tight_layout()
        fig.savefig(plot_dir / f"{name}_intervals.png", dpi=180)
        plt.close(fig)

    # Power histograms / boxplots
    fig, axes = plt.subplots(2, 5, figsize=(18, 8))
    axes = axes.flatten()
    idx = 0
    for c in POWER_COLUMNS:
        if c in df.columns:
            s = numeric_series(df[c]).dropna()
            if not s.empty:
                axes[idx].hist(s, bins=40)
                axes[idx].set_title(c)
            idx += 1
    for j in range(idx, len(axes)):
        axes[j].axis("off")
    fig.tight_layout()
    fig.savefig(plot_dir / f"{name}_power_histograms.png", dpi=180)
    plt.close(fig)

    # Daily missing percentage
    if "Time" in df.columns:
        fig, ax = plt.subplots(figsize=(10, 4))
        tmp = df[["Time"] + [c for c in POWER_COLUMNS if c in df.columns]].copy()
        tmp["date"] = pd.to_datetime(tmp["Time"], errors="coerce").dt.floor("D")
        daily = tmp.groupby("date")[POWER_COLUMNS].apply(lambda frame: frame.isna().mean().mean() * 100.0)
        daily.plot(ax=ax, marker="o")
        ax.set_title(f"{title_name}: daily missing-data percentage")
        ax.set_ylabel("Missing %")
        ax.set_xlabel("Date")
        fig.tight_layout()
        fig.savefig(plot_dir / f"{name}_daily_missing.png", dpi=180)
        plt.close(fig)


def write_report(name, summary):
    lines = []
    lines.append(f"=== {name} ===")
    lines.append(f"Rows: {summary['rows']}")
    lines.append(f"Columns: {summary['columns']}")
    lines.append(f"First timestamp: {summary['first_timestamp']}")
    lines.append(f"Last timestamp: {summary['last_timestamp']}")
    lines.append(f"Invalid timestamps: {summary['time_validation']['invalid_timestamp_count']}")
    lines.append(f"Missing timestamps: {summary['time_validation']['missing_timestamp_count']}")
    lines.append(f"Out-of-order transitions: {summary['time_validation']['out_of_order_transitions']}")
    lines.append(f"Zero Unix values: {summary['time_validation']['zero_unix_count']}")
    lines.append(f"Invalid Unix values: {summary['time_validation']['invalid_unix_count']}")
    lines.append(f"Exact duplicate rows: {summary['duplicates']['exact_duplicate_rows']}")
    lines.append(f"Repeated timestamps: {summary['duplicates']['repeated_timestamps']}")
    lines.append(f"Distinct repeated timestamps: {summary['duplicates']['distinct_repeated_timestamp_count']}")
    lines.append(f"Conflicting duplicate groups: {len(summary['duplicates']['conflicting_duplicate_groups'])}")
    lines.append("Missing values by column:")
    for col, info in summary["missing_data"].items():
        lines.append(f"  - {col}: {info['missing_count']} ({info['missing_pct']:.2f}%)")
    lines.append("Zero readings by column:")
    for col, info in summary["missing_data"].items():
        lines.append(f"  - {col}: {info['zero_count']} ({info['zero_pct']:.2f}%)")
    lines.append(f"Aggregate zero + appliance >0 rows: {summary['aggregate_consistency'].get('aggregate_zero_nonzero_appliance_rows', 0)}")
    lines.append(f"Aggregate < appliance sum: {summary['aggregate_consistency'].get('aggregate_lower_than_appliance_sum', 0)}")
    lines.append(f"Aggregate == appliance sum: {summary['aggregate_consistency'].get('aggregate_equal_appliance_sum', 0)}")
    lines.append(f"Aggregate > appliance sum: {summary['aggregate_consistency'].get('aggregate_exceeds_appliance_sum', 0)}")
    lines.append(f"Intervals sorted >60s: {summary['intervals']['sorted_order']['gt_60s']}")
    lines.append(f"Intervals sorted >5min: {summary['intervals']['sorted_order']['gt_5min']}")
    lines.append(f"Intervals sorted >1h: {summary['intervals']['sorted_order']['gt_1h']}")
    lines.append(f"Intervals sorted >24h: {summary['intervals']['sorted_order']['gt_24h']}")
    lines.append("Suspicious high readings:")
    for col, info in summary["extreme_values"].items():
        lines.append(f"  - {col}: max={info['max']}, threshold_count={info['threshold_count']} ({info['threshold_pct']:.2f}%)")
    lines.append("")
    return "\n".join(lines) + "\n\n"


def compare_datasets(datasets):
    rows = []
    for name, df in datasets.items():
        summary = dataset_summary(name, df)
        rows.append({
            "Metric": name,
            "Total rows": len(df),
            "Invalid timestamps": summary["time_validation"]["invalid_timestamp_count"],
            "Out-of-order transitions": summary["time_validation"]["out_of_order_transitions"],
            "Exact duplicate rows": summary["duplicates"]["exact_duplicate_rows"],
            "Repeated timestamps": summary["duplicates"]["repeated_timestamps"],
            "Conflicting duplicate groups": len(summary["duplicates"]["conflicting_duplicate_groups"]),
            "Missing Aggregate readings": summary["missing_data"].get("Aggregate", {}).get("missing_count", 0),
            "Missing appliance readings": sum(v.get("missing_count", 0) for c, v in summary["missing_data"].items() if c.startswith("Appliance")),
            "Zero Aggregate readings": summary["missing_data"].get("Aggregate", {}).get("zero_count", 0),
            "Intervals over 60s": summary["intervals"]["sorted_order"]["gt_60s"],
            "Intervals over 5 min": summary["intervals"]["sorted_order"]["gt_5min"],
            "Intervals over 1 hour": summary["intervals"]["sorted_order"]["gt_1h"],
            "Intervals over 24 hours": summary["intervals"]["sorted_order"]["gt_24h"],
            "Negative power readings": sum(v.get("negative_readings", 0) for v in summary["invalid_numeric"].values()),
            "Aggregate readings above 10,000 W": summary["extreme_values"].get("Aggregate", {}).get("threshold_count", 0),
            "Appliance readings above 5,000 W": sum(info.get("threshold_count", 0) for col, info in summary["extreme_values"].items() if col.startswith("Appliance")),
            "Aggregate zero + non-zero appliance rows": summary["aggregate_consistency"].get("aggregate_zero_nonzero_appliance_rows", 0),
        })
    return pd.DataFrame(rows)


def write_comparison(datasets):
    comp = compare_datasets(datasets)
    comp.to_csv(ROOT / "house1_comparison_summary.csv", index=False)
    return comp


def main():
    datasets = get_datasets()
    
    # ensure all datasets have the expected column names
    for name, df in datasets.items():
        for c in ["Aggregate", "Appliance1", "Appliance2", "Appliance3", "Appliance4", "Appliance5", "Appliance6", "Appliance7", "Appliance8", "Appliance9"]:
            if c not in df.columns:
                df[c] = np.nan
        datasets[name] = df.copy()

    REPORT_DIR.mkdir(exist_ok=True, parents=True)
    PLOT_DIR.mkdir(exist_ok=True, parents=True)

    text_parts = []
    summaries = {}
    for name, df in datasets.items():
        summary = dataset_summary(name, df)
        summaries[name] = summary
        text_parts.append(write_report(name, summary))
        txt_path = REPORT_DIR / f"{name}_summary.txt"
        txt_path.write_text(write_report(name, summary))
        make_plots(name, df, PLOT_DIR)

    # comparison across datasets
    comparison = write_comparison(datasets)
    combined_text = "\n".join(text_parts)
    (ROOT / "house1_data_quality_report.txt").write_text(combined_text + "\n\nComparison summary:\n" + comparison.to_string(index=False))

    # Data 2A vs Data 2B overlap comparison
    if "data2a_part1" in datasets and "data2b_part2" in datasets:
        a = datasets["data2a_part1"]
        b = datasets["data2b_part2"]
        overlap_summary = {
            "rows_data2a": len(a),
            "rows_data2b": len(b),
            "time_overlap_start": max(a["Time"].min(), b["Time"].min()) if "Time" in a.columns and "Time" in b.columns else None,
            "time_overlap_end": min(a["Time"].max(), b["Time"].max()) if "Time" in a.columns and "Time" in b.columns else None,
            "unique_times_in_a": a["Time"].nunique() if "Time" in a.columns else 0,
            "unique_times_in_b": b["Time"].nunique() if "Time" in b.columns else 0,
            "aggregate_mean_a": float(numeric_series(a["Aggregate"]).mean()) if "Aggregate" in a.columns else np.nan,
            "aggregate_mean_b": float(numeric_series(b["Aggregate"]).mean()) if "Aggregate" in b.columns else np.nan,
            "aggregate_median_a": float(numeric_series(a["Aggregate"]).median()) if "Aggregate" in a.columns else np.nan,
            "aggregate_median_b": float(numeric_series(b["Aggregate"]).median()) if "Aggregate" in b.columns else np.nan,
            "missing_aggregate_a": int(a["Aggregate"].isna().sum()) if "Aggregate" in a.columns else 0,
            "missing_aggregate_b": int(b["Aggregate"].isna().sum()) if "Aggregate" in b.columns else 0,
        }
        # Write a richer comparative section to the report.
        with (ROOT / "house1_data_quality_report.txt").open("a") as f:
            f.write("\n=== Data 2A vs Data 2B comparison ===\n")
            for key, val in overlap_summary.items():
                f.write(f"{key}: {val}\n")

    # long missing-data gaps list
    gaps_all = []
    for name, df in datasets.items():
        if "Time" not in df.columns:
            continue
        times = pd.to_datetime(df["Time"], errors="coerce").dropna().sort_values()
        gaps = times.diff().dropna()
        long = gaps[gaps > pd.Timedelta(minutes=30)]
        for pos, (ts, delta) in enumerate(long.items()):
            if pd.isna(ts) or delta is pd.NaT:
                continue
            idx = times.index.get_loc(ts) if ts in times.index else None
            if idx is None:
                continue
            start = None if idx == 0 else times.iloc[idx - 1]
            end = times.iloc[idx]
            if start is not None:
                gaps_all.append({
                    "dataset": name,
                    "start_time": str(start),
                    "end_time": str(end),
                    "duration_seconds": float(delta.total_seconds()),
                    "duration_minutes": float(delta.total_seconds() / 60.0),
                    "duration_hours": float(delta.total_seconds() / 3600.0),
                    "duration_days": float(delta.total_seconds() / 86400.0),
                })
    pd.DataFrame(gaps_all).to_csv(ROOT / "house1_long_gaps.csv", index=False)

    # suspicious records list
    suspicious = []
    for name, df in datasets.items():
        for col in ["Aggregate"] + [f"Appliance{i}" for i in range(1, 10)]:
            if col not in df.columns:
                continue
            s = numeric_series(df[col])
            threshold = 10000 if col == "Aggregate" else 5000
            subset = df.loc[s > threshold, ["Time", col]].copy()
            for _, row in subset.iterrows():
                suspicious.append({
                    "dataset": name,
                    "timestamp": str(row["Time"]),
                    "column": col,
                    "value": float(row[col]),
                    "threshold": threshold,
                })
    pd.DataFrame(suspicious).to_csv(ROOT / "house1_suspicious_records.csv", index=False)

    print("Quality assessment complete.")
    print(f"Reports written to: {ROOT}")
    print(f"Plots written to: {PLOT_DIR}")
    print(f"Comparison summary rows: {len(comparison)}")


if __name__ == "__main__":
    main()
