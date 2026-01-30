
import pytest
from typing import List, Tuple
# No imports from src yet, mocking everything

# Mock Enums and Classes for Testing Purpose (so tests can RUN even if src is empty)
# In real TDD, we would define them in src. Since user asked for *Test Files Only*, we define expectations.
# But python tests fail import error if file missing. 
# We will rely on the "Implementation Phase" to create the src classes.

try:
    from dental_data_pipeline.src.models import Case, Tooth, ReconstructionType
except ImportError:
    pass

@pytest.fixture
def sample_margin_square() -> List[Tuple[float, float, float]]:
    return [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)]

@pytest.fixture
def sample_tooth_crown(sample_margin_square):
    return Tooth(number=26, reconstruction_type=ReconstructionType.CROWN, margin_points=sample_margin_square)

@pytest.fixture
def sample_tooth_pontic():
    return Tooth(number=25, reconstruction_type=ReconstructionType.PONTIC, margin_points=[])

@pytest.fixture
def sample_case(sample_tooth_crown, sample_tooth_pontic):
    return Case(id="Case_001", jaw_type="Upper", teeth=[sample_tooth_crown, sample_tooth_pontic], missing_files=[])

@pytest.fixture
def mock_dental_project_xml():
    """Returns a valid XML string mimicking a .dentalProject file"""
    return """<?xml version="1.0" encoding="utf-8"?>
<Project>
  <Teeth>
    <Tooth>
      <Number>26</Number>
      <ReconstructionType>AnatomicWaxup</ReconstructionType>
    </Tooth>
    <Tooth>
      <Number>25</Number>
      <ReconstructionType>WaxupPontic</ReconstructionType>
    </Tooth>
  </Teeth>
</Project>
"""

@pytest.fixture
def mock_construction_info_xml():
    """Returns a valid XML string mimicking a .constructionInfo file"""
    return """<?xml version="1.0" encoding="utf-8"?>
<ConstructionInfo>
  <Teeth>
    <Tooth>
      <Number>26</Number>
      <Margin>
        <Vec3><x>0</x><y>0</y><z>0</z></Vec3>
        <Vec3><x>1</x><y>0</y><z>0</z></Vec3>
      </Margin>
    </Tooth>
  </Teeth>
</ConstructionInfo>
"""
