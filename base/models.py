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

    # document analysis results
    category = models.CharField(max_length=100, blank=True, null=True)
    analysis_complete = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.filename)
    
    def save(self, *args, **kwargs):
        # Override save method to update document body from file
        # Note: this is only called when the document is created, not when it is updated
        #       so the user must delete the document and reupload it to update the body
        #       this is because the body is only used for analysis, and we don't want to
        #       parse the document every time it is updated
        
        # return normally
        super().save(*args, **kwargs)

        # Create empty DocumentErrorDetail and DocumentErrorStat objects
        doc_error_detail = DocumentErrorDetail.objects.create(document=self)
        doc_error_detail.save()
        doc_error_stat = DocumentErrorStat.objects.create(document=self)
        doc_error_stat.save()

class DocumentErrorDetail(models.Model):
    # Many to one relationship with Document
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    sentence = models.CharField(max_length=1000, default="")
    mistake_text = models.CharField(max_length=1000, default="")
    error_message = models.CharField(max_length=1000, default="")
    replacement = models.CharField(max_length=1000, default="")
    start_index = models.IntegerField(default=0)
    end_index = models.IntegerField(default=0)
    error_type = models.CharField(max_length=100, default="")
    error_category = models.CharField(max_length=100, default="")

    def __str__(self):
        return "{}".format(self.document.filename)
    

class DocumentErrorStat(models.Model):
    # One to one relationship with Document
    id = models.AutoField(primary_key=True)
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    total_errors = models.IntegerField(default=0)
    spelling_errors = models.IntegerField(default=0)
    grammar_errors = models.IntegerField(default=0)
    punctuation_errors = models.IntegerField(default=0)
    syntax_errors = models.IntegerField(default=0)
    style_errors = models.IntegerField(default=0)
    other_errors = models.IntegerField(default=0)

    def __str__(self):
        return "{}".format(self.document.filename)
    

class UserProfile(models.Model):
    # One to one relationship with User
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updating = models.BooleanField(default=False) # True if the user's documents are being analysed, False otherwise

    def __str__(self):
        return "{}".format(self.user.username)
    
# Override the default User model save method to create a UserProfile object when a User is created
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Connect the create_user_profile function to the post_save signal
models.signals.post_save.connect(create_user_profile, sender=User)