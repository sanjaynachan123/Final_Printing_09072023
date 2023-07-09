from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class File(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='uploads', null=True)
    date = models.DateField(auto_now=True)
    uploader = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='files')

    def __str__(self):
        return self.title
    

class ExtractedData(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()    
  
    
class ExtractedAdvisor(models.Model):
    name = models.CharField(max_length=100,blank=True,null=True)
    address = models.CharField(max_length=100,blank=True,null=True)
    account_owner = models.CharField(max_length=100,blank=True,null=True)
    occupation = models.CharField(max_length=100,blank=True,null=True)
    home_phone= models.CharField(max_length=100,blank=True,null=True)
    pdf_file = models.FileField(upload_to='advisor_pdfs/',blank=True,null=True)  # Field to store the generated PDF

    def __str__(self):
        return f'{self.name} {self.address} {self.account_owner} {self.occupation} {self.home_phone}'    