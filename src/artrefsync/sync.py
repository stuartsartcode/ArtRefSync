from multiprocessing.pool import ThreadPool
import time
from artrefsync.boards.board_handler import ImageBoardHandler
from artrefsync.boards.rule34_handler import R34Handler
from artrefsync.boards.e621_handler import __E621Handler

from artrefsync.stores.storage import ImageStorage
from artrefsync.stores.plain_file_storage import PlainLocalStorage
from artrefsync.stores.eagle_storage import EagleHandler
from artrefsync.config import config
from artrefsync.constants import LOCAL, R34, E621, TABLE,STORE, EAGLE, BOARD, APP
from artrefsync.stores.link_cache import Link_Cache

import logging
logger = logging.getLogger(__name__)
logger.setLevel(config.log_level)

def sync_config():
    print(config)
    limit = config[TABLE.APP][APP.LIMIT]

    stores = []
    if config[TABLE.LOCAL][LOCAL.ENABLED]:
        store = PlainLocalStorage()
        stores.append(store)

    if config[TABLE.EAGLE][EAGLE.ENABLED]:
        store = EagleHandler()
        stores.append(store)

    if config[TABLE.E621][E621.ENABLED]:
        print(f"Syncing {TABLE.E621} with stores: {list(s.get_store() for s in stores)}")
        board = __E621Handler()
        sync(board, stores, limit)

    if config[TABLE.R34][R34.ENABLED]:
        print(f"Syncing {TABLE.R34} with stores: {list(s.get_store() for s in stores)}")
        board = R34Handler()
        sync(board, stores, limit)


def sync(
    board: ImageBoardHandler,
    stores: list[ImageStorage],
    max_per_artist=10000,
):
    print(f"Syncing {board} to {', '.join(board.get_artist_list())}")
    # First, get posts from board
    for artist in board.get_artist_list():

        print(f"{board.get_board()} - Getting external posts meta data for {artist}.")
        posts = board.get_posts(artist)

        with Link_Cache() as cache:
            for store in stores:
                print(f"{store.get_store()} - Getting internal posts meta data for {artist}.")
                store_posts = store.get_posts(board.get_board(), artist)
                missing_posts = set(posts.keys()).difference(set(store_posts.keys()))
                print(f"Missing post count: {len(missing_posts)}")

                if len(missing_posts) == 0:
                    continue

                count = 0

                start_time = time.time()
                with ThreadPool() as pool:
                    cache.set_store_missing_count(store.get_store(), len(missing_posts))
                    print(f"Starting threadpool for {len(missing_posts)}")
                    args = [(posts[pid], cache) for pid in missing_posts]

                    for result in pool.starmap(store.save_post, args):
                        if result.status_code == 200:
                            count += 1
                        else:
                            print("FAILED.")
                execution_time = time.time() - start_time
                print(f"Finished in {execution_time:.2f} seconds")
                
                for retry in range(3):
                    curr_store_posts = store.get_posts(board.get_board(), artist)
                    if len(curr_store_posts) - len(store_posts) < len(missing_posts):
                        print(f"Pausing for {retry+1} seconds. Remaining posts: {len(curr_store_posts) - len(store_posts)}.")
                        time.sleep(retry + 1)
                    else:
                        break