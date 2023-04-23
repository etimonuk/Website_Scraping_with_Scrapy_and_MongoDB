from dataclasses import dataclass
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


@dataclass
class LogrocketArticleItem:
    _id: str
    heading: str
    url: str
    author: str
    published_on: str
    read_time: str


@dataclass
class LogrocketArticleCommentItem:
    _id: str
    author: str
    content: str
    published: str
