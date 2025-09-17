import os
import sys

# Ensure project root is on sys.path so `frontend` package can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
	sys.path.insert(0, ROOT)

from frontend.styles import topic_button_style

print('one-arg:')
print(topic_button_style('#6c757d')[:200])
print('\n---\n')
print('two-arg:')
print(topic_button_style('#6c757d', '#3498db')[:200])
print('\n---\n')
print('tuple-arg:')
print(topic_button_style(('#6c757d', '#3498db'))[:200])
