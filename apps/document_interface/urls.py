from django.urls import path
from . import views

app_name = 'document_interface'

urlpatterns = [
    path("chats/", views.DocumentConversationListView.as_view(),
         name='document_list_url'),
    path('chat/', views.DocumentConversationDetailView.as_view(),
         name='new_document_url'),
    path('chat/<uuid:pk>/', views.DocumentConversationDetailView.as_view(),
         name='document_detail_url'),
    path("<uuid:pk>/delete/", views.DocumentConversationDeleteView.as_view(),
         name='delete_url'),
    path("new/", views.DocumentConversationView.as_view(),
         name='new_documentchat_url'),
]
