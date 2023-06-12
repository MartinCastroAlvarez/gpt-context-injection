from typing import List
from slugify import slugify
from .parser import Parser
from .cache import Cache
from .vector import Vector


class Post:
    """
    Wordpress Blog Post.
    """

    def __init__(self):
        """
        Lazy constructor.
        """
        self.title: str = ''
        self.content: str = ''
        self.image_url: str = ''
        self.date: str = ''
        self.url: str = ''
        self.description: str = ''
        self.summary: str = ''
        self.goal: str = ''
        self.keywords: List[str] = []
        self.vectors: List[Vector] = []

    @property
    def slug(self) -> str:
        """
        Slugifies the post title.
        """
        return slugify(self.title)

    @property
    def paragraphs(self) -> List[str]:
        """
        Parsed HTML text.
        """
        parser: Parser = Parser()
        parser.feed(self.content)
        return parser.data

    def to_json(self) -> dict:
        """
        JSON serializer.
        """
        return {
            "title": self.title,
            "slug": self.slug,
            "date": self.date,
            "content": self.content,
            "image_url": self.image_url,
            "url": self.url,
            "paragraphs": self.paragraphs,
            "description": self.description,
            "summary": self.summary,
            "goal": self.goal,
            "keywords": self.keywords,
            "vectors": [
                vector.to_json()
                for vector in self.vectors
            ],
        }

    def to_small_json(self) -> dict:
        """
        JSON serializer.
        """
        return {
            "title": self.title,
            "date": self.date,
            "image_url": self.image_url,
            "url": self.url,
            "summary": self.summary,
            "keywords": self.keywords,
        }

    @classmethod
    def load(cls, data: dict) -> 'Post':
        """
        JSON deserializer.
        """
        post: 'Post' = cls()
        post.title = data.get("title", "")
        post.date = data.get("date", "")
        post.image_url = data.get("image_url", "")
        post.url = data.get("url", "")
        post.description = data.get("description", "")
        post.content = data.get("content", "")
        post.summary = data.get("summary", "")
        post.goal = data.get("goal", "")
        if data.get('keywords') and all([isinstance(keyword, str) for keyword in data['keywords']]):
            post.keywords = data['keywords']
        if data.get('vectors'):
            post.vectors = [
                Vector.load(vector)
                for vector in data['vectors']
                if vector['word']
            ]
        return post

    def save(self):
        """
        Saves a post to a cache file.
        """
        cache: Cache = Cache(self.slug)
        cache.save(self.to_json())
