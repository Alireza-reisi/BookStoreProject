from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=150, verbose_name="نام")
    email = models.EmailField(verbose_name="ایمیل")
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    message = models.TextField(verbose_name="متن پیام")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "پیام"
        verbose_name_plural = "پیام‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
