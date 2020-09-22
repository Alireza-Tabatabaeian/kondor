from django.contrib import admin

from .models import UserProfile
from .models import Game


# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Game)

