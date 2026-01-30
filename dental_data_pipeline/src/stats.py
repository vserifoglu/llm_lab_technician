
from typing import List, Dict, Tuple
import numpy as np
from collections import defaultdict
from .models import Case, Tooth, ReconstructionType

def calculate_arc_length(points: List[Tuple[float, float, float]]) -> float:
    if len(points) < 2:
        return 0.0
    
    length = 0.0
    arr_points = np.array(points)
    
    # Sum distances between consecutive points
    dists = np.linalg.norm(arr_points[1:] - arr_points[:-1], axis=1)
    length = np.sum(dists)
    
    # Close the loop
    length += np.linalg.norm(arr_points[0] - arr_points[-1])
    
    return float(length)

def calculate_bounding_box(points: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
    """Returns (dx, dy, dz)"""
    if not points:
        return (0.0, 0.0, 0.0)
    pts = np.array(points)
    min_xyz = np.min(pts, axis=0)
    max_xyz = np.max(pts, axis=0)
    diff = max_xyz - min_xyz
    return tuple(diff)

def calculate_z_range(points: List[Tuple[float, float, float]]) -> float:
    """Calculates the vertical range (Z-axis) of the margin."""
    if not points:
        return 0.0
    pts = np.array(points)
    z_values = pts[:, 2] # Assuming Z is index 2
    return float(np.max(z_values) - np.min(z_values))

def calculate_margin_point_counts(cases: List[Case]) -> Dict:
    counts = []
    for c in cases:
        for t in c.teeth:
            if t.margin_points:
                counts.append(len(t.margin_points))
    
    if not counts:
        return {"counts": [], "min": 0, "max": 0, "mean": 0}

    return {
        "counts": counts, 
        "min": min(counts), 
        "max": max(counts), 
        "mean": float(np.mean(counts))
    }

def calculate_jaw_distribution(cases: List[Case]) -> Dict[str, int]:
    dist = {"Upper": 0, "Lower": 0, "Mixed": 0}
    for c in cases:
        if c.jaw_type in dist:
            dist[c.jaw_type] += 1
        else:
            # Handle unknown or other strings
             # Fallback logic if needed
            pass
    return dist

def calculate_completeness_stats(cases: List[Case]) -> Dict[str, int]:
    stats = {"missing_labels": 0, "missing_scans": 0, "complete": 0}
    for c in cases:
        if not c.missing_files:
            stats["complete"] += 1
        else:
            if "constructionInfo" in c.missing_files:
                stats["missing_labels"] += 1
            if "scan_stl" in c.missing_files:
                stats["missing_scans"] += 1
    return stats

def get_tooth_frequency(cases: List[Case]) -> Dict[int, int]:
    freq = defaultdict(int)
    for c in cases:
        for t in c.teeth:
            freq[t.number] += 1
    return freq

def get_cases_size_histogram(cases: List[Case]) -> Dict[str, int]:
    hist = {"1_unit": 0, "2_5_units": 0, "6_9_units": 0, "10_plus_units": 0}
    for c in cases:
        count = len(c.teeth)
        if count == 1:
            hist["1_unit"] += 1
        elif 2 <= count <= 5:
            hist["2_5_units"] += 1
        elif 6 <= count <= 9:
            hist["6_9_units"] += 1
        elif count >= 10:
            hist["10_plus_units"] += 1
    return hist

def get_reconstruction_stats(cases: List[Case]) -> Dict[ReconstructionType, int]:
    stats = defaultdict(int)
    for c in cases:
        for t in c.teeth:
            stats[t.reconstruction_type] += 1
    return stats

def count_missing_margins(teeth: List[Tooth]) -> int:
    """Counts crowns that are expected to have margins but have 0 points."""
    count = 0
    for t in teeth:
        if t.reconstruction_type == ReconstructionType.CROWN and not t.margin_points:
            count += 1
    return count

def count_adjacency(teeth: List[Tooth]) -> Dict[int, int]:
    """Returns {tooth_number: num_neighbors}"""
    neighbors = defaultdict(int)
    tooth_nums = set(t.number for t in teeth)
    
    for t in teeth:
        n = t.number
        count = 0
        if (n + 1) in tooth_nums and (n // 10 == (n+1) // 10): count += 1
        if (n - 1) in tooth_nums and (n // 10 == (n-1) // 10): count += 1
        if n == 11 and 21 in tooth_nums: count += 1
        if n == 21 and 11 in tooth_nums: count += 1
        if n == 31 and 41 in tooth_nums: count += 1
        if n == 41 and 31 in tooth_nums: count += 1
        neighbors[n] = count
    return neighbors

def is_geometric_outlier(points: List[Tuple[float, float, float]]) -> bool:
    bbox = calculate_bounding_box(points)
    max_dim = max(bbox)
    if max_dim < 0.5: return True
    if max_dim > 100: return True
    return False

def calculate_case_types(cases: List[Case]) -> Dict[str, int]:
    stats = {"Implant": 0, "Veneer": 0, "Crown": 0, "PonticOnly": 0}
    for c in cases:
        types = set(t.reconstruction_type for t in c.teeth)
        if ReconstructionType.IMPLANT in types:
            stats["Implant"] += 1
        elif ReconstructionType.VENEER in types:
            stats["Veneer"] += 1
        elif ReconstructionType.CROWN in types:
            stats["Crown"] += 1
        else:
            stats["PonticOnly"] += 1
    return stats

def calculate_scan_resolution(cases: List[Case]) -> Dict:
    resolutions = [c.scan_vertex_count for c in cases]
    if not resolutions:
         return {"mean": 0, "max": 0}
    return {
        "mean": float(np.mean(resolutions)),
        "max": max(resolutions),
        "min": min(resolutions),
        "total_scanned_vertices": sum(resolutions)
    }

def calculate_file_size_stats(cases: List[Case]) -> Dict:
    sizes = [c.file_size_mb for c in cases]
    if not sizes:
        return {"mean": 0.0, "max": 0.0, "min": 0.0}
    return {
        "mean": float(np.mean(sizes)),
        "max": max(sizes),
        "min": min(sizes)
    }

def calculate_points_per_tooth_type(cases: List[Case]) -> Dict[int, Dict]:
    """Returns {tooth_num: {mean: x, min: y, max: z} }"""
    points_map = defaultdict(list)
    
    for c in cases:
        for t in c.teeth:
            if t.margin_points: # Only count if exists
                points_map[t.number].append(len(t.margin_points))
                
    stats = {}
    for t_num, counts in points_map.items():
        if not counts: continue
        stats[t_num] = {
            "mean": float(np.mean(counts)),
            "min": min(counts),
            "max": max(counts),
            "count": len(counts)
        }
    return stats
