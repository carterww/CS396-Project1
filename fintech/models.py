from django.db import models
from django.contrib.auth.models import User
from django.dispatch import Signal
import shutil
import os

# forum board table
class Board (models.Model) :
    # using auto generated primary key
    board_name = models.CharField(max_length=63, unique=True)

# table to represent a topic
class DiscussionTopic (models.Model) :
    # using auto generated primary key
    topic_name = models.CharField(max_length=255, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    FK_board_discussiontopic = models.ForeignKey(Board, on_delete=models.CASCADE)
    FK_user_discussiontopic = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default='Deleted User')

# table to represent a post under a topic
class Post(models.Model) :
    #using auto generated primary key
    title = models.CharField(max_length=63)
    content_text = models.TextField(max_length=511)
    creation_date = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    FK_discussiontopic_post = models.ForeignKey(DiscussionTopic, on_delete=models.CASCADE)
    FK_user_post = models.ForeignKey(User, on_delete=models.CASCADE)

    # override delete method to delete associated files from file system
    def delete(self, *args, **kwargs):
        delete_post(self)
        super().delete(*args, **kwargs)

# finds associated files and deletes
def delete_post(post) :
    try :
        d = DocumentFile.objects.filter(FK_post_document=post)
        for f in d :
            f.delete()
    except :
        return

# table to represent comment under a post
class Comment(models.Model) :
    #using auto generated primary key
    creation_date = models.DateTimeField(auto_now_add=True)
    content_text = models.CharField(max_length=255)
    FK_post_comment = models.ForeignKey(Post, on_delete=models.CASCADE)
    FK_user_comment = models.ForeignKey(User, on_delete=models.CASCADE)

# table that holds one row with latest post information
class Notification(models.Model) :
    text = models.CharField(max_length=255, default='')

# table to hold information related to a post's files
class DocumentFile(models.Model) :
    #using auto generated primary key
    path_to_file = models.CharField(max_length=255, default='./media/junk')
    content = models.FileField()
    FK_user_document = models.ForeignKey(User, on_delete=models.CASCADE)
    FK_post_document = models.ForeignKey(Post, on_delete=models.CASCADE)

    # override delete method to also delete from file system
    def delete(self, *args, **kwargs):
        try :
            shutil.rmtree(self.path_to_file)
            super().delete(*args, **kwargs)
        except :
            super().delete(*args, **kwargs)


