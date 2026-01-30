
import pytest
from dental_data_pipeline.src.models import Tooth, ReconstructionType

def test_tooth_valid_training_sample_crown_with_margin():
    """A CROWN with enough points should be a valid training sample."""
    # Create 51 points
    points = [(float(i), 0.0, 0.0) for i in range(51)]
    
    t = Tooth(
        number=11,
        reconstruction_type=ReconstructionType.CROWN,
        margin_points=points
    )
    assert t.is_valid_training_sample is True

def test_tooth_invalid_pontic():
    """A PONTIC should never be a valid training sample."""
    points = [(float(i), 0.0, 0.0) for i in range(51)]
    t = Tooth(
        number=11,
        reconstruction_type=ReconstructionType.PONTIC,
        margin_points=points
    )
    assert t.is_valid_training_sample is False

def test_tooth_invalid_not_enough_points():
    """A CROWN with few margin points (bad data) should be invalid."""
    points = [(0.0, 0.0, 0.0)] * 10 
    t = Tooth(
        number=11,
        reconstruction_type=ReconstructionType.CROWN,
        margin_points=points
    )
    assert t.is_valid_training_sample is False
