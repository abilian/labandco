#!/usr/bin/env python

import ast
import glob
from ast import ImportFrom, Import
from pathlib import Path
from typing import Any

import pkg_resources
import tomli

installed_packages = list(pkg_resources.working_set)
# debug(installed_packages)

package_to_files = {}

for p in installed_packages:
    # debug(p, vars(p), vars(p._provider), dir(p))
    # debug(p.PKG_INFO)
    # debug(p.module_path)

    metadata = p._provider
    base_dir = metadata.module_path
    egg_info = metadata.egg_info
    # debug(base_dir, egg_info)
    files = set()

    try:
        record = (Path(egg_info) / "RECORD").open()
    except FileNotFoundError:
        continue

    for line in record:
        filename = line.split(",")[0]
        files.add(filename)

    package_to_files[p._key] = sorted(files)


import_map = {}
for k, v in package_to_files.items():
    for f in v:
        if not f.endswith(".py"):
            continue
        if f.startswith("."):
            continue
        name = f.replace("/", ".")[0:-len(".py")]
        if name.endswith(".__init__"):
            name = name[0:-len(".__init__")]
        import_map[name] = k


# for k, v in sorted(list(import_map.items())):
#     print(f"{k} -> {v}")

#     # dist_name = os.path.splitext(os.path.basename(egg_info))[0]
#     # dist = pkg_resources.Distribution(base_dir, project_name=dist_name, metadata=metadata)
#     # debug(dist)
#     # print()
#
#
# # sys.exit()
# external_modules = set()

# for p in installed_packages:
#     if p.location.endswith("/site-packages"):
#         continue
#     debug(p, vars(p))
#     for m in pkgutil.iter_modules([p.location]):
#         debug(m)
#
#
# sys.exit()

class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()

    def visit_Import(self, node: Import) -> Any:
        for name in node.names:
            if isinstance(name, ast.alias):
                name = name.name
            self.imports.add(name)

    def visit_ImportFrom(self, node: ImportFrom) -> Any:
        if not node.module:
            return
        self.imports.add(node.module)


all_imports = set()

source_files = glob.glob("src/**/*.py", recursive=True)
for source_file in source_files:
    # print(f"Parsing {source_file}")
    tree = ast.parse(open(source_file).read(), source_file)

    visitor = Visitor()
    visitor.visit(tree)
    all_imports.update(visitor.imports)


imported_packages = set()
for name in all_imports:
    package = import_map.get(name)
    if not package:
        continue
    # print(f"{name} -> {package}")
    imported_packages.add(package)


pp = tomli.load(open("pyproject.toml", "rb"))
main_dependencies = set(
    pp["tool"]["poetry"]["dependencies"].keys()
)

print("Please check that these dependencies are actually used:\n")

for dep in sorted(main_dependencies - imported_packages):
    print(dep)
