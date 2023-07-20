from django.urls import path
from .views import PostListView, PostDetail, SearchView, CreateNewsView, EditNewsView, DeleteNewsView, CreateArticleView, EditArticleView, DeleteArticleView

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('news/create/', CreateNewsView.as_view(), name='create_news'),
    path('news/<int:pk>/edit/', EditNewsView.as_view(), name='edit_news'),
    path('news/<int:pk>/delete/', DeleteNewsView.as_view(), name='delete_news'),
    path('articles/create/', CreateArticleView.as_view(), name='create_article'),
    path('articles/<int:pk>/edit/', EditArticleView.as_view(), name='edit_article'),
    path('articles/<int:pk>/delete/', DeleteArticleView.as_view(), name='delete_article'),
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('search/', SearchView.as_view(), name='post_search'),
]
