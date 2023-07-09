from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path,include

from user_app.api import views

urlpatterns = [
    path('register/',views.register_view,name='register'),
    path('login/',obtain_auth_token ,name='login'),
    path('logout/',views.logout_view,name='logout'),

    path('files/', views.AllFileView.as_view(), name='all-files'),
    path('files/my-files/', views.AllFileByUserView.as_view(), name='all-user-files'),
    path('files/<int:pk>/', views.FileDetailView.as_view(), name='file-detail'),
    path('files/create-file/', views.FileCreateView.as_view(), name='file-create'),
    path('extract_advisor/',views.ExtractedAdvisorView.as_view(), name='extract_advisor')
]
