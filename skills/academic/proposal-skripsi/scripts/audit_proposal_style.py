#!/usr/bin/env -S uv run --with python-docx --with pypdf --with numpy
"""Audit thesis proposal DOCX/PDF formatting, PII leaks, Indonesian AI-slop, n-gram overlap, and Turnitin split.

Run offline without polluting global Python environments via `uv run`.
Pass `--perplexity` inside an environment with cached HuggingFace `cahya/gpt2-small-indonesian-522M`
(set `HF_HUB_DISABLE_PROGRESS_BARS=1`). Pass `--export-turnitin OUT_PDF` to strip LAMPIRAN pages cleanly.
"""

import argparse
import json
import math
import os
import re
import statistics
import sys
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
    """Extract all visible <w:t> text inside a paragraph, including hyperlinks, excluding field instrText."""
    return "".join(node.text or "" for node in p._p.xpath(".//w:t"))


def extract_docx_metrics(docx_path: Path) -> tuple[dict, str]:
    doc = Document(str(docx_path))
    all_texts: list[str] = []
    main_narrative_paras: list[str] = []
    spacing_bad_main: list[tuple[float, str]] = []
    backtick_hits = 0
    asterisk_hits = 0
    nik_hits = 0
    in_main_body = False

    for p in doc.paragraphs:
        txt = _vis_text(p)
        low = txt.strip().lower()
        if p.style.name == "Heading 1":
            if re.search(r"\b(?:1\.|bab\s+i)\b.*pendahuluan", low):
                in_main_body = True
            elif "daftar pustaka" in low or "lampiran" in low:
                in_main_body = False

        all_texts.append(txt)
        backtick_hits += txt.count("`")
        asterisk_hits += txt.count("**")
        nik_hits += len(re.findall(r"\b\d{16}\b", txt))
        ls = p.paragraph_format.line_spacing
        if in_main_body and len(txt.strip()) >= 120 and p.style.name == "Normal":
            main_narrative_paras.append(txt.strip())
            if ls is None or abs(float(ls) - 1.5) > 0.02:
                spacing_bad_main.append((float(ls) if ls else 0.0, txt[:50]))

    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                txt = " ".join(_vis_text(cp) for cp in cell.paragraphs)
                all_texts.append(txt)
                backtick_hits += txt.count("`")
                asterisk_hits += txt.count("**")
                nik_hits += len(re.findall(r"\b\d{16}\b", txt))

    margins_ok = []
    for idx, sec in enumerate(doc.sections, start=1):
        margins_ok.append(
            {
                "section": idx,
                "w_cm": round(sec.page_width.cm, 2),
                "h_cm": round(sec.page_height.cm, 2),
                "top_cm": round(sec.top_margin.cm, 2),
                "left_cm": round(sec.left_margin.cm, 2),
                "bottom_cm": round(sec.bottom_margin.cm, 2),
                "right_cm": round(sec.right_margin.cm, 2),
            }
        )

    joined = "\n".join(main_narrative_paras) if main_narrative_paras else "\n".join(all_texts)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", joined) if len(s.split()) >= 4]
    lengths = [len(s.split()) for s in sents]
    mean_w = statistics.mean(lengths) if lengths else 0.0
    std_w = statistics.stdev(lengths) if len(lengths) > 1 else 0.0
    cv = (std_w / mean_w) if mean_w else 0.0
    pct_over_35 = (sum(1 for l in lengths if l > 35) / len(lengths) * 100.0) if lengths else 0.0

    low_all = "\n".join(all_texts).lower()
    tells_found = {}
    for pat in INDONESIAN_AI_TELLS:
        cnt = len(re.findall(pat, low_all))
        if cnt:
            tells_found[pat] = cnt

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
    return metrics, "\n".join(all_texts)


def compute_ngram_overlap(text_a: str, text_b: str, n: int = 5) -> float:
    toks_a = re.findall(r"[a-z0-9]+", text_a.lower())
    toks_b = re.findall(r"[a-z0-9]+", text_b.lower())
    if len(toks_a) < n or len(toks_b) < n:
        return 0.0
    grams_a = {tuple(toks_a[i : i + n]) for i in range(len(toks_a) - n + 1)}
    grams_b = {tuple(toks_b[i : i + n]) for i in range(len(toks_b) - n + 1)}
    if not grams_a:
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


def score_indonesian_perplexity(text: str, model_id: str = "cahya/gpt2-small-indonesian-522M") -> dict:
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

    sample = re.sub(r"\s+", " ", text).strip()[:6000]
    enc = tok(sample, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        loss = mdl(**enc, labels=enc["input_ids"]).loss
    ppl = math.exp(float(loss))
    return {"model": model_id, "tokens_evaluated": int(enc["input_ids"].shape[1]), "perplexity": round(ppl, 2)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Indonesian thesis proposal DOCX/PDF quality and Turnitin readiness.")
    parser.add_argument("input_path", type=Path, help="Path to .docx (or .pdf for --export-turnitin only)")
    parser.add_argument("--pdf", type=Path, default=None, help="Companion compiled PDF path for Turnitin split or page check")
    parser.add_argument("--compare", type=Path, default=None, help="Optional reference .docx or .pdf to compute 4/5/6-gram overlap")
    parser.add_argument("--export-turnitin", type=Path, default=None, help="Write clean PDF without raw LAMPIRAN pages")
    parser.add_argument("--appendix-marker", default="ringkasan matriks", help="Case-insensitive marker starting raw appendices")
    parser.add_argument("--perplexity", action="store_true", help="Run cached Indonesian GPT-2 perplexity check (needs torch & transformers)")
    args = parser.parse_args()

    if not args.input_path.exists():
        print(f"ERROR: File not found: {args.input_path}", file=sys.stderr)
        return 1

    result: dict = {}
    full_text = ""

    if args.input_path.suffix.lower() == ".docx":
        metrics, full_text = extract_docx_metrics(args.input_path)
        result["docx_audit"] = metrics
    elif args.input_path.suffix.lower() == ".pdf":
        full_text = read_pdf_text(args.input_path)
        result["pdf_pages"] = len(PdfReader(str(args.input_path)).pages)

    if args.compare and args.compare.exists():
        cmp_text = extract_docx_metrics(args.compare)[1] if args.compare.suffix.lower() == ".docx" else read_pdf_text(args.compare)
        result["overlap_vs_compare_pct"] = {
            "4gram": compute_ngram_overlap(full_text, cmp_text, 4),
            "5gram": compute_ngram_overlap(full_text, cmp_text, 5),
            "6gram": compute_ngram_overlap(full_text, cmp_text, 6),
        }

    pdf_for_split = args.pdf or (args.input_path if args.input_path.suffix.lower() == ".pdf" else None)
    if args.export_turnitin:
        if not pdf_for_split or not pdf_for_split.exists():
            print("ERROR: --export-turnitin requires --pdf path or .pdf input", file=sys.stderr)
            return 2
        result["turnitin_export"] = export_turnitin_pdf(pdf_for_split, args.export_turnitin, args.appendix_marker)

    if args.perplexity and full_text:
        result["perplexity"] = score_indonesian_perplexity(full_text)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    audit = result.get("docx_audit", {})
    has_artifacts = audit.get("leftover_backticks", 0) > 0 or audit.get("leftover_double_asterisks", 0) > 0 or audit.get("nik_16digit_hits", 0) > 0
    return 2 if has_artifacts else 0


if __name__ == "__main__":
    raise SystemExit(main())
