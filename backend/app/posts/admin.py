from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from posts.models import Post


@admin.register(Post)
class PostAdmin(MarkdownxModelAdmin):
    list_display = ('id',
                    'author',
                    'title',
                    'description',
                    'content',
                    'time_stamp',)


