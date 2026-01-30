
from typing import Dict, List, Any
import os

def generate_markdown_report(stats: Dict[str, Any], plots_dir: str = "plots") -> str:
    """
    Generates a comprehensive Markdown report from statistics dictionary.
    Includes links to plots generated in plots_dir.
    """
    
    report = ["# Dental Data Analysis Report", ""]
    
    # 1. Overview
    report.append(f"**Total Cases**: {stats.get('total_cases', 0)}")
    
    # 2. Completeness
    comp = stats.get("completeness", {})
    if comp:
        report.append("\n## Completeness")
        report.append(f"- Complete Cases: {comp.get('complete', 0)}")
        report.append(f"- Missing Scans: {comp.get('missing_scans', 0)}")
        report.append(f"- Missing Labels: {comp.get('missing_labels', 0)}")

    # 3. Jaw Distribution
    jaws = stats.get("jaw_dist", {})
    if jaws:
        report.append("\n## Jaw Distribution")
        report.append(f"![Jaw Distribution]({plots_dir}/jaw_distribution.png)")
        for k, v in jaws.items():
            report.append(f"- **{k}**: {v}")

    # 4. Reconstruction Types (Tooth Level)
    rec = stats.get("reconstruction_stats", {})
    if rec:
        report.append("\n## Reconstruction Types (Tooth Level)")
        report.append(f"![Reconstruction Types]({plots_dir}/reconstruction_types.png)")
        for k, v in rec.items():
            report.append(f"- {k}: {v}")

    # 5. Clinical Case Types (Case Level)
    clin = stats.get("clinical_types", {})
    if clin:
        report.append("\n## Clinical Case Classification")
        report.append(f"![Clinical Case Types]({plots_dir}/clinical_case_types.png)")
        for k, v in clin.items():
            if v > 0:
                report.append(f"- **{k}**: {v}")

    # 6. Margin Stats
    margins = stats.get("margin_stats", {})
    if margins:
        report.append("\n## Margin Analysis (Crowns)")
        report.append(f"- Mean Points: {margins.get('mean', 0):.1f}")
        report.append(f"- Min Points: {margins.get('min', 0)}")
        report.append(f"- Max Points: {margins.get('max', 0)}")

    # 7. Histograms (Teeth per Case)
    hist_tpc = stats.get("hist_teeth_per_case", {})
    if hist_tpc:
        report.append("\n## Teeth Per Case Histogram")
        report.append(f"![Teeth Per Case]({plots_dir}/teeth_per_case.png)")
        report.append("| Bucket | Count |")
        report.append("|---|---|")
        for bucket, count in hist_tpc.items():
            report.append(f"| {bucket} | {count} |")

    # 8. Tooth Frequency Heatmap (Table)
    freq = stats.get("crown_counts", {})
    if freq:
        report.append("\n## Tooth Frequency Heatmap")
        report.append(f"![Tooth Frequency]({plots_dir}/tooth_frequency.png)")
        report.append("| Tooth # | Count |")
        report.append("|---|---|")
        valid_keys = sorted([k for k in freq.keys() if isinstance(k, int)])
        for k in valid_keys:
            report.append(f"| {k} | {freq[k]} |")

    # 9. Scan Specs
    file_stats = stats.get("file_size_stats", {})
    scan_stats = stats.get("scan_resolution_stats", {})
    
    report.append("\n## Scan Specifications")
    if file_stats:
        report.append(f"- **Mean File Size**: {file_stats.get('mean', 0):.2f} MB")
    if scan_stats and scan_stats.get("mean", 0) > 0:
        report.append(f"- **Mean Vertices**: {scan_stats.get('mean', 0):.0f}")

    return "\n".join(report)
