from sortedcontainers import SortedSet
import ttkbootstrap as ttk
from PIL import Image, ImageTk

from artrefsync.constants import E621, R34, TABLE
from artrefsync.config import config


import logging
logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)

class ArtistTab(ttk.Frame):

    def __init__(self, notebook):
        super().__init__(notebook)
        # self.artists_tab = ttk.Frame(notebook)
        notebook.add(self, text = "artists")
        self.artists = {
            TABLE.E621: set(config[TABLE.E621][E621.ARTISTS]),
            TABLE.R34: set(config[TABLE.R34][R34.ARTISTS]),
        }

        self.set_icon_map(16)


        self.artist_set = SortedSet(set().union(*self.artists.values()))
        self.artist_tree = ttk.Treeview(self, columns=("Name",))
        scroll = ttk.Scrollbar(self, orient="vertical",command=self.artist_tree.yview)
        self.artist_tree.configure(yscrollcommand=scroll.set)


        
        self.artist_tree.column("#0", width = 40, stretch=0, anchor='w')

        # self.artist_tree.column("#1", width = 20, stretch=0)
        self.init_artists_tree()

        # (self.artists_tab, artists)
        self.artist_tree.pack(side="left", fill="y")
        scroll.pack(side="right", fill="y")
    
    def set_icon_map(self, size = 24):
        self.icon_map = {}
        for table, icon in [(TABLE.E621, "resources/favicon-32x32.png"), (TABLE.R34,"resources/apple-touch-icon-precomposed.png")]:
            image = Image.open(icon)
            image.thumbnail((size, size))
            self.icon_map[table] = ImageTk.PhotoImage(image)
    
    def init_artists_tree(self):
        artists = self.artists
        atree = self.artist_tree
        aset = self.artist_set
        for table in [TABLE.E621, TABLE.R34]:
            atree.insert("", "end", iid=table, image=self.icon_map[table], values=(table), open=True)
            for artist in aset:
                if artist in artists[table]:
                    atree.insert(table, "end", iid=artist, values=(f"  {artist}",), image=self.icon_map[table])