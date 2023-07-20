import django_filters
from .models import Post

class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='iexact')
    author__user__username = django_filters.CharFilter(lookup_expr='icontains')
    created_at__lt = django_filters.DateFilter(method='filter_created_at_lt')

    class Meta:
        model = Post
        fields = ['title', 'author__user__username']

    def filter_created_at_lt(self, queryset, name, value):
        return queryset.filter(created_at__lt=value)
