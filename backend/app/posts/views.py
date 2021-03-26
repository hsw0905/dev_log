from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from posts.models import Post
from posts.serializers import PostListSerializer


class PostListViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      GenericViewSet):

    queryset = Post.objects.all()
    serializer_class = PostListSerializer

