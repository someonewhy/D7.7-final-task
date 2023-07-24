from django.contrib import admin
from .models import Author, Category, Post, Site

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'post_type', 'created_at', 'rating']
    list_filter = ['post_type', 'categories']
    search_fields = ['title', 'author__user__username']

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain']
