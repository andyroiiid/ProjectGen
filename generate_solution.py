# Copyright 2025 Andrew Huang. All Rights Reserved.

from argparse import ArgumentParser
from pathlib import Path
from xml.etree import ElementTree
import json


def create_property_group(project: ElementTree.Element, properties: dict[str, str]):
    property_group = ElementTree.SubElement(project, "PropertyGroup")
    for key, value in properties.items():
        ElementTree.SubElement(property_group, key).text = value


def create_item_group(project: ElementTree.Element, items: list[tuple[str, dict[str, str]]]):
    item_group = ElementTree.SubElement(project, "ItemGroup")
    for item, attributes in items:
        ElementTree.SubElement(item_group, item, **attributes)


def pretty_write_xml(root: ElementTree.Element, path: Path):
    tree = ElementTree.ElementTree(root)
    ElementTree.indent(tree)
    tree.write(path)


class SolutionGenerator:
    def __init__(self, build_dir: Path):
        self.build_dir = build_dir
        self.project_files = set()
        build_dir.mkdir(exist_ok=True)

    def generate_projects(self, source_dir: Path):
        for project_def_file in source_dir.rglob("*.cslib"):
            assert project_def_file.is_file()
            self.generate_project(project_def_file)

    def generate_project(self, project_def_file: Path):
        with open(project_def_file, "r") as f:
            project_def = json.load(f)

        project_name = project_def_file.stem
        project_dir = project_def_file.parent
        project_file = self.build_dir / f"{project_name}.csproj"

        assert project_file not in self.project_files
        self.project_files.add(project_file)

        project = ElementTree.Element("Project", Sdk="Microsoft.NET.Sdk")

        create_property_group(project, {
            "TargetFramework": "net9.0",
            "ImplicitUsings": "enable",
            "Nullable": "enable",
            "AppendTargetFrameworkToOutputPath": "false",
            "AppendRuntimeIdentifierToOutputPath": "false",
        })

        items = [
            ("Compile", {"Include": str(project_dir / "*.cs")}),
        ]

        references = project_def.get("references")
        if references:
            for reference in references:
                items.append(("ProjectReference", {"Include": f"{reference}.csproj"}))

        create_item_group(project, items)

        pretty_write_xml(project, project_file)

    def generate_solution(self, solution_file):
        solution = ElementTree.Element('Solution')

        for project in self.project_files:
            ElementTree.SubElement(solution, 'Project', Path=str(project), Type="Classic C#")

        pretty_write_xml(solution, solution_file)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("solution_file", type=Path)
    parser.add_argument("source_dir", type=Path)
    args = parser.parse_args()

    generator = SolutionGenerator(Path.cwd() / "Build")
    generator.generate_projects(args.source_dir.absolute())
    generator.generate_solution(args.solution_file.absolute())
