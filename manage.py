import json
import begin
from itertools import chain
from app.cache import Cache
from app.blog import Blog
from app.gpt import Gpt
from app.post import Post
from app.vector import Vector
from app.cluster import Cluster


@begin.subcommand
def download(
    username="",
    password="",
    hostname="localhost",
    protocol="http",
    limit=1000,
    cache_dir="data",
):
    """
    Download posts from Wordpress.
    """
    Cache.PATH = cache_dir
    blog: Blog = Blog()
    blog.hostname = hostname
    blog.username = username
    blog.password = password
    blog.protocol = protocol
    for index, post in enumerate(blog.get_posts()):
        print(post.date, post.title)
        post.save()
        if index >= int(limit):
            break


@begin.subcommand
def summarize(
    cache_dir="data",
    gpt_api_key="",
    temperature=0.5,
):
    """
    Summarize posts using GPT.
    """
    Gpt.API_KEY = gpt_api_key
    Gpt.TEMPERATURE = float(temperature)
    Cache.PATH = cache_dir
    gpt: Gpt = Gpt()
    for cache in Cache.all():
        post: Post = Post.load(cache.load())
        print("Post:", post.date, post.title)
        print(post.paragraphs)
        if not post.summary:
            post.summary = gpt.summarize(" ".join(post.paragraphs))
        if not post.keywords:
            post.keywords = gpt.get_keywords(" ".join(post.paragraphs))
        if not post.goal:
            post.goal = gpt.get_goal(" ".join(post.paragraphs))
        post.save()


@begin.subcommand
def vectorize(
    cache_dir="data",
):
    """
    Vectorize posts using SpaCy.
    """
    Cache.PATH = cache_dir
    for cache in Cache.all():
        post: Post = Post.load(cache.load())
        print("Post:", post.date, post.title)
        print(post.paragraphs)
        if not post.vectors:
            post.vectors.extend(Vector.to_vectors(post.keywords))
            post.vectors.extend(Vector.to_vectors(post.summary.split()))
            post.vectors.extend(Vector.to_vectors(post.goal.split()))
            post.save()


@begin.subcommand
def index(
    hostname="localhost",
    protocol="https",
    port=9200,
    index="default",
    cache_dir="data",
):
    """
    Indexes documents in Elasticsearch.
    """
    Cache.PATH = cache_dir
    cluster: Cluster = Cluster()
    cluster.hostname = hostname
    cluster.port = int(port)
    cluster.protocol = protocol
    cluster.index = index
    cluster.init()
    for cache in Cache.all():
        post: Post = Post.load(cache.load())
        print(post.date, post.title)
        cluster.save(post)


@begin.subcommand
def ask(
    question="",
    hostname="localhost",
    protocol="https",
    port=9200,
    index="default",
    cache_dir="data",
    gpt_api_key="",
    temperature=0.5,
    limit=1000,
):
    """
    Asking the ChatBot with Context Injection.
    Searches for documents in Elasticsearch.
    """
    Cache.PATH = cache_dir
    Gpt.API_KEY = gpt_api_key
    Gpt.TEMPERATURE = float(temperature)
    cluster: Cluster = Cluster()
    cluster.hostname = hostname
    cluster.port = int(port)
    cluster.protocol = protocol
    cluster.index = index
    posts: List[Post] = cluster.search(Vector.to_vectors(question), limit=Gpt.MAX_CONTEXT_DOCUMENTS_SIZE)
    gpt: Gpt = Gpt()
    answer: str = gpt.ask(question=question, context=posts, limit=int(limit))
    print("")
    print("Question:", question)
    print("Answer:", answer)


@begin.start
def run():
    """
    Main hook.
    """
