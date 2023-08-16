from rest_framework.serializers import ModelSerializer
from rest_framework import serializers, status
from base.models import Document

from docx import Document as DocxDocument
from django.utils.timezone import make_aware
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class DocumentSerializer(ModelSerializer): 
    class Meta:
        model = Document
        fields = '__all__'

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
            # data['word_count'] = str(doc.core_properties.words)
        else: 
            print("File is None")
            raise serializers.ValidationError("File must not be None", code=status.HTTP_400_BAD_REQUEST)

        return data
            

class RegisterSerializer(serializers.ModelSerializer): 

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
            password=data['password']
        )
        return user
    
    class Meta:
        model = UserModel
        fields = ('username','email','first_name','last_name','password')
    
