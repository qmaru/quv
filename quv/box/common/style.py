import tkinter as tk
from tkinter import ttk

FONT_MAIN = ("Helvetica", 10)
FONT_SMALL = ("Helvetica", 9)


def init_styles(root: tk.Tk | None = None) -> ttk.Style:
    style = ttk.Style(root) if root is not None else ttk.Style()

    for theme in ("vista", "clam", "alt", "default"):
        try:
            style.theme_use(theme)
            break
        except Exception:
            continue

    style.configure(".", font=FONT_MAIN)
    style.configure("TLabel", font=FONT_MAIN)
    style.configure("TButton", font=FONT_MAIN, padding=(6, 4))
    style.configure("TEntry", font=FONT_MAIN)
    style.configure("TNotebook.Tab", font=FONT_SMALL, padding=(8, 4))

    return style
