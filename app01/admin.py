from django.contrib import admin
from app01 import models


admin.site.register(models.UserInfo)
admin.site.register(models.Tag)
admin.site.register(models.Category)
admin.site.register(models.Commit)
admin.site.register(models.Article)
admin.site.register(models.Blog)
admin.site.register(models.UpAndDown)
admin.site.register(models.ArticleTOTag)





