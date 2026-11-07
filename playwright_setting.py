"""
Playwright configuration and helper functions for the digikala-scraper project.
Equivalent of selenium_setting.py + kill_browser.py in the Selenium version.
"""

import os
import subprocess
import time
import random
from typing import Optional, Tuple, List

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeout,
    Page,
    Browser,
    BrowserContext,
    Locator,
)


# ---------- One-time Chromium bootstrap (for cloud environments) ----------

def _ensure_chromium_installed() -> None:
    """Install Chromium on first run in environments without it (e.g. Streamlit Cloud)."""
    marker = os.path.join(os.path.expanduser("~"), ".playwright_installed")
    if os.path.exists(marker):
        return
    try:
        subprocess.run(
            ["playwright", "install", "chromium"],
            check=True,
            capture_output=True,
            timeout=300,
        )
        with open(marker, "w") as f:
            f.write("ok")
    except Exception as e:
        print(f"[playwright_setting] Chromium install skipped: {e}")


_ensure_chromium_installed()


# ---------- Default configuration ----------

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_VIEWPORT = {"width": 1920, "height": 1080}
DEFAULT_LOCALE = "en-US"
DEFAULT_TIMEZONE = "Asia/Tehran"

LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-setuid-sandbox",
]

# Anti-detection script injected before every page load
ANTI_DETECTION_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
window.chrome = { runtime: {} };
"""


# ---------- Humanization helpers ----------

def human_delay(min_sec: float = 1.5, max_sec: float = 3.5) -> None:
    """Randomized delay to mimic human behavior."""
    time.sleep(random.uniform(min_sec, max_sec))


def human_sleep(min_seconds: float = 2.0, max_seconds: float = 4.0) -> None:
    """Alias for human_delay (kept for backward compatibility)."""
    human_delay(min_seconds, max_seconds)


def human_type(
    element: Locator,
    text: str,
    min_delay: float = 0.05,
    max_delay: float = 0.15,
) -> None:
    """Type character by character with randomized delays."""
    for ch in text:
        element.type(ch, delay=random.uniform(min_delay, max_delay) * 1000)


# ---------- Scrolling and waiting ----------

def scroll_to_bottom(
    page: Page,
    max_scrolls: int = 15,
    pause_min: float = 1.0,
    pause_max: float = 2.0,
) -> None:
    """
    Scroll progressively until the page height stabilizes.
    Suitable for pages with lazy-loaded content (e.g., product lists).
    """
    last_height = page.evaluate("document.body.scrollHeight")
    for _ in range(max_scrolls):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        human_delay(pause_min, pause_max)
        new_height = page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    page.evaluate("window.scrollTo(0, 0)")
    human_delay(pause_min, pause_max)


def wait_for_element(
    page: Page,
    selector: str,
    timeout: int = 30000,
    state: str = "visible",
) -> Optional[Locator]:
    """
    Wait for a single element.
    state can be 'attached' | 'detached' | 'visible' | 'hidden'.
    Returns None on timeout.
    """
    try:
        page.wait_for_selector(selector, timeout=timeout, state=state)
        return page.locator(selector).first
    except PlaywrightTimeout:
        return None


def wait_for_elements(
    page: Page,
    selector: str,
    timeout: int = 30000,
    state: str = "visible",
) -> Optional[Locator]:
    """
    Wait for at least one element from a set.
    Returns a Locator on success, None otherwise.
    """
    try:
        page.wait_for_selector(selector, timeout=timeout, state=state)
        return page.locator(selector)
    except PlaywrightTimeout:
        return None


# ---------- Browser construction and cleanup ----------

def create_browser(playwright, headless: bool = True) -> Browser:
    """Launch Chromium with anti-detection flags."""
    try:
        return playwright.chromium.launch(headless=headless, args=LAUNCH_ARGS)
    except Exception as e:
        msg = str(e)
        if "Executable doesn't exist" in msg or "playwright install" in msg:
            raise RuntimeError(
                "Chromium browser is not installed.\n"
                "Please run: playwright install chromium"
            ) from e
        raise


def create_context(
    browser: Browser,
    user_agent: Optional[str] = None,
    viewport: Optional[dict] = None,
    locale: str = DEFAULT_LOCALE,
    timezone_id: str = DEFAULT_TIMEZONE,
) -> BrowserContext:
    """Build a context with a realistic fingerprint and anti-detection script."""
    context = browser.new_context(
        user_agent=user_agent or DEFAULT_USER_AGENT,
        viewport=viewport or DEFAULT_VIEWPORT,
        locale=locale,
        timezone_id=timezone_id,
    )
    context.add_init_script(ANTI_DETECTION_SCRIPT)
    return context


def create_browser_and_context(
    playwright,
    headless: bool = True,
    user_agent: Optional[str] = None,
) -> Tuple[Browser, BrowserContext]:
    """Combine create_browser + create_context in a single call."""
    browser = create_browser(playwright, headless=headless)
    context = create_context(browser, user_agent=user_agent)
    return browser, context


def close_browser(
    browser: Optional[Browser],
    context: Optional[BrowserContext] = None,
) -> None:
    """
    Safely close context and browser. Playwright handles its own
    processes, so no OS-level process killing is needed.
    """
    if context is not None:
        try:
            context.close()
        except Exception:
            pass
    if browser is not None:
        try:
            browser.close()
        except Exception:
            pass


# ---------- Data extraction ----------

def extract_products(
    page: Page,
    name_selector: str = "h3",
    price_selector: str = 'span[data-testid="price-final"]',
    timeout: int = 30000,
) -> Tuple[List[str], List[str]]:
    """
    Extract product names and prices from the current page.
    Lists are aligned and empty strings are dropped.
    """
    page.wait_for_selector(name_selector, timeout=timeout)

    names = [
        n.strip()
        for n in page.locator(name_selector).all_inner_texts()
        if n.strip()
    ]
    prices = [
        p.strip()
        for p in page.locator(price_selector).all_inner_texts()
        if p.strip()
    ]

    n = min(len(names), len(prices))
    return names[:n], prices[:n]
