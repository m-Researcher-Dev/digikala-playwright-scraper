<div align="center">

# 💻 Digikala Laptop Scraper

**A Playwright-based web scraper for Digikala laptop listings, delivered through a Streamlit interface.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40%2B-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

<div dir="rtl">

## 📖 درباره پروژه

**Digikala Laptop Scraper** یک ابزار سبک و ماژولار برای استخراج نام و قیمت لپ‌تاپ‌ها از دسته‌بندی لپ‌تاپ دیجی‌کالا است. این پروژه از **Playwright** برای خودکارسازی مرورگر و از **Streamlit** برای فراهم کردن رابط کاربری وب استفاده می‌کند. خروجی می‌تواند به‌صورت جدول در برنامه نمایش داده شود یا به فایل Excel تبدیل شود.

طراحی پروژه بر پایهٔ جداسازی دغدغه‌ها (separation of concerns) است: منطق راه‌اندازی مرورگر در `playwright_setting.py` و منطق UI و orchestration در `app.py` قرار دارد. این ساختار توسعه، تست و جایگزینی اجزای مختلف را ساده می‌کند.

## ✨ ویژگی‌های کلیدی

- **بدون نیاز به WebDriver دستی** — Playwright چرخهٔ عمر مرورگر و درایور را خودکار مدیریت می‌کند.
- **مقاوم در برابر تشخیص خودکار** — استفاده از user agent واقعی، viewport استاندارد، locale هماهنگ با سایت هدف، تزریق JavaScript قبل از بارگذاری هر صفحه، و حذف نشانگر `navigator.webdriver`.
- **مدیریت محتوای Lazy-load** — اسکرول تدریجی تا زمانی که ارتفاع صفحه پایدار شود.
- **معماری مبتنی بر Callback** — منطق scraping هیچ وابستگی مستقیمی به Streamlit ندارد.
- **نصب خودکار Chromium** — در محیط‌های ابری، اولین اجرا باینری لازم را نصب می‌کند.
- **خروجی Excel آماده** — جدول نتایج با یک کلیک قابل دانلود است.

## 🚀 نصب

```bash
git clone https://github.com/<your-username>/digikala-playwright-scraper.git
cd digikala-playwright-scraper
pip install -r requirements.txt
playwright install chromium
```

## ▶️ اجرا

```bash
streamlit run app.py
```

سپس در مرورگر به آدرس `http://localhost:8501` مراجعه کنید.

**مراحل استفاده:**

1. در نوار کناری، محدودهٔ صفحات (۱ تا ۴۰) را مشخص کنید.
2. گزینه‌های خروجی را انتخاب کنید: نمایش جدول در برنامه و/یا ذخیره در Excel.
3. روی **Start scraping** کلیک کنید.

## 🗂 ساختار پروژه

| فایل | نقش |
| :--- | :--- |
| `playwright_setting.py` | راه‌اندازی مرورگر، anti-detection، اسکرول و توابع استخراج |
| `app.py` | رابط کاربری Streamlit و تابع `scrape_pages` |
| `packages.txt` | وابستگی‌های سیستمی Chromium برای استقرار ابری |
| `requirements.txt` | وابستگی‌های پایتون |

## ⚙️ تنظیمات

پارامترهای اصلی در بالای `playwright_setting.py` قابل تغییر هستند:

| پارامتر | توضیح |
| :--- | :--- |
| `DEFAULT_USER_AGENT` | برای چرخش fingerprint تغییر دهید |
| `DEFAULT_VIEWPORT` | ابعاد پنجرهٔ مرورگر |
| `DEFAULT_LOCALE` / `DEFAULT_TIMEZONE` | هماهنگ با سایت هدف |
| `LAUNCH_ARGS` | فلگ‌های اجرای Chromium |
| `ANTI_DETECTION_SCRIPT` | اسکریپت JS تزریقی قبل از هر بارگذاری |

پارامترهای scraping (آدرس پایه، محدودهٔ قیمت، ترتیب مرتب‌سازی) در `app.py` تعریف شده‌اند.

## ⚠️ محدودیت‌ها

- وابسته به CSS selectorها (`h3`، `span[data-testid="price-final"]`)؛ تغییر frontend دیجی‌کالا ممکن است استخراج را مختل کند.
- بدون proxy rotation؛ اجرای حجم بالا از یک IP ریسک rate limit دارد.
- فقط برای دستهٔ لپ‌تاپ طراحی شده است؛ برای دسته‌های دیگر `BASE_URL` را تغییر دهید.

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر می‌شود. فایل [LICENSE](LICENSE) را ببینید.

</div>

---

## 📖 Overview

**Digikala Laptop Scraper** is a lightweight, modular tool that extracts laptop product names and prices from Digikala's laptop category. It uses **Playwright** for browser automation and **Streamlit** for a web-based interface. Output can be displayed as an in-app table or exported to Excel.

The project follows a separation-of-concerns design: browser orchestration lives in `playwright_setting.py`, while UI and orchestration logic live in `app.py`. This structure keeps the scraping logic testable and independent of the UI framework.

## ✨ Key Features

- **No manual WebDriver setup** — Playwright handles the entire browser and driver lifecycle.
- **Detection-resistant** — realistic user agent, standard viewport, target-site locale, JavaScript injection before every page load, and `navigator.webdriver` suppression.
- **Lazy-load aware** — progressive scrolling until the page height stabilizes.
- **Callback-driven architecture** — scraping logic has zero direct dependency on Streamlit.
- **Automatic Chromium bootstrap** — in cloud environments, the first run installs the required binary.
- **Ready-to-use Excel export** — results downloadable with one click.

## 🚀 Installation

```bash
git clone https://github.com/<your-username>/digikala-playwright-scraper.git
cd digikala-playwright-scraper
pip install -r requirements.txt
playwright install chromium
```

## ▶️ Usage

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

**Steps:**

1. Select a page range (1–40) in the sidebar.
2. Choose output options: inline table and/or Excel export.
3. Click **Start scraping**.

## 🗂 Project Structure

| File | Purpose |
| :--- | :--- |
| `playwright_setting.py` | Browser setup, anti-detection, scrolling, and extraction helpers |
| `app.py` | Streamlit UI and the `scrape_pages` orchestration function |
| `packages.txt` | System-level Chromium dependencies for cloud deployment |
| `requirements.txt` | Python dependencies |

## ⚙️ Configuration

Primary parameters are defined at the top of `playwright_setting.py`:

| Parameter | Description |
| :--- | :--- |
| `DEFAULT_USER_AGENT` | Override to rotate fingerprints |
| `DEFAULT_VIEWPORT` | Browser window size |
| `DEFAULT_LOCALE` / `DEFAULT_TIMEZONE` | Matching the target site |
| `LAUNCH_ARGS` | Chromium launch flags |
| `ANTI_DETECTION_SCRIPT` | JS injected before every page load |

Scraping parameters (base URL, price range, sort order) are defined in `app.py`.

## ⚠️ Limitations

- Depends on CSS selectors (`h3`, `span[data-testid="price-final"]`); a Digikala frontend change may break extraction.
- No proxy rotation; large-scale runs from a single IP risk rate limiting.
- Designed for laptop listings only; adapt `BASE_URL` for other categories.

## 📄 License

Released under the MIT License. See [LICENSE](LICENSE).
