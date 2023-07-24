from allauth.account.views import PasswordResetView
from django.urls import path
from .views import PostListView, CreateNewsView, EditNewsView, DeleteNewsView, CreateArticleView, EditArticleView, \
    DeleteArticleView, PostDetail, SearchView, BaseRegisterView, BecomeAuthorView, CategoryDetailView

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
    #path('accounts/signup/', BaseRegisterView.as_view(template_name='registration/signup.html'), name='signup'),
    path('accounts/signup/', BaseRegisterView.as_view(), name='signup'),
    path('become_author/', BecomeAuthorView.as_view(),  name='become_author'),
    path('categories/<int:category_id>/', CategoryDetailView.as_view(), name='category_detail'),



]

