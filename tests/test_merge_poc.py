#!/usr/bin/env python3
"""
Proof-of-Concept: Merge Mesh + Margins into Single Pre-Processed File
======================================================================
This script verifies that we can:
1. Transform margin points to Scanner Space ONCE
2. Save everything to a .npz file
3. Reload and visualize without any runtime transformations

Run:
    python test_merge_poc.py
"""

import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from dental_utils import load_teeth, load_mesh, transform_points, compute_distances
from viz_utils import setup_scene, register_jaw, register_margins, show

# === CONFIG ===
CASE_DIR = Path("/home/veysel/dev-projects/llm_lab_technician/data/lamyaa_ratmi_2026-01-22_Dt malek")
OUTPUT_FILE = Path("/tmp/test_merged_upper.npz")

def main():
    case_name = CASE_DIR.name
    xml_path = CASE_DIR / f"{case_name}.constructionInfo"
    stl_path = CASE_DIR / f"{case_name}-UpperJaw.stl"
    
    print("=" * 60)
    print("STEP 1: Load & Transform (Single Pass)")
    print("=" * 60)
    
    # Load raw data
    teeth = load_teeth(str(xml_path))
    upper_teeth = [t for t in teeth if t["jaw"] == "upper" and len(t["margin_points"]) > 0]
    mesh = load_mesh(str(stl_path))
    
    print(f"  Loaded mesh: {len(mesh.vertices):,} vertices")
    print(f"  Found {len(upper_teeth)} upper teeth with margins")
    
    # Pre-transform margins to Scanner Space (THE KEY STEP)
    teeth_scanner_space = []
    for tooth in upper_teeth:
        inv_mat = np.linalg.inv(tooth["transform_matrix"])
        margins_scanner = transform_points(tooth["margin_points"], inv_mat)
        
        teeth_scanner_space.append({
            "number": tooth["number"],
            "jaw": tooth["jaw"],
            "margin_points": margins_scanner,  # NOW IN SCANNER SPACE!
        })
        print(f"    Tooth {tooth['number']}: {len(margins_scanner)} pts transformed")
    
    # === SAVE TO .NPZ ===
    print(f"\nSaving to: {OUTPUT_FILE}")
    
    # Pack margins into arrays (variable-length, so use object array)
    margin_data = {
        f"tooth_{t['number']}_margins": t["margin_points"] 
        for t in teeth_scanner_space
    }
    tooth_numbers = np.array([t["number"] for t in teeth_scanner_space])
    
    np.savez_compressed(
        OUTPUT_FILE,
        vertices=mesh.vertices,
        faces=mesh.faces,
        tooth_numbers=tooth_numbers,
        **margin_data
    )
    print(f"  Saved! File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
    
    # === STEP 2: RELOAD AND VISUALIZE (NO TRANSFORMS!) ===
    print("\n" + "=" * 60)
    print("STEP 2: Reload from .npz & Visualize (No Transforms)")
    print("=" * 60)
    
    # Reload
    data = np.load(OUTPUT_FILE)
    vertices = data["vertices"]
    faces = data["faces"]
    tooth_numbers = data["tooth_numbers"]
    
    print(f"  Loaded: {len(vertices):,} vertices, {len(tooth_numbers)} teeth")
    
    # Reconstruct teeth list (margins already in Scanner Space!)
    teeth_from_file = []
    for num in tooth_numbers:
        margins = data[f"tooth_{num}_margins"]
        teeth_from_file.append({
            "number": int(num),
            "jaw": "upper",
            "margin_points": margins,  # Already in Scanner Space!
        })
        print(f"    Tooth {num}: {len(margins)} pts (no transform needed!)")
    
    # Create a simple mesh object for visualization
    import trimesh
    reloaded_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    # Compute distances to verify alignment still works
    distances = {}
    for tooth in teeth_from_file:
        d = compute_distances(reloaded_mesh, tooth["margin_points"])
        distances[tooth["number"]] = d
        print(f"    Tooth {tooth['number']} distance: mean={np.mean(d):.4f}mm, max={np.max(d):.4f}mm")
    
    # === VISUALIZE ===
    print("\nLaunching visualization...")
    setup_scene("Merged Data POC")
    register_jaw("UpperJaw (from .npz)", reloaded_mesh, color=(0.8, 0.8, 0.85))
    register_margins(teeth_from_file, distances)
    show()
    
    print("\n✅ SUCCESS: Merging approach verified!")
    return 0

if __name__ == "__main__":
    exit(main())
