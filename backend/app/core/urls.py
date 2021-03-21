from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from users.views import UserSignUpViewSet

router = SimpleRouter(trailing_slash=False)

router.register('auth/sign_up', UserSignUpViewSet)

urlpatterns = router.urls

urlpatterns += [
]
