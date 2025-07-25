from __future__ import annotations

"""Parses a very small subset of Synapse XML configuration into mediator objects."""

from pathlib import Path
from typing import Dict, List

import xml.etree.ElementTree as ET

from simple_synapse.mediators import FilterMediator, LogMediator, Mediator, SendMediator


class Sequence:
    """A named collection of mediators executed in order."""

    def __init__(self, name: str, mediators: List[Mediator]):
        self.name = name
        self.mediators = mediators

    async def process(self, ctx):  # noqa: D401
        for m in self.mediators:
            await m.mediate(ctx)


class ConfigLoader:
    """Loads a directory full of `*.xml` sequences."""

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.sequences: Dict[str, Sequence] = {}

    # Public API ----------------------------------------------------------
    def refresh(self) -> None:
        """(Re-)read all XML files into memory."""
        self.sequences.clear()
        for xml_file in self.directory.glob("*.xml"):
            sequence = self._parse_sequence(xml_file)
            self.sequences[sequence.name] = sequence

    def get(self, name: str) -> Sequence:
        return self.sequences[name]

    # Internal -----------------------------------------------------------
    def _parse_sequence(self, xml_path: Path) -> Sequence:
        root = ET.parse(xml_path).getroot()
        if root.tag != "sequence":
            raise ValueError(f"Root element of {xml_path} must be <sequence>")
        name = root.attrib.get("name", xml_path.stem)
        mediators = [self._parse_mediator(child) for child in root]
        return Sequence(name, mediators)

    def _parse_mediator(self, elem):
        tag = elem.tag.lower()
        if tag == "log":
            return LogMediator(level=elem.attrib.get("level", "INFO"), message=elem.attrib.get("message"))
        if tag == "send":
            url = elem.attrib["url"]
            return SendMediator(url)
        if tag == "filter":
            expr = elem.attrib["expr"]
            nested = [self._parse_mediator(child) for child in elem]
            return FilterMediator(expr, nested)
        raise ValueError(f"Unknown mediator type: {tag}")