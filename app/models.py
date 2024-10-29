from django.db import models
from django.contrib.auth.models import AbstractUser
# from datetime import datetime
from django.utils import timezone


class Admins(AbstractUser):
    contact = models.CharField(max_length=12)
    is_superadmin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class Users(models.Model):
    username = models.CharField(max_length=30, unique=True)
    profile_pic = models.ImageField(upload_to='user_profile_pics', null=True, blank=True)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    gender = models.CharField(max_length=10)
    email = models.EmailField()
    phoneno = models.CharField(max_length=12)
    password = models.CharField(max_length=20)
    stream = models.CharField(max_length=30)
    college = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    otp = models.IntegerField(null=True, blank=True)
    otp_expire = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contests(models.Model):
    host = models.ForeignKey(Admins, null=True, blank=True, on_delete=models.SET_NULL)
    contest_type = models.IntegerField(default=0, help_text="0=codeathon, 1=passing_code, 2=code_wars")
    contest_code = models.CharField(max_length=15, unique=True)
    contest_pwd = models.CharField(max_length=15, null=True)
    organiser = models.CharField(max_length=30)
    shuffle = models.BooleanField(default=False)
    poster = models.ImageField(upload_to='posters', null=True, blank=True)
    title = models.CharField(max_length=50)
    description = models.TextField()
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    venue = models.CharField(max_length=30)
    status = models.CharField(max_length=15, default='draft')
    reg_status = models.IntegerField(default=0, help_text="0=user_can_register, 1=admin_need_to_approve")
    total_participants = models.IntegerField(null=True, blank=True)
    winner = models.ForeignKey(Users, null=True, blank=True, on_delete=models.SET_NULL, related_name='winner')
    runner = models.ForeignKey(Users, null=True, blank=True, on_delete=models.SET_NULL, related_name='runner')
    contact = models.CharField(max_length=12)
    prize = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_start_date(self):
        return self.start_date.strftime('%b %d')
    
    def get_start_time(self):
        return self.start_date.strftime('%H:%M')
    
    def time_rem(self):
        return self.start_date - timezone.now()
        
    def contest_url(self):
        if self.contest_type == 0:
            return 'codespace'
        if self.contest_type == 1:
            return 'passing_code'
        if self.contest_type == 2:
            return 'code_wars'


class Registrations(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    contest_id = models.ForeignKey(Contests, on_delete=models.CASCADE)
    started_time = models.DateTimeField(blank=True, null=True)
    test_status = models.IntegerField(default=0, help_text="0=Not Started, 1=Started, 2=Ended")
    email_status = models.IntegerField(default=0, help_text="0=Not sent, 1=sent before contest, 2=sent after contest")
    last_que_no = models.IntegerField(default=0, help_text="last solved que")#passing code
    que_start_time = models.DateTimeField(blank=True, null=True)#passing code
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def time_rem(self):
        return timezone.now() - self.started_time
        
    def que_time_rem(self):
        return timezone.now() - self.que_start_time


class Questions(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    que_desc = models.TextField()
    image = models.ImageField(upload_to='que_img', blank=True, null=True)
    level = models.CharField(max_length=15, blank=True, null=True)
    score = models.IntegerField()
    tc_count = models.IntegerField(blank=True, null=True)
    tle = models.FloatField(blank=True, null=True)
    testcases = models.FileField(upload_to='testcases', blank=True, null=True)
    outputs = models.FileField(upload_to='outputs', blank=True, null=True)
    solution = models.FileField(upload_to='solutions', blank=True, null=True)
    #MCQ
    que_type = models.IntegerField(default=0, help_text="0=coding, 1=mcq, 2=debugging")
    options = models.TextField(blank=True, null=True)
    correct_op = models.IntegerField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True) #for MCQ and PASSING CODE
    #debugging
    debug_language= models.CharField(max_length=15, blank=True, null=True)
    debug_code = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contest_question(models.Model):
    question_id = models.ForeignKey(Questions, blank=True, null=True, on_delete=models.SET_NULL)
    contest_id = models.ForeignKey(Contests, blank=True, null=True, on_delete=models.SET_NULL)


class Submissions(models.Model):
    question_id = models.ForeignKey(Questions, blank=True, null=True, on_delete=models.SET_NULL)
    contest_id = models.ForeignKey(Contests, blank=True, null=True, on_delete=models.SET_NULL)
    user_id = models.ForeignKey(Users, blank=True, null=True, on_delete=models.SET_NULL)
    code = models.TextField(null=True)
    language = models.CharField(max_length=15)
    score = models.IntegerField()
    status = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    

class CodeDuel(models.Model):
    user_id = models.ForeignKey(Users, blank=True, null=True, on_delete=models.SET_NULL)
    contest_id = models.ForeignKey(Contests, blank=True, null=True, on_delete=models.SET_NULL)
    online = models.IntegerField(default=0, help_text="0=ofline, 1=online")
    in_duel = models.IntegerField(default=0, help_text="0=not in duel, 1=in duel")
    opponent = models.CharField(max_length=30, blank=True, null=True)
    user_level = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active_time = models.DateTimeField(auto_now=True)
    

