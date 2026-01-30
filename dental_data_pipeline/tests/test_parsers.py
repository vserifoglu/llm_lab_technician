
import pytest
import os
from unittest import mock
from dental_data_pipeline.src.parsers import parse_dental_project, parse_construction_info
from dental_data_pipeline.src.models import ReconstructionType

# We will use the 'tmp_path' fixture from pytest to create files

def test_parse_dental_project_valid(tmp_path, mock_dental_project_xml):
    """Test extracting basic tooth info from dentalProject XML"""
    p = tmp_path / "test.dentalProject"
    p.write_text(mock_dental_project_xml)
    
    # Run Function with absolute path
    result = parse_dental_project(str(p))
    
    # Assert
    assert result.id == "test" # Should likely default to filename stem
    assert len(result.teeth) == 2
    
    t26 = next(t for t in result.teeth if t.number == 26)
    assert t26.reconstruction_type == ReconstructionType.CROWN
    
    t25 = next(t for t in result.teeth if t.number == 25)
    assert t25.reconstruction_type == ReconstructionType.PONTIC

def test_parse_construction_info_valid(tmp_path, mock_construction_info_xml):
    """Test extracting margin points from constructionInfo XML"""
    p = tmp_path / "test.constructionInfo"
    p.write_text(mock_construction_info_xml)
    
    margins = parse_construction_info(str(p))
    
    # Should get a dict or list of margins mapped to tooth numbers
    # Let's assume the parser returns a Dictionary {ToothNum: List[Points]}
    assert 26 in margins
    assert len(margins[26]) == 2
    assert margins[26][0] == (0.0, 0.0, 0.0)
    assert margins[26][1] == (1.0, 0.0, 0.0)

def test_parse_missing_file():
    with pytest.raises(FileNotFoundError):
        parse_dental_project("/non/existent/path.xml")
