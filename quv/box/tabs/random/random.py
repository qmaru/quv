from tkinter import ttk
from quv.random.main import generate_random


class RandomTab(ttk.Frame):
    def __init__(self, parent, logger, **kwargs):
        super().__init__(parent, **kwargs)
        self.logger = logger
        self._create_widgets()

    def _create_widgets(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        btn = ttk.Button(self, text="Generate Random", command=self.generate)
        btn.grid(row=0, column=0, padx=10, pady=10)

    def generate(self):
        self.logger.clear()
        random_values = generate_random()
        output = f"Password:\n{random_values['password']}\n\nSecure:\n{random_values['secure']}\n\nUUID v4\n{random_values['uuidv4']}"
        self.logger.log(output)


def register(parent, logger):
    tab = RandomTab(parent, logger)
    return tab, "random"
