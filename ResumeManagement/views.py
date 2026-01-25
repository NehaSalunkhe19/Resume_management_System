from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache

from django.core.mail import send_mail
from .models import *


# Create your views here.
def base(request):
    return render(request,'base.html')

def registration(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password1']
        conpassword=request.POST['password2']
        if CustomUser.objects.filter(username=username).exists():
            return render(request,'registration.html',{'error':'Username is already present'})

        if CustomUser.objects.filter(email=email).exists():
            return render(request,'registration.html',{'error':'Email is already present'})
        if password!=conpassword:
            return render(request,'registration.html',{'error':'Password does not match with confirm password'})


        user=CustomUser.objects.create_user(username=username,email=email,password=password)

        user.save()
        subject = 'Welcome to Resume Management System'
        message = f'Hi {username},\n\nThank you for registering with us!'
        recipient_list = [email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        print("Redirecting to login...")

        return redirect('customlogin')





    return render(request,'registration.html')
def loginPage(request):
    return render(request,'loginPage.html')

def home(request):
    pass








def custom_login(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return render(request, 'loginPage.html', {'error': 'Username not found'})

        if user.email != email:
            return render(request, 'loginPage.html', {'error': 'Username and email do not match'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('userprofile')
        else:
            return render(request, 'loginPage.html', {'error': 'Invalid password'})

    return render(request, 'loginPage.html')




def jobs(request):
    allJob = Job.objects.all()

    userinfo = None
    applied_jobs = []  # Default empty

    if request.user.is_authenticated:
        try:
            userinfo = UserInfo.objects.get(user=request.user)
        except UserInfo.DoesNotExist:
            pass

        # ✅ Get job IDs that the user has already applied for
        applied_jobs = Application.objects.filter(user=request.user).values_list('job_id', flat=True)

    return render(request, 'jobs.html', {
        'jobs': allJob,
        'userinfo': userinfo,
        'applied_jobs': applied_jobs,
    })


@login_required(login_url='customlogin')
def userprofile(request):
    try:
        userinfo = UserInfo.objects.get(user=request.user)
        print(userinfo)
    except UserInfo.DoesNotExist:
        userinfo = None  # or handle as needed, but assuming record exists

    courses = Course.objects.filter(user=request.user)
    experiences = Experience.objects.filter(user=request.user)
    skills=Skill.objects.all()
    userSkill=Skill.objects.filter(userinfo__user=request.user)
    print(userSkill)
    if request.method == 'POST':
        # 1️⃣ Update profile image

        profile_image = request.FILES.get('profile_image')
        old_profile=profile_image
        if profile_image and userinfo:
            if userinfo.profile_image:
                userinfo.profile_image.delete(save=False)  # Deletes file from storage

                # Save the new one
            userinfo.profile_image = profile_image
            userinfo.save()


            # print( request.user.profile_image)

        # 2️⃣ Update resume
        resume = request.FILES.get('resume')
        if resume and userinfo:
            userinfo.resume = resume
            userinfo.save()




        # 3️⃣ Update basic info
        mobile = request.POST.get('mobile', '')
        address = request.POST.get('address', '')

        request.user.mobile = mobile
        request.user.save()

        if userinfo:
            userinfo.currentLocation = address
            userinfo.save()


        # 4️⃣ Update education
        total_courses = int(request.POST.get("total_courses", 0))
        for i in range(1, total_courses + 1):
            course_id = request.POST.get(f"course_id_{i}")
            try:
                course = Course.objects.get(id=course_id, user=request.user)
                course.course_name = request.POST.get(f"course_name_{i}", "")
                course.college = request.POST.get(f"college_{i}", "")
                course.passout_year = request.POST.get(f"passout_year_{i}") or None
                course.cgpa = request.POST.get(f"cgpa_{i}") or None
                course.save()
            except Course.DoesNotExist:
                continue

        # ➕ Add new course
        new_course_name = request.POST.get("new_course_name")
        new_college = request.POST.get("new_college")
        new_passout_year = request.POST.get("new_passout_year")
        new_cgpa = request.POST.get("new_cgpa")

        if new_course_name and new_college:
            Course.objects.create(
                user=request.user,
                course_name=new_course_name,
                college=new_college,
                passout_year=new_passout_year or None,
                cgpa=new_cgpa or None
            )

        # 5️⃣ Update experience
        total_exps = int(request.POST.get("total_experiences", 0))
        for i in range(1, total_exps + 1):
            exp_id = request.POST.get(f"exp_id_{i}")
            try:
                exp = Experience.objects.get(id=exp_id, user=request.user)
                exp.role = request.POST.get(f"role_{i}", "")
                exp.company_name = request.POST.get(f"company_name_{i}", "")
                exp.currently_working = f"currently_working_{i}" in request.POST
                exp.save()
            except Experience.DoesNotExist:
                continue

        # ➕ Add new experience
        new_role = request.POST.get("new_role")
        new_company = request.POST.get("new_company_name")
        new_current = "new_currently_working" in request.POST

        saved_skills=request.POST.getlist('saved_skills')
        new_skills=request.POST.getlist('skills')
        final_skills=list(set(saved_skills+new_skills))

        print(final_skills)
        userinfo.skills.set(final_skills)
        if new_role and new_company:
            Experience.objects.create(
                user=request.user,
                role=new_role,
                company_name=new_company,
                currently_working=new_current
            )





        messages.success(request, f"Hey {userinfo},Your profile updated successfully!")
        return redirect('userprofile')  # replace with your actual profile URL name

    return render(request, 'userprofile.html', {
        'userinfo': userinfo,
        'courses': courses,
        'experiences': experiences,
        'skills':skills,
        'userSkills':userSkill
    })


def Logout(request):
    logout(request)
    return redirect('jobs')

@login_required(login_url='customlogin')
@never_cache
def applicationFrom(request):
    return render(request,'applicationform.html')



@login_required
@login_required
def submit_application(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # ✅ Prevent multiple applications
    existing_application = Application.objects.filter(user=request.user, job=job).first()
    if existing_application:
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs')

    if request.method == 'POST':
        location = request.POST.get('location')
        resume = request.FILES.get('new_resume') if 'new_resume' in request.FILES else request.user.userinfo.resume

        Application.objects.create(
            user=request.user,
            job=job,
            resume=resume,
            location=location,
        )

        # Update resume in user profile if new one uploaded
        if 'new_resume' in request.FILES:
            userinfo = request.user.userinfo
            userinfo.resume = request.FILES['new_resume']
            userinfo.save()

        messages.success(request, 'Application submitted successfully!')
        return redirect('jobs')

def savedJobs(request,job_id):
    if request.user.is_authenticated:
        job=get_object_or_404(Job,id=job_id)
        user=request.user
        # Prevent duplicate saved jobs
        saved,created=SavedJobs.objects.get_or_create(user=user,job=job)

        if created:
            messages.success(request,"Job saved successfully")
        else:
            messages.warning(request,"Job is already present")


    return redirect('jobs')
def savej(request):
    return render(request,'savedJobs.html')

def saveJobList(request):
    if request.user.is_authenticated:
        user=request.user

        saved_jobs=SavedJobs.objects.all()
        m=SavedJobs.objects.filter(user=user)
        return render(request,'saveJobList.html',{'saved_jobs':m})
    return render(request,'saveJobList.html ')

def remove_saved_job(request,job_id):
    if request.user.is_authenticated:
        remove_job=get_object_or_404(SavedJobs,user=request.user, id=job_id)

        remove_job.delete()
        return redirect('saveJobList')

def application_status(request):
    if request.user.is_authenticated:
        allJob=Application.objects.all()
        user=request.user
        print(user)
        jobOfUser=Application.objects.filter(user=user)
        print(jobOfUser)

        status=jobOfUser.values_list("status", flat=True)
        print(status)
        return render(request,'applicationStatus.html',{'jobOfUser':jobOfUser})
    return render(request,'applicationStatus.html')


def recommended_jobs(request):
    return render(request,'recommendedJobs.html')

@login_required
def profile_completion_view(request):
    user = request.user

    try:
        userinfo = user.userinfo
    except UserInfo.DoesNotExist:
        userinfo = None

    # Default percentage
    completion = 0

    if userinfo:
        if userinfo.profile_image:
            completion += 20
        if user.mobile and userinfo.currentLocation:
            completion += 20
        if Course.objects.filter(user=user).exists():
            completion += 20
        if Experience.objects.filter(user=user).exists():
            completion += 20
        if userinfo.resume:
            completion += 20

    print("DEBUG VIEW:", completion)  # 👈 check your Django console

    return render(request, "profile.html", {
        "userinfo": userinfo,
        "profile_completion": completion,
    })
