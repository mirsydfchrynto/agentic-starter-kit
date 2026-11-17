#!/usr/bin/env -S uv run --with requests --with python-docx
"""Verify BibTeX / proposal bibliography entries against Crossref, OpenAlex, and live URLs.

Checks 1:1 citation ordering in an optional DOCX manuscript against the parsed
.bib file, verifies DOIs via Crossref REST API (falling back to OpenAlex),
and checks HTTP status of OJS/publisher URLs for entries without a DOI.
"""

import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path

import requests


def parse_bib(bib_path: Path) -> list[dict]:
    raw = bib_path.read_text(encoding="utf-8")
    blocks = re.split(r"@(?:article|book|inproceedings|misc|proceedings)\s*\{", raw)[1:]
    etypes = re.findall(r"@(article|book|inproceedings|misc|proceedings)\s*\{", raw)
    entries = []
    for idx, (etype, blk) in enumerate(zip(etypes, blocks), start=1):
        km = re.match(r"\s*([^,\s]+)\s*,", blk)
        key = km.group(1) if km else f"entry_{idx}"
        nm = re.fullmatch(r"ref_(\d+)", key)
        num = int(nm.group(1)) if nm else idx
        item = {"num": num, "key": key, "etype": etype}
        for field in ("author", "title", "journal", "booktitle", "publisher", "year", "doi", "isbn", "url"):
            fm = re.search(rf"\b{field}\s*=\s*\{{(.*?)\}}", blk, re.DOTALL)
            item[field] = re.sub(r"\s+", " ", fm.group(1)).strip() if fm else ""
        entries.append(item)
    return entries


def _vis_text(p) -> str:
    """Extract all visible <w:t> text inside a paragraph, including hyperlinks, excluding field instrText."""
    return "".join(node.text or "" for node in p._p.xpath(".//w:t"))


def check_docx_citations(docx_path: Path, bib_count: int) -> dict:
    from docx import Document

    doc = Document(str(docx_path))
    body_texts: list[str] = []
    for p in doc.paragraphs:
        txt = _vis_text(p)
        low = txt.strip().lower()
        if (p.style.name == "Heading 1" and "daftar pustaka" in low) or re.match(r"^(?:daftar pustaka|ringkasan matriks)\b", low):
            break
        body_texts.append(txt)

    # Extract tables located inside the main document before bibliography paragraphs
    seen_texts = set(body_texts)
    for t in doc.tables:
        t_first = " ".join(_vis_text(p) for p in t.rows[0].cells[0].paragraphs).lower() if t.rows else ""
        if "ringkasan matriks" in t_first:
            continue
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    ct = _vis_text(p)
                    if ct and ct not in seen_texts:
                        body_texts.append(ct)

    cited_seq: list[int] = []
    for txt in body_texts:
        for m in re.finditer(r"\[(\d+)\]", txt):
            val = int(m.group(1))
            if 1 <= val <= max(bib_count, 200):
                cited_seq.append(val)

    first_seen = []
    seen_set = set()
    for n in cited_seq:
        if n not in seen_set:
            seen_set.add(n)
            first_seen.append(n)

    missing_in_text = [n for n in range(1, bib_count + 1) if n not in seen_set]
    non_ascending = []
    max_so_far = 0
    for n in first_seen:
        if n < max_so_far:
            non_ascending.append(n)
        max_so_far = max(max_so_far, n)

    return {
        "total_occurrences": len(cited_seq),
        "unique_cited": len(seen_set),
        "bib_count": bib_count,
        "missing_in_text": missing_in_text,
        "non_ascending_first_appearance": non_ascending,
    }


def verify_entry_online(item: dict, timeout: float = 12.0) -> tuple[str, str]:
    headers = {"User-Agent": "ProposalSkripsiBibVerifier/2.0 (mailto:academic-verify@example.org)"}
    doi = item.get("doi", "").strip()
    url = item.get("url", "").strip()
    isbn = item.get("isbn", "").strip()

    if doi:
        clean_doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
        try:
            r = requests.get(f"https://api.crossref.org/works/{urllib.parse.quote(clean_doi, safe='')}", headers=headers, timeout=timeout)
            if r.status_code == 200:
                msg = r.json().get("message", {})
                cr_title = " ".join(msg.get("title", [""])).lower()[:50]
                return "CROSSREF_OK", cr_title
        except requests.RequestException:
            pass
        try:
            r2 = requests.get(f"https://api.openalex.org/works/https://doi.org/{clean_doi}", headers=headers, timeout=timeout)
            if r2.status_code == 200:
                return "OPENALEX_OK", (r2.json().get("title") or "").lower()[:50]
        except requests.RequestException:
            pass
        if not url:
            return "DOI_FAILED", clean_doi

    if url:
        try:
            r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            if 200 <= r.status_code < 400:
                return f"URL_HTTP_{r.status_code}", r.url[:60]
            return f"URL_HTTP_{r.status_code}", url[:60]
        except requests.RequestException as exc:
            return "URL_ERROR", str(exc)[:60]

    if isbn or item.get("etype") == "book":
        return "BOOK_ISBN" if isbn else "BOOK_NO_ISBN", isbn or item.get("publisher", "")

    return "UNVERIFIABLE", "no doi/url/isbn"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify thesis .bib references and 1:1 DOCX IEEE citation order.")
    parser.add_argument("bib_path", type=Path, help="Path to daftar-pustaka.bib")
    parser.add_argument("--docx", type=Path, default=None, help="Optional .docx file to check 1:1 ascending [1..N] citations")
    parser.add_argument("--offline", action="store_true", help="Skip live HTTP Crossref/OpenAlex/OJS checks")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional path to save detailed JSON report")
    args = parser.parse_args()

    if not args.bib_path.exists():
        print(f"ERROR: BibTeX file not found: {args.bib_path}", file=sys.stderr)
        return 1

    entries = parse_bib(args.bib_path)
    report: dict = {"bib_entries": len(entries), "checks": [], "docx_citations": None}

    if args.docx and args.docx.exists():
        report["docx_citations"] = check_docx_citations(args.docx, len(entries))

    if not args.offline:
        counts: dict[str, int] = {}
        for item in entries:
            status, detail = verify_entry_online(item)
            counts[status] = counts.get(status, 0) + 1
            report["checks"].append({"num": item["num"], "key": item["key"], "status": status, "detail": detail})
        report["summary_counts"] = counts
    else:
        report["summary_counts"] = {"OFFLINE_STRUCTURAL_ONLY": len(entries)}

    print(json.dumps({"bib_entries": report["bib_entries"], "summary_counts": report["summary_counts"], "docx_citations": report["docx_citations"]}, indent=2))
    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    bad = [c for c in report["checks"] if c["status"] in ("DOI_FAILED", "URL_ERROR", "UNVERIFIABLE") or c["status"].startswith("URL_HTTP_4") or c["status"].startswith("URL_HTTP_5")]
    cit_ok = True
    if report["docx_citations"]:
        cit_ok = not report["docx_citations"]["missing_in_text"] and not report["docx_citations"]["non_ascending_first_appearance"]
    return 0 if (not bad and cit_ok) else 2


if __name__ == "__main__":
    raise SystemExit(main())
