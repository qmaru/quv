import threading
from pathlib import Path
from tkinter import filedialog, ttk

from blake3 import blake3


def hash_calc(data: str) -> str:
    try:
        p = Path(data)
        if p.is_file():
            data_bytes = p.read_bytes()
        else:
            data_bytes = str(data).encode("utf-8")
    except Exception:
        data_bytes = str(data).encode("utf-8")

    hasher = blake3()
    hasher.update(data_bytes)
    return hasher.hexdigest()


class HashTab(ttk.Frame):
    def __init__(self, parent, logger, **kwargs):
        super().__init__(parent, **kwargs)
        self.logger = logger
        self.calculating = False
        self._create_widgets()

    def _create_widgets(self):
        self.input_entry = ttk.Entry(self, width=60)
        self.input_entry.insert(0, "quv box")
        self.input_entry.pack(side="top", padx=(10, 5), pady=10, fill="x", expand=False)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="top", padx=4, pady=(0, 4), anchor="w")

        browse_btn = ttk.Button(btn_frame, text="Browse...", command=self._on_browse)
        browse_btn.pack(side="left", padx=4)

        self.calc_btn = ttk.Button(btn_frame, text="Calculate", command=self._on_calculate)
        self.calc_btn.pack(side="left", padx=4)

    def _on_browse(self):
        path = filedialog.askopenfilename(title="Select file")
        if path:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, path)

    def _on_calculate(self):
        if self.calculating:
            return

        value = self.input_entry.get()
        self.calculating = True
        self.calc_btn.config(state="disabled")

        try:
            self.logger.clear()
            self.logger.log("Calculating hash, please wait...")
        except Exception:
            pass

        # 在后台线程中执行哈希计算
        thread = threading.Thread(target=self._calculate_hash, args=(value,), daemon=True)
        thread.start()

    def _calculate_hash(self, value):
        try:
            digest = hash_calc(value)
            error_msg = None
        except Exception as e:
            digest = None
            error_msg = str(e)

        self.after(0, self._update_result, value, digest, error_msg)

    def _update_result(self, value, digest, error_msg):
        try:
            self.logger.clear()
            if error_msg:
                self.logger.log(f"----- INPUT -----\n{value}\n\n----- ERROR -----\n{error_msg}")
            else:
                self.logger.log(f"----- INPUT -----\n{value}\n\n----- HASH -----\n{digest}")
        except Exception:
            pass
        finally:
            self.calculating = False
            self.calc_btn.config(state="normal")


def register(parent, logger):
    tab = HashTab(parent, logger)
    return tab, "blake3"
