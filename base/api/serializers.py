from rest_framework.serializers import ModelSerializer
from rest_framework import serializers, status
from rest_framework.validators import UniqueValidator
from base.models import Document, DocumentErrorDetail, DocumentErrorStat, UserProfile
from base import models
import random
from docx import Document as DocxDocument
from django.utils.timezone import make_aware
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import re
from django.conf import settings
from base.models import VerificationCode
UserModel = get_user_model()

user_t=None

def send_email(email,code):

    from django.core.mail import EmailMultiAlternatives
    
    now = datetime.now()
    expiration_time = now + timedelta(minutes=10)
    
    subject = 'Confirm from penwell'

    text_content = '''test without html link'''

    html_content = '''
                    <p>Thanks for registering. Here is your validation code:{} ,\
                    Regards from Penwell</p>
                    
                    <p>Last for {} mins</p>
                    '''.format(code, settings.CONFIRM_MINS)

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
    # class Meta:
    #     model = UserModel
    #     fields = ('username','email','first_name','last_name','password')
    
    # username = serializers.CharField(max_length=100, min_length=6)
    # email = serializers.EmailField(max_length=100, min_length=6)
    username = serializers.CharField(
        max_length=100, 
        min_length=6,
        validators=[
            UniqueValidator(
                queryset=UserModel.objects.all(),
                message="This username is already in use."
            )
        ]
    )
    
    email = serializers.EmailField(
        max_length=100, 
        min_length=6,
        validators=[
            UniqueValidator(
                queryset=UserModel.objects.all(),
                message="This email address is already in use."
            )
        ]
    )
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'first_name', 'last_name', 'password')
    
    first_name = serializers.CharField(max_length=20, min_length=2)
    last_name = serializers.CharField(max_length=20, min_length=2)
    password = serializers.CharField(write_only=True)
    
    #VerificationCode.objects.create(email=email,code=code, expiration_time=expiration_time)
    def create(self,data):
        code = ''.join(random.choice('0123456789') for _ in range(6))
        send_email(data['email'],code)
        
        user = VerificationCode.objects.create(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=data['password'],
            code=code,
        )
               
        return user 

    # def create(self,data):
    #     code = ''.join(random.choice('0123456789') for _ in range(6))
    #     send_email(data['email'],code)
        
    #     user = UserModel.objects.create_user(
    #         username=data['username'],
    #         email=data['email'],
    #         first_name=data['first_name'],
    #         last_name=data['last_name'],
    #         password=data['password'],
    #     )
               
    #     return user,code
    
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
    
