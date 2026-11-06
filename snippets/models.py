from django.db import models
from django.contrib.auth.models import User

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter


class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default="")
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(max_length=100, default="python")
    style = models.CharField(max_length=100, default="friendly")

    owner = models.ForeignKey(
        User,
        related_name="snippets",
        on_delete=models.CASCADE
    )

    highlighted = models.TextField()

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return self.title or f"Snippet {self.id}"

    def save(self, *args, **kwargs):
        """
        Use Pygments to create a highlighted HTML
        representation of the code snippet.
        """
        lexer = get_lexer_by_name(self.language)
        linenos = "table" if self.linenos else False
        options = {"title": self.title} if self.title else {}

        formatter = HtmlFormatter(
            style=self.style,
            linenos=linenos,
            full=True,
            **options
        )

        self.highlighted = highlight(self.code, lexer, formatter)

        super().save(*args, **kwargs)