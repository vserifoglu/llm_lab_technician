
import os
import argparse
import sys
import glob
from concurrent.futures import ThreadPoolExecutor
from typing import List
from dental_data_pipeline.src.parsers import parse_dental_project, parse_construction_info
from dental_data_pipeline.src.models import Case
from dental_data_pipeline.src.reporting import generate_markdown_report
from dental_data_pipeline.src.visualization import generate_plots
from dental_data_pipeline.src.stats import (
    calculate_jaw_distribution, 
    calculate_completeness_stats,
    get_tooth_frequency,
    get_reconstruction_stats,
    get_cases_size_histogram,
    calculate_margin_point_counts,
    calculate_scan_resolution,
    calculate_file_size_stats,
    calculate_points_per_tooth_type,
    calculate_case_types
)

def process_case(case_dir: str) -> Case:
    """
    Worker function to process a single case folder.
    """
    case_name = os.path.basename(case_dir)
    dental_project_files = glob.glob(os.path.join(case_dir, "*.dentalProject"))
    
    if not dental_project_files:
        return Case(id=case_name, missing_files=["dentalProject"])
        
    project_path = dental_project_files[0]
    
    try:
        case = parse_dental_project(project_path)
    except Exception as e:
        return Case(id=case_name, missing_files=["dentalProject_corrupt"])

    construction_files = glob.glob(os.path.join(case_dir, "*.constructionInfo"))
    if construction_files:
        margins = parse_construction_info(construction_files[0])
        for tooth in case.teeth:
            if tooth.number in margins:
                tooth.margin_points = margins[tooth.number]
    else:
        case.missing_files.append("constructionInfo")
        
    stl_files = glob.glob(os.path.join(case_dir, "*.stl"))
    if not stl_files:
        case.missing_files.append("scan_stl")
    else:
        try:
             total_size = sum(os.path.getsize(f) for f in stl_files)
             case.file_size_mb = total_size / (1024 * 1024)
        except OSError:
             pass

    return case

def main():
    parser = argparse.ArgumentParser(description="Run Dental Data Pipeline Analysis")
    parser.add_argument("--data-dir", type=str, required=True, help="Path to data directory containing case folders")
    parser.add_argument("--output", type=str, default="report.md", help="Output markdown file")
    parser.add_argument("--plots-dir", type=str, default="plots", help="Directory to save plots")
    args = parser.parse_args()

    if not os.path.exists(args.data_dir):
        print(f"Directory not found: {args.data_dir}")
        sys.exit(1)

    all_items = [os.path.join(args.data_dir, d) for d in os.listdir(args.data_dir)]
    case_dirs = [d for d in all_items if os.path.isdir(d)]
    
    print(f"Found {len(case_dirs)} case directories. Processing...")
    
    cases: List[Case] = []
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_case, case_dirs)
        cases = list(results)

    print("Calculating Statistics...")
    
    stats_payload = {
        "total_cases": len(cases),
        "completeness": calculate_completeness_stats(cases),
        "jaw_dist": calculate_jaw_distribution(cases),
        "reconstruction_stats": get_reconstruction_stats(cases),
        "margin_stats": calculate_margin_point_counts(cases),
        "hist_teeth_per_case": get_cases_size_histogram(cases),
        "crown_counts": get_tooth_frequency(cases),
        "file_size_stats": calculate_file_size_stats(cases),
        "scan_resolution_stats": calculate_scan_resolution(cases),
        "clinical_types": calculate_case_types(cases),
        "points_per_tooth": calculate_points_per_tooth_type(cases) 
    }

    # --- GENERATE PLOTS ---
    print(f"Generating Plots in '{args.plots_dir}'...")
    generate_plots(stats_payload, args.plots_dir)

    # --- GENERATE REPORT ---
    markdown_output = generate_markdown_report(stats_payload, plots_dir=args.plots_dir)
    
    with open(args.output, "w") as f:
        f.write(markdown_output)
        
    print(f"\nReport generated successfully: {args.output}")
    print(f"Total Cases: {len(cases)}")
    print("Done.")

if __name__ == "__main__":
    main()
