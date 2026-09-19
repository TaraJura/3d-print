#!/usr/bin/env python3
"""Vytvoří a ověří ZIP se 13 zbývajícími kusy; nepoužívá CAD ani tiskárnu.

Spuštění: python3 pripravit-zbytek-auticka.py
Přepisuje pouze zbytek-auticka.zip vedle tohoto skriptu.
"""

from collections import Counter
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "zbytek-auticka.zip"
EXPECTED = {
    "ram": 1,
    "kolo-zadni-ozubene": 1,
    "kolo-zadni": 1,
    "kolo-predni": 2,
    "osa-zadni": 1,
    "osa-predni": 1,
    "rozperka-kratka": 1,
    "rozperka-dlouha": 3,
    "pojistka": 2,
}
INSTRUCTIONS = """ZBYTEK AUTÍČKA — 13 JEDNOTLIVÝCH KUSŮ

Rozbalte ZIP a importujte všech 13 souborů STL do Anycubic Slicer Next
jako 13 samostatných objektů. Každý soubor už představuje jeden kus:
další kopie nevytvářejte. Měřítko všech dílů ponechte 100 % (rozměry v mm).

Vyberte tiskárnu Anycubic Kobra X s tryskou 0,4 mm, skutečně založenou
cívku PLA a odpovídající profil. Rozmístěte díly na podložku, zkontrolujte
jejich orientaci a po řezání prohlédněte vrstvy a případná upozornění.

Pastorek a zkušební vzorky do tohoto balíčku nepatří.
Toto jsou modely pro slicer, nikoli G-code ani připravená tisková úloha.
Balíček tisk sám nespouští. Manifest obsahuje původ a SHA-256 souborů.
"""


def make_package():
    report = json.loads((ROOT / "kontrola-modelu.json").read_text(encoding="utf-8"))
    parts = report["parts"]
    unexpected = set(parts) - set(EXPECTED) - {"pastorek"}
    if any(not name.startswith("vzorek") for name in unexpected):
        raise ValueError(f"Nové typy dílů vyžadují aktualizaci balíčku: {unexpected}")

    payloads = {}
    manifest = {"format_version": 1, "source_report": "kontrola-modelu.json",
                "stl_count": 13, "excluded": ["pastorek", "všechny vzorky"],
                "files": []}
    for kind, count in EXPECTED.items():
        part = parts[kind]
        if part["copies"] != count:
            raise ValueError(f"Nesouhlasí počet {kind}: {part['copies']} místo {count}")
        source_name = f"stl/{kind}.stl"
        if part["stl"] != source_name:
            raise ValueError(f"Neočekávaná cesta zdrojového STL: {part['stl']}")
        data = (ROOT / source_name).read_bytes()
        for copy in range(1, count + 1):
            suffix = f"-{copy}" if count > 1 else ""
            name = f"{len(payloads) + 1:02d}-{kind}{suffix}.stl"
            payloads[name] = data
            manifest["files"].append({"file": name, "source": source_name,
                                      "copy": copy, "bytes": len(data),
                                      "sha256": sha256(data).hexdigest()})
    if len(payloads) != 13:
        raise ValueError("Balíček musí obsahovat přesně 13 STL.")
    payloads["CTI-ME.txt"] = INSTRUCTIONS.encode("utf-8")
    payloads["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2)
                                 + "\n").encode("utf-8")

    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        for name, data in payloads.items():
            info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)

    # Ověření zabalených bajtů a počtů; geometrie STL se nemění ani znovu netestuje.
    package = buffer.getvalue()
    with ZipFile(BytesIO(package)) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(payloads):
            raise ValueError("ZIP neprošel kontrolou obsahu.")
        counts = Counter(item["source"] for item in manifest["files"])
        if counts != {f"stl/{kind}.stl": count for kind, count in EXPECTED.items()}:
            raise ValueError("Počty zabalených kusů nesouhlasí.")
        for item in manifest["files"]:
            if archive.read(item["file"]) != (ROOT / item["source"]).read_bytes():
                raise ValueError(f"Neshoda se zdrojem: {item['file']}")
    OUTPUT.write_bytes(package)
    if OUTPUT.read_bytes() != package:
        raise OSError("Uložený ZIP neodpovídá ověřeným datům.")
    print(json.dumps({"zip": str(OUTPUT), "stl_count": 13,
                      "part_types": len(EXPECTED), "bytes": len(package),
                      "sha256": sha256(package).hexdigest()}, ensure_ascii=False))


if __name__ == "__main__":
    make_package()
