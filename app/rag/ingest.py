import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import chromadb
import httpx
from bs4 import BeautifulSoup
from openai import OpenAI

from app.config import settings


GETNET_START_URLS = [
    "https://site.getnet.com.br/produtos-fisicos/",
    "https://site.getnet.com.br/maquininha/get-classica/",
    "https://site.getnet.com.br/maquininha/get-smart/",
    "https://site.getnet.com.br/taxas/",
    "https://site.getnet.com.br/conta-digital/",
]

@dataclass
class Page:
    url: str
    title: str
    text: str


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_page(url: str) -> Page | None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 GetnetAgentChallenge/1.0"
        )
    }

    try:
        response = httpx.get(
            url,
            headers=headers,
            follow_redirects=True,
            timeout=20,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"[WARN] Could not download {url}: {exc}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(
        ["script", "style", "noscript", "svg", "header", "footer"]
    ):
        element.decompose()

    title = soup.title.get_text(strip=True) if soup.title else url
    text = clean_text(soup.get_text(" ", strip=True))

    if len(text) < 200:
        print(f"[WARN] Not enough text found at {url}")
        return None

    return Page(
        url=url,
        title=title,
        text=text,
    )


def find_getnet_links(url: str, max_links: int = 20) -> list[str]:
    headers = {
        "User-Agent": "Mozilla/5.0 GetnetAgentChallenge/1.0"
    }

    try:
        response = httpx.get(
            url,
            headers=headers,
            follow_redirects=True,
            timeout=20,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    base_domain = urlparse(url).netloc
    links = set()

    for anchor in soup.find_all("a", href=True):
        link = urljoin(url, anchor["href"])
        parsed = urlparse(link)

        if parsed.scheme not in {"http", "https"}:
            continue

        if parsed.netloc != base_domain:
            continue

        clean_url = link.split("#")[0].rstrip("/")

        links.add(clean_url)

        if len(links) >= max_links:
            break

    return sorted(links)


def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= chunk_size:
            current += (" " if current else "") + sentence
            continue

        if current:
            chunks.append(current.strip())

        overlap_text = current[-overlap:] if current else ""

        current = (
            overlap_text + " " + sentence
        ).strip()

    if current:
        chunks.append(current.strip())

    return chunks

def ingest_page(
    page: Page,
    collection,
    openai_client: OpenAI,
) -> int:
    chunks = chunk_text(page.text)

    if not chunks:
        return 0

    embeddings_response = openai_client.embeddings.create(
        model=settings.embedding_model,
        input=chunks,
    )

    embeddings = [
        item.embedding
        for item in embeddings_response.data
    ]

    ids = [
        f"{abs(hash(page.url))}-{index}"
        for index in range(len(chunks))
    ]

    metadatas = [
        {
            "source": page.url,
            "title": page.title,
            "chunk": index,
        }
        for index in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def run_ingestion():
    print("Starting Getnet knowledge-base ingestion...")

    openai_client = OpenAI(
        api_key=settings.openai_api_key
    )

    chroma_client = chromadb.PersistentClient(
        path=settings.vector_db_path
    )

    collection = chroma_client.get_or_create_collection(
        name="getnet_knowledge"
    )

    urls = {
        normalize_url(url)
        for url in GETNET_START_URLS
    }

    for start_url in GETNET_START_URLS:
        urls.update(
            normalize_url(url)
            for url in find_getnet_links(
                start_url,
                max_links=10,
            )
        )

    print(f"Found {len(urls)} candidate URLs.")

    total_chunks = 0
    successful_pages = 0

    for index, url in enumerate(sorted(urls), start=1):
        print(f"[{index}/{len(urls)}] {url}")

        page = extract_page(url)

        if page is None:
            continue

        chunks = ingest_page(
            page,
            collection,
            openai_client,
        )

        successful_pages += 1
        total_chunks += chunks

        print(
            f"  -> {chunks} chunks "
            f"({len(page.text)} characters)"
        )

    print()
    print("Ingestion complete.")
    print(f"Pages ingested: {successful_pages}")
    print(f"Chunks stored: {total_chunks}")
    print(f"Vector DB: {settings.vector_db_path}")

def normalize_url(url: str) -> str:
    return url.split("#")[0].rstrip("/")

if __name__ == "__main__":
    run_ingestion()