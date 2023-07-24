from datetime import datetime
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.checks import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .filters import PostFilter
from .models import Post, Category, Author
from .models import BaseRegisterForm
from .forms import BasicSignupForm
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail,BadHeaderError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    show_content = 'content'
    template_name = 'posts.html'
    context_object_name = 'object_list'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['total_posts_count'] = Post.objects.count()
        context['next_sale'] = None
        return context


class PostDetail(View):
    template_name = 'post.html'

    def get(self, request, *args, **kwargs):
        post_id = kwargs['pk']
        post = get_object_or_404(Post, id=post_id)

        # Передаем переменную category в контекст шаблона
        category = post.categories.first()
        context = {
            'post': post,
            'category': category,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        post_id = kwargs['pk']
        post = get_object_or_404(Post, id=post_id)
        rating = request.POST.get('rating')

        if rating:
            post.rating = int(rating)
            post.save()

        # Передаем переменную category в контекст шаблона
        category = post.categories.first()
        context = {
            'post': post,
            'category': category,
        }
        return render(request, self.template_name, context)
class SearchView(View):
    template_name = 'search.html'

    def get(self, request):
        query = request.GET.get('q')
        object_list = Post.objects.filter(post_type='news')

        if query:
            object_list = object_list.filter(
                Q(title__icontains=query) |
                Q(author__user__username__icontains=query) |
                Q(created_at__lt=query)
            )

        filter = PostFilter(request.GET, queryset=object_list)
        filter.form.fields['title'].label = 'Заголовок'
        filter.form.fields['author__user__username'].label = 'Автор'
        filter.form.fields['created_at__lt'].label = 'Позже указываемой даты'

        return render(request, self.template_name, {'filter': filter})


class AuthorPermissionMixin(PermissionRequiredMixin):
    permission_required = ['news.change_post', 'news.create_news_view', 'news.create_article_view','news.edit_news_view',]

    def dispatch(self, request, *args, **kwargs):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return super().dispatch(request, *args, **kwargs)

        if request.user.groups.filter(name='authors').exists():
            return super().dispatch(request, *args, **kwargs)

        return self.handle_no_permission()


class CreateNewsView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['post_type', 'categories', 'title', 'content']
    template_name = 'create_news.html'  # Изменил название шаблона на 'create_news.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        # Проверяем, существует ли объект Author для текущего пользователя
        author, created = Author.objects.get_or_create(user=self.request.user)

        # Устанавливаем текущего пользователя (автора) в качестве автора новости
        form.instance.author = author

        news_count = Post.objects.filter(
            Q(author=author) &  # Замените user на author здесь
            Q(post_type='news') &
            Q(created_at__gte=timezone.now() - timezone.timedelta(days=1))
        ).count()

        if news_count >= 3:
            messages.error(self.request, "Вы уже опубликовали максимальное количество новостей за последние 24 часа.")
            return redirect('post_list')

        form.instance.post_type = 'news'
        return super().form_valid(form)


class EditNewsView(LoginRequiredMixin, AuthorPermissionMixin, UpdateView):
    model = Post
    fields = ['author', 'post_type', 'categories', 'title', 'content']
    template_name = 'edit_news.html'
    success_url = reverse_lazy('edit_news')


class DeleteNewsView(LoginRequiredMixin, AuthorPermissionMixin, DeleteView):
    model = Post
    template_name = 'delete_news.html'
    success_url = reverse_lazy('post_list')


class CreateArticleView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['post_type', 'categories', 'title', 'content']
    template_name = 'create_article.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        # Проверяем, существует ли объект Author для текущего пользователя
        author, created = Author.objects.get_or_create(user=self.request.user)

        # Устанавливаем текущего пользователя (автора) в качестве автора статьи
        form.instance.author = author

        article_count = Post.objects.filter(
            Q(author=author) &  # Замените user на author здесь
            Q(post_type='article') &
            Q(created_at__gte=timezone.now() - timezone.timedelta(days=1))
        ).count()

        if article_count >= 3:
            messages.error(self.request, "Вы уже опубликовали максимальное количество статей за последние 24 часа.")
            return redirect('post_list')

        form.instance.post_type = 'article'
        return super().form_valid(form)


class EditArticleView(LoginRequiredMixin, AuthorPermissionMixin, UpdateView):
    model = Post
    fields = ['author', 'post_type', 'categories', 'title', 'content']
    template_name = 'edit_article.html'
    success_url = reverse_lazy('edit_article')


class DeleteArticleView(LoginRequiredMixin, AuthorPermissionMixin, DeleteView):
    model = Post
    template_name = 'delete_article.html'
    success_url = reverse_lazy('success_url_name')


class BaseRegisterView(CreateView):
    model = User
    form = BasicSignupForm()
    form_class = BaseRegisterForm
    success_url = '/'



class BaseRegisterView(View):
    form_class = BasicSignupForm  # Используем обновленную форму
    template_name = 'registration/signup.html'
    success_url = '/'  # Укажите URL, на который пользователь будет перенаправлен после успешной регистрации

    def send_welcome_email(self, user):
        # Функция для отправки приветственного письма пользователю
        subject = 'Добро пожаловать на нашем сайте!'
        message = f'Привет, {user.username}!\n\nСпасибо за регистрацию на нашем сайте. Надеемся, вам понравится наше сообщество.\n\nС уважением,\nАдминистрация сайта'
        from_email = '' # С какой почты будет отпровляться письма
        recipient_list = [user.email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            print("Ошибка при отправке письма:", e)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(request)  # Вызываем метод save() вашей формы
            self.send_welcome_email(user)  # Отправляем приветственное письмо
            return redirect(self.success_url)
        return render(request, self.template_name, {'form':form})


class BecomeAuthorView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        common_group = Group.objects.get(name='common')
        authors_group = Group.objects.get(name='authors')
        already_author = user.groups.filter(name='authors').exists()

        if not user.groups.filter(name='common').exists():
            common_group.user_set.add(user)

        if not already_author:
            authors_group.user_set.add(user)

            # Создаем объект Author и связываем его с пользователем
            author = Author.objects.create(user=user)

        context = {
            'already_author': already_author,
        }

        return render(request, 'become_author.html', context)

class CategoryDetailView(View):
    template_name = 'category_detail.html'

    def get(self, request, *args, **kwargs):
        category_id = kwargs['category_id']
        category = get_object_or_404(Category, id=category_id)
        context = {'category': category}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        category_id = kwargs['category_id']
        category = get_object_or_404(Category, id=category_id)

        # Обработка подписки пользователя на категорию
        if request.user.is_authenticated:
            if category.subscribers.filter(id=request.user.id).exists():
                # Если пользователь уже подписан, отписываем его
                category.subscribers.remove(request.user)
            else:
                # Если пользователь не подписан, подписываем его
                category.subscribers.add(request.user)

        context = {'category': category}
        return render(request, self.template_name, context)


# Функция, которая будет отправлять уведомление на почту

def send_notification_email(post, instance=None):
    # Получить все категории, которым принадлежит статья
    categories = post.categories.all()

    # Получить всех подписчиков этих категорий
    subscribers = User.objects.filter(subscribed_categories__post=instance)

    # Отправить уведомление каждому подписчику
    for subscriber in subscribers:
        subject = post.title
        message = f"Здравствуй, {subscriber.username}. Новая статья в твоем любимом разделе!"
        send_mail(subject, message, 'ВашаПочтаyandex.ru', [subscriber.email], fail_silently=True)


# Сигнал, который будет отправлять уведомление на почту при добавлении новости в категорию
@receiver(post_save, sender=Post)
def send_notification_on_new_post(sender, instance, created, **kwargs):
    if created and instance.post_type == 'news':
        send_notification_email(instance)

# Сигнал, который будет отправлять уведомление на почту при изменении статуса подписки на категорию
@receiver(post_save, sender=Category)
def send_notification_on_subscription_change(sender, instance, **kwargs):
    post_set = Post.objects.filter(categories=instance)
    for post in post_set:
        send_notification_email(post)


