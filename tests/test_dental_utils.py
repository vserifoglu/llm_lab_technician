
import unittest
import numpy as np
import trimesh
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from dental_utils import (
    transform_points,
    compute_vertex_margin_distances,
    compute_mesh_margin_distances
)

class TestDentalUtils(unittest.TestCase):

    def test_transform_points_identity(self):
        """Test random points with identity matrix."""
        points = np.random.rand(10, 3)
        matrix = np.eye(4)
        transformed = transform_points(points, matrix)
        np.testing.assert_array_almost_equal(points, transformed)

    def test_transform_points_translation(self):
        """Test points with simple translation."""
        points = np.array([[0, 0, 0], [1, 1, 1]])
        matrix = np.eye(4)
        matrix[0, 3] = 10  # Translation X by 10
        
        expected = np.array([[10, 0, 0], [11, 1, 1]])
        transformed = transform_points(points, matrix)
        np.testing.assert_array_almost_equal(expected, transformed)

    def test_compute_mesh_margin_distances_single_tooth(self):
        """
        Verify logic for a single tooth:
        - Mesh is at origin (0,0,0)
        - Design Margin is at (10,0,0)
        - BUT Matrix says "Design->Scanner" is translation (-10, 0, 0)
        - So effectively, Scanner Margin should be at (0,0,0)
        - Distance should be 0.
        """
        # 1. Create simple mesh (single point at origin)
        mesh = trimesh.Trimesh(vertices=[[0, 0, 0]], faces=[])
        
        # 2. Design Margin at (10, 0, 0)
        margin_points = np.array([[10, 0, 0]])
        
        # 3. Matrix: Translates Scanner(0) to Design(10)
        # So Matrix is: T(+10)
        # Inverse Matrix (Design->Scanner) is: T(-10)
        matrix = np.eye(4)
        matrix[0, 3] = 10.0
        
        tooth = {
            "number": 1,
            "margin_points": margin_points,
            "transform_matrix": matrix
        }
        
        # 4. Compute
        distances = compute_mesh_margin_distances(mesh, [tooth])
        
        # 5. Expectation:
        # Margin(Design 10) -> * Inv(T+10) -> Margin(Scanner 0)
        # Distance(Mesh 0, Margin 0) == 0.0
        self.assertAlmostEqual(distances[0], 0.0)

    def test_compute_mesh_margin_distances_offset(self):
        """
        Verify distance is non-zero when there is an offset.
        - Mesh at origin
        - Design Margin at (12, 0, 0)
        - Matrix T(+10)
        - Scanner Margin should be (2, 0, 0)
        - Distance should be 2.0
        """
        mesh = trimesh.Trimesh(vertices=[[0, 0, 0]], faces=[])
        margin_points = np.array([[12, 0, 0]])
        matrix = np.eye(4)
        matrix[0, 3] = 10.0
        
        tooth = {
            "number": 1,
            "margin_points": margin_points,
            "transform_matrix": matrix
        }
        
        distances = compute_mesh_margin_distances(mesh, [tooth])
        self.assertAlmostEqual(distances[0], 2.0)

    def test_multi_tooth_logic(self):
        """
        Verify logic for two teeth with different matrices.
        - Mesh Vertex A at (0,0,0)
        - Mesh Vertex B at (100,0,0)
        
        - Tooth 1 (near A):
          - Matrix T(10) -> Scanner space margin ends up at (0,0,0)
          - Should make dist(A) = 0, dist(B) = large
          
        - Tooth 2 (near B):
          - Matrix T(110) -> Scanner space margin ends up at (100,0,0)
          - Should make dist(A) = large, dist(B) = 0
        """
        mesh = trimesh.Trimesh(vertices=[[0, 0, 0], [100, 0, 0]], faces=[])
        
        # Tooth 1: Design at 10, Matrix +10 -> Scanner 0
        t1 = {
            "number": 1, 
            "margin_points": np.array([[10, 0, 0]]), 
            "transform_matrix": np.eye(4)
        }
        t1["transform_matrix"][0, 3] = 10.0
        
        # Tooth 2: Design at 110, Matrix +10 -> Scanner 100
        t2 = {
            "number": 2, 
            "margin_points": np.array([[110, 0, 0]]), 
            "transform_matrix": np.eye(4)
        }
        # Matrix needs to map Scanner(100) -> Design(110)
        t2["transform_matrix"][0, 3] = 10.0 # Same matrix shift, different point
        
        # Wait, if matrices are different...
        # Let's say Tooth 2 has a DIFFERENT matrix.
        # Tooth 2 Matrix: T(+50).
        # Design Point: 150.
        # Scanner Point = 150 - 50 = 100.
        t2["transform_matrix"][0, 3] = 50.0
        t2["margin_points"] = np.array([[150, 0, 0]])
        
        distances = compute_mesh_margin_distances(mesh, [t1, t2])
        
        # Vertex A (0,0,0) should be close to T1 (dist 0)
        self.assertAlmostEqual(distances[0], 0.0)
        
        # Vertex B (100,0,0) should be close to T2 (dist 0)
        self.assertAlmostEqual(distances[1], 0.0)

if __name__ == '__main__':
    unittest.main()
