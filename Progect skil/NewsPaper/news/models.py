from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.db.models.signals import post_save


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        print("Author: Update rating method is called.")
        article_rating = self.post_set.aggregate(Sum('rating'))['rating__sum'] or 0
        comment_rating = Comment.objects.filter(post__author=self).aggregate(Sum('rating'))['rating__sum'] or 0
        post_comment_rating = \
        Comment.objects.filter(post__author=self).exclude(user=self.user).aggregate(Sum('rating'))['rating__sum'] or 0

        self.rating = article_rating * 3 + comment_rating + post_comment_rating
        self.save()

    def __str__(self):
        return self.user.username

    def create_author(sender, instance, created, **kwargs):
        if created:
            Author.objects.create(user=instance)

    # Подключаем функцию-обработчик к сигналу
    post_save.connect(create_author, sender=User)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories', blank=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    POST_TYPE_CHOICES = [
        ('article', 'Article'),
        ('news', 'News'),
    ]
    post_type = models.CharField(max_length=7, choices=POST_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        preview_length = 124
        if len(self.content) <= preview_length:
            return self.content
        else:
            return self.content[:preview_length] + "..."

    def is_author(self, user):
        return self.author.user == user

    class Meta:
        permissions = [
            ("can_edit_post", "Can edit own post"),
            ("can_delete_post", "Can delete own post"),
        ]

    def __str__(self):
        return self.title


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post.title} - {self.category.name}'

    def save(self, *args, **kwargs):
        if not self.pk:  # Если объект еще не сохранен в базу данных
            self.category.subscribers.add(self.post.author.user)  # Добавляем автора поста в подписчики категории
        super().save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'


class BaseRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя")
    last_name = forms.CharField(label="Фамилия")

    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2",)

class Site(models.Model):
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100)

    def __str__(self):
        return self.name
