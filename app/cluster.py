import json
import requests
from typing import List, Dict
from .vector import Vector
from .post import Post
from .cache import Cache


class Cluster:
    """
    Elasticsearch cluster.
    """

    MAX_SEARCH_SIZE: int = 20
    MAX_DOC_ID_SIZE: int = 5
    MAX_DISCOVERY_SPACE_SIZE: int = 200

    def __init__(self):
        """
        Lazy constructor.
        """
        self.protocol: str = "https"
        self.hostname: str = "localhost"
        self.port: int = 9200
        self.index: str = "default"

    @property
    def api(self) -> str:
        """
        URL getter.
        """
        return f"{self.protocol}://{self.hostname}:{self.port}"

    def post(self, endpoint: str, payload: dict) -> dict:
        """
        Sends POST requests to Elasticsearch.
        """
        url: str = f"{self.api}/{endpoint}"
        print("POST:", url, payload)
        response: requests.Response = requests.post(
            url=url,
            json=payload,
        )
        print(response.status_code, response.reason)
        print(response.headers)
        data: dict = response.json()
        print(json.dumps(data, indent=4, sort_keys=True))
        assert response.status_code in (200, 201), response.text
        return data

    def put(self, endpoint: str, payload: dict) -> dict:
        """
        Sends PUT requests to Elasticsearch.
        """
        url: str = f"{self.api}/{endpoint}"
        print("PUT:", url, payload)
        response: requests.Response = requests.put(
            url=url,
            json=payload,
        )
        print(response.status_code, response.reason)
        print(response.headers)
        assert response.status_code == 200, response.text
        data: dict = response.json()
        print(json.dumps(data, indent=4, sort_keys=True))
        return data

    def init(self):
        """
        Initializes the Elasticsearch index.
        """
        vector: Vector = Vector()
        vector.word = 'dummy'
        mapping: dict = {
            "mappings": {
                "properties": {
                    "vector": {
                        "type": "dense_vector",
                        "dims": len(vector.array),
                        "index": True,
                        "similarity": "cosine",
                    },
                    "word": {
                        "type": "keyword",
                        "index": False,
                    },
                    "slug": {
                        "type": "keyword",
                        "index": False,
                    }
                }
            }
        }
        try:
            self.put(f"{self.index}", mapping)
        except Exception as error:
            if "resource_already_exists_exception" not in str(error):
                raise

    def save(self, post: Post):
        """
        Indexes a Post in Elasticsearch.
        """
        for vector in post.vectors:
            if vector.is_known():
                document: dict = {
                    "vector": vector.to_list(),
                    "keyword": vector.word,
                    "slug": post.slug,
                }
                doc_id: str = f'{vector.word}_{post.slug}'[:self.MAX_DOC_ID_SIZE]
                self.post(f"{self.index}/_doc/{doc_id}", document)

    def search(self, vectors: List[Vector], limit: int = 3) -> List[Post]:
        """
        Indexes a Post in Elasticsearch.
        """
        assert len(vectors) <= self.MAX_SEARCH_SIZE, "Maximum amount of search words reached!"

        # Querying Elastisearch with Painless script.
        script: str = """
            double score = 0;
            for (int i = 0; i < params.query_vectors.length; i++) {
                double similarity = 1.0 + cosineSimilarity(params.query_vectors[i], 'vector');
                score += similarity;
            }
            return score;
        """
        print('Script:', script)
        painless: str = ''
        for line in script.split("\n"):
            line: str = line.strip()
            if line:
                painless += " " + line
        query: dict = {
            "size": self.MAX_DISCOVERY_SPACE_SIZE,
            "fields": [
                "slug",
            ],
            "_source": False,
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": painless,
                        "params": {
                            "query_vectors": [
                                vector.to_list()
                                for vector in vectors
                                if vector.is_known()
                            ]
                        }
                    }
                }
            }
        }
        response: dict = self.post(f"{self.index}/_search", query)

        # Grouping hits by post slug.
        hits: List[dict] = response['hits']['hits']
        scores_by_slug: Dict[str, List[float]] = {}
        for hit in hits:
            print('Hit:', hit)
            slug: str = hit['fields']['slug'][0]
            score: float = hit['_score']
            if slug not in scores_by_slug:
                scores_by_slug[slug] = []
            scores_by_slug[slug].append(score)
        print(json.dumps(scores_by_slug, indent=4))

        # Weighted average score.
        relevance_by_slug: Dict[str, float] = {}
        for slug in scores_by_slug:
            size: int = len(scores_by_slug[slug])
            total: int = sum(scores_by_slug[slug])
            relevance_by_slug[slug] = size * total / size
        print(json.dumps(relevance_by_slug, indent=4))

        # Fetching top posts.
        top_slugs: List[str] = [
            slug
            for slug, score in sorted(relevance_by_slug.items(), key=lambda x: -1 * x[1])
        ][:limit]
        print('Top:', top_slugs)

        # Load Post from the database.
        return [
            Post.load(Cache(slug).load())
            for slug in top_slugs
        ]
