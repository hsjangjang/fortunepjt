import json
import os

files = [
    r"c:\Users\99gkt\OneDrive\바탕 화면\pjt\food.json",
    r"c:\Users\99gkt\OneDrive\바탕 화면\pjt\recommendations\data\food.json"
]

unwanted = ["콘칩", "창난젓", "캐비어"]

for file_path in files:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_count = len(data)
        new_data = [item for item in data if item.get('name_ko') not in unwanted]
        removed_count = original_count - len(new_data)
        
        if removed_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            print(f"Removed {removed_count} items from {file_path}")
        else:
            print(f"No items found to remove in {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
