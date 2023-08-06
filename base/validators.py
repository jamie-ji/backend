# validators.py 
# This file contains the validators for the forms

import os


from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.docx'] # add more extensions if needed in the future
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')
    else:
        return value
    
def validate_file_size(value):
    filesize= value.size
    five_Megabytes_limit = 5242880 # 5MB
    
    if filesize > five_Megabytes_limit:
        raise ValidationError("The maximum file size that can be uploaded is 5MB")
    else:
        return value