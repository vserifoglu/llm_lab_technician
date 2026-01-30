
import pytest
from dental_data_pipeline.src.stats import calculate_arc_length, calculate_margin_point_counts

def test_calculate_arc_length_square(sample_margin_square):
    """Test standard perimeter calculation: Square 1x1 should be 4.0"""
    length = calculate_arc_length(sample_margin_square)
    assert length == 4.0

def test_calculate_arc_length_empty():
    assert calculate_arc_length([]) == 0.0

def test_calculate_arc_length_single_point():
    assert calculate_arc_length([(0,0,0)]) == 0.0


from dental_data_pipeline.src.models import Case, Tooth, ReconstructionType
from dental_data_pipeline.src.stats import (
    calculate_jaw_distribution, 
    get_tooth_frequency, 
    get_cases_size_histogram,
    is_geometric_outlier,
    calculate_completeness_stats,
    calculate_bounding_box,
    is_geometric_outlier,
    calculate_completeness_stats,
    calculate_bounding_box,
    calculate_scan_resolution,
    calculate_z_range,
    calculate_file_size_stats,
    calculate_points_per_tooth_type
)

def test_jaw_distribution_counts():
    """1. Test counting of Upper vs Lower vs Dual arches."""
    cases = [
        Case(id="1", jaw_type="Upper", teeth=[]),
        Case(id="2", jaw_type="Lower", teeth=[]),
        Case(id="3", jaw_type="Upper", teeth=[]),
        Case(id="4", jaw_type="Mixed", teeth=[]), # Dual arch
    ]
    dist = calculate_jaw_distribution(cases)
    assert dist["Upper"] == 2
    assert dist["Lower"] == 1
    assert dist["Mixed"] == 1

def test_case_type_classification_counts():
    """1. Statistics: Count cases by clinical category (Veneer, Implant, Crown)."""
    # Strategies:
    # - If ANY tooth is Implant -> Implant Case
    # - If ANY tooth is Veneer -> Veneer Case
    # - Else -> Crown Case
    
    c_implant = Case(id="1", teeth=[Tooth(number=1, reconstruction_type=ReconstructionType.IMPLANT)])
    c_veneer = Case(id="2", teeth=[Tooth(number=2, reconstruction_type=ReconstructionType.VENEER)])
    c_crown = Case(id="3", teeth=[Tooth(number=3, reconstruction_type=ReconstructionType.CROWN)])
    
    from dental_data_pipeline.src.stats import calculate_case_types
    stats = calculate_case_types([c_implant, c_veneer, c_crown])
    
    assert stats["Implant"] == 1
    assert stats["Veneer"] == 1
    assert stats["Crown"] == 1

def test_completeness_stats():
    """1. Dataset Completeness: Missing files or info."""
    # Assuming Case model has flags for file presence
    cases = [
        Case(id="1", jaw_type="Upper", teeth=[], missing_files=[]),
        Case(id="2", jaw_type="Upper", teeth=[], missing_files=["constructionInfo"]),
        Case(id="3", jaw_type="Upper", teeth=[], missing_files=["scan_stl"]),
    ]
    stats = calculate_completeness_stats(cases)
    assert stats["missing_labels"] == 1
    assert stats["missing_scans"] == 1
    assert stats["complete"] == 1

# --- 2. Tooth-Level Stats Tests ---

def test_tooth_frequency_map():
    """2. Heatmap of most common teeth."""
    cases = [
        Case(id="1", jaw_type="U", teeth=[
            Tooth(number=11, reconstruction_type=ReconstructionType.CROWN),
            Tooth(number=21, reconstruction_type=ReconstructionType.PONTIC) # Should pontics count? User implies "Overall Tooth Frequency"
        ]),
        Case(id="2", jaw_type="U", teeth=[
             Tooth(number=11, reconstruction_type=ReconstructionType.CROWN)
        ])
    ]
    freq = get_tooth_frequency(cases)
    assert freq[11] == 2
    assert freq[21] == 1
    assert freq[26] == 0

def test_teeth_per_case_histogram():
    """2. Histogram buckets: Single, Bridge, Full Arch."""
    c1 = Case(id="1", jaw_type="U", teeth=[Tooth(number=1, reconstruction_type=ReconstructionType.CROWN)])
    c3 = Case(id="2", jaw_type="U", teeth=[
        Tooth(number=1, reconstruction_type=ReconstructionType.CROWN),
        Tooth(number=2, reconstruction_type=ReconstructionType.PONTIC),
        Tooth(number=3, reconstruction_type=ReconstructionType.CROWN)
    ])
    
    # Create 10 teeth for full arch
    ten_teeth = [Tooth(number=i, reconstruction_type=ReconstructionType.CROWN) for i in range(10)]
    c10 = Case(id="3", jaw_type="U", teeth=ten_teeth)
    
    hist = get_cases_size_histogram([c1, c3, c10])
    
    assert hist["1_unit"] == 1
    assert hist["2_5_units"] == 1 # "Small bridges"
    assert hist["10_plus_units"] == 1 # "Full Arch"

def test_reconstruction_type_breakdown():
    """2. Breakdown of Crowns vs Pontics."""
    cases = [
        Case(id="1", jaw_type="U", teeth=[
            Tooth(number=1, reconstruction_type=ReconstructionType.CROWN),
            Tooth(number=2, reconstruction_type=ReconstructionType.PONTIC),
            Tooth(number=3, reconstruction_type=ReconstructionType.CROWN)
        ])
    ]
    # Implement function reference
    from dental_data_pipeline.src.stats import get_reconstruction_stats
    stats = get_reconstruction_stats(cases)
    assert stats[ReconstructionType.CROWN] == 2
    assert stats[ReconstructionType.PONTIC] == 1

# --- 3. Margin Data Stats Tests ---

def test_missing_margins_check():
    """3. Count of AnatomicWaxup (Crowns) that HAVE NO MARGIN POINTS (Bad Data)."""
    bad_tooth = Tooth(number=11, reconstruction_type=ReconstructionType.CROWN, margin_points=[])
    good_tooth = Tooth(number=21, reconstruction_type=ReconstructionType.CROWN, margin_points=[(0,0,0)])
    
    from dental_data_pipeline.src.stats import count_missing_margins
    missing = count_missing_margins([bad_tooth, good_tooth])
    assert missing == 1

# --- 3. Margin Data Stats Tests ---

def test_margin_bounding_box_calculation():
    """Test bounding box size (dx, dy, dz) calculation."""
    # A 1x1x0 square
    margin = [(0,0,0), (1,0,0), (1,1,0), (0,1,0)]
    from dental_data_pipeline.src.stats import calculate_bounding_box
    bbox = calculate_bounding_box(margin)
    assert bbox == (1.0, 1.0, 0.0)

# --- 4. Complexity & Adjacency Tests ---

def test_adjacency_isolated_tooth():
    """Tooth 18 with no neighbors."""
    teeth = [Tooth(number=18, reconstruction_type=ReconstructionType.CROWN)]
    from dental_data_pipeline.src.stats import count_adjacency
    adj = count_adjacency(teeth)
    # map {18: 0_neighbors}
    assert adj[18] == 0

def test_adjacency_neighboring_pair():
    """Teeth 11 and 21 (Front crossing midline) -> Each has 1 neighbor"""
    teeth = [
        Tooth(number=11, reconstruction_type=ReconstructionType.CROWN),
        Tooth(number=21, reconstruction_type=ReconstructionType.CROWN)
    ]
    from dental_data_pipeline.src.stats import count_adjacency
    adj = count_adjacency(teeth)
    assert adj[11] == 1
    assert adj[21] == 1

def test_adjacency_bridge_gap():
    """Teeth 13, 15 (Missing 14) -> Should NOT be adjacent."""
    teeth = [
        Tooth(number=13, reconstruction_type=ReconstructionType.CROWN),
        Tooth(number=15, reconstruction_type=ReconstructionType.CROWN)
    ]
    from dental_data_pipeline.src.stats import count_adjacency
    adj = count_adjacency(teeth)
    assert adj[13] == 0
    assert adj[15] == 0

def test_bridge_identification_connected_units():
    """4. Ratio of Connected vs Separated units."""
    # If 13 and 14 are present, they are "Connected" (Adjacency > 0)
    # Or strict bridge definition: They are in the same 'dentalProject' group?
    # For now, let's use adjacency as proxy for connection strength.
    pass 

# --- SIGNIFICANT NEW TEST CASES ---

def test_detect_outliers_tiny_margin():
    """Safety: Warning if a margin is suspiciously small (e.g. noise)."""
    # A 0.01mm box is likely noise, not a human tooth margin
    tiny_margin = [(0,0,0), (0.01,0,0), (0.01,0.01,0)]
    from dental_data_pipeline.src.stats import is_geometric_outlier
    assert is_geometric_outlier(tiny_margin) is True

def test_detect_outliers_huge_margin():
    """Safety: Warning if margin spans whole jaw (bad coordinates)."""
    huge_margin = [(0,0,0), (1000,0,0)] # 1 meter wide tooth?
    from dental_data_pipeline.src.stats import is_geometric_outlier
    assert is_geometric_outlier(huge_margin) is True

def test_z_range_calculation():
    """Safety: specific test for margin steepness."""
    # Flat margin
    flat = [(0,0,0), (1,1,0)] 
    from dental_data_pipeline.src.stats import calculate_z_range
    assert calculate_z_range(flat) == 0.0
    
    # Steep margin (e.g. 5mm drop)
    steep = [(0,0,0), (1,1,5)]
    assert calculate_z_range(steep) == 5.0

def test_file_size_proxy():
    """Test file size aggregation."""
    # Mock cases with file_size attribute (we need to add this to Model)
    c1 = Case(id="1", file_size_mb=10.5)
    c2 = Case(id="2", file_size_mb=2.5)
    
    from dental_data_pipeline.src.stats import calculate_file_size_stats
    stats = calculate_file_size_stats([c1, c2])
    assert stats["mean"] == 6.5
    assert stats["min"] == 2.5

def test_points_per_tooth_type():
    """Contextual Outliers: Points per tooth number."""
    # Tooth 11 (central) with 100 points
    # Tooth 18 (molar) with 200 points
    c = Case(id="1", teeth=[
        Tooth(number=11, reconstruction_type=ReconstructionType.CROWN, margin_points=[(0,0,0)]*100),
        Tooth(number=18, reconstruction_type=ReconstructionType.CROWN, margin_points=[(0,0,0)]*200)
    ])
    
    from dental_data_pipeline.src.stats import calculate_points_per_tooth_type
    stats = calculate_points_per_tooth_type([c])
    assert stats[11]["mean"] == 100
    assert stats[18]["mean"] == 200


def test_scan_resolution_stats():
    """Safety: Warning if scan is too high res (slow) or too low (bad)."""
    # Assuming 'Case' object has a 'scan_vertex_count' field loaded by parser.
    c_high = Case(id="1", scan_vertex_count=500000)
    c_low = Case(id="2", scan_vertex_count=50000)
    
    from dental_data_pipeline.src.stats import calculate_scan_resolution
    stats = calculate_scan_resolution([c_high, c_low])
    
    assert stats["mean"] == 275000
    assert stats["max"] == 500000
