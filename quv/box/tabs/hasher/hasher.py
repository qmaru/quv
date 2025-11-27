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
        self._create_widgets()

    def _create_widgets(self):
        self.input_entry = ttk.Entry(self, width=60)
        self.input_entry.insert(0, "quv box")
        self.input_entry.pack(side="top", padx=(10, 5), pady=10, fill="x", expand=False)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="top", padx=4, pady=(0, 4), anchor="w")

        browse_btn = ttk.Button(btn_frame, text="Browse...", command=self._on_browse)
        browse_btn.pack(side="left", padx=4)

        calc_btn = ttk.Button(btn_frame, text="Calculate", command=self._on_calculate)
        calc_btn.pack(side="left", padx=4)

    def _on_browse(self):
        path = filedialog.askopenfilename(title="Select file")
        if path:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, path)

    def _on_calculate(self):
        value = self.input_entry.get()
        try:
            digest = hash_calc(value)
        except Exception as e:
            digest = f"Error: {e}"

        try:
            self.logger.clear()
            self.logger.log(
                f"----- INPUT -----\n{value}\n\n"
                f"----- HASH -----\n{digest}"
            )
        except Exception:
            pass


def register(parent, logger):
    tab = HashTab(parent, logger)
    return tab, "Blake3"
