from collections import deque
import dacite
import queue
import requests
import json
import time
from artrefsync.models import EagleItem
from urllib import parse
from artrefsync.stores.link_cache import Link_Cache
from artrefsync.stores.storage import ImageStorage, Post
from artrefsync.constants import BOARD, EAGLE, STORE, STATS
from artrefsync.config import config
from artrefsync.stats import stats
import tempfile
from artrefsync.snail import loading

import logging
logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)

def main():

    # eagle = EagleHandler()
    # print("ARTIST ID")
    # print(eagle.artists_id)
    # print("BOARD DICT")
    # print(eagle.board_dict)
    # print(eagle.board_artist_dict)
    # output = eagle.post_create_folder("test2", eagle.board_dict[BOARD.E621])
    # print(eagle.board_artist_dict[BOARD.E621]["diives"])
    # print(eagle.get_posts(BOARD.E621, "diives"))
    eagle.get_post_tag_dict()
    for board in [BOARD.R34]:
        for artist in eagle.board_artist_dict[board]:
            folder = eagle.board_artist_dict[board][artist]
            for post in eagle.get_list_items(folders=folder):
                print(post.id)

            # print(f"{artist} {folder} {len()}")
    
        



class EagleHandler(ImageStorage):
    """
    Helper class for interacting with Eagle using https://api.eagle.cool/
    """
    


    def __init__(self):
        logger.info("Initializing Eagle Handler")
        self.reload_config()

    def reload_config(self):
        self.library = config[STORE.EAGLE][EAGLE.LIBRARY].strip()
        self.artists_folder_name = config[STORE.EAGLE][EAGLE.ARTIST_FOLDER].strip()
        eagle_url = config[STORE.EAGLE][EAGLE.ENDPOINT].strip()
        self.eagle_url = eagle_url if eagle_url else "http://localhost:41595/api"
        self.artists_id = None
        self.artist_folder_set = set()
        self.board_dict = {}
        self.board_artist_dict = {}

        if self.artists_folder_name == "":
            self.artists_folder_name = "artists"

        self.switch_libary(self.library)

        self.get_or_create_artist_folder()
        logger.debug("%s \n%s", "Board Artist dict:", self.board_artist_dict)

    def get_store(self):
        return STORE.EAGLE


    def post_create_folder(self, folder_name, parent_id) -> dict:
        data = {"folderName": folder_name, "parent": parent_id}
        try:
            response = requests.post(
                "http://localhost:41595/api/folder/create", data=json.dumps(data)
            )
            return json.loads(response.content)["data"]
        except Exception as e:
            print("Failed to create folder for {folder_name} with parent {parent_id}")
            print(e)
            stats.add(STATS.FAILED_COUNT, 1)
            return {}

    def post_add_from_path(self, post: Post, path: str):
        artist_folder = self.board_artist_dict[post.board][post.artist_name]
        request_data = {
            "path": path,
            "name": post.name,
            "website": post.website,
            "tags": post.tags,
            "folderId": artist_folder,
        }
        # time.sleep(1)
        response =  requests.post(
            self.api_endpoint("item/addFromPath"), data=json.dumps(request_data)
        )
        return response

    def get_list_items(self, limit=1000, folders=None) -> list[EagleItem]:
        eagle_url = f"http://localhost:41595/api/item/list"

        data = []
        for offset in range(100):
            suffix = []
            if limit:
                suffix.append(f"limit={limit}")
            if offset:
                suffix.append(f"offset={offset}")
            if folders:
                suffix.append(f"folders={folders}")
            suffix = "&".join(suffix)
            if len(suffix) > 0:
                eagle_url = f"{eagle_url}?{suffix}"
            response = requests.get(eagle_url)
            response_dict = json.loads(response.content)["data"]
            # print(response_dict[0])

            data.extend([dacite.from_dict(EagleItem, item) for item in response_dict])
            print(f"Page {offset} total: {len(data)}")
            if len(response_dict) < limit:
                break
        return data

    def post_update_post(self, id, tags=None, url=None):
        eagle_url = "http://localhost:41595/api/item/update"

        data = {"id": id, "tags": tags}
        if url:
            data["url"] = url
        response = requests.post(eagle_url, json.dumps(data))
        return response
    
    def get_post_tag_dict(self):
        limit = 10000
        data = self.get_list_items(limit)

        items = {}
        for item in data:
            artists= item.folders
            if artists == "":
                continue
            in_artist_folder = False
            for ar in artists:
                if ar in self.artist_folder_set:
                    in_artist_folder = True
                    break
            if not in_artist_folder:
                continue



            name = Post.parse_id(item.name)
            # name = str(item["name"].split("-")[0]).zfill(8)
            items[name] = {
                "id": item.id,
                "tags": item.tags,
                "folder": item.folders[0],
                "file": f"{self.library_path_dict[self.library + ".library"]}/images/{item.id}.info/{item.name}.{item.ext}"
            }
        return items

        
    
    

    # Assuming that we will always call get_posts before save_posts
    def get_posts(self, board: BOARD, artist: str):
        folder_created = False
        # Create board folder if not exists
        if board not in self.board_dict:
            board_folder = self.post_create_folder(board, self.artists_id)
            board_name = board_folder["name"]
            self.board_dict[board_folder["name"]] = board_folder["id"]
            self.board_artist_dict[board_name] = {}
            folder_created = True

        # Create board folder if not exists
        if artist not in self.board_artist_dict[board]:
            artist_folder = self.post_create_folder(artist, self.board_dict[board])
            self.board_artist_dict[board][artist] = artist_folder["id"]
            folder_created = True

        if folder_created:
            return {}

        limit = 1000
        data = self.get_list_items(limit,  self.board_artist_dict[board][artist])
        items = {}
        for item in data:
            name = str(item["name"].split("-")[0]).zfill(8)
            items[name] = item["id"]

        print(f" Eagle Items: {len(items)}")
        return items

    def save_post(self, post: Post, link_cache: Link_Cache = None):
        if link_cache:
            loading(link_cache.increment_store_count(self.get_store())/link_cache.get_store_missing(self.get_store()))
            response = self.post_add_from_path(post, link_cache.get_file_from_link(post.url))
        else:
            suffix = f".{post.url.split(".")[-1]}"
            with tempfile.NamedTemporaryFile(mode="wb", suffix=suffix) as f:
                Link_Cache.download_link_to_file(post.url, tempfile)
                response = self.post_add_from_path(post, f.name)
        
    
        return response
        
            

    def update_post(self, post: Post):
        pass

    def get_or_create_artist_folder(self):

        response = requests.get("http://localhost:41595/api/folder/list")
        folders = json.loads(response.content)["data"]

        folder_q = deque((folder for folder in folders))
        artists_folder: dict = None

        while folder_q:
            folder = folder_q.popleft()
            if folder["name"] == self.artists_folder_name:
                artists_folder = folder
                break
        if not artists_folder:
            data = {
                "folderName": self.artists_folder_name,
            }
            print(f"{self.get_store()} Creating Folder {data["folderName"]}")
            response = requests.post(
                "http://localhost:41595/api/folder/create", data=json.dumps(data)
            )
            artists_folder = json.loads(response.content)["data"]
            # print(response)
        self.artists_id = artists_folder["id"]

        for board in artists_folder["children"]:
            board_name = board["name"]
            self.board_dict[board_name] = board["id"]
            self.board_artist_dict[board_name] = {}
            for artist in board["children"]:
                artist_name = artist["name"]
                self.board_artist_dict[board_name][artist_name] = artist["id"]
                self.artist_folder_set.add(artist["id"])


    def get_library_dict(self):
        if not hasattr(self, "library_path_dict"):
            response = requests.get("http://localhost:41595/api/library/history")
            self.library_path_dict = {}

            for path in json.loads(response.content)["data"]:
                p = path.split("\\")
                self.library_path_dict[p[-1]] = "/".join(p)
        return self.library_path_dict

    def switch_libary(self, library_string):
        try:
            data = {"libraryPath": self.get_library_dict()[f"{library_string}.library"]}
            response = requests.post(
                "http://localhost:41595/api/library/switch", data=json.dumps(data)
            )
            logger.debug(response.status_code)
            logger.debug(response.content)
        except Exception as e:
            logger.error(e)

    def api_endpoint(self, path):
        return f"{self.eagle_url}/{path}"

eagle = EagleHandler()


if __name__ == "__main__":
    main()
