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
