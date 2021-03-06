from django.db import models
from django.contrib.auth.models import User

class SliderArticle(models.Model):
	ARTICLE_CATEGORY = (
		('STOCK MARKET', 'STOCK MARKET'),
		('COMMODITIES', 'COMMODITIES'),
		('FUTURES', 'FUTURES'),
	)
	title = models.CharField(max_length=255)
	description = models.TextField(max_length=4000)
	category = models.CharField(max_length = 255, choices=ARTICLE_CATEGORY, default='STOCK MARKET')
	image = models.ImageField(upload_to='slider', blank=True)
	last_updated = models.DateTimeField(auto_now_add=True)
	starter = models.ForeignKey(User, related_name='article', on_delete=models.CASCADE)

	def __str__(self):
		return self.title

class ArticlePost(models.Model):
	message = models.TextField(max_length=4000)
	article = models.ForeignKey(SliderArticle, related_name='article_posts', on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(null=True)
	created_by = models.ForeignKey(User, related_name='article_posts', on_delete=models.CASCADE)
	updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)

	def __str__(self):
		return self.created_by

