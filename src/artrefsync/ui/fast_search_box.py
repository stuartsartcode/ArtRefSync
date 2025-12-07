from typing import Iterable
import ttkbootstrap as ttk
from fast_autocomplete import AutoComplete
from artrefsync.config import Config
from artrefsync.constants import E621, TABLE

def main():
    root = ttk.Window(themename="darkly", size=(1080,1080))
    config = Config()
    tree_frame = FastFilterTreeView(root, config[TABLE.E621][E621.ARTISTS])
    tree_frame.grid(row=1, column=1, padx= 10, pady=10, sticky=("w", "e"))
    root.mainloop()

class FastFilterTreeView(ttk.Frame):
    def __init__(self, root, input_list: Iterable):
        super().__init__(root)

        entry_frame = ttk.Frame(self)
        entry_frame.pack(side="top", fill="x")
        entry = ttk.Entry(entry_frame)
        entry.pack(side="left")
        button = ttk.Button(entry_frame)
        button.pack(side="left")

        tree_frame = ttk.Frame(self)
        tree_frame.pack(side="bottom", fill="both", pady=10)
        tree = ttk.Treeview(tree_frame, columns=("Artists"), show="")
        tree.column("Artists", anchor="w")

        scroll = ttk.Scrollbar(tree_frame,orient="vertical",command=tree.yview)

        tree.pack(side = "left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        tree.configure(yscrollcommand=scroll.set)
        
        
        for j, val in enumerate(input_list):
            tree.insert("", "end", iid=str(j), values=(val,))
            print(f"Adding {val} with id: {j}")


        
if __name__ == "__main__":
    main()
        

        




