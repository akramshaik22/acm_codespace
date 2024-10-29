from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    
    path('',views.home, name='home'),
    #USER LOGIN
    path('user_registration', views.user_reg, name='user_reg'),
    path('user_login', views.userlogin, name='user login'),
    path('validate', views.check_username, name='user_reg'),
    path('user_logout', views.userlogout, name='user logout'),
    path('test_mail', views.test_mail, name='test mail'),
    #RESET PASSWORD
    path('reset_password', views.reset_password, name='reset_password'),
    path('reset_password/send_otp', views.send_otp, name='reset_password'),
    path('reset_password/verify_otp', views.verify_otp, name='reset_password'),
    #PROFILE
    path('profile/<username>/', views.user_profile, name='user_profile'),
    #CONTESTS
    path('contests', views.contests, name='contests'),
    path('contests/<contest_code>/', views.contest_info, name='contest_register'),
    path('<contest_code>/register/', views.register_contest, name='contest_register'),
    path('<contest_code>/codespace/', views.codespace, name='codespace'),
    path('<contest_code>/change_que', views.change_que, name='change_que'),
    path('<contest_code>/submit_que', views.submit_que, name='submit_que'),
    path('<contest_code>/testend', views.testend, name='End Test'),
    #PASSING CODE
    path('<contest_code>/passing_code/', views.passing_code, name='passing_code'),
    #CODE WARS
    path('<contest_code>/code_wars/', views.code_wars_arena, name='code_wars_arena'),
    path('<contest_code>/code_wars/set_opponent/', views.set_opponent, name='set_opponent'),
    path('<contest_code>/code_wars/check_battle_winner/', views.check_battle_winner, name='check_battle_winner'),
    path('<contest_code>/code_wars/code_duel/', views.code_wars, name='code_duel'),
    path('admin_contests/<contest_type>/<contest_code>/set_opponents/', views.set_all_opponents, name='set_all_opponents'),
    #MCQ
    path('<contest_code>/mcq/', views.mcq, name='mcq contest'),
    #PRACTICE
    path('practice/', views.practice, name='practice'),
    path('practice/<que_id>/', views.practice_codespace, name='practice_codespace'),
    #ADMIN
    path('admin_login', views.admin_login, name='admin login'),
    path('admin_logout', views.admin_logout, name='admin logout'),
    path('admin_contests/custom_email/', views.custom_mail, name='custom_mail'),
    path('admin_contests/send_custom_mails/', views.send_custom_mails, name='admin_contests'),
    path('admin_contests/<contest_type>/', views.admin_contests, name='admin_contests'),
    path('admin_contests/<contest_type>/<contest_code>/', views.contest_details, name='contest_details'),
    path('admin_contests/<contest_type>/<contest_code>/edit_contest', views.edit_contest, name='contest_details'),
    path('admin_contests/<contest_type>/<contest_code>/publish/', views.publish_contest, name='contest_questions'),
    path('admin_contests/<contest_type>/<contest_code>/start_contest/', views.start_contest, name='contest_questions'),
    path('admin_contests/<contest_type>/<contest_code>/end_contest/', views.end_contest, name='contest_questions'),
    path('admin_contests/<contest_type>/<contest_code>/questions/', views.contest_questions, name='contest_questions'),
    path('admin_contests/<contest_type>/<contest_code>/questions/add_que', views.add_que, name='add_que'),
    path('admin_contests/<contest_type>/<contest_code>/questions/edit_que', views.edit_que, name='edit_que'),
    path('get_que_data/', views.get_que_data, name='get_que_data'),
    path('admin_contests/<contest_type>/<contest_code>/registrations/', views.registrations, name='Registrations'),
    path('admin_contests/<contest_type>/<contest_code>/submissions/', views.submissions, name='Submissions'),
    path('admin_contests/<contest_type>/<contest_code>/dashboard/', views.dashboard, name='dashboard'),
    path('admin_contests/<contest_type>/<contest_code>/promoted/', views.event_promoted_status, name='promoted_contest'),
    path('admin_contests/<contest_type>/<contest_code>/promote_to_contest/', views.promote_to_contest, name='promoted_contest'),
    
    path('admin_contests/<contest_type>/<contest_code>/questions/add_mcq', views.add_mcq, name='add_mcq'),
    # path('admin_contests/add_contest/', views.add_contest, name='add_contest'),
    # path('admin_contests/<url_type>/<contest_code>/add_que', views.add_que, name='add_que'),
    
    # sse path
    # path('sse/', views.sse_stream, name = 'sse stream'),
    
    
]


#ABHISHEK API
urlpatterns += [path('acmw_submit_que', views.abhi_compile, name='abhi compiler')]

