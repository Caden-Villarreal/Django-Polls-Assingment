
import os

from django import forms
from .models import Comment, UploadedFile


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment_text"]
        widgets = {
            "comment_text": forms.Textarea(attrs={"rows": 3}),
        }


class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ["file"]

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")

        if uploaded_file:
            allowed_extensions = {
                ".pdf",
                ".png",
                ".jpg",
                ".jpeg",
                ".txt",
            }

            extension = os.path.splitext(uploaded_file.name)[1].lower()

            if extension not in allowed_extensions:
                raise forms.ValidationError(
                    "Only PDF, PNG, JPG, JPEG, and TXT files are allowed."
                )

            max_size = 5 * 1024 * 1024

            if uploaded_file.size > max_size:
                raise forms.ValidationError(
                    "The file cannot be larger than 5 MB."
                )

        return uploaded_file
