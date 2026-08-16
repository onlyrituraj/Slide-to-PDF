import streamlit as st
import pymupdf
import os
import io
import time

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Slide Handout Converter",
    page_icon="📄",
    layout="centered",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Page background */
.stApp {
    background: #0f1117;
}

/* Main container */
.block-container {
    max-width: 760px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

/* Hero title */
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin-bottom: 0.3rem;
}
.hero-sub {
    font-size: 1.05rem;
    color: #8b8fa8;
    margin-bottom: 2.2rem;
}

/* Settings card */
.settings-card {
    background: #1a1d2e;
    border: 1px solid #2a2d3e;
    border-radius: 14px;
    padding: 1.4rem 1.6rem 1.2rem;
    margin-bottom: 1.6rem;
}
.settings-card h4 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: #5b6aff;
    margin: 0 0 1rem 0;
}

/* Upload zone */
.upload-label {
    font-size: 0.82rem;
    font-weight: 500;
    color: #c8cbd8;
    margin-bottom: 0.4rem;
}

/* Stat chips */
.stat-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 1.2rem 0 1.4rem;
}
.stat-chip {
    background: #1a1d2e;
    border: 1px solid #2a2d3e;
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: #c8cbd8;
}
.stat-chip span {
    color: #ffffff;
    font-weight: 600;
}

/* Progress bar accent */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #5b6aff, #a78bfa);
    border-radius: 999px;
}

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #5b6aff 0%, #a78bfa 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
    transition: opacity 0.2s !important;
}
.stDownloadButton > button:hover {
    opacity: 0.88 !important;
}

/* File uploader */
[data-testid="stFileUploadDropzone"] {
    background: #1a1d2e !important;
    border: 2px dashed #2a2d3e !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #5b6aff !important;
}

/* Sliders */
[data-testid="stSlider"] > div > div > div > div {
    background: #5b6aff !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #1a1d2e !important;
    border-color: #2a2d3e !important;
    color: #ffffff !important;
    border-radius: 8px !important;
}

/* Success / info boxes */
.stSuccess {
    background: #0e2a1a !important;
    border-color: #1a5c33 !important;
    border-radius: 10px !important;
}
.stInfo {
    background: #131b3a !important;
    border-color: #1e2d6b !important;
    border-radius: 10px !important;
}

/* Preview image */
.preview-frame {
    border: 1px solid #2a2d3e;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 0.8rem;
}

/* Divider */
hr {
    border-color: #2a2d3e !important;
    margin: 1.8rem 0 !important;
}

/* Footer */
.footer {
    text-align: center;
    color: #3d4060;
    font-size: 0.78rem;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Core conversion function ────────────────────────────────────────────────
def convert_pdf(input_bytes: bytes, slides_per_page: int,
                dpi: int, margin: float, gap: float, border: float) -> bytes:
    """Convert slide PDF bytes → handout PDF bytes (in memory, no disk I/O)."""
    PAGE_W, PAGE_H = 595.28, 841.89   # A4

    src = pymupdf.open(stream=input_bytes, filetype="pdf")
    dst = pymupdf.open()
    total = len(src)

    out_page = None
    slot_idx = 0

    progress = st.progress(0, text="Converting slides…")

    for i in range(total):
        if slot_idx == 0:
            out_page = dst.new_page(width=PAGE_W, height=PAGE_H)
            out_page.draw_rect(out_page.rect, color=(1, 1, 1), fill=(1, 1, 1))

        slide = src[i]
        mat = pymupdf.Matrix(dpi / 72, dpi / 72)
        pix = slide.get_pixmap(matrix=mat, alpha=False, colorspace=pymupdf.csRGB)

        available_h = PAGE_H - 2 * margin - (slides_per_page - 1) * gap
        slot_h = available_h / slides_per_page
        slot_w = PAGE_W - 2 * margin

        scale = min(slot_w / pix.width, slot_h / pix.height)
        tw, th = pix.width * scale, pix.height * scale

        x0 = margin + (slot_w - tw) / 2
        y0 = margin + slot_idx * (slot_h + gap) + (slot_h - th) / 2
        rect = pymupdf.Rect(x0, y0, x0 + tw, y0 + th)

        if border > 0:
            b = rect + (-border, -border, border, border)
            out_page.draw_rect(b, color=(0.75, 0.75, 0.75), fill=None, width=border)

        out_page.insert_image(rect, pixmap=pix)

        slot_idx = (slot_idx + 1) % slides_per_page
        progress.progress((i + 1) / total,
                          text=f"Processing slide {i + 1} of {total}…")

    buf = io.BytesIO()
    dst.save(buf, garbage=4, deflate=True, clean=True)
    src.close()
    dst.close()
    progress.empty()
    return buf.getvalue()


# ─── UI ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">📄 Slide Handout Maker</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Upload a PDF of presentation slides and get a '
    'compact, print-ready handout — white background, multiple slides per page.</div>',
    unsafe_allow_html=True,
)

# ── Settings card ─────────────────────────────────────────────────────────────
st.markdown('<div class="settings-card"><h4>⚙️ Layout Settings</h4>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    slides_per_page = st.selectbox(
        "Slides per page",
        options=[2, 3, 4, 6],
        index=1,
        help="How many slides appear on each A4 page"
    )
with col2:
    dpi = st.select_slider(
        "Render quality (DPI)",
        options=[100, 150, 200, 250, 300],
        value=150,
        help="Higher = sharper text & images, but larger file size"
    )

col3, col4 = st.columns(2)
with col3:
    margin = st.slider("Page margin (pt)", 10, 40, 20, step=5)
with col4:
    gap = st.slider("Gap between slides (pt)", 6, 24, 12, step=2)

border = st.toggle("Show border around each slide", value=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── File uploader ─────────────────────────────────────────────────────────────
st.markdown('<div class="upload-label">📂 Upload your PDF</div>', unsafe_allow_html=True)
uploaded = st.file_uploader(
    label="upload",
    type=["pdf"],
    label_visibility="collapsed",
    help="Upload any PDF of presentation slides"
)

# ── Convert ───────────────────────────────────────────────────────────────────
if uploaded:
    input_bytes = uploaded.read()
    src_peek = pymupdf.open(stream=input_bytes, filetype="pdf")
    total_slides = len(src_peek)
    out_pages = -(-total_slides // slides_per_page)   # ceiling div
    src_peek.close()

    # Stats row
    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-chip">📑 <span>{total_slides}</span> slides</div>'
        f'<div class="stat-chip">📋 <span>{out_pages}</span> output pages</div>'
        f'<div class="stat-chip">🖨️ A4 portrait</div>'
        f'<div class="stat-chip">⚡ {dpi} DPI</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if st.button("▶  Convert Now", use_container_width=True, type="primary"):
        with st.spinner(""):
            t0 = time.time()
            output_bytes = convert_pdf(
                input_bytes,
                slides_per_page=slides_per_page,
                dpi=dpi,
                margin=margin,
                gap=gap,
                border=1 if border else 0,
            )
            elapsed = time.time() - t0

        size_kb = len(output_bytes) / 1024
        st.success(
            f"✅ Done in {elapsed:.1f}s  ·  "
            f"{total_slides} slides → {out_pages} pages  ·  "
            f"{size_kb:.0f} KB"
        )

        base_name = os.path.splitext(uploaded.name)[0]
        st.download_button(
            label="⬇  Download Handout PDF",
            data=output_bytes,
            file_name=f"{base_name}_handout.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

        st.info(
            "💡 **Tip:** For physical printing, use **200–300 DPI** for sharper text. "
            "Use **2 slides/page** for larger text size, **6 slides/page** for ultra-compact notes."
        )

else:
    st.markdown(
        '<div style="color:#3d4060;font-size:0.9rem;margin-top:0.5rem;">'
        'No file uploaded yet. Select a PDF above to begin.</div>',
        unsafe_allow_html=True,
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    '<div class="footer">Slide Handout Maker · Built with Streamlit + PyMuPDF · '
    'White-background A4 output, no data stored</div>',
    unsafe_allow_html=True,
)
