from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey('users.User', related_name='authors', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    content = MarkdownxField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def formatted_markdown(self):
        return markdownify(self.content)
