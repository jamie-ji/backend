from rest_framework.serializers import ModelSerializer
from rest_framework import serializers, status

from base.models import Document, DocumentErrorDetail, DocumentErrorStat, UserProfile

from docx import Document as DocxDocument
from django.utils.timezone import make_aware
from django.contrib.auth import get_user_model
import datetime
import hashlib
import re
from django.conf import settings

UserModel = get_user_model()

def hash_code(s, salt='penwell'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()
def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.username, now)
    models.ConfirmString.objects.create(code=code, user=user)
    return code
def send_email(email, code):

    from django.core.mail import EmailMultiAlternatives

    subject = 'Confirm from penwell'

    text_content = '''test without html link'''

    html_content = '''
                    <p>Thanks for registering. <a href="http://{}/confirm/?code={}" target=blank>www.penwell.com</a>,\
                    Link to Penwell</p>
                    <p>Please click link to finish registeration</p>
                    <p>Last for {} days</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

class DocumentUploadSerializer(ModelSerializer):
    # model for uploading a document, only one file field
    class Meta:
        model = Document
        fields = ['file']

    def preprocess(self, data):
        print("Preprocessing data")
        file = data.get('file', None)
        if file is not None:
            ext = file.name.split('.')[-1]

            if ext != 'docx': 
                print("File must be a docx file")
                raise serializers.ValidationError("File must be a docx file", code=status.HTTP_400_BAD_REQUEST)
            
            try: 
                doc = DocxDocument(file)
            except:
                print("Cannot parse file, possible file corruption")
                raise serializers.ValidationError("Cannot parse file, possible file corruption", code=status.HTTP_400_BAD_REQUEST)
            
            data['body'] = '\n'.join([para.text for para in doc.paragraphs])
            data['filename'] = file.name
            data['author'] = doc.core_properties.author
            data['created_at'] = doc.core_properties.created
            data['last_modified'] = doc.core_properties.modified
            data['word_count'] = len(re.findall(r'\w+', data['body']))
        else: 
            print("File is None")
            raise serializers.ValidationError("File must not be None", code=status.HTTP_400_BAD_REQUEST)
        return data
    
class DocumentSerializer(ModelSerializer): 
    # model for viewing a document, all fields included
    class Meta:
        model = Document
        fields = '__all__'

            
# Registration functionality using get_user_model.
class RegisterSerializer(serializers.ModelSerializer): 
    # model for registering a user
    class Meta:
        model = UserModel
        fields = ('username','email','first_name','last_name','password')
    
    username = serializers.CharField(max_length=100, min_length=6)
    email = serializers.EmailField(max_length=100, min_length=6)
    first_name = serializers.CharField(max_length=20, min_length=2)
    last_name = serializers.CharField(max_length=20, min_length=2)
    password = serializers.CharField(write_only=True)
    def create(self,data):

        user = UserModel.objects.create_user(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=data['password'],
        )
        # send email to user
        code = make_confirm_string(user)
        send_email(data['email'], code)
        
        return user
    
class UserSerializer(serializers.ModelSerializer):
    # model for viewing a user, all fields included
    class Meta:
        model = UserModel
        exclude = ('password',)
    
class UserProfilesSerializer(serializers.ModelSerializer):
    # model for viewing a user profile, all fields included
    class Meta:
        model = UserProfile
        exclude = ('id', 'user',)

class DocumentErrorDetailSerializer(ModelSerializer):
    # model for viewing/updating a document error detail, all fields included
    class Meta:
        model = DocumentErrorDetail
        fields = '__all__'

class DocumentErrorStatSerializer(ModelSerializer):
    # model for viewing/updating a document error stat, all fields included
    class Meta:
        model = DocumentErrorStat
        fields = '__all__'
    
