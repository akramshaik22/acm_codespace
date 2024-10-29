from django.contrib import admin

from app.models import Users, Contests, Registrations, Questions, Contest_question, Submissions, Admins

admin.site.register(Users)
admin.site.register(Contests)
admin.site.register(Registrations)
admin.site.register(Questions)
admin.site.register(Contest_question)
admin.site.register(Submissions)
admin.site.register(Admins)
