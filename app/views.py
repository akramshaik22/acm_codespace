from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from app.models import Users, Contests, Registrations, Questions, Contest_question, Submissions, Admins, CodeDuel
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse

from django.db.models import Max, Sum, Count
from django.db.models import F, Q
from django.db.models import Subquery, OuterRef
from django.utils import timezone
from django.template.loader import render_to_string

#ABHISHEK
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
####

from django.core.mail import send_mail

import mysql.connector as mysql
import subprocess
import os
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta
import random

import threading
from django.core.mail import get_connection, EmailMultiAlternatives

def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, connection=None):

    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        # message.attach_alternative(html, 'text/html')
        messages.append(message)

    return connection.send_messages(messages)

# from django import template
# register = template.Library()

# @register.filter(name='time_difference')
# def time_difference(value):
#     current_time = datetime.now()
#     time_difference = value - current_time
#     return time_difference

def generate_otp():
    return random.randint(100000, 999999)

def test_mail(req):
    if req.method == 'POST':
        from_email = settings.EMAIL_HOST_USER
        datatuple = [['subject', '', render_to_string('otp_email_template.html', {'user': ''}), from_email, ['ssabadocs.786@gmail.com']], ['subject', '', render_to_string('otp_email_template.html', {'user': ''}), from_email, ['bhargavratnala2004@gmail.com']]]*1000
        thread = threading.Thread(target=send_mass_html_mail, args=(datatuple,))
        thread.start()
        # akram, bhargav = [], []
        # for i in range(300):
        #     if i&1:
        #         status = send_mail(
        #                 subject='Bhargav',
        #                 message='This is temp mail from ACM Codespace.',
        #                 from_email=from_email,
        #                 recipient_list=['bhargavratnala2004@gmail.com'],
        #                 # html_message=render_to_string('otp_email_template.html', {'user': user}),
        #                 )
        #         bhargav.append(status)
        #     else:
        #         status = send_mail(
        #                 subject='Akram',
        #                 message='This is temp mail from ACM Codespace.',
        #                 from_email=from_email,
        #                 recipient_list=['ssabadocs.786@gmail.com'],
        #                 # html_message=render_to_string('otp_email_template.html', {'user': user}),
        #                 )
        #         akram.append(status)
    
        # return JsonResponse({'akram':akram.count(0), 'bhargav':bhargav.count(0)})
        return JsonResponse({'akram':'success'})
    
    return render(req, 'temp.html')
        
    
    
def send_otp(req):
    if req.method == 'POST':
        if '@' in req.POST['email']:
            user = Users.objects.filter(email=req.POST['email'])
        else:
            user = Users.objects.filter(username=req.POST['email'])
            
        if not user:
            return JsonResponse({'status':2}, status=200)
            
        user = user[0]
        otp = generate_otp()
        user.otp = otp
        user.otp_expire = timezone.now() + timedelta(minutes=30)
        user.save()
        from_email = settings.EMAIL_HOST_USER
        status = send_mail(
            subject='OTP to Reset Password for ACM_CODESPACE.',
            message='',
            from_email=from_email,
            recipient_list=[user.email],
            html_message=render_to_string('otp_email_template.html', {'user': user}),
            )
        
        args = {
            'status': status,
        }
            
        return JsonResponse(args, status = 200)
    
    return JsonResponse({'status':2}, status=200)
    
    
def verify_otp(req):
    if req.method == 'POST':
        if '@' in req.POST['email']:
            user = Users.objects.filter(email=req.POST['email'], otp=req.POST['otp'])
        else:
            user = Users.objects.filter(username=req.POST['email'], otp=req.POST['otp'])
            
        if not user:
            return JsonResponse({'status':0}, status=200) #INVALID OTP OR USER NOT EXISTS
        user = user[0]
        if user.otp_expire < timezone.now():
            return JsonResponse({'status':2}, status=200) #OTP EXPIRED
        
        return JsonResponse({'status':1}, status=200) #OTP VERIFIED
    
    return JsonResponse({'status':0}, status=200)
    
    
def reset_password(req):
    if req.method == 'POST':
        if '@' in req.POST['email']:
            user = Users.objects.filter(email=req.POST['email'], otp=req.POST['otp'])
        else:
            user = Users.objects.filter(username=req.POST['email'], otp=req.POST['otp'])
        
        if not user:
            return render(req, 'reset_password.html', {'error':'username/email and otp doesnt match'})
        
        user = user[0]
        user.password = req.POST['password']
        user.save()
        
        return redirect('/codespace/user_login')
        
    return render(req, 'reset_password.html', {'error':''})
    

def custom_mail(req):
    if req.user.is_authenticated:
        contests = Contests.objects.all()
        args = {
            'contests':contests,
        }
        return render(req, 'custom_mail_template.html', args)
    
    return redirect('/codespace/admin_login')


def send_custom_mails(req):
    if req.method == 'POST':
        contest_code = req.POST['contest_code']
        recipient_list = []
        # datatuple = []
        subject = req.POST['subject']
        from_email = settings.EMAIL_HOST_USER
        
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest = contest[0]
            participants = Registrations.objects.filter(contest_id=contest)
            for user in participants:
                # datatuple.append([subject, '', render_to_string(req.POST['email_content']), from_email, [user.email]])
                recipient_list.append(user.user_id.email)
                
        elif contest_code=='all_users':
            # recipient_list = ['ssabadocs.786@gmail.com', 'bhargavratnala2004@gmail.com', 'ssabamovies.786@gmail.com']
            
            users = Users.objects.all()
            recipient_list = []
            for user in users:
                recipient_list.append(user.email)
        else:
            return JsonResponse({'status':2}, status=200)
        
        # send_mass_html_mail(datatuple)
        # try:
        status = send_mail(
                subject=subject,
                message='',
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=req.POST['email_content'],
                )
        # except:
        #     status = 2
            
        return JsonResponse({'status':status}, status=200)
        
    return redirect('/codespace/admin_login') 


def home(req):
    # send_mail_to_user("subject", "Hi this is Akram", ["bhargavratnala2004@gmail.com"])
    arg = {'username':''}
    if 'username' in req.session:
        username = req.session['username']
        user = Users.objects.filter(username=username)[0]
        arg['username'] = username
        if user.profile_pic:
            arg['profileUrl'] = user.profile_pic.url
        else:
            arg['profileUrl'] = ''
            
    upcoming = Contests.objects.filter(status='published').order_by('-start_date')
    past = Contests.objects.filter(status='past').order_by('-start_date')[:2]
    
    arg['past'] = past
    arg['upcoming'] = upcoming
    
    return render(req, 'home.html', arg)


def admin_login(req):
    if req.method == 'POST':
        if '@' in req.POST['username']:
            user = authenticate(email=req.POST['username'], password=req.POST['password'])
        else:
            user = authenticate(username=req.POST['username'], password=req.POST['password'])
            
        if user:
            login(req, user)
            
            return redirect('/codespace/admin_contests/published')
        
    return render(req, 'admin_login.html')


def admin_logout(req):
    if req.user.is_authenticated:
        logout(req)
        return redirect('/codespace/admin_login')


def admin_contests(req, contest_type):
    if req.user.is_authenticated:
        if  contest_type in ['ongoing', 'published', 'drafts', 'past']:
                
            args = {
                'contests': Contests.objects.filter(status=contest_type).order_by('-start_date'),
                'contest_type': contest_type.title(),
                'is_superadmin': req.user.is_superadmin
            }
            
            return render(req, 'admin_contests.html', args)
        
        elif contest_type in ['add_contest']:
            return add_contest(req)
    
    return redirect('/codespace/admin_login')
    

def add_contest(req):
    
    if req.method=="POST":
        
        poster = ''
        if 'poster' in req.FILES:
            poster = req.FILES['poster']
            
        contest = Contests(
            host = req.user,
            contest_code = req.POST['contest_code'],
            contest_pwd = req.POST['contest_pwd'],
            organiser = req.POST['organiser'],
            title = req.POST['title'],
            poster = poster,
            description = req.POST['description'],
            time = req.POST['time'],
            venue = req.POST['venue'],
            contact = req.POST['contact'],
            prize = req.POST['prize'],
            status='drafts',
            start_date = req.POST['start_date'],
            end_date = req.POST['end_date'],
            contest_type = req.POST['contest_type'],
            )
            
        contest.save()
        
        return redirect('/codespace/admin_contests/drafts')
            
    return render(req, 'addcontest.html')


def edit_contest(req, contest_type, contest_code):
    
    if req.method=="POST":
            
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest = contest[0]
            
            contest.contest_pwd = req.POST['contest_pwd']
            contest.organiser = req.POST['organiser']
            contest.title = req.POST['title']
            contest.description = req.POST['description']
            contest.time = req.POST['time']
            contest.venue = req.POST['venue']
            contest.contact = req.POST['contact']
            contest.prize = req.POST['prize']
            contest.start_date = req.POST['start_date']
            contest.end_date = req.POST['end_date']
            
            winner = Users.objects.filter(username=req.POST['winner'])
            runner = Users.objects.filter(username=req.POST['runner'])
            
            if winner:
                contest.winner = winner[0]
                if runner:
                    contest.runner = runner[0]
            
            if 'poster' in req.FILES:
                contest.poster = req.FILES['poster']
                
            contest.save()
        
    return redirect(f'/codespace/admin_contests/{ contest_type }/{ contest_code }/')


def publish_contest(req, contest_type, contest_code):
    if req.user.is_authenticated:
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest[0].status = 'published'
            contest[0].save()
    
    return redirect(f"/codespace/admin_contests/published")
    
    
def start_contest(req, contest_type, contest_code):
    if req.user.is_authenticated:
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest[0].status = 'ongoing'
            contest[0].start_date = timezone.now()
            contest[0].end_date = timezone.now() + timedelta(minutes=contest[0].time)
            contest[0].save()
            
            try:
                contest = contest[0]
                participants = Registrations.objects.filter(contest_id=contest)#, email_status=1)
                from_email = settings.EMAIL_HOST_USER
                
                datatuple = []
                subject=f'{contest.title} Contest Have been Started'
                for user in participants:
                    datatuple.append([subject, '',render_to_string('contest_started_email_template.html', {'user': user.user_id, 'contest':contest}), from_email, [user.user_id.email]])
                    
                send_mass_html_mail(datatuple)
                
                # for user in participants:
                #     status = send_mail(
                #         subject=f'{contest.title} Contest Have been Started',
                #         message='',
                #         from_email=from_email,
                #         recipient_list=[user.user_id.email],
                #         html_message=render_to_string('contest_started_email_template.html', {'user': user.user_id, 'contest':contest}),
                #         )
                    
                    # user.email_status = 2
                    # user.save()
            except:
                pass
    
    return redirect(f"/codespace/admin_contests/ongoing")
    
    
def end_contest(req, contest_type, contest_code):
    if req.user.is_authenticated:
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            reg = Registrations.objects.filter(contest_id=contest[0])
            contest[0].total_participants = reg.count()
            contest[0].status = 'past'
            contest[0].save()
            try:
                contest = contest[0]
                participants = Registrations.objects.filter(contest_id=contest)#, email_status=2)
                from_email = settings.EMAIL_HOST_USER
                
                datatuple = []
                subject=f'{contest.title} Contest Have been Started'
                for user in participants:
                    datatuple.append([subject, '',render_to_string('contest_ended_email_template.html', {'user': user.user_id, 'contest':contest}), from_email, [user.user_id.email]])
                    
                send_mass_html_mail(datatuple)
                
                # for user in participants:
                #     status = send_mail(
                #         subject=f'{contest.title} Contest Have been Ended',
                #         message='',
                #         from_email=from_email,
                #         recipient_list=[user.user_id.email],
                #         html_message=render_to_string('contest_ended_email_template.html', {'user': user.user_id, 'contest':contest}),
                #         )
                    
                    # user.email_status = 3
                    # user.save()
            except:
                pass
    
    return redirect(f"/codespace/admin_contests/past")


def contest_details(req, contest_type, contest_code):
    if req.user.is_authenticated:
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest = contest[0]
            opponent_status = 0
            ln = 0
            codewars = 0
            if contest.contest_type==2:
                code_duel = CodeDuel.objects.filter(contest_id=contest, online=1)
                ln = len(code_duel)
                if code_duel:
                    if code_duel[0].opponent:
                        opponent_status = 0
                    else:
                        opponent_status = 1
                codewars = 1
                
            args = {
                'contest':contest,
                'contest_title': contest.title,
                'contest_type': contest_type,
                'contest_code': contest_code,
                'winner': contest.winner.username if contest.winner else "",
                'runner': contest.runner.username if contest.runner else "",
                'type': "disabled",
                'codewars':codewars,#CODEWARS
                'opponent_status': opponent_status, #CODE_WARS Set Opponents
                "online_participants": ln,  #CODE_WARS online count
            }
            if req.method == "POST":
                if req.POST["type"] == "disabled":
                    args["type"] = ""
            
            return render(req, 'contest_details.html', args)
        
    return redirect('/codespace/admin_contests')
    

def contest_questions(req, contest_type, contest_code):
    
    if req.user.is_authenticated:
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            # contest = contest[0]
            que_obj = [i.question_id for i in Contest_question.objects.filter(contest_id=contest[0])]
            
            args = {
                'contest_type': contest_type,
                'contest_code': contest_code,
                'contest_title': contest[0].title,
                'ques': que_obj,
                'total_que': len(que_obj),
                'total_score': sum([i.score for i in que_obj]),
                
            }
            
            return render(req, 'contest_questions.html', args)
    
    return redirect('/codespace/admin_contests')


def add_que(req, contest_type, contest_code):
    
    if req.method=="POST":
        
        que_img = ''
        if 'que_img' in req.FILES:
            que_img = req.FILES['que_img']
            
        que = Questions(
            title=req.POST['title'],
            que_desc=req.POST['que_desc'],
            image=que_img,
            level=req.POST['level'],
            score=req.POST['score'],
            tc_count=req.POST['tc_count'],
            tle=req.POST['tle'],
            testcases=req.FILES['input_cases'],
            outputs=req.FILES['output_cases'],
            solution=req.FILES['solution'],
            que_type = req.POST['que_type'],
            )
            
        if req.POST['que_type'] == "2":
            que.que_type = 2
            que.debug_code = req.POST['debug_code']
            que.debug_language = req.POST['debug_lang']
            
        que.save()
            
        Contest_question(
            question_id=que,
            contest_id=Contests.objects.get(contest_code=req.POST['contest_code'])
            ).save()
        
        return redirect(f"/codespace/admin_contests/{ contest_type }/{ contest_code }/questions/")
        

def edit_que(req, contest_type, contest_code):
    if req.method == 'POST':
        
        que = Questions.objects.filter(id=req.POST['que_id'])
        
        if que:
            
            que = que[0]
            que.title=req.POST['title']
            que.que_desc=req.POST['que_desc']
            # que.image=que_img
            que.level=req.POST['level']
            que.score=req.POST['score']
            que.tc_count=req.POST['tc_count']
            que.tle=req.POST['tle']
            que.testcases=req.FILES['input_cases']
            que.outputs=req.FILES['output_cases']
            if 'que_img' in req.FILES:
                que.image = req.FILES['que_img']
            if 'solution' in req.FILES:
                que.solution=req.FILES['solution']
            
            if req.POST['que_type'] == "2":
                que.que_type = 2
                que.debug_code = req.POST['debug_code']
            
            que.save()
            
    return redirect(f"/codespace/admin_contests/{ contest_type }/{ contest_code }/questions/")


def get_que_data(req):
    if req.method == 'POST':
        que = Questions.objects.filter(id=req.POST['que_id'])
        if que:
            que = que[0]
            
            que_img = ''
            if que.image:
                que_img = '/codespace/' + str(que.image.url)
                
            args = {
                'title': que.title,
                'level': que.level,
                'que_desc': que.que_desc,
                'score': que.score,
                'tc_count': que.tc_count,
                'tle': que.tle,
                'que_img': que_img,
                'que_type':que.que_type,
                'inputs': i_o_extract(que.testcases.url),
                'outputs': i_o_extract(que.outputs.url),
            }
                
            if req.POST['sub_type'] == '0':
                #VIEW
                with open(str(settings.BASE_DIR) + que.solution.url) as file:
                    args['solution'] = file.read()
            else:
                #EDIT
                args['solution'] = que.solution.url
            
            return JsonResponse(args, status = 200)


def registrations(req, contest_type, contest_code):
    if req.user.is_authenticated:
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest = contest[0]
            reg = Registrations.objects.filter(contest_id=contest).order_by('created_at')
            
            args = {
                'registrations': reg,
                'contest_title': contest.title,
                'contest_code': contest_code,
                'contest_type': contest_type,
            }
            
            return render(req, 'contest_registrations.html', args)
    
    return redirect('/codespace/admin_contests/'+contest_type)


def submissions(req, contest_type, contest_code):
    
    if req.user.is_authenticated:
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest = contest[0]
            max_score_subquery = Submissions.objects.filter(
                contest_id=contest,
                user_id=OuterRef('user_id'),
                question_id=OuterRef('question_id')
            ).order_by('-score', 'created_at').values('score')[:1]
            
            time_subquery = Submissions.objects.filter(
                contest_id=contest,
                user_id=OuterRef('user_id'),
                question_id=OuterRef('question_id')
            ).order_by('-score', 'created_at').values('created_at')[:1]
            
            code_subquery = Submissions.objects.filter(
                contest_id=contest,
                user_id=OuterRef('user_id'),
                question_id=OuterRef('question_id'),
                created_at=OuterRef('time'),
                score=OuterRef('score')
            ).values('code')[:1]
            
            username_subquery = Users.objects.filter(
                id=OuterRef('user_id')
                ).values('username')[:1]
                
            que_title_subquery = Questions.objects.filter(
                id = OuterRef('question_id')
                ).values('title')[:1]
                
            que_desc_subquery = Questions.objects.filter(
                id = OuterRef('question_id')
                ).values('que_desc')[:1]
            
            queryset = Submissions.objects.filter(contest_id=contest).values('user_id', 'question_id').annotate(
                username=Subquery(username_subquery),
                que_title=Subquery(que_title_subquery),
                que_desc=Subquery(que_desc_subquery),
                score=Subquery(max_score_subquery),
                time=Subquery(time_subquery),
                code = Subquery(code_subquery)
            ).order_by('user_id', 'question_id').distinct()
            
            pd.DataFrame(queryset).to_csv("./media/submissions.csv")
            
            args = {
                'submissions': queryset,
                'contest_title': contest.title,
                'contest_code': contest_code,
                'contest_type': contest_type,
            }
            
            return render(req, 'contest_submissions.html', args)
            
    return redirect('/codespace/admin_contests/'+contest_type)
    

def dashboard(req, contest_type, contest_code):
    
    if req.user.is_authenticated:
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest_id = contest[0].id
            # query = "SELECT t1.user_id_id, t4.username, concat(t4.fname, ' ', t4.lname) as Name, t2.score, t1.time FROM ( (SELECT MAX(created_at) AS time, user_id_id FROM app_submissions GROUP BY user_id_id) t1 JOIN (SELECT user_id_id, SUM(q_score) AS score FROM ( SELECT user_id_id, question_id_id, MAX(score) AS q_score FROM app_submissions GROUP BY user_id_id, question_id_id ) t3 GROUP BY user_id_id) t2 JOIN (SELECT id, username, fname, lname FROM app_users) t4 ON t1.user_id_id = t2.user_id_id and t1.user_id_id = t4.id ) ORDER BY t2.score DESC, t1.time ASC;"
            query = f"SELECT t1.user_id_id, t4.username, concat(t4.fname, ' ', t4.lname) as Name, t2.score, t1.time FROM ( (SELECT MAX(created_at) AS time, user_id_id FROM app_submissions where contest_id_id={contest_id} GROUP BY user_id_id) t1 JOIN (SELECT user_id_id, SUM(q_score) AS score FROM ( SELECT user_id_id, question_id_id, MAX(score) AS q_score FROM app_submissions  where contest_id_id={contest_id} GROUP BY user_id_id, question_id_id ) t3 GROUP BY user_id_id) t2 JOIN (SELECT id, username, fname, lname FROM app_users) t4 ON t1.user_id_id = t2.user_id_id and t1.user_id_id = t4.id ) ORDER BY t2.score DESC, t1.time ASC;"
            
            # dashboard = Submissions.objects.all().raw(query)
            
            mycon = mysql.connect(host = 'localhost',
                                  user = 'gmritchapterhost_codespace_admin',
                                  password = 'Codespace@2023' ,
                                  database = 'gmritchapterhost_codespace')
            cur = mycon.cursor()
            cur.execute(query)
            res = cur.fetchall()
            
            mycon.close()
            
            pd.DataFrame(res, columns=['user_id', 'username', 'Name', 'Total Score', 'Time']).to_csv('./media/dashboard.csv')
            
            args = {
                'dashboard': res,
                'contest_title': contest[0].title,
                'contest_code': contest_code,
                'contest_type': contest_type,
                'contest_list': Contests.objects.filter(reg_status=1, status='published')
            }
            
            return render(req, 'contest_dashboard.html', args)
            
    return redirect('/codespace/admin_contests/'+contest_type)


def event_promoted_status(req, contest_type, contest_code):
    if req.user.is_authenticated:
        if req.method == 'POST':
            promoted_contest = Contests.objects.filter(contest_code=req.POST['promoted_contest'])[0]
            promoted_contest_id = promoted_contest.id
            # reg = Registrations.objects.filter(contest_id=promoted_contest)
            contest = Contests.objects.filter(contest_code=contest_code)
            contest_id = contest[0].id
            # query = "SELECT t1.user_id_id, t4.username, concat(t4.fname, ' ', t4.lname) as Name, t2.score, t1.time FROM ( (SELECT MAX(created_at) AS time, user_id_id FROM app_submissions GROUP BY user_id_id) t1 JOIN (SELECT user_id_id, SUM(q_score) AS score FROM ( SELECT user_id_id, question_id_id, MAX(score) AS q_score FROM app_submissions GROUP BY user_id_id, question_id_id ) t3 GROUP BY user_id_id) t2 JOIN (SELECT id, username, fname, lname FROM app_users) t4 ON t1.user_id_id = t2.user_id_id and t1.user_id_id = t4.id ) ORDER BY t2.score DESC, t1.time ASC;"
            query = f"SELECT t1.user_id_id, t4.username, concat(t4.fname, ' ', t4.lname) as Name, t2.score, case when t1.user_id_id in (select user_id_id from app_registrations where contest_id_id = {promoted_contest_id}) then 1 else 0 end as promote, t1.time FROM ( (SELECT MAX(created_at) AS time, user_id_id FROM app_submissions where contest_id_id={contest_id} GROUP BY user_id_id) t1 JOIN (SELECT user_id_id, SUM(q_score) AS score FROM ( SELECT user_id_id, question_id_id, MAX(score) AS q_score FROM app_submissions  where contest_id_id={contest_id} GROUP BY user_id_id, question_id_id ) t3 GROUP BY user_id_id) t2 JOIN (SELECT id, username, fname, lname FROM app_users) t4 ON t1.user_id_id = t2.user_id_id and t1.user_id_id = t4.id ) ORDER BY t2.score DESC, t1.time ASC;"
            
            # dashboard = Submissions.objects.all().raw(query)
            
            mycon = mysql.connect(host = 'localhost',
                                  user = 'gmritchapterhost_codespace_admin',
                                  password = 'Codespace@2023' ,
                                  database = 'gmritchapterhost_codespace')
            cur = mycon.cursor()
            cur.execute(query)
            res = cur.fetchall()
            
            mycon.close()
        
            args = {
                'dashboard': res,
            }
            
            return JsonResponse(args, status=200)


def promote_to_contest(req, contest_type, contest_code):
    if req.user.is_authenticated:
        if req.method == 'POST':
            promoted_contest = Contests.objects.filter(contest_code=req.POST['promoted_contest'])[0]
            promoted_contest_id = promoted_contest.id
            
            contest = Contests.objects.filter(contest_code=contest_code)[0]
            contest_id = contest.id
            
            usernames_list = req.POST['usernames'].split(',')
            
            users = Users.objects.filter(username__in=usernames_list)
            from_email = settings.EMAIL_HOST_USER
            if users:
                datatuple = []
                subject=f'Results for {contest.title}'
                for user in users:
                    reg = Registrations(
                        user_id = user,
                        contest_id = promoted_contest,
                        )
                    
                    datatuple.append([subject, 'You are Promoted to PassingCode ', None, from_email, [user.email]])
                    # datatuple.append([subject, '',render_to_string('contest_promoted_email_template.html', {'user': user, 'contest':contest, 'promoted_contest':promoted_contest}), from_email, [user.email]])
                    
                    # status = send_mail(
                    #     subject = f'Results for {contest.title}',
                    #     message= '', #f'You have Promoted to {promoted_contest.title}',
                    #     from_email=from_email,
                    #     recipient_list=[user.email],
                    #     html_message=render_to_string('contest_promoted_email_template.html', {'user': user, 'contest':contest, 'promoted_contest':promoted_contest}),
                    #     )
                    
                    # if status:
                    #     reg.email_status = 1
                        
                    reg.save()
                
                send_mass_html_mail(datatuple)
            
        return redirect(f'/codespace/admin_contests/{contest_type}/{contest_code}/dashboard')
    
    return redirect(f'/codespace/admin_login')
        
        


def userlogin(req):
    
    if req.method == "POST":
        username = req.POST['username']
        password = req.POST['password']
        
        if '@' in username:
            user = Users.objects.filter(email=username, password=password)
        else:
            user = Users.objects.filter(username=username, password=password)
            
        if user:
            req.session['username'] = user[0].username
            
            try:
                os.mkdir("./media/submissions/"+ req.session["username"])
            except:
                pass
            
            return redirect('/codespace')
        
        else:
            return render(req, 'loginuser.html', {'message' : 'Invalid Username or password'})
    
    return render(req, 'loginuser.html')
 
    
def userlogout(req):
    if('username' in req.session):
        del req.session['username']
    return redirect('/codespace')


def user_reg(req):
    
    if req.method=="POST":
        
        profile_pic = ''
        if 'profile_pic' in req.FILES:
            profile_pic = req.FILES['profile_pic']
        
        Users(
            username = req.POST['username'],
            profile_pic = profile_pic,
            fname = req.POST['fname'],
            lname = req.POST['lname'],
            gender = req.POST['gender'],
            email = req.POST['email'],
            phoneno = req.POST['contact'],
            password = req.POST['password'],
            stream = req.POST['stream'],
            college = req.POST['college'],
            ).save()
            
        try:
            os.mkdir("./media/submissions/"+ req.POST["username"])
        except:
            pass
        
        return redirect('/codespace/user_login')
    return render(req, 'registeruser.html')
    
    
def check_username(req):
    
    status = 0
    if req.method == "POST":
        if 'contest_code' in req.POST:
            obj = Contests.objects.filter(contest_code=req.POST['contest_code'])
        elif 'username' in req.POST:
            obj = Users.objects.filter(username=req.POST['username'])
        elif 'email' in req.POST:
            obj = Users.objects.filter(email=req.POST['email'])
        else:
            obj = Users.objects.filter(phoneno=req.POST['phone'])
        
        if obj:
            status = 0
        else:
            status = 1
     
    return JsonResponse({"status": status}, status = 200)
    
    
def user_profile(req, username):
    
    user = Users.objects.filter(username=username)
    if user:
        user = user[0]
        
        sub_subquery = Submissions.objects.filter(
            user_id=OuterRef('user_id'),
            question_id=OuterRef('question_id'),
            status__in=["W", "PA", "A"]
        ).order_by('-score')
            
        que_subquery = Questions.objects.filter(
            id = OuterRef('question_id'),
            )
        
        sub_que = Submissions.objects.filter(user_id=user).values('question_id').annotate(
            # que=Subquery(que_subquery),
            que_title=Subquery(que_subquery.values('title')[:1]),
            level=Subquery(que_subquery.values('level')[:1]),
            max_score=Subquery(que_subquery.values('score')[:1]),
            # sub=Subquery(sub_subquery),
            score=Subquery(sub_subquery.values('score')[:1]),
            status=Subquery(sub_subquery.values('status')[:1]),
        ).order_by('question_id').distinct().filter(status__in=["W", "PA", "A"])
        
        solved_que = sub_que.filter(status="A")
        e_count, m_count, h_count = [], [], []
        if solved_que:
            e_count = solved_que.filter(level="easy")
            m_count = solved_que.filter(level="medium")
            h_count = solved_que.filter(level="hard")
        
        profile_pic = ""    
        if user.profile_pic:
            profile_pic = user.profile_pic.url
        
        args = {
            'name': (user.fname + " " + user.lname).title(),
            'username' : user.username,
            'profileUrl':profile_pic,
            'email' : "",
            'phno' : "",
            'gender' : user.gender, 
            'college' : user.college,
            'stream' : user.stream,
            'login_username': "",
            'login_profileUrl': "",
            'sub_que': sub_que,
            'solved_que_count': len(solved_que),
            'e_count':len(e_count),
            'm_count':len(m_count),
            'h_count':len(h_count),
        }
        
        if 'username' in req.session:
            if req.session['username']==username:
                args['email'] = user.email
                args['phno'] = user.phoneno
                args['login_username'] = args['username']
                args['login_profileUrl'] = args['profileUrl']
            else:
                login_user = Users.objects.filter(username=req.session['username'])[0]
                args['login_username'] = login_user.username
                args['login_profileUrl'] = login_user.profile_pic.url
            
        
        return render(req, 'user_profile.html', args)
    else:
        return redirect('/codespace')


def contests(req):
    args = {'username':''}
    if 'username' in req.session:
        username = req.session['username']
        user = Users.objects.get(username=username)
        args['username'] = username
        if user.profile_pic:
            args['profileUrl'] =  user.profile_pic.url
        else:
            args['profileUrl'] = ''
        args['reg_list'] = [i.contest_id.id for i in Registrations.objects.filter(user_id=user)]
    else:
        args['reg_list'] = []
    args['ongoing'] = Contests.objects.filter(status='ongoing').order_by('-start_date')
    args['upcoming'] = Contests.objects.filter(status='published').order_by('-start_date')
    args['past'] = Contests.objects.filter(status='past').order_by('-start_date')
    
    
    return render(req, 'contests.html', args)
    

def contest_info(req, contest_code):
    args = {'username':''}
    if 'username' in req.session:
        username = req.session['username']
        user = Users.objects.get(username=username)
        args['username'] = username
        if user.profile_pic:
            args['profileUrl'] =  user.profile_pic.url
        else:
            args['profileUrl'] = ''
        args['reg_list'] = [i.contest_id.id for i in Registrations.objects.filter(user_id=user)]
    else:
        args['reg_list'] = []
        
    contest = Contests.objects.filter(status__in=['ongoing', 'published', 'past'], contest_code=contest_code)
    
    if not contest:
        return redirect('/codespace/contests')
    
    args['contest'] = contest[0]
    
    return render(req, 'contest_info.html', args)
    

def register_contest(req, contest_code):
    if 'username' in req.session:
        user = Users.objects.filter(username=req.session['username'])[0]
        # user = Users.objects.all()
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest = contest[0]
            reg = Registrations.objects.filter(user_id=user, contest_id=contest)
            # if reg or timezone.now()>contest.start_date:
            #     return redirect('/codespace/contests')
            
            reg = Registrations(
                    user_id = user,
                    contest_id = contest,
                    )
                    
            reg.save()
            try:
                from_email = settings.EMAIL_HOST_USER
                status = send_mail(
                    subject=f'Registration for {contest.title} is Accepted.',
                    message='',
                    from_email=from_email,
                    recipient_list=[user.email],
                    html_message=render_to_string('contest_reg_email_template.html', {'user': user, 'contest':contest}),
                    )
            except:
                pass
            
            # if status:
            # reg.email_status = 1
            # reg.save()
            
            return redirect('/codespace/contests')
            
    return redirect('/codespace/user_login')
        

def testend(req, contest_code):
    arg = {'username':''}
    if 'username' in req.session:
        username = req.session['username']
        user = Users.objects.get(username=username)
        
        arg['username'] = username
        if user.profile_pic:
            arg['profileUrl'] =  user.profile_pic.url
        else:
            arg['profileUrl'] = ''
            
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            reg = Registrations.objects.filter(user_id=user, contest_id=contest[0])
            if reg:
                reg[0].test_status = 2
                reg[0].save()
                try:
                    from_email = settings.EMAIL_HOST_USER
                    status = send_mail(
                        subject=f'Thank You For Participating in {contest[0].title}.',
                        message=f'Thank You For Participating in {contest[0].title}.',
                        from_email=from_email,
                        recipient_list=[user.email],
                        html_message=render_to_string('contest_ended_email_template.html', {'user': user, 'contest':contest[0]}),
                        )
                except:
                    pass
        else:
            return redirect('/codespace')
            
        return render(req, 'testend.html', arg)
        
    return redirect('/codespace/user_login')


def practice(req):
    
    args = {}
    
    if 'username' in req.session:
        user = Users.objects.filter(username=req.session['username'])[0]
        contest_list = [i.id for i in Contests.objects.filter(status__in=['past', 'practice'])]
        # contest_list.append()
        que_list = [i.question_id.id for i in Contest_question.objects.filter(Q(contest_id__in=contest_list) | Q(contest_id__isnull=True))]
        
        sub_subquery = Submissions.objects.filter(
                user_id=user.id,
                question_id=OuterRef('id'),
                status='A'
            )
        
        que = Questions.objects.filter(id__in=que_list, que_type=0).values('id', 'title', 'level').annotate(
            status=Subquery(sub_subquery.values('status')[:1]),
            )
        
        profile_pic = ""    
        if user.profile_pic:
            profile_pic = user.profile_pic.url
        args = {
            'que': que,
            'username': user.username,
            'profileUrl': profile_pic,
            
        }
        
        return render(req, 'practice.html', args)
    
    return redirect('/codespace/user_login')


def practice_codespace(req, que_id):
    if 'username' in req.session:
        user = Users.objects.filter(username=req.session['username'])[0]
        que_id = int(que_id)
        contest_list = [i.id for i in Contests.objects.filter(status__in=['past', 'practice'])]
        que_list = [i.question_id.id for i in Contest_question.objects.filter(contest_id__in=contest_list)]
        # que_obj = Questions.objects.filter(id__in=que_list)
        
        sub_subquery = Submissions.objects.filter(
                user_id=user.id,
                question_id=OuterRef('id'),
                status='A'
            )
        
        que_obj = Questions.objects.filter(id__in=que_list, que_type=0).values('id', 'title', 'level', 'score').annotate(
            status=Subquery(sub_subquery.values('status')[:1]),
            ).order_by('id')
        
        obj = Questions.objects.filter(id=que_id)
        if obj:
            que_no = 1
            for i in que_obj:
                if i['id'] == que_id:
                    break
                que_no += 1
                
            obj = obj[0]
            sub = Submissions.objects.filter(user_id=user, question_id=obj).order_by('-id')
            que_status = ''
            prev_code = ''
            if(sub):
                prev_code = sub[0].code
                
                que_status = sub.order_by('-score')[0].status
            que_status = "Solved" if que_status=='A' else "Unsolved"
            
            inp = i_o_extract(obj.testcases.url)
            out = i_o_extract(obj.outputs.url)
            
            img_url = obj.image
            if img_url:
                img_url = '/codespace/' + img_url.url
            else:
                img_url = ''
            
            args = {
                "que_type": obj.que_type,
                "username":req.session["username"],
                "contest_code": "",
                "que_no": que_no,
                "que": obj.que_desc,
                "total_que": len(que_obj),
                "code": prev_code,
                "inputs": inp[0],
                "outputs": out[0],
                "results" : '\n',
                "img_url": img_url,
                "obj": que_obj,
                "total_score": "--",
                "que_status": que_status,
            }
            
            return render(req, 'codespace.html', args)
            
        else:
            return redirect('/codespace/practice')
        
    else:
        return redirect('/codespace/user_login')


def codespace(req, contest_code):
    
    args = {}
    
    # req.session["contest_code"] = contest_code
    if 'username' in req.session:
        contest = Contests.objects.filter(contest_code=contest_code, status='ongoing')
        
        user = Users.objects.filter(username=req.session['username'])[0]
        
        
        if contest:
            contest = contest[0]
            
            profile_pic = ""    
            if user.profile_pic:
                profile_pic = user.profile_pic.url
                
            if contest.contest_pwd:
                args = {
                    'username': user.username,
                    'profileUrl': profile_pic,
                    'contest_code': contest_code,
                    'alert': '',
                }
                if 'contest_pwd' in req.POST:
                    if req.POST['contest_pwd'] != contest.contest_pwd:
                        args['alert'] = 'Enter Valid Contest Password'
                        return render(req, 'contest_pwd_validate.html', args)
                else:
                    return render(req, 'contest_pwd_validate.html', args)
                
            reg = Registrations.objects.filter(user_id=user, contest_id=contest)
            
            if not reg:
                return redirect(f'/codespace/contests')
                
            reg = reg[0]
            
            if reg.test_status == 2:
                return redirect(f'/codespace/{ contest_code }/testend')
            
            if reg.test_status == 0:
                reg.test_status = 1
                reg.started_time = timezone.now()
                reg.save()
            
            # contest_list = [i.id for i in Contests.objects.filter(status__in=['past', 'practice'])]
            que_list = [i.question_id.id for i in Contest_question.objects.filter(contest_id=contest.id)]
            # que_obj = Questions.objects.filter(id__in=que_list)
            
            sub_subquery = Submissions.objects.filter(
                    user_id=user.id,
                    question_id=OuterRef('id'),
                    status='A'
                )
            
            que_obj = Questions.objects.filter(id__in=que_list).values('id', 'title', 'level', 'score', 'image').annotate(
                status=Subquery(sub_subquery.values('status')[:1]),
                )
            
            obj = Questions.objects.filter(id=que_obj[0]['id'])[0]
            
            sub = Submissions.objects.filter(user_id=user, question_id=obj, language="python").order_by('-id')
            que_status = ''
            prev_code = ''
            # debug_code = ""
            debug_lang = ""
            if obj.que_type == 2:
                prev_code = obj.debug_code
                debug_lang = obj.debug_language
            if sub:
                prev_code = sub[0].code
                
                que_status = sub.order_by('-score')[0].status
            que_status = "Solved" if que_status=='A' else "Unsolved"
            
            img_url = obj.image
            if img_url:
                img_url = '/codespace/' + img_url.url
            else:
                img_url = ''
                
            # try:
            #     os.mkdir("./media/submissions/"+ req.session["username"])
            # except:
            #     pass
            
            # user = Registerations()
            
            # rem_time = 3600
            cur_time = timezone.now()
            start_time = reg.started_time
            
            if cur_time>contest.end_date:
                return redirect(f'/codespace/{ contest_code }/testend')
            
            rem_time = int(min(contest.time*60 - (cur_time-start_time).total_seconds(), (contest.end_date - cur_time).total_seconds()))
            
            if rem_time < 1 or rem_time>contest.time*60:
                reg.test_status = 2
                reg.save()
                return redirect(f'/codespace/{ contest_code }/testend')
                
            if obj.que_type == 1:
                args = {
                    "que_type": obj.que_type,
                    "que": obj.que_desc,
                    'img_url' : img_url,
                    'options' : obj.options.split("@dlim@"),
                    "selected_op": prev_code,
                    
                    "username":req.session["username"],
                    "contest_code": contest_code,
                    "test_time": rem_time,
                    "que_no": '1',
                    "total_que": len(que_list),
                    "code": '',
                    "img_url": img_url,
                    "inputs": '',
                    "outputs": '',
                    "results" : '\n',
                    "obj": que_obj,
                    "total_score":sum([i['score'] for i in que_obj]),
                    "que_status": que_status,
                    }
                    
                return render(req, 'codespace.html', args)
            
            inp = i_o_extract(obj.testcases.url)
            out = i_o_extract(obj.outputs.url)
            
            args = {
                "que_type": obj.que_type,
                "username":req.session["username"],
                "contest_code": contest_code,
                "test_time": rem_time,
                "que_no": '1',
                "que": obj.que_desc,
                "total_que": len(que_list),
                "code": prev_code,
                "img_url": img_url,
                "inputs": inp[0],
                "outputs": out[0],
                "results" : '\n',
                "obj": que_obj,
                "total_score":sum([i['score'] for i in que_obj]),
                "que_status": que_status,
            }    
            
            return render(req, 'codespace.html', args)
        
    
        else:
            return redirect('/codespace')
            
    else:
        return redirect('/codespace/user_login')


def passing_code(req, contest_code):
    args = {}
    
    # req.session["contest_code"] = contest_code
    if 'username' in req.session:
        contest = Contests.objects.filter(contest_code=contest_code, status='ongoing')
        
        user = Users.objects.filter(username=req.session['username'])[0]
        
        
        if contest:
            contest = contest[0]
            
            profile_pic = ""    
            if user.profile_pic:
                profile_pic = user.profile_pic.url
                
            if contest.contest_pwd:
                args = {
                    'username': user.username,
                    'profileUrl': profile_pic,
                    'contest_code': contest_code,
                    'alert': '',
                }
                if 'contest_pwd' in req.POST:
                    if req.POST['contest_pwd'] != contest.contest_pwd:
                        args['alert'] = 'Enter Valid Contest Password'
                        return render(req, 'contest_pwd_validate.html', args)
                else:
                    return render(req, 'contest_pwd_validate.html', args)
                
            reg = Registrations.objects.filter(user_id=user, contest_id=contest)
            
            if not reg:
                return redirect(f'/codespace/contests')
                
            reg = reg[0]
            
            if reg.test_status == 2:
                return redirect(f'/codespace/{ contest_code }/testend')
            
            if reg.test_status == 0:
                reg.test_status = 1
                reg.started_time = timezone.now()
                reg.save()
            
            # contest_list = [i.id for i in Contests.objects.filter(status__in=['past', 'practice'])]
            que_list = [i.question_id.id for i in Contest_question.objects.filter(contest_id=contest.id)]
            # que_obj = Questions.objects.filter(id__in=que_list)
            
            sub_subquery = Submissions.objects.filter(
                    user_id=user.id,
                    question_id=OuterRef('id'),
                    status='A'
                )
            
            que_obj = Questions.objects.filter(id__in=que_list).values('id', 'title', 'level', 'score', 'image').annotate(
                status=Subquery(sub_subquery.values('status')[:1]),
                ).order_by('id')
            
            obj = Questions.objects.filter(id=que_obj[reg.last_que_no]['id'])[0]
            
            sub = Submissions.objects.filter(user_id=user, question_id=obj).order_by('-id')
            que_status = ''
            prev_code = ''
            # debug_code = ""
            debug_lang = ""
            if obj.que_type == 2:
                prev_code = obj.debug_code
                debug_lang = obj.debug_language
            if sub:
                prev_code = sub[0].code
                
                que_status = sub.order_by('-score')[0].status
                
            que_status = "Solved" if que_status=='A' else "Unsolved"
            
            img_url = obj.image
            if img_url:
                img_url = '/codespace/' + img_url.url
            else:
                img_url = ''
                
            # try:
            #     os.mkdir("./media/submissions/"+ req.session["username"])
            # except:
            #     pass
            
            # user = Registerations()
            
            # rem_time = 3600
            # cur_time = timezone.now()
            # start_time = reg.started_time
            
            # if cur_time>contest.end_date:
            #     return redirect(f'/codespace/{ contest_code }/testend')
            
            # rem_time = int(min(contest.time*60 - (cur_time-start_time).total_seconds(), (contest.end_date - cur_time).total_seconds()))
            
            # if rem_time < 1 or rem_time>contest.time*60:
            #     reg.test_status = 2
            #     reg.save()
            #     return redirect(f'/codespace/{ contest_code }/testend')
                
            
            inp = i_o_extract(obj.testcases.url)
            out = i_o_extract(obj.outputs.url)
            
            if not reg.que_start_time:
                reg.que_start_time = timezone.now()
                reg.save()
            
            args = {
                "que_type": obj.que_type,
                "username":req.session["username"],
                "contest_code": contest_code,
                "remainingTime": obj.duration*60 - reg.que_time_rem().total_seconds(),
                # "test_time": rem_time,
                "que_no": reg.last_que_no + 1 ,
                "que": obj.que_desc,
                "duration": obj.duration*60,
                "total_que": len(que_list),
                "code": prev_code,
                "img_url": img_url,
                "inputs": inp[0],
                "outputs": out[0],
                "results" : '\n',
                "obj": que_obj,
                "total_score":sum([i['score'] for i in que_obj]),
                "que_status": que_status,
            }    
            
            return render(req, 'passing_code.html', args)
        
    
        else:
            return redirect('/codespace')
            
    else:
        return redirect('/codespace/user_login')
    return render(req, 'passing_code.html')


def change_que(req, contest_code):
    
    loc = settings.MEDIA_ROOT
    args = {}
    if req.method == 'POST':
        user_id=Users.objects.filter(username=req.session['username'])[0]
    
        # que_list = eval(req.session["que_list"])
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest = contest[0]
        else:
            contest = None
            
        reg = Registrations.objects.filter(user_id=user_id, contest_id=contest)
        if reg:
            reg = reg[0]
        else:
            reg = None
        
        prev_que = Questions.objects.filter(id=int(req.POST['prev_que_id']))[0]
        
        if prev_que.que_type != 1:
            Submissions(
                question_id = prev_que,
                contest_id = contest,
                user_id = user_id,
                code = req.POST['code'],
                language = req.POST["prev_lang"],
                score = 0,
                status = ' ').save()
        else:
            sub = Submissions.objects.filter(user_id=user_id, question_id=prev_que, contest_id = contest)
            if sub and prev_que.que_type == 1:
                # score = 0
                # if 'selected_op' in req.POST and req.POST['selected_op'] == prev_que.correct_op:
                #     score = prev_que.score
                sub[0].code = '' if 'selected_op' not in req.POST else req.POST['selected_op']
                sub[0].score = prev_que.score if 'selected_op' in req.POST and req.POST['selected_op'] == str(prev_que.correct_op) else 0
                sub[0].save()
            else:
                score = 0
                if 'selected_op' in req.POST and req.POST['selected_op'] == str(prev_que.correct_op):
                    score = prev_que.score
                Submissions(
                    question_id = prev_que,
                    contest_id = contest,
                    user_id = user_id,
                    code = '' if 'selected_op' not in req.POST else req.POST['selected_op'],
                    score = score,
                    ).save()
        
        obj = Questions.objects.filter(id=int(req.POST['que_id']))[0]
        
        img_url = obj.image
        if img_url:
            img_url = '/codespace/' + img_url.url
        else:
            img_url = ''
        
        prev_code = ''
        # debug_code = ""
        debug_lang = ""
        if obj.que_type == 2:
            prev_code = obj.debug_code
            debug_lang = obj.debug_language
        # sub = Submissions.objects.raw("select * from app_submissions where contest_id_id=" + str(contest.id) + " and user_id_id='" + req.session["username"] + f"' and question_id_id={que_list[0]} order by id")
        sub = Submissions.objects.filter(contest_id=contest, user_id=user_id, question_id=obj, language = req.POST["lang"]).order_by('-id')
        status = 'Unsolved'
        if(sub):
            prev_code = sub[0].code
            status = 'Solved' if sub.filter(status='A') else 'Unsolved'
        
        if contest and contest.contest_type == 1 and reg:
            reg.last_que_no = reg.last_que_no+1
            reg.que_start_time = timezone.now()
            reg.save()
        
        if obj.que_type == 1:
            args = {
                "que_type": obj.que_type,
                "que_desc" : obj.que_desc,
                'img_url' : img_url,
                # "remainingTime": reg.que_time_rem,
                'options' : obj.options.split("@dlim@"),
                'selected_op': prev_code,
                "que" : '',
                'code' : '',
                "inputs": '',
                "outputs": '',
                "results" : '\n',
                "status" : '',
                "tc_count" : '',
                'alert': '',
                }
            return JsonResponse(args, status = 200)
        
        inp = i_o_extract(obj.testcases.url)
        out = i_o_extract(obj.outputs.url)
        
        remainingTime = 0
        if contest and contest.contest_type == 1:
            remainingTime = (obj.duration * 60) - reg.que_time_rem().total_seconds() if obj.duration and reg and contest and contest.contest_type == 1 else (obj.duration*60) if obj.duration and contest else 0
        
            
        args = {
            
            "que_type": obj.que_type,
            "que" : obj.que_desc,
            "duration": (obj.duration * 60) if obj.duration and contest and contest.contest_type==1 else 0,
            # 'img_url' : img_url,
            "remainingTime": remainingTime,
            'code' : prev_code,
            "inputs": inp[0],
            "outputs": out[0],
            "results" : '\n',
            "status" : status,
            "tc_count" : obj.tc_count,
            'img_url' : img_url,
            "debug_lang": debug_lang,
            'alert': '',
                }
    # print(obj.filter(que_no=int(req.session["quesno"]))[0].que_img)            
    return JsonResponse(args, status = 200)


def submit_que(req, contest_code):
    
    loc = settings.MEDIA_ROOT
    file_ext = {'c':'.c', 'cpp':'.cpp', 'java':'.java', 'python':'.py'}
    args = {}
    
    if req.method == 'POST':
        # que_list = eval(req.session["que_list"])
        # que_id = que_list[int(req.POST['que_no'])-1]
        que_id = int(req.POST['que_id'])
        
        contest = Contests.objects.filter(contest_code=contest_code)
        if contest:
            contest = contest[0]
        else:
            contest = None
        
        # obj = Questions.objects.filter(id=que_id)[0]
        obj = Questions.objects.get(id=que_id)
        code = req.POST['code']
        print(code)
        # a = 1/0
        inp = i_o_extract(obj.testcases.url)
        out = i_o_extract(obj.outputs.url)
        lang = req.POST['lang']
        
        # print(inp, out)
        
        with open(loc + "/submissions/"+ req.session["username"] + "/" + req.session["username"]+file_ext[lang], 'w') as file:
            file.write(code)
        
        output=''
        score = 0
        if req.POST['sub_type']=='submit':
            status, score, results = run_testcases(req.session["username"], req.POST["lang"], inp, out, obj.tc_count, obj.score, obj.tle)
            # if status=='A':
                # req.session['que_status'][int(req.POST['que_no'])-1]["status"] = 'A'
                
            #CODE WARS
            if status=='A' and contest and contest.contest_type == 2:
                user = Users.objects.filter(username=req.session['username'])[0]
                user_ = CodeDuel.objects.filter(user_id=user, contest_id=contest)[0]
                opponent = Users.objects.filter(username=user_.opponent)[0]
                opponent_ = CodeDuel.objects.filter(user_id=opponent, contest_id=contest)[0]
                if opponent_.user_level>user_.user_level:
                    #redirect to opponent winning page
                    user_.online = 0
                    user_.in_duel = 0
                    user_.save()
                    redirect(f'/codespace/{contest_code}/testend')
                else:
                    user_.user_level = user_.user_level + 1
                    opponent_.online = 0
                    opponent_.in_duel = 0
                    opponent_.save()
                    user_.save()
                
            #PASSING CODE
            # if status=='A' and contest and contest.contest_type == 1:
            #     reg.last_que_no = reg.last_que_no+1
            #     reg.que_start_time = timezone.now()
            #     reg.save()
            
            args = {
                "status": status,
                "results": results,
                "score": score,
                "total_score":obj.score,
                "tc_count": obj.tc_count-1,
            }
        else:
            if 'custom_input' in req.POST:
                status, results = run(req.session["username"], req.POST["lang"], req.POST['custom_input'], obj.tle)
                inputs = req.POST['custom_input']
                outputs = '---'
            else:
                status, results = run(req.session["username"], req.POST["lang"], inp[0], obj.tle)
                inputs = inp[0]
                outputs = out[0]
                
            args = {
                "status": status, 
                "score": score,
                "inputs":inputs,
                "outputs": outputs,
                "results": '\n'.join(results),
                "tc_count": obj.tc_count-1,
                "alerts":inp[0],
            }
            
        Submissions(
            question_id = obj,
            contest_id = contest,
            user_id = Users.objects.get(username=req.session['username']),
            code = code,
            language = req.POST["lang"],
            score = score,
            status = status
            ).save()
            
        # args["que_status"] = req.session["que_status"]
                
    return JsonResponse(args, status = 200)


def code_wars_arena(req, contest_code):
    if 'username' in req.session:
        user = Users.objects.filter(username=req.session['username'])[0]
        contest = Contests.objects.filter(contest_code=contest_code)[0]
        user_ = CodeDuel.objects.filter(user_id=user, contest_id=contest)
        if not user_:
            user_ = CodeDuel(
                    user_id = user,
                    contest_id = contest,
                    online = 1,
                    )
            user_.save()
        else:
            user_ = user_[0]
            
        profile_pic = ""    
        if user.profile_pic:
            profile_pic = user.profile_pic.url
        args = {
            'username': req.session['username'],
            "contest_code": contest_code,
            'profileUrl': profile_pic,
            'status': 1 if user_.opponent else 0
        }
        
        return render(req, 'codewars_home.html', args)
        
    else:
        return redirect('/codespace/user_login')


def code_wars(req, contest_code):
    args = {}
    
    # req.session["contest_code"] = contest_code
    if 'username' in req.session:
        contest = Contests.objects.filter(contest_code=contest_code, status='ongoing')
        
        if contest:
            contest = contest[0]
            
            user = Users.objects.filter(username=req.session['username'])[0]
            user_ = CodeDuel.objects.filter(user_id=user, contest_id=contest)[0]
            
            profile_pic = ""    
            if user.profile_pic:
                profile_pic = user.profile_pic.url
            
            if not user_.opponent:
                # return redirect(f'/codespace/{contest_code}/code_wars/')
                args = {
                    "username":req.session["username"],
                    "contest_code": contest_code,
                    'profileUrl': profile_pic,
                }
                return render(req, 'codewars_contest.html', args)
                
            opponent = Users.objects.filter(username=user_.opponent)[0]
            opponent_ = CodeDuel.objects.filter(user_id=opponent, contest_id=contest)[0]
            
            if user_.user_level != opponent_.user_level:
                args = {
                    "username":req.session["username"],
                    "contest_code": contest_code,
                    'profileUrl': profile_pic,
                }
                return render(req, 'codewars_contest.html', args)
            
            profile_pic = ""    
            if user.profile_pic:
                profile_pic = user.profile_pic.url
                
            if contest.contest_pwd:
                args = {
                    'username': user.username,
                    'profileUrl': profile_pic,
                    'contest_code': contest_code,
                    'alert': '',
                }
                if 'contest_pwd' in req.POST:
                    if req.POST['contest_pwd'] != contest.contest_pwd:
                        args['alert'] = 'Enter Valid Contest Password'
                        return render(req, 'contest_pwd_validate.html', args)
                else:
                    return render(req, 'contest_pwd_validate.html', args)
                
            reg = Registrations.objects.filter(user_id=user, contest_id=contest)
            
            if not reg:
                return redirect(f'/codespace/contests')
                
            reg = reg[0]
            
            if reg.test_status == 2:
                return redirect(f'/codespace/{ contest_code }/testend')
            
            if reg.test_status == 0:
                reg.test_status = 1
                reg.started_time = timezone.now()
                reg.save()
            
            # contest_list = [i.id for i in Contests.objects.filter(status__in=['past', 'practice'])]
            que_list = [i.question_id.id for i in Contest_question.objects.filter(contest_id=contest.id)]
            # que_obj = Questions.objects.filter(id__in=que_list)
            
            sub_subquery = Submissions.objects.filter(
                    user_id=user.id,
                    question_id=OuterRef('id'),
                    status='A'
                )
            
            que_obj = Questions.objects.filter(id__in=que_list).values('id', 'title', 'level', 'score', 'image').annotate(
                status=Subquery(sub_subquery.values('status')[:1]),
                )
            
            obj = Questions.objects.filter(id=que_obj[0]['id'])[0]
            
            sub = Submissions.objects.filter(user_id=user, question_id=obj).order_by('-id')
            que_status = ''
            prev_code = ''
            # debug_code = ""
            debug_lang = ""
            if obj.que_type == 2:
                prev_code = obj.debug_code
                debug_lang = obj.debug_language
            if sub:
                prev_code = sub[0].code
                
                que_status = sub.order_by('-score')[0].status
            que_status = "Solved" if que_status=='A' else "Unsolved"
            
            img_url = obj.image
            if img_url:
                img_url = '/codespace/' + img_url.url
            else:
                img_url = ''
                
            # try:
            #     os.mkdir("./media/submissions/"+ req.session["username"])
            # except:
            #     pass
            
            # user = Registerations()
            
            # rem_time = 3600
            # cur_time = timezone.now()
            # start_time = reg.started_time
            
            # if cur_time>contest.end_date:
            #     return redirect(f'/codespace/{ contest_code }/testend')
            
            # rem_time = int(min(contest.time*60 - (cur_time-start_time).total_seconds(), (contest.end_date - cur_time).total_seconds()))
            
            # if rem_time < 1 or rem_time>contest.time*60:
            #     reg.test_status = 2
            #     reg.save()
            #     return redirect(f'/codespace/{ contest_code }/testend')
                
            
            inp = i_o_extract(obj.testcases.url)
            out = i_o_extract(obj.outputs.url)
            
            opponent_profile_pic = ""    
            if opponent.profile_pic:
                opponent_profile_pic = opponent.profile_pic.url
            
            args = {
                "que_type": obj.que_type,
                "username":req.session["username"],
                "contest_code": contest_code,
                # "test_time": rem_time,
                "que_no": '1',
                "que": obj.que_desc,
                "duration": obj.duration,
                "total_que": len(que_list),
                "code": prev_code,
                "img_url": img_url,
                "inputs": inp[0],
                "outputs": out[0],
                "results" : '\n',
                "obj": que_obj,
                "total_score":sum([i['score'] for i in que_obj]),
                "que_status": que_status,
                "opponentName":user_.opponent,
                "opponentProfileUrl":opponent_profile_pic,
                "profileUrl":profile_pic,
            }    
            
            return render(req, 'code_wars.html', args)
        
    
        else:
            return redirect('/codespace')
            
    else:
        return redirect('/codespace/user_login')
        
    return render(req, 'code_wars.html')


def set_all_opponents(req, contest_type, contest_code):
    contest = Contests.objects.filter(contest_code=contest_code)[0]
    participants = list(CodeDuel.objects.filter(contest_id=contest, online=1))
    random.shuffle(participants)
    for i in range(0, len(participants), 2):
        participants[i].opponent, participants[i+1].opponent = participants[i+1].user_id.username, participants[i].user_id.username
        participants[i].save()
        participants[i+1].save()
    
    return redirect(f'/codespace/admin_contests/{contest_type}/{contest_code}/')
        

def set_opponent(req, contest_code):
    args = {'opponent':''}
    
    if req.method == 'POST':
        contest = Contests.objects.filter(contest_code=contest_code)[0]
        user = Users.objects.filter(username=req.session['username'])[0]
        user_ = CodeDuel.objects.filter(user_id = user)[0]
        # opponents.remove(user_)
        if user_.in_duel == 1:
            # opponent = Users.objects.filter(username=user_.opponent)[0]
            # opponent_ = CodeDuel.objects.filter(user_id=opponent, contest_id=contest)[0]
            return JsonResponse({"status":1}, status = 200)
        else:
            opponents = CodeDuel.objects.filter(online=1, in_duel=0, user_level=user_.user_level, contest_id=contest).exclude(user_id=user)
            # opponents = list(CodeDuel.objects.filter(online=1, in_duel=0, user_level=user_.user_level, contest_id=contest))
            if opponents:
                opponent = random.choice(opponents)
                user_.in_duel = 1
                opponent.in_duel = 1
                
                user_.opponent = opponent.user_id.username
                opponent.opponent = req.session['username']
                
                user_.save()
                opponent.save()
                
                return JsonResponse({"status":1}, status = 200)
        
    return JsonResponse({"status":0}, status = 200)


def check_battle_winner(req, contest_code):
    if req.method == "POST":
        contest = Contests.objects.filter(contest_code=contest_code)[0]
        user = Users.objects.filter(username=req.session['username'])[0]
        user_ = CodeDuel.objects.filter(user_id = user)[0]
        opponent = Users.objects.filter(username=user_.opponent)[0]
        opponent_ = CodeDuel.objects.filter(user_id=opponent)[0]
        if opponent_.user_level>user_.user_level:
            #redirect to opponent winning page
            user_.online = 0
            user_.in_duel = 0
            opponent_.in_duel = 0
            opponent_.save()
            user_.save()
            # redirect(f'/codespace/{contest_code}/testend')
            return JsonResponse({"status":0}, status = 200)
        elif opponent_.user_level<user_.user_level:
            opponent_.online = 0
            opponent_.in_duel = 0
            user_.in_duel = 0
            opponent_.save()
            user_.save()
            return JsonResponse({"status":1}, status = 200)
        else:
            return JsonResponse({"status":2}, status = 200)
    
    return JsonResponse({"status":1}, status = 200)
            


def i_o_extract(loc):
    file = open(str(settings.BASE_DIR) + loc, 'r')
    data = file.read()
    
    data = [tc.rstrip() for tc in data.split("@dlim@\n")]
    file.close()
    return data


def compile(inpt, lang, username, tle):
    loc=settings.MEDIA_ROOT
    try:
        if lang == 'c':
            p = subprocess.run(["gcc", "./media/submissions/"+ username + "/" + username+".c", "-o", "./media/submissions/"+ username + "/" + username], stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE, text=True)
            if p.stderr:
                return False, p.stderr
            p = subprocess.run("./media/submissions/"+ username + "/" + './'+username, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, input=inpt, timeout=tle)

        elif lang == 'cpp':
            p = subprocess.run(["g++", "./media/submissions/"+ username + "/" + username+".cpp", "-o", "./media/submissions/"+ username + "/" + username], stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE, text=True)
            # p.stdout, p.stderr = p.communicate()
            if p.stderr:
                return False, p.stderr
            p = subprocess.run("./media/submissions/"+ username + "/" + './'+username, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, input=inpt, timeout=tle)

        elif lang == 'java':
            p = subprocess.Popen(["./media/compilers/java2/bin/javac", "./media/submissions/"+ username + "/" + username+".java"], stderr=subprocess.PIPE, shell=False,
                                 stdout=subprocess.PIPE, text=True)
            p.stdout, p.stderr = p.communicate()
            if p.stderr:
                return False, p.stderr
            p = subprocess.run(["./media/compilers/java2/bin/java", '-cp', "./media/submissions/"+ username + "/", "Solution"], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, input=inpt, timeout=tle)

        else:
            p = subprocess.run(["/opt/alt/python37/bin/python3", loc + "/submissions/"+ username + "/" + username+".py"], text=True, input=inpt, timeout=tle, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    except subprocess.TimeoutExpired:
        return True, "TLE"
        
    if p.stderr:
        return False, p.stderr
        
    return True, p.stdout


def check_output(outget, actout):
    outget = outget.rstrip().split('\n')
    actout = actout.split('\n')
    ln1 = len(outget)
    ln2 = len(actout)
    
    if ln1==ln2:
        for i in range(len(outget)):
            if(outget[i].rstrip() != actout[i].rstrip()):
                return False
        return True
    else:
        return False


def run(username, lang, inputs, tle):
    success, out = compile(inputs, lang, username, tle)
    if not success:
        return "", out.split('\n') # RUNTIME ERROR
    elif out=="TLE":
        return "", ["TLE"]         # TLE
    else:
        return "", out.split('\n') # RESULT


def run_testcases(username, lang, inputs, outputs, tc_count, total_score, tle):
    l = []
    score = 0
    
    for i in range(1, tc_count):
        success, out = compile(inputs[i], lang, username, tle)
        if not success:
            return 'RE', 0, ['E']*(tc_count-1) # RUNTIME ERROR
        elif out=="TLE":
            l.append('T')
        elif check_output(out, outputs[i]):
            l.append('C')
            score += (total_score // (tc_count-1))
        else:
            l.append('W')
    
    if(score == 0):
        status = "W" # WRONG ANSWER
    elif(score < total_score):
        status = "PA" # PARTIALLY ACCEPTED
    else:
        status = "A"  # ACCEPTED
        
    return status, score, l


def custom_input(username, lang, inputs, tle):
    success, out = compile(inputs, lang, username, tle)
    if not success:
        return "E", out.split('\n')
    elif out=="TLE":
        return "T", ["TLE"]
    elif check_output(out, outputs):
        return "S", out.split('\n')
        

def add_mcq(req, contest_type, contest_code):
    if req.user.is_authenticated:
        if req.method == "POST":
            # return render(req, 'add_mcq_que.html')
            que_img = ''
            if 'que_img' in req.FILES:
                que_img = req.FILES['que_img']
                
            que = Questions(
                que_type = 1,
                que_desc=req.POST['que_desc'],
                image=que_img,
                score=req.POST['score'],
                duration=req.POST['duration'],
                correct_op=req.POST['selected_op'],
                options = req.POST['options'],
                )
            
            que.save()
                
            Contest_question(
                question_id=que,
                contest_id=Contests.objects.get(contest_code=req.POST['contest_code'])
                ).save()
            
            return redirect(f"/codespace/admin_contests/{ contest_type }/{ contest_code }/questions/")
            
        return render(req, 'add_mcq_que.html')
        
    else:
        return redirect('/codespace/admin_login')


def mcq(req, contest_code):
    
    return render(req, 'mcq.html')
    

@csrf_exempt
@require_http_methods(["POST"])
def abhi_compile(request):
    if (request.method == "POST"):
        code = request.POST.get('code')
        user_input = request.POST.get("user_input")
        time_limit = int(request.POST.get("time_limit"))
        language = request.POST.get("language")
        user = request.POST.get("user")
        a = {"python": "pyprogram.py",
             "java": "temp.java",
             "c++": "temp.cpp",
             "c": "temp.c"}
        user_input = json.loads(user_input)
        base_path = f"./media/testapp/temparary/{str(user)}"
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        file_path = base_path + "/" + a[language]
        with open(file_path, "w") as f:
            f.write(code)
        output = []
        time1 = []
        type = []
        for i in user_input:
            start_time = time.time()
            try:
                if (language == "python"):
                    p = subprocess.run(["/opt/alt/python37/bin/python3", file_path], text=True, input=i,
                                       timeout=time_limit, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                elif (language == "c"):
                    p = subprocess.run(["gcc", file_path, "-o",
                                        base_path + "/cprogram"], text=True, stderr=subprocess.PIPE, timeout=1)
                    if p.returncode != 0:
                        output.append(p.stderr)
                        type.append("compilation_error")
                        time1.append(0)
                        break

                    p = subprocess.run([f"{base_path}/cprogram"], text=True, input=i,
                                       timeout=time_limit, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                elif (language == 'c++'):
                    p = subprocess.run(["g++", file_path, "-o",
                                        base_path + "/cppprogram"], text=True, stderr=subprocess.PIPE, timeout=1)
                    if p.returncode != 0:
                        output.append(p.stderr)
                        type.append("compilation_error")
                        time1.append(0)
                        break

                    p = subprocess.run([f"{base_path}/cppprogram"], text=True, input=i,
                                       timeout=time_limit, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                else:
                    p = subprocess.run(
                        ['./media/compilers/java/bin/javac', file_path, "-d", base_path], text=True, stderr=subprocess.PIPE, timeout=2)

                    if p.returncode != 0:
                        output.append(p.stderr)
                        type.append("compilation_error")
                        time1.append(0)
                        break

                    p = subprocess.run(['./media/compilers/java/bin/java', "-cp", base_path, 'temp'], text=True, input=i,
                                       timeout=time_limit, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

                end_time = time.time()
            except subprocess.TimeoutExpired:
                end_time = time.time()
                output.append(",Time limit exceeded")
                type.append("time_limit_exeed")
                time1.append(str(round(end_time-start_time, 5)))
                break
            if p.stderr:
                output.append(p.stderr)
                type.append("error")
                time1.append(0)
                break
            output.append(p.stdout.rstrip())
            type.append("successfully executed")
            time1.append(str(round(end_time-start_time, 5)))
        return JsonResponse({"output": output, "type": type, "time": time1})

# sse server-side event implementation
# def sse_stream(request):
#     # Set the content type to text/event-stream
#     response = StreamingHttpResponse(streaming_content=sse_generator(), content_type='text/event-stream')
#     return response

# def sse_generator():
#     while True:
#         # You can replace this with your dynamic data
#         data = "data: {}\n\n".format("Your dynamic data here")

#         # Yield the data to be sent to the client
#         yield data
        
#         # Optional: Add a delay to control the frequency of updates
#         time.sleep(1)