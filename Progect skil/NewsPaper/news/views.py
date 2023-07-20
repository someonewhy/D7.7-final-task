from datetime import datetime
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .filters import PostFilter
from .models import Post


class PostListView(ListView):
    model = Post
    show_content = 'content'
    template_name = 'posts.html'
    context_object_name = 'object_list'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        # С помощью super() мы обращаемся к родительским классам
        # и вызываем у них метод get_context_data с теми же аргументами,
        # что и были переданы нам.
        # В ответе мы должны получить словарь.
        context = super().get_context_data(**kwargs)
        # К словарю добавим текущую дату в ключ 'time_now'.
        context['time_now'] = datetime.utcnow()
        context['total_posts_count'] = Post.objects.count()
        # Добавим ещё одну пустую переменную,
        # чтобы на её примере рассмотреть работу ещё одного фильтра.
        context['next_sale'] = None
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    # pk_url_kwarg = 'id'
    def post(self, request, *args, **kwargs):
        post = self.get_object()  # Получаем объект поста
        rating = request.POST.get('rating')  # Получаем значение рейтинга из POST-запроса

        if rating:
            post.rating = int(rating)  # Преобразуем значение рейтинга в целое число
            post.save()  # Сохраняем изменения в базе данных

        return render(request, self.template_name, {self.context_object_name: post})


class SearchView(View):
    template_name = 'search.html'

    def get(self, request):
        query = request.GET.get('q')
        object_list = Post.objects.filter(post_type='news')

        if query:
            object_list = object_list.filter(
                Q(title__icontains=query) |    # Поиск по названию
                Q(author__user__username__icontains=query) |   # Поиск по имени автора
                Q(created_at__lt=query)       # Поиск по дате
            )

        filter = PostFilter(request.GET, queryset=object_list)
        filter.form.fields['title'].label = 'Заголовок'
        filter.form.fields['author__user__username'].label = 'Автор'
        filter.form.fields['created_at__lt'].label = 'Позже указываемой даты'

        return render(request, self.template_name, {'filter': filter})


class CreateNewsView(CreateView):
    model = Post
    fields = ['author', 'post_type', 'categories', 'title', 'content']
    template_name = 'create_news.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.post_type = 'news'
        return super().form_valid(form)


class EditNewsView(UpdateView):
    model = Post
    fields = ['author', 'post_type', 'categories', 'title', 'content']
    template_name = 'edit_news.html'
    success_url = reverse_lazy('post_list')


class DeleteNewsView(DeleteView):
    model = Post
    template_name = 'delete_news.html'
    success_url = reverse_lazy('post_list')


# Представления для статей

class CreateArticleView(CreateView):
    model = Post
    fields = ['author', 'post_type', 'categories', 'title', 'content']
    template_name = 'create_article.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.post_type = 'article'
        return super().form_valid(form)


class EditArticleView(UpdateView):
    model = Post
    fields = ['author', 'post_type', 'categories', 'title', 'content']
    template_name = 'edit_article.html'
    success_url = reverse_lazy('post_list')


class DeleteArticleView(DeleteView):
    model = Post
    template_name = 'delete_article.html'
    success_url = reverse_lazy('post_list')


""" {% block content %}
<h1>Все Посты</h1>
<ul>
  {% for post in object_list %}
    <li>
      <h2>{{ post.title }}</h2>
      <p>{{ post.content }}</p>
    </li>
  {% endfor %}
</ul>
{% endblock content %}"""
