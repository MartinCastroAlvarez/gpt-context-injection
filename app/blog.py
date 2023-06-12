import json
from typing import Generator
from typing import Union

import requests

from .post import Post


class Blog:
    """
    Wordpress Blog.
    """

    def __init__(self):
        """
        Lazy constructor.
        """
        self.protocol: str = "https"
        self.username: str = ""
        self.password: str = ""
        self.hostname: str = ""

    @property
    def api(self) -> str:
        """
        API getter.
        """
        return f"{self.protocol}://{self.hostname}/wp-json/wp"

    @property
    def auth(self) -> tuple:
        """
        Auth credentials getter.
        """
        return (self.username, self.password)

    def get(self, endpoint: str, params: dict) -> Union[dict, list]:
        """
        Sends GET requests to Wordpress.
        """
        url: str = f"{self.api}/{endpoint}"
        print("GET:", url, params)
        response: requests.Response = requests.get(
            url=url,
            params=params,
            auth=self.auth,
        )
        print(response.status_code, response.reason)
        print(response.headers)
        if "rest_post_invalid_page_number" in str(response.text):
            return []
        assert response.status_code == 200, response.text
        data: Union[dict, list] = response.json()
        print(json.dumps(data, indent=4, sort_keys=True))
        return data

    def get_posts(self, page_size: int = 20) -> Generator[Post, None, None]:
        """
        Iterates over the list of all Posts.
        """
        params: dict = {"status": "publish", "limit": page_size}
        params['page'] = 1
        while True:
            rows: list = self.get("v2/posts", params)
            if not rows:
                return
            for row in rows:
                post: Post = Post()
                post.title = row["yoast_head_json"]["og_title"]
                post.description = row["yoast_head_json"]["og_description"]
                post.image_url = row["yoast_head_json"]["og_image"][0]["url"]
                post.date = row["yoast_head_json"]["article_published_time"][:10]
                post.url = row["yoast_head_json"]["og_url"]
                post.content = row["content"]["rendered"]
                yield post
            params['page'] += 1

