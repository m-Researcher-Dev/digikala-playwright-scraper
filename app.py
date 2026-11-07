"""
Digikala laptop scraper - Playwright version.
Only UI and scraping logic live here. Browser setup is in playwright_setting.py.
"""

import streamlit as st
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from typing import Callable, Optional

from playwright_setting import (
    create_browser_and_context,
    close_browser,
    human_delay,
    scroll_to_bottom,
    extract_products,
)


# ---------- Constants ----------

BASE_URL = "https://www.digikala.com/search/notebook-netbook-ultrabook/"
QUERY_STRING = (
    "?price%5Bmin%5D=10000000"
    "&price%5Bmax%5D=700000000"
    "&q=laptop"
    "&sort=20"
)

MAX_PAGES = 40


def build_url(page_num: int) -> str:
    return f"{BASE_URL}{QUERY_STRING}&page={page_num}"


# ---------- Scraping logic ----------

def scrape_pages(
    min_page: int,
    max_page: int,
    progress_callback: Optional[Callable[[int], None]] = None,
    status_callback: Optional[Callable[[str], None]] = None,
    warning_callback: Optional[Callable[[str], None]] = None,
):
    """
    Walk through the selected page range and return lists of names and prices.
    Callbacks are used to update the UI without coupling the logic to Streamlit.
    """
    all_names: list[str] = []
    all_prices: list[str] = []

    with sync_playwright() as p:
        browser, context = create_browser_and_context(p, headless=True)
        page = context.new_page()
        try:
            total = max_page - min_page + 1
            for idx, page_num in enumerate(range(min_page, max_page + 1)):
                if status_callback:
                    status_callback(f"Processing page {page_num} of {max_page}...")
                if progress_callback:
                    progress_callback(int((idx / total) * 100))

                try:
                    page.goto(
                        build_url(page_num),
                        wait_until="domcontentloaded",
                        timeout=60000,
                    )
                    human_delay(2, 4)
                    scroll_to_bottom(page)
                    names, prices = extract_products(page)
                    all_names.extend(names)
                    all_prices.extend(prices)
                    human_delay(2, 4)
                except PlaywrightTimeout:
                    if warning_callback:
                        warning_callback(f"Timeout on page {page_num}. Skipping.")
                except Exception as e:
                    if warning_callback:
                        warning_callback(f"Error on page {page_num}: {e}")
        finally:
            close_browser(browser, context)

    return all_names, all_prices


# ---------- Streamlit UI ----------

st.set_page_config(
    page_title="Digikala Laptop Scraper (Playwright)",
    page_icon="💻",
    layout="wide",
)

st.title("💻 Digikala Laptop Scraper - Playwright")
st.markdown("---")

with st.expander("Help"):
    st.write(
        """
        - Choose a page range (1 to 40).
        - Export results either inline or as an Excel file.
        - This version uses **Playwright**; no manual driver setup required.
        """
    )

# ---------- Sidebar controls ----------

st.sidebar.header("⚙️ Scraper Settings")
min_page = st.sidebar.number_input("Start page", min_value=1, max_value=MAX_PAGES, value=1)
max_page = st.sidebar.number_input("End page", min_value=1, max_value=MAX_PAGES, value=3)
output_options = st.sidebar.multiselect(
    "Output options",
    ["Show in app", "Save as Excel"],
    default=["Show in app"],
)

# ---------- Run scraping ----------

if st.sidebar.button("🚀 Start scraping", type="primary"):
    if min_page > max_page:
        st.error("Start page must be less than or equal to end page.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        warning_box = st.empty()

        def _warn(msg: str) -> None:
            warning_box.warning(msg)

        try:
            all_names, all_prices = scrape_pages(
                min_page,
                max_page,
                progress_callback=progress_bar.progress,
                status_callback=status_text.text,
                warning_callback=_warn,
            )
        except RuntimeError as e:
            st.error(str(e))
            st.stop()

        progress_bar.progress(100)
        status_text.text("✅ Scraping finished.")

        if not all_names:
            st.warning("No data was extracted. The page structure may have changed.")
            st.stop()

        df = pd.DataFrame({"Product name": all_names, "Price": all_prices})

        if "Show in app" in output_options:
            st.subheader("📋 Scraped results")
            st.dataframe(df, use_container_width=True)

        if "Save as Excel" in output_options:
            output_path = "digikala_laptops.xlsx"
            df.to_excel(output_path, index=False, engine="openpyxl")
            with open(output_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Excel file",
                    data=f,
                    file_name="digikala_laptops.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            st.success(f"📁 Excel file saved to: `{output_path}`")
