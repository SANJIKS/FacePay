from django.urls import path, include
from rest_framework import routers
from .views import UserCreateView, FindUserByFaceView, PaymentByFaceViewSet

router = routers.DefaultRouter()
router.register(r'payment', PaymentByFaceViewSet, basename='payment')

urlpatterns = [
    path('create_user/', UserCreateView.as_view(), name='create_user'),
    path('find_user/', FindUserByFaceView.as_view(), name='find_user_by_face'),
    path('', include(router.urls))
]
