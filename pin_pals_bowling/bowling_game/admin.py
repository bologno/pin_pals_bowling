from django.contrib import admin
from .models import BowlingGame, Frame, Roll

# Register your models here.

admin.site.register(BowlingGame)
admin.site.register(Frame)
admin.site.register(Roll)