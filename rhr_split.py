import re
from pathlib import Path
import csv
import pdfplumber
from pypdf import PdfReader, PdfWriter

# Config
INPUT_PDF = Path("sample_batch.pdf")   # change as needed

OUTPUT_DIR = Path("RHR_output")
OUTPUT_DIR.mkdir(exist_ok=True)
MANIFEST_PATH = OUTPUT_DIR / "manifest.csv"

NAME_REGEX = re.compile(r"Name:\s*(?P<name>.+?)(?:\s+e-Postmark|$|\n|\r)")
YEAR_REGEX = re.compile(r"Fiscal Year (?:Begin|End) Date:\s*\d{2}/\d{2}/(?P<year>20\d{2})", re.IGNORECASE)
PRODUCT_MARKER = "Product:"

# Helpers 
def open_manifest_for_append(path: Path):
    file_exists = path.exists()
    f = open(path, "a", newline="", encoding="utf-8")
    fieldnames = [
        "source_pdf",
        "section_index",
        "page_start_1based",
        "page_end_1based",
        "page_count",
        "client_name",
        "fiscal_year",
        "output_pdf",
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    if not file_exists or path.stat().st_size == 0:
        writer.writeheader()
    return f, writer

def extract_name(text: str) -> str:
    m = NAME_REGEX.search(text or "")
    return m.group("name").strip() if m else None

def extract_year(text: str) -> str:
    m = YEAR_REGEX.search(text or "")
    return m.group("year") if m else None

# Build section ranges 
with pdfplumber.open(str(INPUT_PDF)) as pdf:
    # Optional debug: returns the first 200 characters of each page to preview accuracy
    # for i, page in enumerate(pdf.pages):
    #     text = page.extract_text() or ""
    #     print(f"Page {i+1}:\n{text[:200]}...\n")

    starts = []
    for i, page in enumerate(pdf.pages):
        if PRODUCT_MARKER in (page.extract_text() or ""):
            starts.append(i)

    ranges = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] - 1 if idx + 1 < len(starts) else len(pdf.pages) - 1
        ranges.append((start, end))

# Split & write + manifest 
reader = PdfReader(str(INPUT_PDF))
mf, mwriter = open_manifest_for_append(MANIFEST_PATH)

try:
    for sec_idx, (p0, p1) in enumerate(ranges, start=1):
        # Parse name/year from the first page of the section
        with pdfplumber.open(str(INPUT_PDF)) as pdf_for_section:
            first_page_text = pdf_for_section.pages[p0].extract_text() or ""

        name = extract_name(first_page_text)
        year = extract_year(first_page_text)

        # Throw error if no name or year
        if not name:
            raise ValueError(f"Name not found in section starting page {p0+1}")
        if not year:
            raise ValueError(f"Year not found in section starting page {p0+1}")

        # Write the section PDF
        writer = PdfWriter()
        for pi in range(p0, p1 + 1):
            writer.add_page(reader.pages[pi])

        outname = f"{name}_{year}_RHR.pdf"
        outpath = OUTPUT_DIR / outname
        with open(outpath, "wb") as f:
            writer.write(f)

        # Append manifest row
        mwriter.writerow({
            "source_pdf": str(INPUT_PDF),
            "section_index": sec_idx,
            "page_start_1based": p0 + 1,
            "page_end_1based": p1 + 1,
            "page_count": (p1 - p0 + 1),
            "client_name": name,
            "fiscal_year": year,
            "output_pdf": str(outpath),
        })

        print(f"Wrote: {outpath}")

finally:
    mf.close()
