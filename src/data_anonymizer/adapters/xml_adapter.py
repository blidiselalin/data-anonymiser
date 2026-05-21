"""XML format adapter."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from data_anonymizer.adapters.base import DataFormatAdapter
from data_anonymizer.core.methods import apply_method
from data_anonymizer.core.rules import FieldRule, method_options_for
from data_anonymizer.models import FieldInfo


def _local_name(tag: str) -> str:
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1]
    return tag


def _attribute_field_id(parent_tag: str, attr_name: str) -> str:
    return f"@{parent_tag}/{_local_name(attr_name)}"


class XmlAdapter(DataFormatAdapter):
    format_id = "xml"
    display_name = "XML"
    extensions = (".xml",)

    def __init__(self) -> None:
        super().__init__()
        self._tree: ET.ElementTree | None = None
        self.root: ET.Element | None = None

    @classmethod
    def supports(cls, path: Path) -> bool:
        return path.suffix.lower() in cls.extensions

    def load(self, path: Path) -> None:
        self._source_path = Path(path)
        self._tree = ET.parse(self._source_path)
        self.root = self._tree.getroot()

    def discover_fields(self, *, include_empty: bool = False) -> dict[str, FieldInfo]:
        if self.root is None:
            raise RuntimeError("Document not loaded")
        fields: dict[str, FieldInfo] = {}
        for elem in self.root.iter():
            local_tag = _local_name(elem.tag)

            if elem is not self.root:
                text = (elem.text or "").strip()
                if text or include_empty:
                    self._register_field(fields, local_tag, text if text else None)

            for attr_name, attr_value in elem.attrib.items():
                value = attr_value.strip()
                if not value and not include_empty:
                    continue
                field_id = _attribute_field_id(local_tag, attr_name)
                self._register_field(fields, field_id, value if value else None)

        return dict(sorted(fields.items(), key=lambda kv: kv[0]))

    def header_snapshot(self, max_depth: int = 4) -> dict[str, list[str]]:
        if self.root is None:
            return {}
        header_root = self.root.find("FEED_HEADER")
        if header_root is None:
            header_root = self.root
        snapshot: dict[str, list[str]] = {}

        def walk(elem: ET.Element, depth: int) -> None:
            if depth > max_depth:
                return
            local_tag = _local_name(elem.tag)
            text = (elem.text or "").strip()
            if text:
                bucket = snapshot.setdefault(local_tag, [])
                if text not in bucket and len(bucket) < 3:
                    bucket.append(text)
            for attr_name, attr_value in elem.attrib.items():
                value = attr_value.strip()
                if not value:
                    continue
                field_id = _attribute_field_id(local_tag, attr_name)
                bucket = snapshot.setdefault(field_id, [])
                if value not in bucket and len(bucket) < 3:
                    bucket.append(value)
            for child in elem:
                walk(child, depth + 1)

        walk(header_root, 0)
        return dict(sorted(snapshot.items()))

    def anonymize(self, rules: list[FieldRule], *, salt: str = "", skip_empty: bool = True) -> int:
        if self.root is None:
            raise RuntimeError("Document not loaded")
        rule_map = {r.field_id: r for r in rules}
        changed = 0
        for elem in self.root.iter():
            local_tag = _local_name(elem.tag)

            rule = rule_map.get(local_tag)
            if rule is not None:
                text = elem.text or ""
                if not (skip_empty and not text.strip()):
                    opts = dict(rule.options or method_options_for(str(rule.method)))
                    opts.setdefault("salt", salt)
                    opts.setdefault("namespace", local_tag)
                    elem.text = apply_method(rule.method, text, **opts)
                    changed += 1

            for attr_name, attr_value in list(elem.attrib.items()):
                field_id = _attribute_field_id(local_tag, attr_name)
                rule = rule_map.get(field_id)
                if rule is None:
                    continue
                if skip_empty and not attr_value.strip():
                    continue
                opts = dict(rule.options or method_options_for(str(rule.method)))
                opts.setdefault("salt", salt)
                opts.setdefault("namespace", field_id)
                elem.attrib[attr_name] = apply_method(rule.method, attr_value, **opts)
                changed += 1
        return changed

    def to_text(self) -> str:
        if self._tree is None or self.root is None:
            raise RuntimeError("Document not loaded")
        ET.indent(self._tree, space="    ")
        body = ET.tostring(self.root, encoding="unicode")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + body

    def export(self, path: Path) -> None:
        Path(path).write_text(self.to_text(), encoding="utf-8")

    @staticmethod
    def _register_field(
        fields: dict[str, FieldInfo],
        field_id: str,
        sample: str | None,
    ) -> None:
        info = fields.get(field_id)
        if info is None:
            info = FieldInfo(field_id=field_id, count=0)
            fields[field_id] = info
        info.count += 1
        info.add_sample(sample)
