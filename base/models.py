from django.db import models
from jsonfield import JSONField
from django.utils import timezone
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
    

class DocumentErrorDetail(models.Model):
    # Many to one relationship with Document
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)

    check_time = models.DateTimeField(auto_now_add=True)
    error_type = models.CharField(max_length=100, blank=True, null=True)
    error_sub_type = models.CharField(max_length=100, blank=True, null=True)
    error_msg =  models.CharField(max_length=100, blank=True, null=True)
    sentence = models.TextField(max_length=500000, blank=True, null=True)
    char_position_in_text_from = models.IntegerField(blank=True,null=True)
    char_position_in_text_to = models.IntegerField(blank=True,null=True)
    replacements = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        # return f"Document Error : Type({self.error_type}), Sub-Type({self.error_sub_type}), " \
        #        f"Message({self.error_msg}), Sentence({self.sentence}), From({self.char_position_in_text_from}), To({self.char_position_in_text_to}), " \
        #        f"Replacements({self.replacements})"
        return f"Replacements({self.replacements})"
    

class DocumentErrorStat(models.Model):
    # One to one relationship with Document
    id = models.AutoField(primary_key=True)
    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    total_errors = models.IntegerField(default=0)
    all_errors = models.JSONField(default=dict)

    def __str__(self):
        return "{},{}".format(self.document.filename, self.total_errors)
    

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

class VerificationCode(models.Model):
    username=models.CharField(max_length=30)  
    email=models.CharField(max_length=30)  
    first_name=models.CharField(max_length=30)  
    last_name=models.CharField(max_length=30)  
    password=models.CharField(max_length=30)  
    code = models.CharField(max_length=6)  
    
    def __str__(self):
        return self.code
    # def is_valid(self):
    #     return self.expire_at > timezone.now()