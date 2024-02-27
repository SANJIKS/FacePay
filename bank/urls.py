from django.urls import path, include
from rest_framework import routers
from .views import UserCreateView, PaymentByFaceViewSet

router = routers.DefaultRouter()
router.register(r'payment', PaymentByFaceViewSet, basename='payment')

urlpatterns = [
    path('create_user/', UserCreateView.as_view(), name='create_user'),
    path('', include(router.urls))
]
