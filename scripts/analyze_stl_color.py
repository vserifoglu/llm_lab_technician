"""
Analyze STL files for color/texture data.

This script checks whether STL scans contain color/texture information
that could indicate the white margin marking on prepped teeth.

Usage:
    python analyze_stl_color.py [path_to_stl_or_case_folder]
    
If no path provided, analyzes all cases in the data folder.
"""

import sys
from pathlib import Path
import trimesh
import numpy as np

# Add parent scripts folder to path
sys.path.insert(0, str(Path(__file__).parent))
from dental_utils import load_mesh


def analyze_stl_properties(stl_path: Path) -> dict:
    """
    Analyze an STL file for color/texture properties.
    
    Returns dict with:
        - has_vertex_colors: bool
        - has_face_colors: bool  
        - has_visual: bool (texture/material)
        - color_stats: dict with color statistics if present
        - mesh_stats: dict with basic mesh info
    """
    mesh = trimesh.load(str(stl_path))
    
    result = {
        "filename": stl_path.name,
        "file_size_mb": stl_path.stat().st_size / (1024 * 1024),
        "mesh_type": type(mesh).__name__,
    }
    
    # Handle Scene vs Trimesh
    if isinstance(mesh, trimesh.Scene):
        # Scene contains multiple meshes
        result["is_scene"] = True
        result["num_geometries"] = len(mesh.geometry)
        # Get the first/main mesh
        if mesh.geometry:
            mesh = list(mesh.geometry.values())[0]
        else:
            result["error"] = "Empty scene"
            return result
    else:
        result["is_scene"] = False
    
    # Basic mesh stats
    result["num_vertices"] = len(mesh.vertices)
    result["num_faces"] = len(mesh.faces)
    
    # Check for vertex colors
    if hasattr(mesh, 'visual') and mesh.visual is not None:
        visual = mesh.visual
        result["visual_kind"] = visual.kind if hasattr(visual, 'kind') else str(type(visual).__name__)
        
        # ColorVisuals - vertex or face colors
        if hasattr(visual, 'vertex_colors'):
            vc = visual.vertex_colors
            if vc is not None and len(vc) > 0:
                result["has_vertex_colors"] = True
                result["vertex_colors_shape"] = vc.shape
                
                # Analyze color distribution
                if len(vc.shape) >= 2 and vc.shape[1] >= 3:
                    # Check if colors vary or are uniform
                    unique_colors = len(np.unique(vc[:, :3], axis=0))
                    result["unique_vertex_colors"] = unique_colors
                    result["color_variance"] = float(np.var(vc[:, :3]))
                    
                    # Sample some colors
                    sample_idx = np.linspace(0, len(vc)-1, min(5, len(vc)), dtype=int)
                    result["sample_colors_rgb"] = vc[sample_idx, :3].tolist()
            else:
                result["has_vertex_colors"] = False
        else:
            result["has_vertex_colors"] = False
            
        # Face colors
        if hasattr(visual, 'face_colors'):
            fc = visual.face_colors
            if fc is not None and len(fc) > 0:
                result["has_face_colors"] = True
                result["face_colors_shape"] = fc.shape
                unique_fc = len(np.unique(fc[:, :3], axis=0))
                result["unique_face_colors"] = unique_fc
            else:
                result["has_face_colors"] = False
        else:
            result["has_face_colors"] = False
            
        # Texture/Material
        if hasattr(visual, 'material'):
            result["has_material"] = visual.material is not None
        else:
            result["has_material"] = False
            
        if hasattr(visual, 'uv'):
            uv = visual.uv
            result["has_uv_coords"] = uv is not None and len(uv) > 0
        else:
            result["has_uv_coords"] = False
    else:
        result["has_vertex_colors"] = False
        result["has_face_colors"] = False
        result["has_material"] = False
        result["has_uv_coords"] = False
        result["visual_kind"] = "None"
    
    return result


def print_analysis(result: dict):
    """Pretty print the analysis result."""
    print(f"\n{'='*60}")
    print(f"File: {result['filename']}")
    print(f"Size: {result['file_size_mb']:.2f} MB")
    print(f"{'='*60}")
    
    if "error" in result:
        print(f"  ERROR: {result['error']}")
        return
        
    print(f"  Mesh Type: {result['mesh_type']}")
    print(f"  Vertices: {result.get('num_vertices', 'N/A'):,}")
    print(f"  Faces: {result.get('num_faces', 'N/A'):,}")
    print(f"  Visual Kind: {result.get('visual_kind', 'N/A')}")
    print()
    
    # Color analysis
    print("  COLOR/TEXTURE ANALYSIS:")
    print(f"    Vertex Colors: {'✓ YES' if result.get('has_vertex_colors') else '✗ NO'}")
    if result.get('has_vertex_colors'):
        print(f"      - Shape: {result.get('vertex_colors_shape')}")
        print(f"      - Unique Colors: {result.get('unique_vertex_colors', 'N/A'):,}")
        print(f"      - Variance: {result.get('color_variance', 0):.4f}")
        if 'sample_colors_rgb' in result:
            print(f"      - Sample RGB: {result['sample_colors_rgb'][:3]}")
            
    print(f"    Face Colors: {'✓ YES' if result.get('has_face_colors') else '✗ NO'}")
    if result.get('has_face_colors'):
        print(f"      - Unique: {result.get('unique_face_colors', 'N/A')}")
        
    print(f"    Material: {'✓ YES' if result.get('has_material') else '✗ NO'}")
    print(f"    UV Coords: {'✓ YES' if result.get('has_uv_coords') else '✗ NO'}")
    
    # Verdict
    print()
    has_color = (result.get('has_vertex_colors') or result.get('has_face_colors'))
    if has_color and result.get('unique_vertex_colors', 0) > 10:
        print("  VERDICT: ✓ This STL contains color data that varies across the mesh!")
    elif has_color:
        print("  VERDICT: ~ STL has color data but appears uniform (single color)")
    else:
        print("  VERDICT: ✗ This STL is geometry-only (no color/texture)")


def main():
    # Determine what to analyze
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        # Default: analyze first case in data folder
        data_dir = Path(__file__).parent.parent / "data"
        cases = list(data_dir.iterdir())
        if not cases:
            print("No cases found in data folder")
            return
        target = cases[0]
        print(f"No path provided, analyzing: {target}")
    
    # Collect STL files
    stl_files = []
    if target.is_file() and target.suffix.lower() == '.stl':
        stl_files = [target]
    elif target.is_dir():
        stl_files = list(target.glob("*.stl")) + list(target.glob("*.STL"))
    
    if not stl_files:
        print(f"No STL files found in: {target}")
        return
    
    print(f"\nAnalyzing {len(stl_files)} STL file(s)...")
    
    # Analyze each
    results = []
    for stl_path in sorted(stl_files):
        try:
            result = analyze_stl_properties(stl_path)
            results.append(result)
            print_analysis(result)
        except Exception as e:
            print(f"\nError analyzing {stl_path.name}: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    has_any_color = any(r.get('has_vertex_colors') or r.get('has_face_colors') for r in results)
    if has_any_color:
        print("✓ At least one STL contains color data!")
        print("  → The white margin marking MAY be detectable from color")
    else:
        print("✗ No STL files contain color data")
        print("  → Must rely on geometry-only approaches")


if __name__ == "__main__":
    main()
