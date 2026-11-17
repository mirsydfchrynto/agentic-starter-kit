"""Reusable OOXML helpers for Indonesian thesis proposals (Proposal Skripsi).

Provides A4 portrait/landscape margins, Roman-to-Arabic section page numbering,
clickable bookmarks, TOC/LOT/LOF fields, Zotero CSL IEEE fields, external DOI
hyperlinks, fixed-width tables with header repeat, behind-text watermarks,
non-recursive inline formatting (`add_rich_runs`), and heading-anchored PDF
page-number mapping.
"""

import json
import re
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

HEADING_HANG_CM = 1.05


def cm_to_emu(cm_val: float) -> int:
    """Convert centimeters to English Metric Units (EMU)."""
    return int(round(cm_val * 360000))


def cm_to_dxa(cm_val: float) -> int:
    """Convert centimeters to twentieths of a point (DXA)."""
    return int(round(cm_val * 566.929))


class BookmarkRegistry:
    """Tracks unique OOXML bookmark IDs and Zotero citation occurrence IDs."""

    def __init__(self):
        self._bm_id = 10
        self._cit_seq = 0
        self._names: set[str] = set()

    def next_id(self) -> str:
        self._bm_id += 1
        return str(self._bm_id)

    def next_cit_id(self) -> str:
        self._cit_seq += 1
        return f"cit_{self._cit_seq:04d}"

    def make_unique_name(self, raw_name: str) -> str:
        base = re.sub(r"[^A-Za-z0-9_]", "_", raw_name)[:36]
        if not base or not (base[0].isalpha() or base[0] == "_"):
            base = f"bm_{base}"
        cand = base
        idx = 2
        while cand in self._names:
            cand = f"{base[:33]}_{idx}"
            idx += 1
        self._names.add(cand)
        return cand


def load_bib_entries(bib_path: str) -> dict[int, dict]:
    """Parse a BibTeX file into {1: {...}, ..., N: {...}} ordered entries."""
    with open(bib_path, "r", encoding="utf-8") as f:
        raw = f.read()

    entries: dict[int, dict] = {}
    blocks = re.split(r"@(?:article|book|inproceedings|misc|proceedings)\s*\{", raw)[1:]
    entry_types = re.findall(r"@(article|book|inproceedings|misc|proceedings)\s*\{", raw)
    seq_num = 0
    for etype, blk in zip(entry_types, blocks):
        key_m = re.match(r"\s*([^,\s]+)\s*,", blk)
        if not key_m:
            continue
        key = key_m.group(1)
        ref_num_m = re.fullmatch(r"ref_(\d+)", key)
        seq_num = int(ref_num_m.group(1)) if ref_num_m else (seq_num + 1)
        data = {"key": key, "num": seq_num, "etype": etype}
        for field in ("author", "title", "journal", "booktitle", "publisher", "year", "doi", "isbn", "url"):
            fm = re.search(rf"\b{field}\s*=\s*\{{(.*?)\}}", blk, re.DOTALL)
            data[field] = re.sub(r"\s+", " ", fm.group(1)).strip() if fm else ""
        if not data["journal"]:
            data["journal"] = data["booktitle"] or data["publisher"]
        entries[seq_num] = data
    return entries


def build_zotero_csl_instr(ref_num: int, bib_db: dict, reg: BookmarkRegistry | None, namespace: str = "academic") -> str:
    """Build Zotero Word field instruction JSON for an IEEE reference [n]."""
    entry = (bib_db or {}).get(ref_num, {})
    etype = entry.get("etype", "article")
    csl_type = "book" if etype == "book" else ("paper-conference" if etype == "inproceedings" else "article-journal")
    author_raw = entry.get("author", "")

    authors = []
    for part in re.split(r"\s+and\s+|,\s+(?=[A-Z]\.)", author_raw):
        clean_a = part.strip().strip(",")
        if not clean_a:
            continue
        tokens = clean_a.split()
        if len(tokens) > 1:
            authors.append({"family": tokens[-1], "given": " ".join(tokens[:-1])})
        else:
            authors.append({"literal": clean_a})

    year_m = re.search(r"\d{4}", entry.get("year", ""))
    year_int = int(year_m.group(0)) if year_m else 2026

    payload = {
        "citationID": reg.next_cit_id() if reg else f"cit_{ref_num}",
        "properties": {"formattedCitation": f"[{ref_num}]", "plainCitation": f"[{ref_num}]", "noteIndex": 0},
        "citationItems": [
            {
                "id": ref_num,
                "uris": [f"http://zotero.org/users/local/{namespace}/items/ref_{ref_num:02d}"],
                "itemData": {
                    "id": ref_num,
                    "type": csl_type,
                    "title": entry.get("title", f"Reference {ref_num}"),
                    "container-title": entry.get("journal", ""),
                    "DOI": entry.get("doi", ""),
                    "URL": entry.get("url", ""),
                    "author": authors,
                    "issued": {"date-parts": [[year_int]]},
                },
            }
        ],
        "schema": "https://github.com/citation-style-language/schema/raw/master/csl-citation.json",
    }
    return " ADDIN ZOTERO_ITEM CSL_CITATION " + json.dumps(payload, ensure_ascii=False) + " "


def build_zotero_bibl_instr() -> str:
    """Return Zotero bibliography field instruction string."""
    return ' ADDIN ZOTERO_BIBL {"uncited":[],"omitted":[],"custom":[]} CSL_BIBLIOGRAPHY '


def add_bookmark_to_paragraph(p, raw_name: str, reg: BookmarkRegistry) -> str:
    """Wrap paragraph content in valid OOXML bookmarkStart/bookmarkEnd after w:pPr."""
    bm_name = reg.make_unique_name(raw_name)
    bm_id = reg.next_id()
    bm_start = OxmlElement("w:bookmarkStart")
    bm_start.set(qn("w:id"), bm_id)
    bm_start.set(qn("w:name"), bm_name)
    bm_end = OxmlElement("w:bookmarkEnd")
    bm_end.set(qn("w:id"), bm_id)

    insert_idx = 1 if (len(p._p) > 0 and p._p[0].tag == qn("w:pPr")) else 0
    p._p.insert(insert_idx, bm_start)
    p._p.append(bm_end)
    return bm_name


def append_field_token(p, fld_type=None, instr_text=None, font_size: float = 12, target_container=None):
    """Append w:fldChar or w:instrText run either to a paragraph or hyperlink container."""
    r = p.add_run()
    r.font.name = "Times New Roman"
    r.font.size = Pt(font_size)
    if fld_type is not None:
        fc = OxmlElement("w:fldChar")
        fc.set(qn("w:fldCharType"), fld_type)
        r._r.append(fc)
    if instr_text is not None:
        it = OxmlElement("w:instrText")
        it.set(qn("xml:space"), "preserve")
        it.text = instr_text
        r._r.append(it)
    if target_container is not None:
        p._p.remove(r._r)
        target_container.append(r._r)
    return r


def create_internal_hyperlink(anchor_name: str):
    """Create a w:hyperlink pointing to a document bookmark."""
    hl = OxmlElement("w:hyperlink")
    hl.set(qn("w:anchor"), anchor_name)
    hl.set(qn("w:history"), "1")
    return hl


def create_external_hyperlink(p, url: str):
    """Create an external w:hyperlink registered on the paragraph part."""
    r_id = p.part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hl = OxmlElement("w:hyperlink")
    hl.set(qn("r:id"), r_id)
    hl.set(qn("w:history"), "1")
    return hl


def move_run_into(p, run, container) -> None:
    """Move an existing run from its paragraph into an OOXML container (e.g., hyperlink)."""
    p._p.remove(run._r)
    container.append(run._r)


def apply_a4_margins(section, landscape: bool = False) -> None:
    """Apply standard Indonesian academic A4 margins (4-4-3-3 portrait, 3.5L-3-3-3 landscape)."""
    if landscape:
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = Cm(29.7)
        section.page_height = Cm(21.0)
        section.top_margin = Cm(3.0)
        section.bottom_margin = Cm(3.0)
        section.left_margin = Cm(3.5)
        section.right_margin = Cm(3.0)
    else:
        section.orientation = WD_ORIENT.PORTRAIT
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(4.0)
        section.bottom_margin = Cm(3.0)
        section.left_margin = Cm(4.0)
        section.right_margin = Cm(3.0)


def configure_page_number_xml(section, fmt: str = "decimal", start: int | None = None) -> None:
    """Configure XML page numbering format ('lowerRoman' or 'decimal') and optional restart value."""
    sectPr = section._sectPr
    for child in list(sectPr):
        if child.tag == qn("w:pgNumType"):
            sectPr.remove(child)
    pgNumType = OxmlElement("w:pgNumType")
    pgNumType.set(qn("w:fmt"), fmt)
    if start is not None:
        pgNumType.set(qn("w:start"), str(start))
    sectPr.append(pgNumType)


def add_page_number_footer(section, align=WD_ALIGN_PARAGRAPH.CENTER) -> None:
    """Insert dynamic Word PAGE field into an unlinked footer."""
    section.footer.is_linked_to_previous = False
    p = section.footer.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.first_line_indent = Cm(0)

    def _run(txt=""):
        r = p.add_run(txt)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0, 0, 0)
        return r

    append_field_token(p, fld_type="begin", font_size=11)
    append_field_token(p, instr_text=" PAGE ", font_size=11)
    append_field_token(p, fld_type="separate", font_size=11)
    _run("1")
    append_field_token(p, fld_type="end", font_size=11)


def set_cell_shading(cell, fill_hex: str) -> None:
    cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))


def set_cell_margins(cell, top: int = 55, bottom: int = 55, left: int = 85, right: int = 85) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    for ch in list(tcPr):
        if ch.tag == qn("w:tcMar"):
            tcPr.remove(ch)
    tcMar = OxmlElement("w:tcMar")
    for side, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def _apply_border_spec(table, border_val: str, sz: str, color: str) -> None:
    tblPr = table._tbl.tblPr
    for ch in list(tblPr):
        if ch.tag == qn("w:tblBorders"):
            tblPr.remove(ch)
    tags = "".join(
        f'<w:{edge} w:val="{border_val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        for edge in ("top", "bottom", "left", "right", "insideH", "insideV")
    )
    tblPr.append(parse_xml(f'<w:tblBorders {nsdecls("w")}>{tags}</w:tblBorders>'))


def set_table_borders(table, border_color: str = "444444", sz: str = "4") -> None:
    _apply_border_spec(table, "single", sz, border_color)


def clear_table_borders(table) -> None:
    _apply_border_spec(table, "none", "0", "auto")


def set_row_cant_split(row) -> None:
    row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))


def set_repeat_header(row) -> None:
    row._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))


def set_cell_vertical_border_none(cell, right: bool = True, left: bool = False) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = tcPr.find(qn("w:tcBorders"))
    if tcBorders is None:
        tcBorders = OxmlElement("w:tcBorders")
        tcPr.append(tcBorders)
    for enabled, side in ((right, "right"), (left, "left")):
        if enabled:
            node = OxmlElement(f"w:{side}")
            node.set(qn("w:val"), "nil")
            tcBorders.append(node)


def apply_fixed_table_widths(table, col_widths_cm: list[float]) -> None:
    """Enforce deterministic fixed table column widths across Word and LibreOffice."""
    tblPr = table._tbl.tblPr
    for child in list(tblPr):
        if child.tag in (qn("w:tblW"), qn("w:tblLayout")):
            tblPr.remove(child)
    tblW = OxmlElement("w:tblW")
    tblW.set(qn("w:w"), str(sum(cm_to_dxa(w) for w in col_widths_cm)))
    tblW.set(qn("w:type"), "dxa")
    tblPr.append(tblW)
    tblLayout = OxmlElement("w:tblLayout")
    tblLayout.set(qn("w:type"), "fixed")
    tblPr.append(tblLayout)

    tblGrid = table._tbl.tblGrid
    for child in list(tblGrid):
        tblGrid.remove(child)
    for w in col_widths_cm:
        gc = OxmlElement("w:gridCol")
        gc.set(qn("w:w"), str(cm_to_dxa(w)))
        tblGrid.append(gc)

    for row in table.rows:
        for j, w in enumerate(col_widths_cm):
            tcPr = row.cells[j]._tc.get_or_add_tcPr()
            for child in list(tcPr):
                if child.tag == qn("w:tcW"):
                    tcPr.remove(child)
            tcW = OxmlElement("w:tcW")
            tcW.set(qn("w:w"), str(cm_to_dxa(w)))
            tcW.set(qn("w:type"), "dxa")
            tcPr.append(tcW)


def _emit_styled_run(p, content, font_name, font_size, bold, italic, sub, sup, color, underline=None, target_container=None):
    r = p.add_run(content)
    r.font.name = font_name
    r.font.size = Pt(font_size if font_name == "Times New Roman" else max(8, font_size - 1))
    r.bold = bold
    r.italic = italic
    r.font.subscript = sub
    r.font.superscript = sup
    r.font.color.rgb = color
    if underline is not None:
        r.font.underline = underline
    if target_container is not None:
        move_run_into(p, r, target_container)
    return r


def add_rich_runs(
    p,
    text: str,
    font_size: float = 12,
    base_bold: bool = False,
    base_italic: bool = False,
    color=RGBColor(0, 0, 0),
    doc=None,
    enable_citations: bool = True,
    target_container=None,
    underline=None,
    namespace: str = "academic",
) -> None:
    """Parse non-nested inline markdown (***, **, *, ``, _{}, ^{}) and link [N] IEEE citations."""
    pattern = r"(\*\*\*.*?\*\*\*|\*\*.*?\*\*|`[^`]+?`|_\{[^}]+?\}|\^\{[^}]+?\}|\*[^*]+?\*)"
    bm_reg = getattr(doc, "_bm_reg", None) if doc is not None else None
    bib_db = getattr(doc, "_bib_db", None) if doc is not None else None
    cite_tracker = getattr(doc, "_cite_seq", None) if doc is not None else None

    for tok in re.split(pattern, text):
        if not tok:
            continue
        bold, italic, sub, sup, font_name, content = base_bold, base_italic, False, False, "Times New Roman", tok
        if tok.startswith("***") and tok.endswith("***"):
            bold, italic, content = True, True, tok[3:-3]
        elif tok.startswith("**") and tok.endswith("**"):
            bold, content = True, tok[2:-2]
        elif tok.startswith("*") and tok.endswith("*"):
            italic, content = True, tok[1:-1]
        elif tok.startswith("`") and tok.endswith("`"):
            font_name, content = "Courier New", tok[1:-1]
        elif tok.startswith("_{") and tok.endswith("}"):
            sub, content = True, tok[2:-1]
        elif tok.startswith("^{") and tok.endswith("}"):
            sup, content = True, tok[2:-1]

        can_cite = enable_citations and (target_container is None) and not sub and not sup and font_name == "Times New Roman"
        if can_cite and re.search(r"\[\d+\]", content):
            for sp in re.split(r"(\[\d+\])", content):
                if not sp:
                    continue
                cm = re.fullmatch(r"\[(\d+)\]", sp)
                if cm and bib_db and 1 <= int(cm.group(1)) <= len(bib_db):
                    ref_num = int(cm.group(1))
                    if cite_tracker is not None:
                        cite_tracker.append(ref_num)
                    append_field_token(p, fld_type="begin", font_size=font_size)
                    append_field_token(p, instr_text=build_zotero_csl_instr(ref_num, bib_db, bm_reg, namespace=namespace), font_size=font_size)
                    append_field_token(p, fld_type="separate", font_size=font_size)
                    hl = create_internal_hyperlink(f"ref_{ref_num:02d}")
                    _emit_styled_run(p, sp, font_name, font_size, bold, italic, False, False, color, underline=False, target_container=hl)
                    p._p.append(hl)
                    append_field_token(p, fld_type="end", font_size=font_size)
                else:
                    _emit_styled_run(p, sp, font_name, font_size, bold, italic, sub, sup, color, underline=underline)
        else:
            _emit_styled_run(p, content, font_name, font_size, bold, italic, sub, sup, color, underline=underline, target_container=target_container)


def add_body_p(doc, text: str, indent: bool = True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after: float = 2.2, space_before: float = 0, line_spacing: float = 1.5, font_size: float = 12, left_cm: float | None = None):
    """Add formatted body paragraph (default 1.50 line spacing, Times New Roman 12pt)."""
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    base_left = getattr(doc, "_body_left_cm", 0.0) if left_cm is None else left_cm
    p.paragraph_format.left_indent = Cm(base_left)
    p.paragraph_format.first_line_indent = Cm(1.0) if indent else Cm(0)
    add_rich_runs(p, text, font_size=font_size, doc=doc)
    return p


def add_numbered_item(doc, num_str: str, text: str, start_cm: float | None = None, hanging_cm: float = 0.65, space_after: float = 2.5, font_size: float = 12):
    """Add hanging-indented numbered list paragraph aligned at 1.50 line spacing."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    base_left = getattr(doc, "_body_left_cm", 0.0) if start_cm is None else start_cm
    text_col = base_left + hanging_cm
    p.paragraph_format.left_indent = Cm(text_col)
    p.paragraph_format.first_line_indent = Cm(-hanging_cm)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(text_col), WD_TAB_ALIGNMENT.LEFT)
    add_rich_runs(p, f"{num_str}\t", font_size=font_size, doc=doc, enable_citations=False)
    add_rich_runs(p, text, font_size=font_size, doc=doc)
    return p


def add_chapter_heading(doc, title_line1: str, title_line2: str | None = None, page_break: bool = True, toc_tracker=None, bm_slug: str | None = None, align=WD_ALIGN_PARAGRAPH.LEFT, font_size: float = 12, hang_cm: float = HEADING_HANG_CM):
    """Add Heading 1 chapter title with optional bookmark registration for TOC linking."""
    p = doc.add_paragraph(style="Heading 1")
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.keep_with_next = True
    if page_break:
        p.paragraph_format.page_break_before = True

    emit_line1, full_title = title_line1, title_line1
    m_num = re.match(r"^([IVX]+|\d+)\.\s+(.*)$", title_line1) if (align == WD_ALIGN_PARAGRAPH.LEFT and not title_line2) else None
    if m_num:
        emit_line1 = f"{m_num.group(1)}.\t{m_num.group(2)}"
        full_title = f"{m_num.group(1)}. {m_num.group(2)}"
        p.paragraph_format.left_indent = Cm(hang_cm)
        p.paragraph_format.first_line_indent = Cm(-hang_cm)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(hang_cm), WD_TAB_ALIGNMENT.LEFT)
    else:
        p.paragraph_format.left_indent = Cm(0)
        p.paragraph_format.first_line_indent = Cm(0)

    for idx, chunk in enumerate((emit_line1,) + (("\n" + title_line2,) if title_line2 else ())):
        r = p.add_run(chunk)
        r.font.name = "Times New Roman"
        r.font.size = Pt(font_size)
        r.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        if idx == 1:
            full_title = f"{title_line1} {title_line2}"

    bm_reg = getattr(doc, "_bm_reg", None)
    bm_name = add_bookmark_to_paragraph(p, bm_slug or f"bm_{full_title}", bm_reg) if bm_reg else None
    if toc_tracker is not None:
        toc_tracker.append((1, full_title, bm_name))
    return p


def _add_sub_heading(doc, text: str, level: int, toc_tracker=None, hang_cm: float = HEADING_HANG_CM):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8 if level == 2 else 6)
    p.paragraph_format.space_after = Pt(3 if level == 2 else 2)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.keep_with_next = True
    m_num = re.match(r"^(\d+(?:\.\d+)+)\s+(.*)$", text)
    if m_num:
        emit_txt = f"{m_num.group(1)}\t{m_num.group(2)}"
        p.paragraph_format.left_indent = Cm(hang_cm)
        p.paragraph_format.first_line_indent = Cm(-hang_cm)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(hang_cm), WD_TAB_ALIGNMENT.LEFT)
    else:
        emit_txt = text
        p.paragraph_format.left_indent = Cm(0)
        p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run(emit_txt)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    bm_reg = getattr(doc, "_bm_reg", None)
    bm_name = add_bookmark_to_paragraph(p, f"bm_{text}", bm_reg) if bm_reg else None
    if toc_tracker is not None:
        toc_tracker.append((level, text, bm_name))
    return p


def add_h2(doc, text: str, toc_tracker=None, hang_cm: float = HEADING_HANG_CM):
    return _add_sub_heading(doc, text, 2, toc_tracker=toc_tracker, hang_cm=hang_cm)


def add_h3(doc, text: str, toc_tracker=None, hang_cm: float = HEADING_HANG_CM):
    return _add_sub_heading(doc, text, 3, toc_tracker=toc_tracker, hang_cm=hang_cm)


def add_table_caption(doc, caption: str, tbl_tracker=None):
    p = doc.add_paragraph(style="Caption")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.keep_with_next = True
    add_rich_runs(p, caption, font_size=11, doc=doc, enable_citations=False)
    bm_reg = getattr(doc, "_bm_reg", None)
    clean_slug = re.sub(r"[^A-Za-z0-9]+", "_", caption[:26])
    bm_name = add_bookmark_to_paragraph(p, f"bm_tbl_{clean_slug}", bm_reg) if bm_reg else None
    if tbl_tracker is not None:
        tbl_tracker.append((caption, bm_name))
    return p


def add_styled_table(doc, headers, rows, col_widths_cm, font_size: float = 9.5, center_cols=None, bold_last_col: bool = False, bold_last_row: bool = False, keep_together: bool = True, enable_citations: bool = True, header_fill: str = "DDE8E8", highlight_fill: str = "F2F7F7"):
    """Build a bordered academic table with repeating headers and unbreakable rows."""
    center_cols = set(center_cols or [])
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_table_borders(tbl, "334155", "4")
    apply_fixed_table_widths(tbl, col_widths_cm)

    hdr_row = tbl.rows[0]
    set_repeat_header(hdr_row)
    set_row_cant_split(hdr_row)
    for j, h_text in enumerate(headers):
        cell = hdr_row.cells[j]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(cell, header_fill)
        set_cell_margins(cell, top=55, bottom=55, left=70, right=70)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.1
        p.paragraph_format.first_line_indent = Cm(0)
        if keep_together:
            p.paragraph_format.keep_with_next = True
        add_rich_runs(p, h_text, font_size=font_size, base_bold=True, doc=doc, enable_citations=enable_citations)

    for i, row_data in enumerate(rows):
        row = tbl.rows[i + 1]
        set_row_cant_split(row)
        is_last = i == len(rows) - 1
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            is_bold_cell = bool((bold_last_col and j == len(headers) - 1) or (bold_last_row and is_last))
            if is_bold_cell:
                set_cell_shading(cell, highlight_fill)
            set_cell_margins(cell, top=48, bottom=48, left=70, right=70)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j in center_cols else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.12
            p.paragraph_format.first_line_indent = Cm(0)
            if keep_together and not is_last:
                p.paragraph_format.keep_with_next = True
            add_rich_runs(p, str(val), font_size=font_size, base_bold=is_bold_cell, doc=doc, enable_citations=enable_citations)
    return tbl


def add_toc_entry_linked(doc, label: str, page_num, anchor_name=None, level: int = 1, total_width_cm: float = 14.0, is_first: bool = False, is_last: bool = False, toc_instr=None, force_left_cm=None, force_bold=None, font_size: float = 11.0):
    """Insert a clickable dotted-leader TOC/LOT/LOF entry optionally wrapped inside a Word TOC field."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(0.5 if level == 1 else 0)
    p.paragraph_format.space_after = Pt(0.4 if level == 1 else 0.1)
    p.paragraph_format.line_spacing = 1.08
    indent_cm = force_left_cm if force_left_cm is not None else {1: 0.0, 2: 0.5, 3: 1.0}.get(level, 0.0)
    is_bold = force_bold if force_bold is not None else (level == 1)
    p.paragraph_format.left_indent = Cm(indent_cm)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(total_width_cm), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

    if is_first and toc_instr:
        append_field_token(p, fld_type="begin", font_size=font_size)
        append_field_token(p, instr_text=toc_instr, font_size=font_size)
        append_field_token(p, fld_type="separate", font_size=font_size)

    hl = create_internal_hyperlink(anchor_name) if anchor_name else None
    add_rich_runs(p, label, font_size=font_size, base_bold=is_bold, doc=doc, enable_citations=False, target_container=hl, underline=False)
    r_tab = p.add_run("\t" + str(page_num))
    r_tab.font.name = "Times New Roman"
    r_tab.font.size = Pt(font_size)
    r_tab.bold = is_bold
    r_tab.font.color.rgb = RGBColor(0, 0, 0)
    r_tab.font.underline = False
    if hl is not None:
        move_run_into(p, r_tab, hl)
        p._p.append(hl)

    if is_last and toc_instr:
        append_field_token(p, fld_type="end", font_size=font_size)
    return p


def insert_behind_watermark(paragraph, img_path: str, width_cm: float = 12.4, top_offset_cm: float = 0.8, src_rect_bottom: int = 14733, name: str = "Watermark") -> None:
    """Embed image as a centered behind-text (<wp:anchor behindDoc='1'>) watermark."""
    run = paragraph.add_run()
    run.add_picture(img_path, width=Cm(width_cm))
    drawing = run._r.find(qn("w:drawing"))
    inline = drawing.find(qn("wp:inline"))
    extent = inline.find(qn("wp:extent"))
    cNvPr = inline.find(qn("wp:cNvGraphicFramePr"))
    graphic = inline.find(qn("a:graphic"))

    if src_rect_bottom:
        blip_fill = graphic.find(".//" + qn("pic:blipFill"))
        if blip_fill is not None:
            src_rect = blip_fill.find(qn("a:srcRect"))
            if src_rect is None:
                src_rect = OxmlElement("a:srcRect")
                blip = blip_fill.find(qn("a:blip"))
                blip_fill.insert(list(blip_fill).index(blip) + 1 if blip is not None else 0, src_rect)
            src_rect.set("b", str(src_rect_bottom))

    cx, cy = int(extent.get("cx")), int(extent.get("cy"))
    if src_rect_bottom:
        cy = int(round(cy * (100000 - src_rect_bottom) / 100000.0))

    anchor = OxmlElement("wp:anchor")
    for k, v in (("distT", "0"), ("distB", "0"), ("distL", "0"), ("distR", "0"), ("simplePos", "0"), ("relativeHeight", "251658240"), ("behindDoc", "1"), ("locked", "0"), ("layoutInCell", "1"), ("allowOverlap", "1")):
        anchor.set(k, v)

    simple_pos = OxmlElement("wp:simplePos")
    simple_pos.set("x", "0")
    simple_pos.set("y", "0")
    anchor.append(simple_pos)

    pos_h = OxmlElement("wp:positionH")
    pos_h.set("relativeFrom", "margin")
    align_h = OxmlElement("wp:align")
    align_h.text = "center"
    pos_h.append(align_h)
    anchor.append(pos_h)

    pos_v = OxmlElement("wp:positionV")
    pos_v.set("relativeFrom", "paragraph")
    offset_v = OxmlElement("wp:posOffset")
    offset_v.text = str(cm_to_emu(top_offset_cm))
    pos_v.append(offset_v)
    anchor.append(pos_v)

    new_extent = OxmlElement("wp:extent")
    new_extent.set("cx", str(cx))
    new_extent.set("cy", str(cy))
    anchor.append(new_extent)

    eff = OxmlElement("wp:effectExtent")
    for side in ("l", "t", "r", "b"):
        eff.set(side, "0")
    anchor.append(eff)
    anchor.append(OxmlElement("wp:wrapNone"))

    new_docPr = OxmlElement("wp:docPr")
    new_docPr.set("id", "901")
    new_docPr.set("name", name)
    anchor.append(new_docPr)
    anchor.append(cNvPr if cNvPr is not None else OxmlElement("wp:cNvGraphicFramePr"))
    anchor.append(graphic)
    drawing.remove(inline)
    drawing.append(anchor)
