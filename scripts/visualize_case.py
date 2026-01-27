#!/usr/bin/env python3
"""
Universal Dental Case Visualizer
================================
Visualize any dental case (single or multi-tooth) with margin alignment.

Uses:
- dental_utils.py for data loading
- viz_utils.py for display

Usage:
    # View upper jaw
    python visualize_case.py "data/some_case/" --jaw upper
    
    # View lower jaw
    python visualize_case.py "data/some_case/" --jaw lower
    
    # View both side-by-side
    python visualize_case.py "data/some_case/" --jaw both
    
    # Just print report, no visualization
    python visualize_case.py "data/some_case/" --headless
"""

import numpy as np
from pathlib import Path
import argparse
import time
import sys

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dental_utils import load_teeth, load_mesh, compute_distances, transform_points
from viz_utils import (
    setup_scene, register_jaw, register_margins, 
    focus_on_margins, show, print_report
)


def find_case_files(case_dir: Path) -> dict:
    """Find XML and STL files in case directory."""
    case_name = case_dir.name
    
    xml_file = case_dir / f"{case_name}.constructionInfo"
    upper_stl = case_dir / f"{case_name}-UpperJaw.stl"
    lower_stl = case_dir / f"{case_name}-LowerJaw.stl"
    
    return {
        "name": case_name,
        "xml": xml_file if xml_file.exists() else None,
        "upper_stl": upper_stl if upper_stl.exists() else None,
        "lower_stl": lower_stl if lower_stl.exists() else None,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Visualize dental case with margin alignment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python visualize_case.py "data/lamyaa_ratmi.../" --jaw upper
    python visualize_case.py "data/steven_mourad.../" --jaw both
    python visualize_case.py "data/steven_mourad.../" --headless
        """
    )
    parser.add_argument("case_dir", type=str, help="Path to case directory")
    parser.add_argument("--jaw", choices=["upper", "lower", "both"], default="both",
                        help="Which jaw to visualize (default: both)")
    parser.add_argument("--headless", action="store_true", 
                        help="Print report only, no visualization")
    parser.add_argument("--screenshot", type=str, default=None,
                        help="Save screenshot to this path")
    args = parser.parse_args()
    
    case_dir = Path(args.case_dir)
    if not case_dir.exists():
        print(f"Error: Case directory not found: {case_dir}")
        return 1
    
    # === Find files ===
    files = find_case_files(case_dir)
    if files["xml"] is None:
        print(f"Error: No .constructionInfo file found in {case_dir}")
        return 1
    
    print(f"Case: {files['name']}")
    t_start = time.time()
    
    # === Load teeth data ===
    teeth = load_teeth(str(files["xml"]))
    teeth_with_margins = [t for t in teeth if len(t["margin_points"]) > 0]
    
    upper_teeth = [t for t in teeth_with_margins if t["jaw"] == "upper"]
    lower_teeth = [t for t in teeth_with_margins if t["jaw"] == "lower"]
    
    print(f"  Teeth with margins: {len(teeth_with_margins)} "
          f"(upper: {len(upper_teeth)}, lower: {len(lower_teeth)})")
    
    # === Load meshes (only what we need) ===
    upper_mesh = None
    lower_mesh = None
    
    if (args.jaw in ["upper", "both"]) and files["upper_stl"] and upper_teeth:
        print(f"  Loading UpperJaw...")
        upper_mesh = load_mesh(str(files["upper_stl"]))
        print(f"    {len(upper_mesh.vertices):,} vertices")
    
    if (args.jaw in ["lower", "both"]) and files["lower_stl"] and lower_teeth:
        print(f"  Loading LowerJaw...")
        lower_mesh = load_mesh(str(files["lower_stl"]))
        print(f"    {len(lower_mesh.vertices):,} vertices")
    
    # === Compute distances (inverse transform method) ===
    print("  Computing distances...")
    distances = {}
    
    for tooth in upper_teeth:
        if upper_mesh is None:
            continue
        inv_matrix = np.linalg.inv(tooth["transform_matrix"])
        margins_scanner = transform_points(tooth["margin_points"], inv_matrix)
        distances[tooth["number"]] = compute_distances(upper_mesh, margins_scanner)
    
    for tooth in lower_teeth:
        if lower_mesh is None:
            continue
        inv_matrix = np.linalg.inv(tooth["transform_matrix"])
        margins_scanner = transform_points(tooth["margin_points"], inv_matrix)
        distances[tooth["number"]] = compute_distances(lower_mesh, margins_scanner)
    
    t_compute = time.time()
    print(f"  Done in {t_compute - t_start:.1f}s")
    
    # === Print report ===
    teeth_to_show = []
    if args.jaw in ["upper", "both"]:
        teeth_to_show.extend(upper_teeth)
    if args.jaw in ["lower", "both"]:
        teeth_to_show.extend(lower_teeth)
    
    print_report(teeth_to_show, distances)
    
    # === Visualize ===
    if args.headless:
        print("[Headless mode] Skipping visualization.")
        return 0
    
    print("  Preparing visualization...")
    setup_scene(f"Case: {files['name']}")
    
    # Determine offsets for side-by-side layout
    upper_offset = (0, 0, 0)
    lower_offset = (0, 0, 0)
    
    if args.jaw == "both" and upper_mesh and lower_mesh:
        # Offset lower jaw to the right for side-by-side view
        lower_offset = (70, 0, 0)  # 70mm separation
    
    # Register meshes (transform to design space for visualization)
    if upper_mesh and upper_teeth and args.jaw in ["upper", "both"]:
        upper_mesh.apply_transform(upper_teeth[0]["transform_matrix"])
        register_jaw("UpperJaw", upper_mesh, 
                     color=(0.9, 0.85, 0.8), 
                     offset=upper_offset)
        register_margins(upper_teeth, distances, offset=upper_offset)
    
    if lower_mesh and lower_teeth and args.jaw in ["lower", "both"]:
        lower_mesh.apply_transform(lower_teeth[0]["transform_matrix"])
        register_jaw("LowerJaw", lower_mesh, 
                     color=(0.8, 0.85, 0.9), 
                     offset=lower_offset)
        register_margins(lower_teeth, distances, offset=lower_offset)
    
    # Focus camera
    if args.jaw == "upper":
        focus_on_margins(upper_teeth)
    elif args.jaw == "lower":
        focus_on_margins(lower_teeth)
    else:
        # For both, focus between them
        focus_on_margins(teeth_to_show, offset=(35, 0, 0))
    
    print(f"\n  Launching viewer (jaw: {args.jaw})...")
    show(screenshot_path=args.screenshot)
    
    return 0


if __name__ == "__main__":
    exit(main())
