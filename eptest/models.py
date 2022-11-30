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
from mptt.models import MPTTModel, TreeForeignKey

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
    file_type = models.CharField(max_length=10,
                                 choices=(('gerber274x', 'Gerber274X'), ('dxf', 'DXF'),('dwg', 'DWG'), ('odb', 'ODB'),
                                          ('pcb', 'PCB'), ('none', 'none')),default='none',
                                 help_text='料号文件类型', verbose_name="料号文件类型")


    test_usage_for_epcam_module = TreeForeignKey(to='eptest.EpcamModule',on_delete=models.CASCADE, null=True, blank=True,
                            related_name='eptest_job_for_test_epcam_module', verbose_name="模块名称")

    standard_odb = models.FileField(upload_to='files', blank=True, null=True,help_text='标准料号，用来测试比对用的',verbose_name="标准料号")

    vs_result_ep = models.CharField(max_length=10, choices=(('passed', '成功'), ('failed', '失败'), ('none', '未比对')),
                                    default='none', help_text='导入测试管理员负责填写', verbose_name="悦谱比图结果")
    vs_result_g = models.CharField(max_length=10, choices=(('passed', '成功'), ('failed', '失败'), ('none', '未比对')),
                                   default='none', help_text='导入测试管理员负责填写', verbose_name="G软件比图结果")
    bug_info = models.CharField(max_length=20, validators=[validators.MinLengthValidator(limit_value=0)], blank=True,
                                null=True, help_text='Bug信息', verbose_name="Bug信息")

    bool_layer_info = models.CharField(max_length=10, choices=(('true', 'true'), ('false', 'false')), default='false',
                                       null=True, blank=True, help_text='不需要人工填写,系统用',
                                       verbose_name="是否有层别信息")

    vs_time_ep = models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=0)],
                                  null=True, blank=True, help_text='系统生成', verbose_name="悦谱比对时间戳")
    vs_time_g = models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=0)],
                                 null=True, blank=True, help_text='系统生成', verbose_name="G比对时间戳")


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




class EpcamModule(MPTTModel):
    # name = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, unique=False)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        db_table = 'eptest_epcam_module'
        ordering = ('id',)

    def __str__(self):
        # Return a string that represents the instance
        return self.name