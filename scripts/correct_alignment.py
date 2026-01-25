
import numpy as np
import trimesh
import json
import argparse
import xml.etree.ElementTree as ET

def load_matrix(json_path, matrix_name="ZRotationMatrix"):
    """
    Load the matrix from JSON and return it in a standard Numpy usage format (Row-Vector convention).
    The JSON stores translation in the bottom row indices (_30, _31, _32).
    This means if loaded literally into 4x4, it works with:
        v_new = v_old @ M
    """
    with open(json_path, 'r') as f:
        matrices = json.load(f)
    
    for m in matrices:
        if m['Name'] == matrix_name:
            d = m['Data']
            mat = np.identity(4)
            for r in range(4):
                for c in range(4):
                    key = f"_{r}{c}"
                    if key in d:
                        mat[r, c] = float(d[key])
            return mat
    raise ValueError(f"Matrix {matrix_name} not found in {json_path}")


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def load_margin(xml_path):
    """Load margin points from constructionInfo XML."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        margin = []
        for m in root.findall(".//Margin"):
            for vec in m.findall("Vec3"):
                margin.append([
                    float(vec.find('x').text),
                    float(vec.find('y').text),
                    float(vec.find('z').text)
                ])
        return np.array(margin)
    except Exception as e:
        print(f"Warning: Could not load margin from {xml_path}: {e}")
        return getattr(np, "array")([])

def verify_alignment(aligned_mesh, margin_points):
    """
    Mathematical Proof:
    Calculate the distance from every point on the Margin (Design Space) 
    to the surface of the Aligned Mesh (which started in Scanner Space).
    """
    if len(margin_points) == 0:
        print("No margin points loaded, cannot verify.")
        return

    print("\n" + "="*50)
    print("MATHEMATICAL PROOF OF ALIGNMENT")
    print("="*50)
    print(f"Checking {len(margin_points)} margin points against aligned mesh surface...")
    
    # Use Trimesh's nearest point search
    # This finds the closest point on the mesh surface for each margin point
    closest_points, distances, triangle_ids = aligned_mesh.nearest.on_surface(margin_points)
    
    mean_error = np.mean(distances)
    max_error = np.max(distances)
    std_error = np.std(distances)
    
    print(f"Mean Distance (Margin -> Mesh): {mean_error:.6f} mm")
    print(f"Max Distance:                   {max_error:.6f} mm")
    print(f"Standard Deviation:             {std_error:.6f} mm")
    
    print("-" * 30)
    print("Sample Verification (First 5 Points):")
    for i in range(min(5, len(margin_points))):
        p_margin = margin_points[i]
        p_mesh = closest_points[i]
        dist = distances[i]
        print(f"Margin Pt {i}: {p_margin} -> Mesh Pt: {p_mesh} | Dist: {dist:.6f}mm")
        
    if mean_error < 0.05:
        print("\n✅ PROOF SUCCESSFUL: The margin lies on the mesh surface (< 0.05mm).")
    else:
        print("\n❌ PROOF FAILED: Significant deviation detected.")
    print("="*50 + "\n")

def plot_alignment(aligned_mesh, margin_points, output_image="scripts/alignment_plot.png"):
    """Generate a 3D plot of the aligned mesh and margin."""
    print(f"Generating plot to {output_image}...")
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. Plot Margin (Red Loop)
    # Close the loop for visualization
    if len(margin_points) > 0:
        closed_margin = np.vstack([margin_points, margin_points[0]])
        ax.plot(closed_margin[:,0], closed_margin[:,1], closed_margin[:,2], 
                c='red', linewidth=2, label='Margin (Design Space)', zorder=10)
        
        # Calculate centroid for focusing the camera
        center = np.mean(margin_points, axis=0)
    else:
        center = aligned_mesh.centroid

    # 2. Plot Aligned Mesh (Grey Point Cloud for performance)
    # We crop the mesh to the relevant area to make the plot readable
    # Radius of 15mm around the margin center
    dists = np.linalg.norm(aligned_mesh.vertices - center, axis=1)
    mask = dists < 15
    local_verts = aligned_mesh.vertices[mask]
    
    # Downsample for plotting speed
    stride = max(1, len(local_verts) // 2000)
    plot_verts = local_verts[::stride]
    
    ax.scatter(plot_verts[:,0], plot_verts[:,1], plot_verts[:,2], 
               c='grey', s=1, alpha=0.3, label='Aligned Scanner Mesh')
    
    ax.set_title("Alignment Verification: Scanner Mesh transformed to Design Space")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()
    
    # Set generous limits to ensure everything is visible
    ax.auto_scale_xyz(plot_verts[:,0], plot_verts[:,1], plot_verts[:,2])
    
    plt.savefig(output_image)
    print("Plot saved.")

def main():
    # Hardcoded paths as requested
    SCANNER = "data/lamyaa_ratmi_2026-01-22_Dt malek/lamyaa_ratmi_2026-01-22_Dt malek-UpperJaw.stl"
    MARGIN_XML = "data/lamyaa_ratmi_2026-01-22_Dt malek/lamyaa_ratmi_2026-01-22_Dt malek.constructionInfo"
    MATRICES = "scripts/matrices.json" 
    OUTPUT = "scripts/aligned_scanner.stl"
    PLOT_OUTPUT = "scripts/alignment_plot.png"

    # 1. Load Scanner Mesh
    print(f"Loading Scanner: {SCANNER}")
    mesh = trimesh.load(SCANNER)
    
    # 2. Load Matrix
    print(f"Loading Matrix: {MATRICES}")
    M_transform = load_matrix(MATRICES, "ZRotationMatrix")
    
    # 3. Apply Transform
    if np.linalg.norm(M_transform[3, :3]) > 0:
        print(" -> Detected Row-Vector Matrix (Translation in Row 3). Transposing for Trimesh usage.")
        M_for_trimesh = M_transform.T
    else:
        M_for_trimesh = M_transform
        
    print("Applying transform...")
    mesh.apply_transform(M_for_trimesh)
    
    # 4. Verify & Plot (Mathematical Proof)
    print(f"Loading Margin for Verification: {MARGIN_XML}")
    margin_points = load_margin(MARGIN_XML)
    
    verify_alignment(mesh, margin_points)
    plot_alignment(mesh, margin_points, PLOT_OUTPUT)

    # 5. Save
    print(f"Saving aligned mesh to: {OUTPUT}")
    mesh.export(OUTPUT)
    
    print("Done! The scanner mesh should now align with the margin line in Design Space.")

if __name__ == "__main__":
    main()
