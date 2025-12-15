import pywinstyles
import ttkbootstrap as ttk
import time
import sv_ttk
from PIL import Image, ImageTk
import logging
from artrefsync.config import config

logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)

def main():
    app = ImagViewerApp()
    app.start()

class ImagViewerApp():
    def __init__(self):
        logger.info("Starting App")
        self.stime = time.time()
        self.root = ttk.Window(themename="darkly", size=(1080,1080))
        pywinstyles.apply_style(self.root, "optimised")
        ico = Image.open("resources/small_cat.png")
        photo= ImageTk.PhotoImage(ico)
        self.root.wm_iconphoto(False, photo)
    
    def start(self):
        self.root.after(30, self.after)
        self.root.mainloop()

    def after(self):
        logger.info("Window start time: %s", time.time() - self.stime)
        self.stime=time.time()
        from artrefsync.ui.TagViewer import TagViewer
        self.viewer = TagViewer(self.root)
        logger.info("App start time: %s", time.time() - self.stime)


if __name__ == "__main__":
    main()