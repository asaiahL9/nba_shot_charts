from pathlib import Path

# Create a single directory
Path("example_directory").mkdir(exist_ok=True)

# Create nested directories
Path("parent_directory/child_directory").mkdir(parents=True, exist_ok=True)
