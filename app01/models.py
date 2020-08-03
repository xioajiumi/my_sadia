from django.db import models
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    nid = models.AutoField(primary_key=True)
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.png')
    blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '用户表'
        verbose_name_plural = verbose_name


class Blog(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    site_name = models.CharField(max_length=32)
    theme = models.CharField(max_length=64)

    def __str__(self):
        return self.site_name


class Category(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    blog = models.ForeignKey(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    blog = models.ForeignKey(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, verbose_name='文章标题')
    desc = models.CharField(max_length=255)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    commit_num = models.IntegerField(default=0)
    up_num = models.IntegerField(default=0)
    down_num = models.IntegerField(default=0)
    blog = models.ForeignKey(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category', to_field='nid', null=True, on_delete=models.CASCADE)
    tag = models.ManyToManyField(to='Tag', through='ArticleTOTag', through_fields=('article', 'tag'))

    def __str__(self):
        return self.title


class ArticleTOTag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to='Article', to_field='nid', on_delete=models.CASCADE)
    tag = models.ForeignKey(to='Tag', to_field='nid', on_delete=models.CASCADE)


class Commit(models.Model):
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', to_field='nid', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    parent = models.ForeignKey(to='self', to_field='nid', null=True, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)

class UpAndDown(models.Model):
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', to_field='nid', on_delete=models.CASCADE)
    is_up = models.BooleanField()

    class Meta:
        unique_together = (('user', 'article'), )

