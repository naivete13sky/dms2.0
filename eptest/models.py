from django import forms
from django.db import models
from django.core import validators
from django.forms import widgets, fields
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from taggit.models import TagBase,GenericTaggedItemBase
from django.utils.text import slugify
from django.utils.translation import gettext, gettext_lazy as _
from account.models import Customer
from multiselectfield import MultiSelectField
from job.models import Job

class MyTagForEptest(TagBase):
    # 这一步是关键，要设置allow_unicode=True，这样这个字段才能支持中文
    slug = models.SlugField(verbose_name=_("slug"), unique=True, max_length=100, allow_unicode=True)

    # 这个方法也是要覆盖的，它是用来计算slug的，也是添加allow_unicode=True参数
    def slugify(self, tag, i=None):
        slug = slugify(tag, allow_unicode=True)
        if i is not None:
            slug += "_%d" % i
        return slug

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        app_label = "taggit"


class TaggedWhateverForEptest(GenericTaggedItemBase):
    # 把我们自定义的模型类传进来，它就能知道如何处理
    tag = models.ForeignKey(
        MyTagForEptest,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )


class JobForTest(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True,
                            related_name='eptest_job_for_test_job_job', verbose_name="料号名称")
    file = models.FileField(upload_to='files', blank=True, null=True,
                                       help_text='整理过的测试料号，包括：Gerber为rar压缩包；ODB++为tgz压缩包；DXF为单个文件；PCB为单个文件；', verbose_name="测试料号")

    # test_type_multi = MultiSelectField(choices=(('input_test', '导入测试'), ('dxf', 'DXF'),
    #                                             ('dwg', 'DWG'), ('odb', 'ODB'), ('pcb', 'PCB'),('else', '其它')),default='else',help_text='料号使用类型',
    #                                  blank=True,null=True, max_choices=20, max_length=200,
    #                                  verbose_name="包含文件类型")







    status = models.CharField(max_length=10, choices=(('draft', '草稿'), ('published', '正式')), default='draft',
                              help_text='草稿表示未经人工确认', verbose_name="状态")

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eptest_job_for_test_user', null=True, blank=True,
                               help_text='负责人', verbose_name="负责人")
    publish = models.DateTimeField(default=timezone.now, null=True, blank=True, verbose_name='发布时间')
    create_time = models.DateTimeField(auto_now_add=True,blank=True,null=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    tags = TaggableManager(through=TaggedWhateverForEptest,help_text='必填')
    remark = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=0)], blank=True,
                              null=True, help_text='说明备注', verbose_name="备注")

    class Meta:
        db_table = 'eptest_job_for_test'
        ordering = ('-create_time',)

    # def get_absolute_url(self):
    #     return reverse('job:JobDetailViewForm', args=[self.id, ])

    def __str__(self):
        # Return a string that represents the instance
        return self.job.job_name

    # def to_dict(self):
    #     data = {}
    #     for f in self._meta.concrete_fields:
    #         data[f.name] = f.value_from_object(self)
    #     return data