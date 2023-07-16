from django.db import models
from django.contrib.auth.models import User


class ProcessedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    file_name = models.CharField(max_length=255)
    generated_code = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.file_name}"


class UploadedFile(models.Model):
    prompt = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/")
