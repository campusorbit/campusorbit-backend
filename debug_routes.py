"""Debug script to list all registered routes."""
from app.main import app

print("\nRegistered Routes:")
print("=" * 80)
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        methods = ', '.join(route.methods)
        print(f"{methods:20} {route.path}")
print("=" * 80)
