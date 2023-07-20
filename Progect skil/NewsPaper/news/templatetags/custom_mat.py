from django import template
import re

register = template.Library()

PROFANITY_LIST = ['редиска', 'нецензурное слово', 'брань','мат']  # список нецензурных слов

@register.filter()
def censor(value):
    """
    value: текст, к которому нужно применить фильтр
    """
    if not isinstance(value, str):
        raise ValueError("Censor filter can only be applied to string variables.")

    words = re.findall(r'\b\w+\b', value)  # Разбиваем текст на отдельные слова
    for word in words:
        if word.lower() in PROFANITY_LIST:
            censored_word = ' Не хорошее слово - ' + word[0] + '*' * (len(word) - 1)
            value = re.sub(r'\b' + re.escape(word) + r'\b', censored_word, value)

    return value