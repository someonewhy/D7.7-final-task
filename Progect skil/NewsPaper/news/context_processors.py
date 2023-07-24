# context_processors.py

def user_groups(request):
    return {'user_groups': request.user.groups.values_list('name', flat=True)}
