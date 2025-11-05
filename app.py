import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# --- CONFIG ---
CSV_FILE = "test.txt"
CLOUDFRONT_BASE = "https://d3b45akprxecp4.cloudfront.net/GTSD-220-test/"
MAX_WORKERS = 10

st.title("🔥 CloudFront Cache Warmer")

st.markdown("""
This app warms your CloudFront cache by sending parallel `HEAD` requests  
for each file listed in `test.txt`.
""")

if not os.path.exists(CSV_FILE):
    st.error(f"File `{CSV_FILE}` not found.")
    st.stop()

if st.button("🚀 Start Warming"):
    # Datei einlesen
    urls = []
    with open(CSV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if not line.startswith("http"):
                line = CLOUDFRONT_BASE.rstrip("/") + "/" + line
            urls.append(line)

    st.info(f"Loaded **{len(urls)} URLs** from `{CSV_FILE}`")

    progress = st.progress(0)
    status_area = st.empty()
    completed = 0

    def warm_url(url):
        try:
            r = requests.head(url, timeout=10)
            return url, r.status_code, r.headers.get("x-cache", "N/A")
        except Exception as e:
            return url, None, str(e)

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(warm_url, url) for url in urls]
        for future in as_completed(futures):
            url, code, info = future.result()
            completed += 1
            progress.progress(completed / len(urls))
            status_area.write(f"{completed}/{len(urls)} — {url} → {code or 'ERR'} ({info})")
            results.append((url, code, info))

    st.success("✅ Cache warming complete!")
    st.write("Results:")
    st.dataframe(results)
