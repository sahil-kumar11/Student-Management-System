from django.contrib import admin
from .models import*

# Register your models here.
admin.site.register(ClassRoom)
admin.site.register(Student)
admin.site.register(Notice)
admin.site.register(Attendance)
admin.site.register(Teacher)