"""Extract paragraph and table text from DOCX files without modifying them."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def paragraph_text(paragraph: ET.Element) -> str:
    texts = [node.text or "" for node in paragraph.findall(".//w:t", NS)]
    return "".join(texts).strip()


def table_text(table: ET.Element) -> str:
    rows = []
    for row in table.findall(".//w:tr", NS):
        cells = []
        for cell in row.findall("./w:tc", NS):
            parts = [paragraph_text(p) for p in cell.findall(".//w:p", NS)]
            cells.append(" ".join(part for part in parts if part))
        if any(cells):
            rows.append(" | ".join(cells))
    return "\n".join(rows)


def extract(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as docx:
        xml = docx.read("word/document.xml")
    root = ET.fromstring(xml)
    body = root.find("w:body", NS)
    if body is None:
        return []
    output = []
    for child in body:
        if child.tag.endswith("}p"):
            text = paragraph_text(child)
            if text:
                output.append(text)
        elif child.tag.endswith("}tbl"):
            text = table_text(child)
            if text:
                output.append("[TABLE]\n" + text)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", nargs="+")
    parser.add_argument("--out_dir", default="docs/docx_extracts")
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for item in args.docx:
        source = Path(item)
        lines = extract(source)
        out = out_dir / f"{source.stem}.txt"
        out.write_text("\n\n".join(lines), encoding="utf-8")
        print(f"{source}: {len(lines)} blocks -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
