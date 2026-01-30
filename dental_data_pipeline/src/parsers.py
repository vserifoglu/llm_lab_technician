
import xml.etree.ElementTree as ET
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from .models import Case, Tooth, ReconstructionType

def get_xml_root(file_path: str) -> Optional[ET.Element]:
    try:
        tree = ET.parse(file_path)
        return tree.getroot()
    except (ET.ParseError, FileNotFoundError):
        return None

def parse_dental_project(path: str) -> Case:
    """
    Parses a .dentalProject file to extract Case metadata and Tooth definitions.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    root = get_xml_root(path)
    if root is None:
        raise ValueError(f"Invalid XML: {path}")

    # Extract Case ID from filename or XML
    # Usually filename is "ProjectName.dentalProject"
    case_id = Path(path).stem

    teeth_list = []
    
    # <Teeth> <Tooth> ... </Tooth> </Teeth>
    teeth_node = root.find("Teeth")
    if teeth_node is not None:
        for tooth_node in teeth_node.findall("Tooth"):
            try:
                elem_num = tooth_node.find("Number")
                elem_type = tooth_node.find("ReconstructionType")
                
                if elem_num is not None and elem_type is not None:
                    t_num = int(elem_num.text)
                    t_type_str = elem_type.text
                    
                    # Convert string to Enum safeley
                    try:
                        rec_type = ReconstructionType(t_type_str)
                    except ValueError:
                        rec_type = ReconstructionType.OTHER

                    # We initialize with empty margin points; those come from ConstructionInfo
                    teeth_list.append(Tooth(number=t_num, reconstruction_type=rec_type))
            except (ValueError, AttributeError):
                continue

    # Determine Jaw Type based on teeth numbers
    # ISO: 1x, 2x = Upper; 3x, 4x = Lower
    has_upper = any(10 <= t.number < 30 for t in teeth_list)
    has_lower = any(30 <= t.number < 50 for t in teeth_list)
    
    jaw_type = "Unknown"
    if has_upper and has_lower:
        jaw_type = "Mixed"
    elif has_upper:
        jaw_type = "Upper"
    elif has_lower:
        jaw_type = "Lower"

    return Case(id=case_id, jaw_type=jaw_type, teeth=teeth_list)

def parse_construction_info(path: str) -> Dict[int, List[Tuple[float, float, float]]]:
    """
    Parses .constructionInfo to extract Margin points.
    Returns a dict: {tooth_number: [(x,y,z), ...]}
    """
    if not os.path.exists(path):
        return {}

    root = get_xml_root(path)
    if root is None:
        return {}

    margins = {}
    
    teeth_node = root.find("Teeth")
    if teeth_node is not None:
        for tooth_node in teeth_node.findall("Tooth"):
            elem_num = tooth_node.find("Number")
            if elem_num is None:
                continue
                
            try:
                t_num = int(elem_num.text)
            except ValueError:
                continue

            margin_node = tooth_node.find("Margin")
            if margin_node is not None:
                points = []
                for vec in margin_node.findall("Vec3"):
                    try:
                        x = float(vec.find("x").text)
                        y = float(vec.find("y").text)
                        z = float(vec.find("z").text)
                        points.append((x, y, z))
                    except (AttributeError, ValueError):
                        continue
                margins[t_num] = points
    
    return margins
