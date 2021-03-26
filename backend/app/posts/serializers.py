from rest_framework.serializers import ModelSerializer

from posts.models import Post


class PostListSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'author', 'description', 'content', 'time_stamp']
        read_only_fields = ('id', 'title', 'author', 'description', 'content', 'time_stamp')
