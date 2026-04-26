from django import forms
from django.contrib.contenttypes.models import ContentType
from .models import Comment, Book, Author


class CommentAdminForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # فقط مدل‌های مجاز
        allowed_models = [Book, Author]

        # contenttype های مجاز
        allowed_cts = ContentType.objects.get_for_models(*allowed_models)

        # محدود کردن queryset
        self.fields["content_type"].queryset = ContentType.objects.filter(
            id__in=[ct.id for ct in allowed_cts.values()]
        )
