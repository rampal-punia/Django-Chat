# apps/audio_interface/urls.py

from django.urls import path
from . import views

app_name = 'audio_interface'

urlpatterns = [
    path("chats/", views.AudioConversationListView.as_view(),
         name='audio_list_url'),
    path('chat/', views.AudioConversationDetailView.as_view(),
         name='new_audio_url'),
    path('chat/<uuid:pk>/', views.AudioConversationDetailView.as_view(),
         name='audio_detail_url'),
    path("<uuid:pk>/delete/", views.AudioConversationDeleteView.as_view(),
         name='delete_url'),
    path("new/", views.AudioConversationView.as_view(), name='new_audiochat_url'),
]
