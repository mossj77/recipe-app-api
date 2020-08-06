from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', TokenObtainPairView.as_view(), name='token'),

]
