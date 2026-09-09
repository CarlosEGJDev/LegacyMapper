from pathlib import Path
import xml.etree.ElementTree as ET

from legacy_documenter.models import Project


def _strip_namespace(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _children_by_name(root: ET.Element, name: str) -> list[ET.Element]:
    return [node for node in root.iter() if _strip_namespace(node.tag) == name]


class VBProjExtractor:
    def extract(self, path: str | Path, root: str | Path | None = None) -> Project:
        file_path = Path(path)
        tree = ET.parse(file_path)
        xml_root = tree.getroot()
        rel = str(file_path.relative_to(root)) if root else str(file_path)
        props = self._properties(xml_root)
        project = Project(
            name=props.get("ProjectName") or props.get("AssemblyName") or file_path.stem,
            path=rel,
            assembly_name=props.get("AssemblyName"),
            root_namespace=props.get("RootNamespace"),
            target_framework=props.get("TargetFrameworkVersion"),
            output_type=props.get("OutputType"),
            configurations=props,
        )
        for item in _children_by_name(xml_root, "ProjectReference"):
            project.project_references.append(
                {
                    "include": item.attrib.get("Include", ""),
                    "name": self._child_text(item, "Name"),
                    "project": self._child_text(item, "Project"),
                }
            )
        for item in _children_by_name(xml_root, "Reference"):
            project.assembly_references.append(
                {
                    "include": item.attrib.get("Include", ""),
                    "hint_path": self._child_text(item, "HintPath"),
                }
            )
        project.compile_items = [item.attrib.get("Include", "") for item in _children_by_name(xml_root, "Compile")]
        project.content_items = [item.attrib.get("Include", "") for item in _children_by_name(xml_root, "Content")]
        return project

    def _properties(self, root: ET.Element) -> dict:
        wanted = {"ProjectName", "AssemblyName", "RootNamespace", "TargetFrameworkVersion", "OutputType"}
        return {
            _strip_namespace(node.tag): (node.text or "").strip()
            for node in root.iter()
            if _strip_namespace(node.tag) in wanted and node.text
        }

    def _child_text(self, node: ET.Element, name: str) -> str | None:
        for child in node:
            if _strip_namespace(child.tag) == name:
                return (child.text or "").strip() or None
        return None
