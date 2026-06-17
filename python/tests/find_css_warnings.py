# find_css_warnings.py
import os
import re

def find_css_properties(directory, properties):
    """Find CSS properties that might cause warnings"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        for prop in properties:
                            pattern = re.compile(rf'{prop}\s*:')
                            if pattern.search(content):
                                print(f"Found '{prop}' in {filepath}")
                                # Show the lines with this property
                                lines = content.split('\n')
                                for i, line in enumerate(lines, 1):
                                    if pattern.search(line):
                                        print(f"  Line {i}: {line.strip()}")
                                print()
                                break
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

if __name__ == "__main__":
    # Properties that commonly cause warnings in Qt
    problematic_properties = [
        'transform',
        'box-shadow',
        'text-shadow',
        'transition',
        'animation',
        'filter',
        'backdrop-filter',
        'gradient',
        'flex',
        'grid'
    ]
    
    print("Searching for problematic CSS properties...")
    find_css_properties('.', problematic_properties)