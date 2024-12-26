import os
import ast
import pkg_resources

def find_imports(filename):
    with open(filename) as f:
        content = f.read()
    tree = ast.parse(content)
    imports = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    
    return imports

def generate_targeted_requirements(filename):
    # Get imports from the file
    imports = find_imports(filename)
    
    # Get installed packages that match the imports
    packages = []
    for dist in pkg_resources.working_set:
        if dist.project_name.lower() in {imp.lower() for imp in imports}:
            packages.append(f"{dist.project_name}=={dist.version}")
    
    # Write to requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(sorted(packages)))
    
    print(f"Requirements file created with {len(packages)} packages")

# Use it on your app.py
generate_targeted_requirements('app.py')