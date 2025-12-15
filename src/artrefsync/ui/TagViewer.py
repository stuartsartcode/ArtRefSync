import os
import tkinter as tk
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from artrefsync.config import config
from artrefsync.constants import E621, TABLE, get_table_mapping
from artrefsync.ui.InputTreeView import InputTreeviewFrame
from artrefsync.ui.ReadTreeView import ReadTreeView
from artrefsync.sync import sync_config
from artrefsync.ui.tabs.ArtistTab import ArtistTab
from artrefsync.ui.tag_post_manager import TagPostManager
from artrefsync.ui.TkThreadCaller import TkThreadCaller

import logging
logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)

class TagViewer:
    def __init__(self, root):
        self.root = root
        self.threads = TkThreadCaller(root)

        self.configure_style(self.root)
        self.menus(self.root)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        self.init_config_tab(self.notebook)
        self.init_artists_tab(self.notebook)

    def configure_style(self, root):
        self.style = ttk.Style()
        self.style.configure("vert.TNotebook", tabposition="wn", tabmargins=(0, 30))
        self.style.configure("vert.TNotebook.Tab", expand=(10, 0, 0, 0))

    def menus(self, root):
        self.menu = ttk.Menu(root)
        self.filemenu = ttk.Menu(self.menu, tearoff=0)
        self.filemenu.add_command(
            label="Edit Config", command=lambda: os.startfile(config.path)
        )
        self.menu.add_cascade(label="File", menu=self.filemenu)
        root.config(menu=self.menu)
        self.menu.add

    def init_config_tab(self, notebook: ttk.Notebook):
        self.config_tab = ttk.Frame(notebook)
        notebook.add(self.config_tab, text="Config")

        self.config_notebook = ttk.Notebook(self.config_tab, style="vert.TNotebook")
        self.config_notebook.pack(expand=True, fill="both", padx=10, pady=10)
        self.config_table_tabs = {}
        self.widget_dict = {}
        self.var_dict = {}
        for table in TABLE:
            tab_frame = ttk.Frame(self.config_notebook)
            if table == TABLE.APP:

                self.save_config_button = ttk.Button(
                    tab_frame, text="Save Config", command=self.save_config
                )
                self.save_config_button.grid(
                    row=1, column=1, sticky=("w", "e"), pady=10, padx=5
                )
                self.start_sync_button = ttk.Button(
                    tab_frame, text="Start Sync", command=self.start_sync
                )
                self.start_sync_button.grid(
                    row=2, column=1, sticky=("w", "e"), pady=10, padx=5
                )

            self.config_table_tabs[table] = tab_frame
            self.widget_dict[table] = {}
            self.var_dict[table] = {}

            for i, table_field in enumerate(get_table_mapping()[table], 3 if table == TABLE.APP else 0):
                lspacer = ttk.Label(tab_frame, text="", width=5)
                lspacer.grid(row=i, column=0, sticky="w", pady=10, padx=5)
                label = ttk.Label(
                    tab_frame, text=f"{table_field.capitalize()}:", width=20
                )
                label.grid(row=i, column=1, sticky="w", pady=10, padx=5)

                if "list" in table_field or "artists" == table_field:
                    list_frame = InputTreeviewFrame(
                        tab_frame, config[table][table_field]
                    )
                    widget = list_frame
                    list_frame.grid(row=i, column=2, sticky=("w", "E"), pady=10)
                else:
                    if "enabled" in table_field:
                        check_var = tk.IntVar()
                        check_var.set(1 if config[table][table_field] else 0)
                        self.var_dict[table][table_field] = check_var
                        entry = ttk.Checkbutton(
                            tab_frame,
                            text="",
                            style="Roundtoggle.Toolbutton",
                            variable=check_var,
                        )
                    elif "api" in table_field or "name" in table_field:
                        entry = ttk.Entry(tab_frame, width=30, show="*")
                        entry.insert(0, config[table][table_field])
                    else:
                        entry = ttk.Entry(
                            tab_frame,
                            width=30,
                        )
                        entry.insert(0, config[table][table_field])
                    entry.grid(row=i, column=2, sticky=("w", "e"), pady=10, padx=5)
                    widget = entry
                self.widget_dict[table][table_field] = widget

            self.config_notebook.add(
                tab_frame,
                text=table.capitalize().ljust(6),
            )

    def save_config(self):
        for table in TABLE:
            for table_field in get_table_mapping()[table]:
                widget = self.widget_dict[table][table_field]
                if isinstance(widget, ttk.Checkbutton):
                    val = self.var_dict[table][table_field].get() == 1
                else:
                    val = widget.get()
                config[table][table_field] = val
        config.settings.update()

    def start_sync(self):
        self.threads.add(sync_config, on_finish=print)

    def start_sync_config(self, data):
        sync_config()

    def init_artists_tab(self, notebook: ttk.Notebook):
        self.artist_tab = ArtistTab(notebook)


if __name__ == "__main__":
    import artrefsync.ui.TagApp as TagApp

    TagApp.main()
