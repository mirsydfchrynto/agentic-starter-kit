#!/usr/bin/env -S uv run --with python-docx --with pypdf --with numpy --with requests
"""Audit thesis proposal DOCX/PDF formatting, PII, Indonesian AI tells, full-body perplexity,
bib-abstract anti-patchwriting overlap, n-gram cross-overlap, and Turnitin PDF export.
"""

import argparse
import html
import json
import math
import os
import re
import statistics
import sys
import urllib.parse
from pathlib import Path

from docx import Document
from pypdf import PdfReader, PdfWriter

INDONESIAN_AI_TELLS = [
    r"\bperlu dicatat\b",
    r"\bperlu diperhatikan\b",
    r"\bbukan sekadar\b",
    r"\bbukanlah sekadar\b",
    r"\bdi era digital(?: saat ini)?\b",
    r"\bdalam era industri\b",
    r"\bdapat disimpulkan bahwa\b",
    r"\bsangatlah penting\b",
    r"\bsecara keseluruhan\b",
    r"\bmenandai tonggak\b",
    r"\bmemainkan peran penting\b",
    r"\brevolusioner\b",
    r"\bholistik\b",
    r"\bkomprehensif\b",
    r"\brobust\b",
    r"\bleverage\b",
    r"\bstreamline\b",
]


def _vis_text(p) -> str:
    """Extract visible paragraph text including hyperlinks and tabs, excluding field instrText."""
    return "".join(
        " " if node.tag.endswith("}tab") else (node.text or "")
        for node in p._p.xpath(".//w:t | .//w:tab")
    )


def _norm_section(heading_text: str) -> str:
    low = re.sub(r"\s+", " ", heading_text).strip().lower()
    if "ringkasan" in low:
        return "RINGKASAN"
    if re.search(r"^(?:1\.|bab\s+i\b)\s*pendahuluan", low):
        return "BAB I"
    if re.search(r"^(?:2\.|bab\s+ii\b)\s*tinjauan", low):
        return "BAB II"
    if re.search(r"^(?:3\.|bab\s+iii\b)\s*metode", low):
        return "BAB III"
    if "daftar pustaka" in low:
        return "DAFTAR PUSTAKA"
    if "lampiran" in low:
        return "LAMPIRAN"
    return heading_text.strip()[:30]


def extract_docx_data(docx_path: Path) -> tuple[dict, str, list[tuple[str, int, str]]]:
    doc = Document(str(docx_path))
    all_texts: list[str] = []
    main_narrative_paras: list[str] = []
    sectioned_paras: list[tuple[str, int, str]] = []
    spacing_bad_main: list[tuple[float, str]] = []
    backtick_hits = 0
    asterisk_hits = 0
    nik_hits = 0
    cur_sec = "FRONT"

    for idx, p in enumerate(doc.paragraphs):
        txt = _vis_text(p)
        if p.style.name == "Heading 1":
            cur_sec = _norm_section(txt)

        all_texts.append(txt)
        backtick_hits += txt.count("`")
        asterisk_hits += txt.count("**")
        nik_hits += len(re.findall(r"\b\d{16}\b", txt))

        clean = re.sub(r"\s+", " ", txt).strip()
        if cur_sec in ("RINGKASAN", "BAB I", "BAB II", "BAB III") and p.style.name == "Normal" and len(clean) >= 80:
            sectioned_paras.append((cur_sec, idx, clean))
        if cur_sec in ("BAB I", "BAB II", "BAB III") and p.style.name == "Normal" and len(clean) >= 120:
            main_narrative_paras.append(clean)
            ls = p.paragraph_format.line_spacing
            if ls is None or abs(float(ls) - 1.5) > 0.02:
                spacing_bad_main.append((float(ls) if ls else 0.0, clean[:50]))

    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                txt = " ".join(_vis_text(cp) for cp in cell.paragraphs)
                all_texts.append(txt)
                backtick_hits += txt.count("`")
                asterisk_hits += txt.count("**")
                nik_hits += len(re.findall(r"\b\d{16}\b", txt))

    margins_ok = [
        {
            "section": idx,
            "w_cm": round(sec.page_width.cm, 2),
            "h_cm": round(sec.page_height.cm, 2),
            "top_cm": round(sec.top_margin.cm, 2),
            "left_cm": round(sec.left_margin.cm, 2),
            "bottom_cm": round(sec.bottom_margin.cm, 2),
            "right_cm": round(sec.right_margin.cm, 2),
        }
        for idx, sec in enumerate(doc.sections, start=1)
    ]

    joined = "\n".join(main_narrative_paras) if main_narrative_paras else "\n".join(all_texts)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", joined) if len(s.split()) >= 4]
    lengths = [len(s.split()) for s in sents]
    mean_w = statistics.mean(lengths) if lengths else 0.0
    std_w = statistics.stdev(lengths) if len(lengths) > 1 else 0.0
    cv = (std_w / mean_w) if mean_w else 0.0
    pct_over_35 = (sum(1 for l in lengths if l > 35) / len(lengths) * 100.0) if lengths else 0.0

    low_all = "\n".join(all_texts).lower()
    tells_found = {pat: len(re.findall(pat, low_all)) for pat in INDONESIAN_AI_TELLS if re.search(pat, low_all)}

    metrics = {
        "paragraphs_total": len(doc.paragraphs),
        "main_body_narrative_paragraphs": len(main_narrative_paras),
        "tables_total": len(doc.tables),
        "non_1_5_main_body_paragraphs": len(spacing_bad_main),
        "leftover_backticks": backtick_hits,
        "leftover_double_asterisks": asterisk_hits,
        "nik_16digit_hits": nik_hits,
        "sentence_count": len(lengths),
        "sentence_mean_words": round(mean_w, 2),
        "sentence_cv_burstiness": round(cv, 3),
        "sentences_over_35w_pct": round(pct_over_35, 1),
        "ai_slop_tells": tells_found,
        "sections_geometry": margins_ok,
    }
    return metrics, "\n".join(all_texts), sectioned_paras


def _ngrams(text: str, n: int) -> set[tuple[str, ...]]:
    toks = re.findall(r"[a-z0-9]+", text.lower())
    if len(toks) < n:
        return set()
    return {tuple(toks[i : i + n]) for i in range(len(toks) - n + 1)}


def compute_ngram_overlap(text_a: str, text_b: str, n: int = 5) -> float:
    grams_a = _ngrams(text_a, n)
    grams_b = _ngrams(text_b, n)
    if not grams_a or not grams_b:
        return 0.0
    return round(len(grams_a & grams_b) / len(grams_a) * 100.0, 2)


def read_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def export_turnitin_pdf(pdf_path: Path, out_pdf: Path, marker: str) -> dict:
    reader = PdfReader(str(pdf_path))
    marker_low = marker.lower()
    cutoff = len(reader.pages)
    for idx, page in enumerate(reader.pages):
        txt = re.sub(r"\s+", " ", (page.extract_text() or "")).lower()
        if idx >= 5 and marker_low in txt:
            cutoff = idx
            break
    writer = PdfWriter()
    for p in reader.pages[:cutoff]:
        writer.add_page(p)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    with out_pdf.open("wb") as f:
        writer.write(f)
    return {"source_pages": len(reader.pages), "turnitin_pages": cutoff, "output": str(out_pdf)}


def score_indonesian_perplexity_full(
    sectioned_paras: list[tuple[str, int, str]],
    model_id: str = "cahya/gpt2-small-indonesian-522M",
) -> dict:
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    try:
        tok = AutoTokenizer.from_pretrained(model_id, local_files_only=True)
        mdl = AutoModelForCausalLM.from_pretrained(model_id, local_files_only=True)
    except Exception:
        tok = AutoTokenizer.from_pretrained(model_id)
        mdl = AutoModelForCausalLM.from_pretrained(model_id)
    mdl.eval()

    scored: list[dict] = []
    by_sec: dict[str, list[float]] = {}
    for sec, idx, txt in sectioned_paras:
        if len(txt) < 100:
            continue
        enc = tok(txt, return_tensors="pt", truncation=True, max_length=512)
        n_tok = int(enc["input_ids"].shape[1])
        if n_tok < 12:
            continue
        with torch.no_grad():
            loss = mdl(**enc, labels=enc["input_ids"]).loss
        ppl = round(math.exp(float(loss)), 2)
        by_sec.setdefault(sec, []).append(ppl)
        scored.append({"section": sec, "p_idx": idx, "tokens": n_tok, "ppl": ppl, "snippet": txt[:95]})

    scored_sorted = sorted(scored, key=lambda x: x["ppl"])
    all_ppls = [x["ppl"] for x in scored]
    sec_summary = {
        s: {
            "paragraphs": len(vals),
            "mean_ppl": round(statistics.mean(vals), 2),
            "min_ppl": min(vals),
            "max_ppl": max(vals),
        }
        for s, vals in by_sec.items()
    }
    return {
        "model": model_id,
        "paragraphs_scored": len(scored),
        "overall_mean_ppl": round(statistics.mean(all_ppls), 2) if all_ppls else 0.0,
        "overall_median_ppl": round(statistics.median(all_ppls), 2) if all_ppls else 0.0,
        "by_section": sec_summary,
        "lowest_5_predictable": scored_sorted[:5],
        "highest_5_varied": list(reversed(scored_sorted[-5:])),
    }


def _reconstruct_openalex_abstract(inv_idx: dict | None) -> str:
    if not inv_idx:
        return ""
    pos_map: dict[int, str] = {}
    for word, positions in inv_idx.items():
        for p in positions:
            pos_map[p] = word
    return " ".join(pos_map[i] for i in sorted(pos_map))


def _fetch_bib_abstract(entry: dict, headers: dict) -> tuple[str, str]:
    import requests

    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", entry.get("doi", "").strip())
    if doi:
        try:
            r = requests.get(f"https://api.openalex.org/works/https://doi.org/{doi}", headers=headers, timeout=10)
            if r.status_code == 200:
                abs_txt = _reconstruct_openalex_abstract(r.json().get("abstract_inverted_index"))
                if abs_txt:
                    return "openalex", abs_txt
        except requests.RequestException:
            pass
        try:
            r2 = requests.get(f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}", headers=headers, timeout=10)
            if r2.status_code == 200:
                raw_abs = r2.json().get("message", {}).get("abstract", "")
                if raw_abs:
                    clean_abs = html.unescape(re.sub(r"<[^>]+>", " ", raw_abs))
                    return "crossref", re.sub(r"\s+", " ", clean_abs).strip()
        except requests.RequestException:
            pass

    url = entry.get("url", "").strip()
    if url:
        try:
            r3 = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
            if r3.status_code == 200:
                m = re.search(
                    r'<meta[^>]+name=["\'](?:citation_abstract|DC\.Description|description)["\'][^>]+content=["\'](.*?)["\']',
                    r3.text,
                    re.IGNORECASE | re.DOTALL,
                )
                if m and len(m.group(1).strip()) > 60:
                    return "ojs_meta", re.sub(r"\s+", " ", html.unescape(m.group(1))).strip()
        except requests.RequestException:
            pass
    return "title_only", ""


def check_bib_abstract_overlap(sectioned_paras: list[tuple[str, int, str]], bib_path: Path) -> dict:
    raw = bib_path.read_text(encoding="utf-8")
    blocks = re.split(r"@(?:article|book|inproceedings|misc|proceedings)\s*\{", raw)[1:]
    headers = {"User-Agent": "ProposalSkripsiAudit/2.0 (mailto:academic-verify@example.org)"}

    sources: list[dict] = []
    source_types: dict[str, int] = {}
    for idx, blk in enumerate(blocks, start=1):
        km = re.match(r"\s*([^,\s]+)\s*,", blk)
        key = km.group(1) if km else f"entry_{idx}"
        entry = {"key": key}
        for field in ("title", "doi", "url"):
            fm = re.search(rf"\b{field}\s*=\s*\{{(.*?)\}}", blk, re.DOTALL)
            entry[field] = re.sub(r"\s+", " ", fm.group(1)).strip() if fm else ""
        src_kind, abs_txt = _fetch_bib_abstract(entry, headers)
        source_types[src_kind] = source_types.get(src_kind, 0) + 1
        combined = f"{entry['title']} {abs_txt}".strip()
        sources.append({"key": key, "kind": src_kind, "g4": _ngrams(combined, 4), "g5": _ngrams(combined, 5)})

    hits: list[dict] = []
    for sec, p_idx, txt in sectioned_paras:
        p4, p5 = _ngrams(txt, 4), _ngrams(txt, 5)
        if not p4:
            continue
        for src in sources:
            ov4 = p4 & src["g4"]
            ov5 = p5 & src["g5"]
            pct4 = round(len(ov4) / len(p4) * 100.0, 2)
            if len(ov5) >= 1 or pct4 >= 5.0:
                hits.append(
                    {
                        "section": sec,
                        "p_idx": p_idx,
                        "ref_key": src["key"],
                        "src_kind": src["kind"],
                        "overlap_4gram_pct": pct4,
                        "shared_5grams_count": len(ov5),
                        "shared_5gram_samples": [" ".join(g) for g in list(ov5)[:3]],
                        "para_snippet": txt[:80],
                    }
                )

    hits.sort(key=lambda h: (h["shared_5grams_count"], h["overlap_4gram_pct"]), reverse=True)
    return {
        "bib_entries": len(sources),
        "abstract_fetch_breakdown": source_types,
        "flagged_pairs_count": len(hits),
        "top_10_overlaps": hits[:10],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Indonesian thesis proposal DOCX/PDF quality and Turnitin readiness.")
    parser.add_argument("input_path", type=Path, help="Path to .docx (or .pdf for --export-turnitin only)")
    parser.add_argument("--pdf", type=Path, default=None, help="Companion compiled PDF path for Turnitin split or page check")
    parser.add_argument("--compare", type=Path, default=None, help="Optional reference .docx or .pdf to compute 4/5/6-gram overlap")
    parser.add_argument("--check-bib", type=Path, default=None, help="Check draft paragraphs against fetched Crossref/OpenAlex/OJS abstracts")
    parser.add_argument("--export-turnitin", type=Path, default=None, help="Write clean PDF without raw LAMPIRAN pages")
    parser.add_argument("--appendix-marker", default="ringkasan matriks", help="Case-insensitive marker starting raw appendices")
    parser.add_argument("--perplexity", action="store_true", help="Run full-body per-paragraph Indonesian GPT-2 perplexity check")
    args = parser.parse_args()

    if not args.input_path.exists():
        print(f"ERROR: File not found: {args.input_path}", file=sys.stderr)
        return 1

    result: dict = {}
    full_text = ""
    sectioned_paras: list[tuple[str, int, str]] = []

    if args.input_path.suffix.lower() == ".docx":
        metrics, full_text, sectioned_paras = extract_docx_data(args.input_path)
        result["docx_audit"] = metrics
    elif args.input_path.suffix.lower() == ".pdf":
        full_text = read_pdf_text(args.input_path)
        result["pdf_pages"] = len(PdfReader(str(args.input_path)).pages)

    if args.compare and args.compare.exists():
        cmp_text = extract_docx_data(args.compare)[1] if args.compare.suffix.lower() == ".docx" else read_pdf_text(args.compare)
        result["overlap_vs_compare_pct"] = {
            "4gram": compute_ngram_overlap(full_text, cmp_text, 4),
            "5gram": compute_ngram_overlap(full_text, cmp_text, 5),
            "6gram": compute_ngram_overlap(full_text, cmp_text, 6),
        }

    if args.check_bib and args.check_bib.exists() and sectioned_paras:
        result["bib_abstract_overlap"] = check_bib_abstract_overlap(sectioned_paras, args.check_bib)

    pdf_for_split = args.pdf or (args.input_path if args.input_path.suffix.lower() == ".pdf" else None)
    if args.export_turnitin:
        if not pdf_for_split or not pdf_for_split.exists():
            print("ERROR: --export-turnitin requires --pdf path or .pdf input", file=sys.stderr)
            return 2
        result["turnitin_export"] = export_turnitin_pdf(pdf_for_split, args.export_turnitin, args.appendix_marker)

    if args.perplexity and sectioned_paras:
        result["perplexity_full_body"] = score_indonesian_perplexity_full(sectioned_paras)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    audit = result.get("docx_audit", {})
    has_artifacts = audit.get("leftover_backticks", 0) > 0 or audit.get("leftover_double_asterisks", 0) > 0 or audit.get("nik_16digit_hits", 0) > 0
    return 2 if has_artifacts else 0


if __name__ == "__main__":
    raise SystemExit(main())
