import tkinter as tk
from tkinter import ttk

from quv.box.common.logger import Logger
from quv.box.common.style import init_styles
from quv.box.tabs.hasher.hasher import register as hasher_register
from quv.box.tabs.hello.hello import register as hello_register
from quv.box.tabs.mdp.mdp import register as mdp_register
from quv.box.tabs.random.random import register as random_register

TITLE = "quv Box"
WIDTH = 800
HEIGHT = 600


class QBox(tk.Tk):
    def __init__(self):
        super().__init__()
        init_styles(self)

        self.title(TITLE)
        self.resizable(False, False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WIDTH) // 2
        y = (screen_height - HEIGHT) // 2
        self.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

        self.logger = Logger(self)

        self._create_menu()
        self._create_widgets()
        self._register_tabs()

    def _create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Clear Log", command=self.logger.clear)
        file_menu.add_separator()
        file_menu.add_command(label="Close", command=self.destroy)

        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def _create_widgets(self):
        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.logger.pack(side=tk.BOTTOM, fill=tk.X)

        self.tab_control.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        try:
            self.logger.clear()
        except Exception:
            pass

        self.update_idletasks()
        try:
            sel = self.tab_control.select()
            if sel:
                widget = self.tab_control.nametowidget(sel)
                req_h = widget.winfo_reqheight()
                logger_h = self.logger.winfo_reqheight()
                pad = 32
                new_h = req_h + logger_h + pad
                cur_w = int(self.geometry().split("+")[0].split("x")[0])
                self.geometry(f"{cur_w}x{new_h}")
        except Exception:
            pass

    def _register_tabs(self):
        tabs = [
            hello_register(self.tab_control, self.logger),
            random_register(self.tab_control, self.logger),
            hasher_register(self.tab_control, self.logger),
            mdp_register(self.tab_control, self.logger),
        ]

        for tab_frame, tab_name in tabs:
            self.tab_control.add(tab_frame, text=tab_name)


def cli():
    app = QBox()
    app.mainloop()


if __name__ == "__main__":
    app = QBox()
    app.mainloop()
