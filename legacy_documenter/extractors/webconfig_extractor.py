from pathlib import Path
import re
import xml.etree.ElementTree as ET


SECRET_KEYS = re.compile(r"(?i)\b(password|pwd|user id|uid)\s*=\s*[^;]+")


def _strip_namespace(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


class WebConfigExtractor:
    def extract(self, path: str | Path, root: str | Path | None = None) -> dict:
        file_path = Path(path)
        rel = str(file_path.relative_to(root)) if root else str(file_path)
        tree = ET.parse(file_path)
        xml_root = tree.getroot()
        result = {
            "path": rel,
            "appSettings": [],
            "connectionStrings": [],
            "assemblies": [],
            "authentication": None,
            "authorization": [],
            "compilation": None,
            "httpHandlers": [],
            "httpModules": [],
            "sessionState": None,
            "customErrors": None,
            "pages": None,
            "controls": [],
            "impersonation": None,
            "assemblyBinding": [],
        }
        for node in xml_root.iter():
            tag = _strip_namespace(node.tag)
            if tag == "appSettings":
                result["appSettings"].extend(child.attrib for child in node if _strip_namespace(child.tag) == "add")
            elif tag == "connectionStrings":
                for child in node:
                    if _strip_namespace(child.tag) == "add":
                        item = dict(child.attrib)
                        if "connectionString" in item:
                            item["connectionString"] = self.sanitize_connection_string(item["connectionString"])
                        result["connectionStrings"].append(item)
            elif tag == "assemblies":
                result["assemblies"].extend(child.attrib for child in node if _strip_namespace(child.tag) == "add")
            elif tag in {"authentication", "compilation", "sessionState", "customErrors", "pages", "impersonation"}:
                result[tag] = dict(node.attrib)
            elif tag == "authorization":
                result["authorization"].extend({**child.attrib, "tag": _strip_namespace(child.tag)} for child in node)
            elif tag == "httpHandlers":
                result["httpHandlers"].extend(child.attrib for child in node)
            elif tag == "httpModules":
                result["httpModules"].extend(child.attrib for child in node)
            elif tag == "controls":
                result["controls"].extend(child.attrib for child in node)
            elif tag == "assemblyBinding":
                result["assemblyBinding"].extend(child.attrib for child in node)
        return result

    def sanitize_connection_string(self, value: str) -> str:
        return SECRET_KEYS.sub(lambda m: m.group(1) + "=********", value)
