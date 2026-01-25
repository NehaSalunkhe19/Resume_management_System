from django.conf import settings
from django.urls import path
# from setuptools.extern import names

from .views import *
from django.contrib.auth.views import LoginView,LogoutView
from django.urls import reverse_lazy

 
urlpatterns = [
    path('',base,name='base'),
    path('registration/',registration,name='registration'),
    # path('loginPage/',loginPage,name='loginPage'),
    path('userprofile/',userprofile,name='userprofile'),
    path('jobs/', jobs, name='jobs'),
    path('login/',custom_login,name='customlogin'),
    path('logout/', Logout, name='logout'),
    path('applicationForm/',applicationFrom,name='applicationForm'),
    path('apply/<int:job_id>/',submit_application, name='submit_application'),
    path('savedJobs/<int:job_id>',savedJobs,name='savedJobs'),
    path('savej',savej,name='savej'),

    path('saveJobList/',saveJobList,name='saveJobList'),
    path('remove_saved_job/<int:job_id>',remove_saved_job,name='remove_saved_job'),
    path('application_status/',application_status,name='application_status'),
    path('recommended_jobs/',recommended_jobs,name='recommended_jobs'),
    # path('profile_completion_view/',profile_completion_view,name='profile_completion_view'),
    path("profile/", profile_completion_view, name="profile"),

]

