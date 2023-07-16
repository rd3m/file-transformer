from django.urls import path
from . import views

from .views import signup

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('accounts/signup/', signup, name='signup'),
]
