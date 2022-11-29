from django.db import models
from django.conf import settings
from django.core import validators
from django.urls import reverse
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



class Customer(models.Model):
    name_full = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=0)],null=True,blank=True,verbose_name="客户全称")
    name_simple = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=0)],null=True,blank=True,verbose_name="客户简称")
    department = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=0)],null=True,blank=True,verbose_name="部门")


    # name = models.CharField('标题', max_length=256,null=True,blank=True)
    country = models.CharField('国家', max_length=256,null=True,blank=True)
    province = models.CharField('省份', max_length=256,null=True,blank=True)
    city = models.CharField('城市', max_length=256,null=True,blank=True)



    customer_type=models.CharField(max_length=20, choices=(('pcb_factory', '板厂'), ('design_customer', '设计端客户')), default='pcb_factory',
                                   null=True,blank=True,verbose_name="客户类型")

    remark = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=0)], blank=True,
                              null=True, help_text='备注', verbose_name="备注")
    publish = models.DateTimeField(default=timezone.now)
    create_time = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        # return "Profile for customer {}".format(self.name_simple)
        return self.name_simple

    # def get_absolute_url(self):
    #     return reverse('CustomerDetailView', args=[self.id, ])