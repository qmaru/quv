import asyncio
import threading
import time
from tkinter import ttk
from urllib.parse import urlparse

from pymdp.pymdp import MdprMedia


async def get_images(url: str) -> list[str]:
    async with MdprMedia(url) as mdpr:
        image_index = await mdpr.get_image_index()
        if image_index:
            image_urls = await mdpr.get_image_urls(image_index)
            return image_urls
        else:
            return []


def is_valid_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


class MdpTab(ttk.Frame):
    def __init__(self, parent, logger, **kwargs):
        super().__init__(parent, **kwargs)
        self.logger = logger
        self._create_widgets()

    def _create_widgets(self):
        self.input_entry = ttk.Entry(self, width=60)
        self.input_entry.insert(0, "")
        self.input_entry.pack(side="top", padx=(10, 5), pady=10, fill="x", expand=False)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="top", padx=4, pady=(0, 4), anchor="w")

        self.get_btn = ttk.Button(btn_frame, text="Get", command=self._on_get)
        self.get_btn.pack(side="left", padx=4)

    def _on_get(self):
        url = self.input_entry.get().strip()

        if not is_valid_url(url):
            try:
                self.logger.clear()
                self.logger.log(f"Invalid URL: {url or '<empty>'}")
            except Exception:
                pass
            return

        try:
            self.get_btn.config(state="disabled")
            self.logger.log("Fetching images...")
        except Exception:
            pass

        threading.Thread(target=self._fetch_images_thread, args=(url,), daemon=True).start()

    def _fetch_images_thread(self, url: str):
        try:
            start = time.perf_counter()
            image_urls = asyncio.run(get_images(url))
            elapsed = time.perf_counter() - start
            data = "\n".join(image_urls) if image_urls else "No images found."
            data = f"{data}\n\nElapsed: {elapsed:.3f}s"
        except Exception as e:
            elapsed = time.perf_counter() - start if "start" in locals() else 0.0
            data = f"Error: {e}\n\nElapsed: {elapsed:.3f}s"

        def finish():
            try:
                self.logger.clear()
                self.logger.log(f"----- URL -----\n{url}\n\n----- IMAGES -----\n{data}")
            except Exception:
                pass
            try:
                self.get_btn.config(state="normal")
            except Exception:
                pass

        self.after(0, finish)


def register(parent, logger):
    tab = MdpTab(parent, logger)
    return tab, "mdpr"
