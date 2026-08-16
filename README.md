# 📄 Slide Handout Maker

Convert any PDF of presentation slides into a print-ready handout
(3 slides per A4 page, white background).

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run locally
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

## Deploy to Streamlit Cloud (Free)

1. Push this folder to a **GitHub repo** (public or private)
2. Go to → https://share.streamlit.io
3. Click **New app** → connect your GitHub repo
4. Set **Main file path** = `app.py`
5. Click **Deploy** — done, get a public URL!

## Settings Available in UI

| Setting | Options | Default |
|---|---|---|
| Slides per page | 2 / 3 / 4 / 6 | 3 |
| Render DPI | 100 / 150 / 200 / 250 / 300 | 150 |
| Page margin | 10–40 pt | 20 |
| Gap between slides | 6–24 pt | 12 |
| Slide border | On / Off | On |
