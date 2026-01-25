from django.contrib import admin
from .models import (
    UserInfo, Job, Application, CustomUser, Skill,
    Course, Experience, SavedJobs
)

# 🔹 CustomUser Admin (Optional customization)
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_active']
    search_fields = ['username', 'email']
    list_filter = ['is_active', 'is_staff']

# 🔹 UserInfo Admin
@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'currentLocation']
    search_fields = ['user__username', 'currentLocation']

# 🔹 Application Admin
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'status', 'appliedDate']
    list_filter = ['status', 'job__companyName']
    search_fields = ['user__username', 'job__role']

# 🔹 Skill Admin
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# 🔹 Job Admin
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['role', 'companyName', 'location', 'datePosted']
    search_fields = ['role', 'companyName']
    list_filter = ['location', 'companyName']
    filter_horizontal = ['skills']

# 🔹 Course (Education) Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['user', 'course_name', 'college', 'passout_year', 'cgpa']
    list_filter = ['passout_year']
    search_fields = ['course_name', 'college', 'user__username']

# 🔹 Experience Admin
@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'company_name', 'currently_working']
    list_filter = ['currently_working', 'company_name']
    search_fields = ['role', 'company_name', 'user__username']

@admin.register(SavedJobs)
class SavedJobsAdmin(admin.ModelAdmin):
    list_display = ['user']
