# check_current_styles.py
import re

def check_file_for_transform(filepath):
    """Check a specific file for transform properties"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Look for transform properties
            transform_pattern = re.compile(r'transform\s*:')
            matches = transform_pattern.findall(content)
            
            if matches:
                print(f"Found {len(matches)} transform properties in {filepath}")
                
                # Show the lines with transform
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if transform_pattern.search(line):
                        print(f"  Line {i}: {line.strip()}")
                print()
            else:
                print(f"No transform properties found in {filepath}")
                
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

# Check the main files that might have CSS
files_to_check = [
    'frontend/main_window.py',
    'frontend/widgets.py',
    'frontend/dialogs.py'
]

for filepath in files_to_check:
    check_file_for_transform(filepath)