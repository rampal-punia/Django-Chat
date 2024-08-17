from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path("", views.Dashboard.as_view(), name='home_url'),
    path("chats/", views.ConversationListView.as_view(),
         name='conversation_list_url'),
    path('chat/', views.ConversationDetailView.as_view(),
         name='new_conversation_url'),
    path('chat/<uuid:pk>/', views.ConversationDetailView.as_view(),
         name='conversation_detail_url'),
    path("<uuid:pk>/delete/", views.ConversationDeleteView.as_view(),
         name='conversation_delete_url'),
    path("new/", views.ChatView.as_view(), name='new_chat_url'),
]
