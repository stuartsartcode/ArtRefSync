
from dataclasses import dataclass
from typing import List

import dacite

config = dacite.Config(
    cast=[int],
    type_hooks={List[str]: (lambda x: x.split())}
)

@dataclass
class R34_Post():
    height: int
    score: int
    file_url: str
    parent_id: str
    sample_url: str
    sample_width: int
    sample_height: int
    preview_url: str
    rating: str
    tags: List[str]
    id: int
    width: int
    change: int
    md5: str
    creator_id: int
    has_children: str
    created_at: str
    status: str
    source: str
    has_notes: str
    has_comments: str
    preview_width: int
    preview_height: int    
    
def parse_r34_post(post_dict) -> R34_Post:
    return dacite.from_dict(R34_Post, post_dict, config=config)