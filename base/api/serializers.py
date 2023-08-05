from rest_framework.serializers import ModelSerializer
from base.models import Document

class DocumentSerializer(ModelSerializer): 
    class Meta:
        model = Document
        fields = '__all__'
