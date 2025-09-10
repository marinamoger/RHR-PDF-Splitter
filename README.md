# RHR-PDF-Splitter
# Overview Description
Python program that takes a multi-client IRS electronic filing confirmation (RHR) batch PDF and automatically splits it into individual client PDFs. Each output file is named with the client’s name and fiscal year. A cumulative CSV manifest is generated for all runs, making retrieval fast and reliable.

# Use-Case Scenario
Tax firms often receive a single batch PDF containing RHR pages for dozens of clients. Each client’s section starts on a page whose header includes "Product:" and contains a "Name:" line and Fiscal Year Begin/End dates. Manually finding and extracting a single client's proof of e-filing is slow and error-prone.

# What does this program do?
This script automatically:
- Detects the start of each client’s section based on "Product:".
- Collects all pages until the next "Product:" header as belonging to that client.
- Extracts the client’s name from the "Name:" line.
- Extracts the fiscal year from the "Fiscal Year Begin Date".
- Splits the batch PDF into individual client PDFs named "RHR_<Name>_<Year>.pdf".
- Appends an entry to a cumulative manifest.csv.

# Parts of this Repo:
split_rhr.py : the main Python script

sample_batch.pdf : a fake batch PDF containing multiple clients across different years (for demonstration)

RHR_output/ : created automatically at runtime to hold:
- Split client PDFs
- manifest.csv

# Example output using sample_batch.pdf

The provided sample_batch.pdf contains four clients. When processed, the program produces:
- RHR_Doe, John_2022.pdf
- RHR_Smith, Jane_2023.pdf
- RHR_Johnson, Susie_2024.pdf
- RHR_Main Street LLC_2020.pdf

It also appends rows to RHR_output/manifest.csv that record:
- source_pdf
- section_index
- page_start_1based
- page_end_1based
- page_count
- client_name
- fiscal_year
- output_pdf

# HOW TO RUN !
1. Install dependencies:
pip install pdfplumber pypdf

2. Run the script:
python split_rhr.py

**By default it processes sample_batch.pdf. You can adjust the input path inside the script if you want to run it on your own file.**

3. Check RHR_output/ for the results.
