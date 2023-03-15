from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class HackerNews(models.Model):
    news_id = models.BigIntegerField(unique=True, primary_key=True)
    by         = models.CharField(max_length=100)
    descendants= models.CharField(max_length=100)
    score      = models.CharField(max_length=100)
    time       = models.CharField(max_length=100)
    title      = models.CharField(max_length=250)
    type       = models.CharField(max_length=100)
    kids       = models.JSONField(null=True)    
    url        = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner      = models.ForeignKey(User, related_name="news", on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        if self.owner.is_staff:
            self.news_id = int(__class__.objects.last().news_id) + 1
        self.id = self.news_id 
        super(HackerNews, self).save(*args, **kwargs)

    def __str__(self):
        return f'news-{str(self.hackernews)}'