# check_widgets_css.py
import re

def check_widgets_for_css():
    """Check widgets.py for problematic CSS"""
    with open('frontend/widgets.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Check for transform properties
        transform_pattern = re.compile(r'transform\s*:')
        if transform_pattern.search(content):
            print("Found transform properties in widgets.py")
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if transform_pattern.search(line):
                    print(f"  Line {i}: {line.strip()}")
        else:
            print("No transform properties found in widgets.py")
            
        # Check for box-shadow properties
        box_shadow_pattern = re.compile(r'box-shadow\s*:')
        if box_shadow_pattern.search(content):
            print("Found box-shadow properties in widgets.py")
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if box_shadow_pattern.search(line):
                    print(f"  Line {i}: {line.strip()}")
        else:
            print("No box-shadow properties found in widgets.py")

check_widgets_for_css()