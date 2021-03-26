from model_bakery import baker
from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post


class PostTestCase(APITestCase):
    def setUp(self):
        # given
        self.user = baker.make('users.User')
        self.test_post_1 = Post.objects.create(title='test',
                                               author=self.user,
                                               description='test description',
                                               content='<h1>Hi</h1>')
        self.test_post_2 = Post.objects.create(title='test2',
                                               author=self.user,
                                               description='test description 2',
                                               content='<h1>Bye</h1>')
        self.posts = [self.test_post_1, self.test_post_2]
        self.expected_post_count = 2

    def test_should_list_posts(self):
        # when
        response = self.client.get('/api/posts')

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Post.objects.all().count(), self.expected_post_count)

        for test_post, post_response in zip(self.posts[::-1], response.data):
            self.assertEqual(test_post.id, post_response['id'])
            self.assertEqual(test_post.author.id, post_response['author'])
            self.assertEqual(test_post.title, post_response['title'])
            self.assertEqual(test_post.description, post_response['description'])
            self.assertEqual(test_post.content, post_response['content'])

    def test_should_detail_post(self):
        # when
        response = self.client.get(f'/api/posts/{self.test_post_1.id}')

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post_response = Munch(response.data)

        self.assertEqual(post_response.id, self.test_post_1.id)
        self.assertEqual(post_response.author, self.test_post_1.author.id)
        self.assertEqual(post_response.title, self.test_post_1.title)
        self.assertEqual(post_response.description, self.test_post_1.description)
        self.assertEqual(post_response.content, self.test_post_1.content)

