import xml.etree.ElementTree as ET
import sys
import os
import json

def is_matrix(element):
    """
    Heuristic to determine if an XML element represents a 4x4 matrix.
    Checks if it has children named _00, _01, ... _33.
    """
    children_tags = {child.tag for child in element}
    # Check for a few key matrix elements to verify
    required_keys = {'_00', '_11', '_22'} 
    return required_keys.issubset(children_tags)

def extract_matrices(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return []

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []

    matrices = []

    def visit(node, path):
        current_path = f"{path}/{node.tag}" if path else node.tag
        
        if is_matrix(node):
            matrix_data = {child.tag: child.text for child in node}
            matrices.append({
                "Name": node.tag,
                "Path": current_path,
                "Data": matrix_data
            })
            # Once we found a matrix, we likely don't need to look inside it for MORE matrices 
            # (unless matrices are nested which is rare/impossible here)
            return

        for child in node:
            visit(child, current_path)

    visit(root, "")
    return matrices

if __name__ == "__main__":
    default_path = "data/lamyaa_ratmi_2026-01-22_Dt malek/lamyaa_ratmi_2026-01-22_Dt malek.constructionInfo"
    target_file = sys.argv[1] if len(sys.argv) > 1 else default_path
    output_file = "scripts/matrices.json"
    
    found_matrices = extract_matrices(target_file)
    
    if found_matrices:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(found_matrices, f, indent=4)
        print(f"Successfully extracted {len(found_matrices)} matrices to {output_file}")
    else:
        print("No matrices found.")
