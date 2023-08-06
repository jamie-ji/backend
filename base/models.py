from django.db import models

from django.contrib.auth.models import User

from .validators import validate_file_extension, validate_file_size

# Create your models here.


def user_directory_path(instance, filename):
    # file will be uploaded to documents/user_<id>/<filename>
    return "documents/user_{0}/{1}".format(instance.user.id, filename)

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Note this validation only works after the file has been uploaded, need to add frontend validation as well
    file = models.FileField(upload_to=user_directory_path, max_length=500000, validators=[validate_file_extension, validate_file_size]) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    body = models.TextField(max_length=500000, blank=True, null=True)
    filename = models.CharField(max_length=100, blank=True, null=True)

    # Metadata info, blank=True, null=True allows for empty fields (potentially from Google docs)
    author = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    word_count = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return "{}-{}".format(self.filename, self.body[:20])
