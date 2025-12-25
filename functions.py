import csv
import re
import requests
from bs4 import BeautifulSoup

## ff

def scrape_antonyms_find(url: str, headers: dict | None = None) -> list[dict]:
    """
    Mesma ideia da versão anterior, mas usando apenas
    .find() e .find_all() em vez de .select().
    """
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "lxml")

    # Cada bloco está em <div class="content-detail">
    blocks = soup.find_all("div", class_="content-detail")

    results = []
    for block in blocks:
        # Número do bloco
        num_tag = block.find("em", class_="ant-number")
        if not num_tag:
            continue
        number = int(num_tag.text.strip())

        # Contexto (pode não existir)
        tip_tag = block.find("div", class_="content-detail--subtitle")
        context_tip = (
            re.sub(r":\s*$", "", tip_tag.text.strip()) if tip_tag else None
        )

        # Palavras: dentro de <p class="ant-list">
        p_list = block.find("p", class_="ant-list")
        if not p_list:
            continue
        word_tags = p_list.find_all(["a", "span"])
        words = [
            re.sub(r"[.,;]\s*$", "", w.get_text(strip=True))
            for w in word_tags
            if w.get_text(strip=True)
        ]

        results.append(
            {
                "context_number": number,
                "context_tip": context_tip,
                "related_words": words,
            }
        )

    return results


def save_antonyms_csv(data: list[dict], filename: str = "antonyms.csv") -> None:
    if not data:
        print("Nenhum dado para salvar.")
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["context_number", "context_tip", "related_words"],
        )
        writer.writeheader()
        for row in data:
            writer.writerow(
                {
                    "context_number": row["context_number"],
                    "context_tip": row["context_tip"] or "",
                    "related_words": ", ".join(row["related_words"]),
                }
            )
    print(f"CSV salvo em {filename}")
