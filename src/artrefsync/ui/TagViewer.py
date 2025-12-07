import ttkbootstrap as ttk
import tkinter as tk
from artrefsync.config import Config
from artrefsync.constants import TABLE, get_table_mapping
from PIL import Image, ImageTk
import os
from artrefsync.ui.filtering_search import SearchableComboBox

def main():
    config = Config()
    app = ImagViewerApp(config)
    app.start()
    

class ImagViewerApp():
    def __init__(self, config:Config):
        self.config = config
        self.root = ttk.Window(themename="darkly", size=(1080,1080))
        self.configure_style(self.root)

        ico = Image.open("resources/small_cat.png")
        photo= ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)
        self.menus(self.root)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        self.init_config_tab(self.notebook)
        self.init_artists_tab(self.notebook)
        self.config_tab

    def configure_style(self, root):
        self.style = ttk.Style()
        self.style.configure("vert.TNotebook", tabposition = "wn", tabmargins = (5,5))
        self.style.configure("vert.TNotebook.Tab", expand = (10,0,0,0))


    def menus(self, root):
        self.menu = ttk.Menu(root)
        self.filemenu = ttk.Menu(self.menu, tearoff=0)
        self.filemenu.add_command(label="Edit Config", command=lambda: os.startfile(self.config.path))
        self.menu.add_cascade(label="File", menu=self.filemenu)
        root.config(menu=self.menu)
        self.menu.add



        
    def init_config_tab(self, notebook):
        self.config_tab = ttk.Frame(notebook)   
        notebook.add(self.config_tab, text = "Config")

        self.config_notebook = ttk.Notebook(self.config_tab, style="vert.TNotebook")
        self.config_notebook.pack(expand=True, fill='both', padx=10, pady=10)
        self.config_table_tabs = {}
        for table in TABLE:
            tab_frame = ttk.Frame(self.config_notebook)
            self.config_table_tabs[table] = tab_frame

            for i, table_field in enumerate(get_table_mapping()[table]):
                lspacer = ttk.Label(tab_frame, text="", width=5)
                lspacer.grid(row=i, column=0, sticky='w', pady=10, padx=5)
                label = ttk.Label(tab_frame, text=f"{table_field.capitalize()}:", width= 20)
                label.grid(row=i, column=1, sticky='w', pady=10, padx=5)
                
                if "list" in table_field or 'artists' == table_field:
                    list_frame = ttk.Frame(tab_frame)
                    list_entry = ttk.Entry(list_frame)
                    list_entry.pack(fill="x", side="top")
                    bar_frame = ttk.Frame(list_frame)
                    bar_frame.pack(fill="both", side="bottom", expand=True)
                    entry = ttk.Treeview(bar_frame,columns=("List",), show="", height= 10)
                    entry.column("List", anchor="w")

                    for j, val in enumerate(self.config[table][table_field]):
                        entry.insert("", "end", iid=str(j), values=(val,))
                        print(f"Adding {val} from {table}{table_field}")
                    entry.pack(fill="both", side="left", expand=True)
                    # entry.grid(row=i, column=2, sticky=('w', 'e'), pady=10, padx=0)
                    scrollbar = ttk.Scrollbar(bar_frame, orient="vertical", command=entry.yview)
                    # scrollbar.grid(row=i, column=3, sticky=('n', 's'), pady=10, padx=0, )
                    # scrollbar.pack(side="right", fill="y")
                    scrollbar.pack(side="right", fill="y")
                    entry.configure(yscrollcommand=scrollbar.set)
                    list_frame.grid(row=i, column=2, sticky=("w", "E"), pady=10)
                else:
                    if "enabled" in table_field:
                        check_var = tk.IntVar()
                        check_var.set(1 if self.config[table][table_field] else 0)
                        # entry = ttk.Combobox(tab_frame, textvariable=selected_option, state="readonly")
                        # entry['values'] = 
                        entry = ttk.Checkbutton(tab_frame, text="", style='Roundtoggle.Toolbutton', variable=check_var)
                    elif "api" in table_field or "name" in table_field:
                        entry = ttk.Entry(tab_frame, width= 30, show="*")
                        entry.insert(0,self.config[table][table_field])
                    else:
                        entry = ttk.Entry(tab_frame, width=30, )
                        entry.insert(0,self.config[table][table_field])
                    entry.grid(row=i, column=2, sticky=('w', 'e'), pady=10, padx=5)

            self.config_notebook.add(tab_frame, text = table.capitalize())
        

    
    def init_artists_tab(self, notebook):
        self.artists_tab = ttk.Frame(notebook)
        notebook.add(self.artists_tab, text = "artists")
        label2 = ttk.Label(self.artists_tab, text="artists text")
        label2.pack()





        
    def start(self):
        self.root.mainloop()



if __name__ == "__main__":
    main()