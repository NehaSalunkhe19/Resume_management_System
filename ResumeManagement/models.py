from tkinter.constants import CASCADE

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from tinymce.models import HTMLField
from django.db import models
from django.conf import settings
from django.core.mail import send_mail


# Create your models here.
class CustomUser(AbstractUser):
    email=models.EmailField(unique=True)
    mobile=models.CharField(max_length=12)

    def __str__(self):
        return self.username

class Skill(models.Model):
    name=models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Job(models.Model):
    role=models.CharField(max_length=100)
    companyName=models.CharField(max_length=100)
    location=models.CharField(max_length=100)
    skills = models.ManyToManyField(Skill)
    datePosted=models.DateTimeField(auto_now_add=True)
    jobDescription=HTMLField()
    jobType = models.CharField(max_length=50, choices=[('Full-Time', 'Full-Time'), ('Part-Time', 'Part-Time'),
                                                       ('Internship', 'Internship')])
    salary= models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.role


class Course(models.Model):
    YEAR_CHOICES = [(r, r) for r in range(1990, 2031)]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    course_name = models.CharField(max_length=100, null=True, blank=True)
    college = models.CharField(max_length=300, null=True, blank=True)
    passout_year = models.IntegerField(choices=YEAR_CHOICES, null=True, blank=True)
    cgpa = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.course_name} at {self.college}"


class Experience(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    role = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    currently_working = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.role} at {self.company_name}"

class UserInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    currentLocation= models.TextField(null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return self.user.username

    def profile_completion(self):
        completion = 0
        total_sections = 5  # update as per your logic

        if self.profile_image:
            completion += 20
        if self.user.mobile and self.currentLocation:
            completion += 20
        if self.user.course_set.exists():  # or Course.objects.filter(user=self.user).exists()
            completion += 20
        if self.user.experience_set.exists():  # or Experience.objects.filter(user=self.user).exists()
            completion += 20
        if self.resume:
            completion += 20

        return completion


class SavedJobs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    savedDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'job'], name='unique_saved_job')
        ]

class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    location = models.CharField(max_length=100, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    appliedDate = models.DateTimeField(auto_now_add=True)
    statusUpdatedDate = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'job')  # prevent duplicate applications

    def __str__(self):
        return f"{self.user.username} - {self.job.role} ({self.status})"

    def save(self, *args, **kwargs):
        # Check if this is an update (object exists already)
        if self.pk:
            previous = Application.objects.get(pk=self.pk)
            if previous.status != self.status:
                self.send_status_change_email()

        super().save(*args, **kwargs)

    def send_status_change_email(self):
        subject = f"Your application status for {self.job.role} has changed"
        if self.status == 'approved':
            message = f"Hi {self.user.first_name},\n\n🎉 Congratulations! Your application for '{self.job.role}' has been *approved*."
        elif self.status == 'rejected':
            message = f"Hi {self.user.first_name},\n\nThank you for applying for '{self.job.role}', but unfortunately your application has been *rejected*."
        else:
            return  # Don't send email for 'applied' status

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            fail_silently=False
        )

