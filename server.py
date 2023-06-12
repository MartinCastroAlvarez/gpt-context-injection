import os
from typing import List
from flask import Flask, request
from app.cache import Cache
from app.vector import Vector
from app.gpt import Gpt
from app.cluster import Cluster
from app.post import Post

Cache.PATH = os.environ.get('BENJI_DATA_PATH', '~/data')
Gpt.API_KEY = os.environ['BENJI_GPT_API_KEY']
Gpt.TEMPERATURE = 0.5
cluster: Cluster = Cluster()
cluster.hostname = os.environ.get('BENJI_SEARCH_HOST', '127.0.0.1')
cluster.port = int(os.environ.get('BENJI_SEARCH_PORT', '9200'))
cluster.protocol = os.environ.get('BENJI_SEARCH_PROTOCOL', 'http')
cluster.index = os.environ.get('BENJI_SEARCH_INDEX', 'benji')

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'GET':
        question: str = request.args.get('question') or ''
        tokens: int = int(request.args.get('tokens') or '1000')
        assert question, request.args
    if request.method == 'POST':
        question: str = request.json.get('question') or ''
        tokens: int = int(request.json.get('tokens') or '1000')
        assert question, request.json
    posts: List[Post] = cluster.search(Vector.to_vectors(question), limit=Gpt.MAX_CONTEXT_DOCUMENTS_SIZE)
    gpt: Gpt = Gpt()
    answer: str = gpt.ask(question=question, context=posts, limit=tokens)
    return {
        'answer': answer,
        'question': question,
        'posts': [
            post.to_small_json()
            for post in posts
        ]
    }


if __name__ == '__main__':
    app.run()
