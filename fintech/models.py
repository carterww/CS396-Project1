from django.db import models
from django.contrib.auth.models import User
import os
import shutil

# Create your models here.
class Board (models.Model) :
    # using auto generated primary key
    board_name = models.CharField(max_length=63, unique=True)

class DiscussionTopic (models.Model) :
    # using auto generated primary key
    topic_name = models.CharField(max_length=255, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    FK_board_discussiontopic = models.ForeignKey(Board, on_delete=models.CASCADE)
    FK_user_discussiontopic = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default='Deleted User')

class Post(models.Model) :
    #using auto generated primary key
    title = models.CharField(max_length=63)
    content_text = models.TextField(max_length=511)
    creation_date = models.DateTimeField(auto_now_add=True)
    FK_discussiontopic_post = models.ForeignKey(DiscussionTopic, on_delete=models.CASCADE)
    FK_user_post = models.ForeignKey(User, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        delete_post(self)
        super().delete(*args, **kwargs)

def delete_post(post) :
    try :
        d = DocumentFile.objects.get(FK_post_document=post)
        d.delete()
    except :
        return

class Comment(models.Model) :
    #using auto generated primary key
    creation_date = models.DateTimeField(auto_now_add=True)
    content_text = models.CharField(max_length=255)
    FK_post_comment = models.ForeignKey(Post, on_delete=models.CASCADE)
    FK_user_comment = models.ForeignKey(User, on_delete=models.CASCADE)


class DocumentFile(models.Model) :
    #using auto generated primary key
    path_to_file = models.CharField(max_length=255, default='./media/junk')
    content = models.FileField()
    FK_user_document = models.ForeignKey(User, on_delete=models.CASCADE)
    FK_post_document = models.ForeignKey(Post, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        try :
            shutil.rmtree(self.path_to_file)
            super().delete(*args, **kwargs)
        except :
            super().delete(*args, **kwargs)


