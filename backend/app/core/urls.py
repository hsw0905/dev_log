from rest_framework.routers import SimpleRouter

from posts.views import PostListViewSet
from users.views import UserViewSet

router = SimpleRouter(trailing_slash=False)

router.register('users', UserViewSet)
router.register('posts', PostListViewSet)

urlpatterns = router.urls

urlpatterns += [
]
