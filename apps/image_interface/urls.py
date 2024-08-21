from django.urls import path
from . import views

app_name = 'image_interface'

urlpatterns = [
    path("chats/", views.ImageConversationListView.as_view(),
         name='image_list_url'),
    path('chat/', views.ImageConversationDetailView.as_view(),
         name='new_image_url'),
    path('chat/<uuid:pk>/', views.ImageConversationDetailView.as_view(),
         name='image_detail_url'),
    path("<uuid:pk>/delete/", views.ImageConversationDeleteView.as_view(),
         name='delete_url'),
    path("new/", views.ImageConversationView.as_view(), name='new_imagechat_url'),
]
