from django.db import models

from lib.helpers import reverse


class Category(models.Model):
    id = models.IntegerField(primary_key=True, db_column='cat_id')
    name = models.CharField(max_length=165, db_column='cat_name')

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'wp_categories'


class Comment(models.Model):
    id = models.IntegerField(primary_key=True, db_column='comment_id')
    post = models.ForeignKey('WPost', db_column='comment_post_id', related_name='comments')
    author = models.TextField(db_column='comment_author')
    author_email = models.CharField(max_length=300, db_column='comment_author_email')
    author_url = models.CharField(max_length=600, db_column='comment_author_url')
    date = models.DateTimeField(db_column='comment_date')
    content = models.TextField(db_column='comment_content')
    approved = models.CharField(max_length=12, db_column='comment_approved')
    user = models.IntegerField(db_column='user_id')

    def __unicode__(self):
        return u'%s to %s' % (self.author, self.post.title)

    def dict(self):
        return self.__dict__

    class Meta:
        db_table = u'wp_comments'
        ordering = ['date']


class WPost(models.Model):
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey('User', db_column='post_author')
    title = models.TextField(db_column='post_title')
    slug = models.CharField(max_length=600, db_column='post_name')
    content = models.TextField(db_column='post_content')
    date = models.DateTimeField(db_column='post_date')
    modified = models.DateTimeField(db_column='post_modified')
    comment_status = models.CharField(max_length=45)
    type = models.CharField(max_length=60, db_column='post_type')
    categories = models.ManyToManyField('Category', db_table='wp_post2cat')

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('wpimport.views.post_detail', self.id)

    def dict(self):
        return self.__dict__

    class Meta:
        db_table = u'wp_posts'
        ordering = ['-date']


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    user_login = models.CharField(max_length=180)
    user_pass = models.CharField(max_length=192)
    user_nicename = models.CharField(max_length=150)
    user_email = models.CharField(max_length=300)
    user_url = models.CharField(max_length=300)
    user_registered = models.DateTimeField()
    user_activation_key = models.CharField(max_length=180)
    user_status = models.IntegerField()
    display_name = models.CharField(max_length=750)

    def __unicode__(self):
        return self.display_name

    class Meta:
        db_table = u'wp_users'
