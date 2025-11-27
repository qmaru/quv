import asyncio
import os
import threading
import time
from pathlib import Path
from tkinter import filedialog, ttk
from urllib.parse import unquote, urlparse

import aiofiles
import httpx
from pymdp.pymdp import MdprMedia


async def get_images(url: str) -> list[str]:
    async with MdprMedia(url) as mdpr:
        image_index = await mdpr.get_image_index()
        return await mdpr.get_image_urls(image_index) if image_index else []


def is_valid_url(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


class MdpTab(ttk.Frame):
    def __init__(self, parent, logger, **kwargs):
        super().__init__(parent, **kwargs)
        self.logger = logger
        self._image_urls: list[str] = []
        self._create_widgets()

    def _create_widgets(self):
        self.input_entry = ttk.Entry(self, width=60)
        self.input_entry.insert(0, "")
        self.input_entry.pack(side="top", padx=(10, 5), pady=10, fill="x", expand=False)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="top", padx=4, pady=(0, 4), anchor="w")

        self.get_btn = ttk.Button(btn_frame, text="Get", command=self._on_get)
        self.get_btn.pack(side="left", padx=4)

        self.download_btn = ttk.Button(
            btn_frame, text="Download", command=self._on_download, state="disabled"
        )
        self.download_btn.pack(side="left", padx=4)

    def _safe_log(self, msg: str, clear: bool = False):
        try:
            if clear:
                self.logger.clear()
            self.logger.log(msg)
        except Exception:
            pass

    def _set_buttons(self, get_enabled: bool | None = None, download_enabled: bool | None = None):
        try:
            if get_enabled is not None:
                self.get_btn.config(state="normal" if get_enabled else "disabled")
            if download_enabled is not None:
                self.download_btn.config(state="normal" if download_enabled else "disabled")
        except Exception:
            pass

    def _on_get(self):
        url = self.input_entry.get().strip()

        if not is_valid_url(url):
            self._safe_log(f"Invalid URL: {url or '<empty>'}", clear=True)
            return

        self._set_buttons(False, False)
        self._image_urls = []
        self._safe_log("Fetching images...")

        threading.Thread(target=self._fetch_images_thread, args=(url,), daemon=True).start()

    def _fetch_images_thread(self, url: str):
        try:
            start = time.perf_counter()
            image_urls = asyncio.run(get_images(url))
            elapsed = time.perf_counter() - start
            data = "\n".join(image_urls) if image_urls else "No images found."
            data = f"{data}\n\nElapsed: {elapsed:.3f}s"
            self._image_urls = image_urls or []
        except Exception as e:
            elapsed = time.perf_counter() - start if "start" in locals() else 0.0
            data = f"Error: {e}\n\nElapsed: {elapsed:.3f}s"
            self._image_urls = []

        def finish():
            self._safe_log(f"----- URL -----\n{url}\n\n----- IMAGES -----\n{data}", clear=True)
            self._set_buttons(True, bool(self._image_urls))

        self.after(0, finish)

    def _on_download(self):
        if not self._image_urls:
            self._safe_log("No images to download. Please click Get first.", clear=True)
            return

        folder = filedialog.askdirectory(title="Choose download folder")
        if not folder:
            return

        self._set_buttons(False, False)
        self._safe_log(f"Starting download: {len(self._image_urls)} images -> {folder}", clear=True)

        threading.Thread(target=self._download_images_thread, args=(folder,), daemon=True).start()

    def _download_images_thread(self, folder: str):
        try:
            data = asyncio.run(self._download_images_async(folder))
        except Exception as e:
            elapsed = 0.0
            data = f"Error: {e}\n\nElapsed: {elapsed:.3f}s"

        def finish():
            self._safe_log(f"----- DOWNLOAD -----\n{data}", clear=True)
            self._set_buttons(True, bool(self._image_urls))

        self.after(0, finish)

    async def _download_images_async(self, folder: str) -> str:
        start = time.perf_counter()
        total = len(self._image_urls)
        successes = 0
        failures = 0
        messages: list[str] = []

        semaphore = asyncio.Semaphore(4)

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:

            async def download_one(idx: int, img_url: str):
                nonlocal successes, failures
                async with semaphore:
                    try:
                        async with client.stream("GET", img_url) as resp:
                            resp.raise_for_status()

                            parsed = urlparse(img_url)
                            name = os.path.basename(unquote(parsed.path)) or f"image_{idx}"
                            dst = Path(folder) / name

                            if dst.exists():
                                stem = dst.stem
                                suffix = dst.suffix
                                k = 1
                                while True:
                                    new_name = f"{stem}_{k}{suffix}"
                                    new_dst = dst.with_name(new_name)
                                    if not new_dst.exists():
                                        dst = new_dst
                                        break
                                    k += 1

                            total_bytes = 0
                            chunk_size = 65536
                            async with aiofiles.open(dst, "wb") as f:
                                async for chunk in resp.aiter_bytes(chunk_size=chunk_size):
                                    if chunk:
                                        await f.write(chunk)
                                        total_bytes += len(chunk)

                        msg = f"[{idx}/{total}] Saved: {dst} ({total_bytes} bytes)"
                        try:
                            self.after(0, lambda m=msg: self.logger.log(m))
                        except Exception:
                            pass
                        successes += 1
                        return msg
                    except Exception as e:
                        msg = f"[{idx}/{total}] Failed: {img_url} -> {e}"
                        try:
                            self.after(0, lambda m=msg: self.logger.log(m))
                        except Exception:
                            pass
                        failures += 1
                        return msg

            tasks = [
                asyncio.create_task(download_one(idx, url))
                for idx, url in enumerate(self._image_urls, start=1)
            ]
            for coro in asyncio.as_completed(tasks):
                msg = await coro
                messages.append(msg)

        elapsed = time.perf_counter() - start
        summary = f"Downloaded: {successes}, Failed: {failures}, Elapsed: {elapsed:.3f}s"
        return "\n".join(messages + ["", summary])


def register(parent, logger):
    tab = MdpTab(parent, logger)
    return tab, "mdpr"
