"""
Visualization Utilities - Polyscope Display Helpers
====================================================
Wraps Polyscope API for dental visualization.
Uses data from dental_utils, provides display functions.

Usage:
    from viz_utils import setup_scene, register_jaw, register_margins, show
"""

import numpy as np
import polyscope as ps
import colorsys


def setup_scene(title: str = "Dental Visualization"):
    """Initialize Polyscope with standard dental visualization settings."""
    ps.init()
    ps.set_up_dir("z_up")
    ps.set_ground_plane_mode("none")


def register_jaw(
    name: str,
    mesh,
    color: tuple = (0.85, 0.85, 0.88),
    transparency: float = 0.9,
    offset: tuple = (0, 0, 0),
    vertex_colors: np.ndarray = None
):
    """
    Add a jaw mesh to the scene.
    
    Args:
        name: Display name (e.g., "UpperJaw")
        mesh: trimesh.Trimesh object
        color: RGB tuple (0-1 range), used if vertex_colors is None
        transparency: 0=opaque, 1=invisible
        offset: (x, y, z) translation for side-by-side layout
        vertex_colors: Optional (N, 3) array of RGB colors for each vertex
    
    Returns:
        Polyscope mesh object
    """
    vertices = mesh.vertices.copy()
    
    if offset != (0, 0, 0):
        vertices = vertices + np.array(offset)
    
    ps_mesh = ps.register_surface_mesh(
        name,
        vertices,
        mesh.faces,
        color=color,
        transparency=transparency,
        smooth_shade=True
    )

    if vertex_colors is not None:
        ps_mesh.add_color_quantity("Semantic Colors", vertex_colors, enabled=True)
        
    return ps_mesh


def generate_tooth_color(tooth_number: int) -> tuple:
    """Generate a distinct color for each tooth using golden ratio."""
    hue = (tooth_number * 0.618033988749895) % 1.0
    return colorsys.hsv_to_rgb(hue, 0.7, 0.9)


def register_margins(
    teeth: list,
    distances: dict = None,
    offset: tuple = (0, 0, 0),
    line_radius: float = 0.0009,
    fixed_color: tuple = (0.0, 0.0, 0.8)
):
    """
    Add margin curves for multiple teeth to the scene.
    
    Args:
        teeth: List of tooth dicts from dental_utils.load_teeth()
        distances: Optional dict {tooth_number: distance_array} for coloring
        offset: (x, y, z) translation to match jaw offset
        line_radius: Thickness of margin lines
    
    Returns:
        List of Polyscope curve objects
    """
    curves = []
    offset_arr = np.array(offset)
    
    for tooth in teeth:
        margin = tooth["margin_points"]
        if len(margin) == 0:
            continue
        
        # Apply offset if provided
        if offset != (0, 0, 0):
            margin = margin + offset_arr
        
        # Create closed loop edges
        n = len(margin)
        edges = np.array([[i, (i + 1) % n] for i in range(n)])
        
        name = f"Tooth {tooth['number']} ({tooth['jaw'][0].upper()})"
        # color = generate_tooth_color(tooth["number"])
        
        ps_curve = ps.register_curve_network(
            name,
            margin,
            edges,
            radius=line_radius,
            color=fixed_color
        )
        
        # Add distance coloring if provided
        if distances and tooth["number"] in distances:
            dist = distances[tooth["number"]]
            ps_curve.add_scalar_quantity(
                "Distance (mm)",
                dist,
                defined_on="nodes",
                enabled=True,
                cmap="coolwarm",
                vminmax=(0, 0.05)
            )
        
        curves.append(ps_curve)
    
    return curves


def focus_on_margins(teeth: list, offset: tuple = (0, 0, 0)):
    """Set camera to focus on the margin points."""
    all_points = []
    for tooth in teeth:
        if len(tooth["margin_points"]) > 0:
            all_points.append(tooth["margin_points"])
    
    if not all_points:
        return
    
    combined = np.vstack(all_points) + np.array(offset)
    center = np.mean(combined, axis=0)
    ps.look_at(center + np.array([0, -40, 20]), center)


def show(screenshot_path: str = None):
    """
    Display the scene.
    
    Args:
        screenshot_path: Optional path to save screenshot before showing
    """
    if screenshot_path:
        ps.screenshot(screenshot_path, transparent_bg=False)
        print(f"Screenshot saved: {screenshot_path}")
    
    ps.show()


def print_report(teeth: list, distances: dict):
    """
    Print alignment report to console.
    
    Args:
        teeth: List of tooth dicts
        distances: Dict {tooth_number: distance_array}
    """
    print("\n" + "=" * 70)
    print("MARGIN ALIGNMENT REPORT")
    print("=" * 70)
    print(f"{'Tooth':<8} {'Jaw':<8} {'Points':<8} {'Mean(mm)':<12} {'Max(mm)':<12} {'Grade':<10}")
    print("-" * 70)
    
    all_dist = []
    
    for tooth in teeth:
        num = tooth["number"]
        if num not in distances or len(distances[num]) == 0:
            continue
        
        d = distances[num]
        mean_d = np.mean(d)
        max_d = np.max(d)
        grade = "🌟 EXCEL" if mean_d < 0.01 else "✅ PASS" if mean_d < 0.05 else "❌ FAIL"
        
        print(f"{num:<8} {tooth['jaw']:<8} {len(d):<8} {mean_d:<12.4f} {max_d:<12.4f} {grade}")
        all_dist.extend(d)
    
    if all_dist:
        print("-" * 70)
        print(f"{'TOTAL':<8} {'':<8} {len(all_dist):<8} {np.mean(all_dist):<12.4f} {np.max(all_dist):<12.4f}")
    print("=" * 70 + "\n")
