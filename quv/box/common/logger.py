import tkinter as tk
from tkinter import ttk


class Logger(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.text = tk.Text(self, wrap=tk.WORD)
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.text.grid(row=0, column=0, sticky="nsew", padx=(4, 0), pady=0)
        self.scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 4), pady=4)
        self.text.config(state=tk.DISABLED)

    def log(self, msg):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def clear(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.config(state=tk.DISABLED)
