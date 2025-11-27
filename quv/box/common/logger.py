import tkinter as tk
from tkinter import ttk

from quv.box.common.style import FONT_MAIN


class Logger(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.text = tk.Text(self, wrap=tk.WORD, font=FONT_MAIN)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.text.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 8), pady=8)
        self.text.config(state=tk.DISABLED, padx=8, pady=8)

    def log(self, msg):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def clear(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.config(state=tk.DISABLED)
