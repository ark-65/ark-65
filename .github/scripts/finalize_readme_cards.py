from pathlib import Path
import re
import xml.etree.ElementTree as ET


CARD_DIR = Path("assets/cards")


def finalize_card(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    content = re.sub(
        r"(\.stagger\s*\{\s*)opacity:\s*0;",
        r"\1opacity: 1;",
        content,
    )
    content = "\n".join(line.rstrip() for line in content.splitlines()) + "\n"
    ET.fromstring(content)
    path.write_text(content, encoding="utf-8")


cards = sorted(CARD_DIR.glob("*.svg"))
if len(cards) != 10:
    raise RuntimeError(f"Expected 10 README cards, found {len(cards)}")

for card in cards:
    finalize_card(card)
    print(f"Finalized {card}")
