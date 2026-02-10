from datetime import datetime
from tkinter import ttk

from quv.utils.catsay import catsay


class HelloTab(ttk.Frame):
    def __init__(self, parent, logger, **kwargs):
        super().__init__(parent, **kwargs)
        self.logger = logger
        self._create_widgets()

    def _create_widgets(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        btn = ttk.Button(self, text="Say Hello", command=self.say_hello)
        btn.grid(row=0, column=0, padx=10, pady=10)

    def say_hello(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.clear()
        self.logger.log(f"{now}\n{catsay('quv box meow')}")


def register(parent, logger):
    tab = HelloTab(parent, logger)
    return tab, "hello"
