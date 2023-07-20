import unittest
from peewee import *
from app import TimelinePost
from playhouse.shortcuts import model_to_dict


MODELS = [TimelinePost]
test_db = SqliteDatabase(':memory:')

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self):
        test_db.drop_tables(MODELS)
        test_db.close()

    def test_timeline_post(self):
        first_post = TimelinePost.create(name="John Doe", email="john@example.com", content="Hello world, I'm John!")
        assert first_post.id == 1
        second_post = TimelinePost.create(name="Jane Doe", email="jane@example.com", content="Hello world, I'm Jane!")
        assert second_post.id == 2
        
        retrieved_posts = [model_to_dict(p) for p in TimelinePost.select().order_by(TimelinePost.created_at.asc())]
        ret_post_one = retrieved_posts[0]
        ret_post_two = retrieved_posts[1]

        assert ret_post_one["name"] == first_post.name
        assert ret_post_one["email"] == first_post.email
        assert ret_post_one["content"] == first_post.content

        assert ret_post_two["name"] == second_post.name
        assert ret_post_two["email"] == second_post.email
        assert ret_post_two["content"] == second_post.content