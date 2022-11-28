from django.db import models
from django.conf import settings
from django.core import validators
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='user/photo', blank=True,null=True)
    mobile=models.CharField(blank=True,null=True,max_length=11, validators=[validators.MinLengthValidator(limit_value=11)],verbose_name="手机号")


    publish = models.DateTimeField(default=timezone.now)
    create_time = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return "Profile for user {}".format(self.user.username)