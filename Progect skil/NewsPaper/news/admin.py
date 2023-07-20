from django.contrib import admin

from .models import Author, Category


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')


@admin.register(Category)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
