import xml.etree.ElementTree as ET
import sys
import os
import json

def extract_structure(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return {}

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return {}

    def process_element(element):
        children = list(element)
        if not children:
            # Leaf node: return text content stripping whitespace
            return element.text.strip() if element.text else ""
        
        # Branch node
        child_dict = {}
        seen_tags = set()
        
        for child in children:
            if child.tag not in seen_tags:
                seen_tags.add(child.tag)
                # Recursively process the first occurrence of this tag
                child_dict[child.tag] = process_element(child)
        
        return child_dict

    # Result structure with root as top key
    structure = {root.tag: process_element(root)}
    return structure

if __name__ == "__main__":
    default_path = "data/lamyaa_ratmi_2026-01-22_Dt malek/lamyaa_ratmi_2026-01-22_Dt malek.constructionInfo"
    target_file = sys.argv[1] if len(sys.argv) > 1 else default_path
    output_file = "scripts/construction_structure.json"
    
    result = extract_structure(target_file)
    
    if result:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"Successfully extracted structure to {output_file}")
    else:
        print("Extraction failed.")
