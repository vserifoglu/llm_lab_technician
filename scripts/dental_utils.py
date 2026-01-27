"""
Dental Utilities - Core Loading & Transformation Functions
===========================================================
Minimal utilities for loading dental case data (STL meshes + margin points)
and transforming them to the correct coordinate space.

Usage:
    from dental_utils import load_teeth, load_mesh, align_mesh, compute_distances
"""

import numpy as np
import trimesh
import xml.etree.ElementTree as ET
from pathlib import Path


def load_teeth(xml_path: str) -> list[dict]:
    """
    Parse all teeth from constructionInfo XML.
    
    Returns list of dicts with keys:
        - number: int (tooth number, e.g. 25)
        - jaw: str ("upper" or "lower")
        - margin_points: ndarray (Nx3, empty if pontic)
        - transform_matrix: ndarray (4x4, ready for trimesh - already transposed)
        - scan_filename: str (which STL file this tooth uses)
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    teeth = []
    
    for tooth_elem in root.findall(".//Tooth"):
        # Number
        num_elem = tooth_elem.find("Number")
        if num_elem is None:
            continue
        number = int(num_elem.text)
        
        # Jaw (FDI: 11-28 = upper, 31-48 = lower)
        jaw = "upper" if 11 <= number <= 28 else "lower"
        
        # Margin points
        margin = []
        margin_elem = tooth_elem.find("Margin")
        if margin_elem is not None:
            for vec in margin_elem.findall("Vec3"):
                margin.append([
                    float(vec.find('x').text),
                    float(vec.find('y').text),
                    float(vec.find('z').text)
                ])
        margin_points = np.array(margin) if margin else np.zeros((0, 3))
        
        # Transform matrix (transposed for column-vector convention)
        mat = np.identity(4)
        zrot = tooth_elem.find("ZRotationMatrix")
        if zrot is not None:
            for r in range(4):
                for c in range(4):
                    elem = zrot.find(f"_{r}{c}")
                    if elem is not None and elem.text:
                        mat[r, c] = float(elem.text)
        transform_matrix = mat.T  # Transpose for trimesh!
        
        # Scan filename
        scan_elem = tooth_elem.find("ToothScanFileName")
        scan_filename = scan_elem.text if scan_elem is not None else ""
        
        teeth.append({
            "number": number,
            "jaw": jaw,
            "margin_points": margin_points,
            "transform_matrix": transform_matrix,
            "scan_filename": scan_filename,
        })
    
    return teeth


def load_mesh(stl_path: str) -> trimesh.Trimesh:
    """Load STL file as trimesh object."""
    return trimesh.load(str(stl_path))


def align_mesh(mesh: trimesh.Trimesh, matrix: np.ndarray) -> trimesh.Trimesh:
    """
    Apply transformation matrix to mesh (Scanner Space → Design Space).
    Returns a NEW mesh, does not modify the original.
    """
    aligned = mesh.copy()
    aligned.apply_transform(matrix)
    return aligned


def compute_distances(mesh: trimesh.Trimesh, points: np.ndarray) -> np.ndarray:
    """
    Compute distance from each point to the nearest mesh surface.
    Returns array of distances (same length as points).
    """
    if len(points) == 0:
        return np.array([])
    _, distances, _ = mesh.nearest.on_surface(points)
    return distances


def transform_points(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """
    Apply 4x4 homogeneous transformation matrix to Nx3 points.
    Handles both rotation and translation correctly.
    
    Args:
        points: Nx3 array of 3D points
        matrix: 4x4 transformation matrix
    
    Returns:
        Nx3 array of transformed points
    """
    if len(points) == 0:
        return points
    # Convert to homogeneous coordinates (add column of 1s)
    ones = np.ones((len(points), 1))
    pts_homogeneous = np.hstack([points, ones])  # Nx4
    # Apply transformation: (Nx4) @ (4x4).T = Nx4
    transformed = pts_homogeneous @ matrix.T
    # Return just xyz (drop the w component)
    return transformed[:, :3]


def classify_vertices(mesh: trimesh.Trimesh, teeth: list) -> np.ndarray:
    """
    Classify vertices as Gum (0) or Tooth (1) based on margin geometry.
    
    Args:
        mesh: The jaw mesh (in Scanner Space)
        teeth: List of tooth dicts (must contain 'transform_matrix' and 'margin_points' in Design Space)
        
    Returns:
        np.ndarray: Integer array of shape (N,) where 1=Tooth, 0=Gum
    """
    vertices = mesh.vertices
    labels = np.zeros(len(vertices), dtype=int)
    
    for tooth in teeth:
        if len(tooth["margin_points"]) < 3:
            continue
            
        # The transform_matrix in tooth dict is (M^T), which aligns Scanner -> Design.
        # See load_teeth: transform_matrix = mat.T
        scanner_to_design = tooth["transform_matrix"]
        
        # Optimization: Filter by distance to Centroid
        # The matrix origin (0,0,0) is NOT the tooth center (offset by ~30mm).
        # Use the mean of the margin points (in Design Space) as the centroid.
        margin_design = tooth["margin_points"]
        centroid_design = np.mean(margin_design, axis=0)
        
        # Transform centroid to Scanner Space for filtering
        inv_mat = np.linalg.inv(scanner_to_design)
        
        # Note: transform_points expects (N,3) array
        centroid_scanner = transform_points(centroid_design.reshape(1, 3), inv_mat)[0]
        
        # Fast distance check (15mm radius captures most teeth)
        dists = np.linalg.norm(vertices - centroid_scanner, axis=1)
        nearby_indices = np.where(dists < 15.0)[0]
        
        if len(nearby_indices) == 0:
            continue
            
        nearby_verts = vertices[nearby_indices]
        
        # Transform candidates to Design Space
        verts_design = transform_points(nearby_verts, scanner_to_design)
        
        # Cylindrical/Radial Check
        # Instead of a global min_z, we compare with the NEAREST margin point's Z.
        # This handles the undulating margin line correctly.
        
        # 1. Broad radial filter (Cylinder footprint)
        # Vertices must be roughly within the margin's XY footprint
        margin = margin_design
        margin_radii = np.linalg.norm(margin[:, :2], axis=1)
        max_radius = np.max(margin_radii) * 1.2  # 20% buffer for gum area
        
        verts_radii = np.linalg.norm(verts_design[:, :2], axis=1)
        in_cylinder = verts_radii < max_radius
        
        if not np.any(in_cylinder):
            continue
            
        # 2. Precise Z-check against nearest margin point
        # We only care about vertices in the cylinder
        candidates_idx = np.where(in_cylinder)[0]
        candidates_design = verts_design[candidates_idx]
        
        # Find nearest margin point for each candidate (using XY distance only)
        # Broadcast: (M, 1, 2) - (1, P, 2)
        dists_xy = np.linalg.norm(
            margin[:, :2].reshape(-1, 1, 2) - candidates_design[:, :2].reshape(1, -1, 2),
            axis=2
        )
        nearest_margin_idx = np.argmin(dists_xy, axis=0)
        nearest_margin_z = margin[nearest_margin_idx, 2]
        
        # 3. Classify
        # Tooth (1): Z > Nearest Margin Z
        # Gum (2): Z <= Nearest Margin Z (but inside cylinder)
        is_tooth = candidates_design[:, 2] > nearest_margin_z
        
        # Map back to global indices
        global_indices = nearby_indices[candidates_idx]
        
        # Update labels (prioritize Tooth over Gum over Jaw)
        # If already marked as Tooth (1) by another tooth (rare overlap), keep it.
        # If currently 0, set to new label.
        current_labels = labels[global_indices]
        
        new_labels = np.full(len(candidates_idx), 2) # Default to Gum
        new_labels[is_tooth] = 1 # Set Tooth
        
        # Only update where we have a "stronger" or equal classification? 
        # Actually, just overwrite 0s. 
        # If overlap: Tooth wins over Gum.
        mask_update = (current_labels == 0) | ((current_labels == 2) & (new_labels == 1))
        
        labels[global_indices[mask_update]] = new_labels[mask_update]
        
    return labels
        
    return labels
