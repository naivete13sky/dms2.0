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
    job_parent = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, blank=True,
                            related_name='eptest_job_for_test_job_job', verbose_name="父料号名称")
    job_name = models.CharField(max_length=20, null=True, blank=True,validators=[validators.MinLengthValidator(limit_value=3)],
                                help_text='料号名称,有可能有重复名字', verbose_name="料号名称")

    file = models.FileField(upload_to='files', blank=True, null=True,
                                       help_text='整理过的测试料号，包括：Gerber为rar压缩包；ODB++为tgz压缩包；DXF为单个文件；PCB为单个文件；', verbose_name="测试料号")
    file_type = models.CharField(max_length=10,
                                 choices=(('gerber274X', 'Gerber274X'),('gerber274D', 'Gerber274D'), ('dxf', 'DXF'),('dwg', 'DWG'), ('odb', 'ODB'),
                                          ('pcb', 'PCB'), ('else', 'Else')),default='else',
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

    def get_absolute_url(self):
        return reverse('eptest:JobForTestDetailViewForm', args=[self.id, ])

    def __str__(self):
        # Return a string that represents the instance
        return self.job_name

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



class Layer(models.Model):
    job = models.ForeignKey(to="eptest.JobForTest", on_delete=models.CASCADE,null=True,blank=True, related_name='eptest_job_for_test_layer',verbose_name="料号名称")

    layer=models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=1)],
                            verbose_name="层名称")
    layer_org=models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=1)],null=True,blank=True,
                            verbose_name="原始层名称")
    vs_result_manual = models.CharField(max_length=10, choices=(('passed', '通过'), ('failed', '失败'), ('none', '未比对')),
                                    default='none', null=True, blank=True, verbose_name="人工比对结果")
    vs_result_ep = models.CharField(max_length=10, choices=(('passed', '通过'), ('failed', '失败'), ('none', '未比对')),
                                 default='none', null=True, blank=True, verbose_name="悦谱比对结果")
    vs_result_g = models.CharField(max_length=10, choices=(('passed', '通过'), ('failed', '失败'), ('none', '未比对')),
                                    default='none', null=True, blank=True, verbose_name="G软件比对结果")

    layer_file_type=models.CharField(max_length=100, choices=(('gerber274X', 'Gerber274-X'), ('gerber274D', 'Gerber274-D'), ('excellon2', 'Excellon2'),
                                                         ('excellon1', 'Excellon1'),('dxf', 'DXF'),
                                                             ('else', '其它')), default='else',verbose_name="层文件类型")

    layer_type = models.CharField(max_length=100, choices=(('signal_outter', '外层'),  ('signal_inner', '内层'),('solder', '防焊'),('silk', '丝印'),('paste', '锡膏'),
    ('drill', '孔层'), ('rout', 'Rout'), ('slot', '槽孔'), ('else', '其它')), default='else', verbose_name="层类型")
    features_count=models.IntegerField(default=0,null=True,blank=True,
                                     validators=[validators.MaxValueValidator(100000000), validators.MinValueValidator(0)],verbose_name="物件数")


    units = models.CharField(max_length=10, choices=(('Inch', 'Inch'), ('MM', 'MM'), ('none', '未记录')), default='none',
                                             verbose_name="units")

    coordinates = models.CharField(max_length=20, choices=(('Absolute', 'Absolute'), ('Incremental', 'Incremental'), ('none', '未记录')),
                                default='none',
                                verbose_name="坐标")

    zeroes_omitted = models.CharField(max_length=10, choices=(
    ('Leading', 'Leading'), ('Trailing', 'Trailing'), ('none', '未记录')), default='none', verbose_name="省零")
    number_format_A = models.CharField(max_length=10, choices=(
    ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('none', '未记录')),
                                                       default='none', verbose_name="整数")
    number_format_B = models.CharField(max_length=10, choices=(
        ('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('none', '未记录')),
                                                       default='none', verbose_name="小数")
    tool_units_ep = models.CharField(max_length=10,
                                                  choices=(('Inch', 'Inch'), ('MM', 'MM'), ('Mils', 'Mils'), ('none', '未记录')),
                                                  default='none',
                                                  verbose_name="Tool_units_EP")

    tool_units_g = models.CharField(max_length=10,
                                     choices=(('Inch', 'Inch'), ('MM', 'MM'), ('Mils', 'Mils'), ('none', '未记录')),
                                     default='none',
                                     verbose_name="Tool_units_G")

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_manage_layer_user', null=True, blank=True,
                               verbose_name="负责人")
    STATUS_CHOICES = (('draft', '草稿'), ('published', '正式'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    vs_time_ep = models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=0)],
                               null=True, blank=True, verbose_name="悦谱比对时间戳")
    vs_time_g = models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=0)],
                                  null=True, blank=True, verbose_name="G比对时间戳")
    remark = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=0)],
                              verbose_name="备注", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')



    class Meta:
        db_table = 'eptest_layer'
        ordering = ('-create_time',)


    # def get_absolute_url(self):
    #     return reverse('job_manage:LayerFormView', args=[self.id, ])

    def __str__(self):
        # Return a string that represents the instance
        return self.layer



class Bug(models.Model):
    job = models.ForeignKey(to="eptest.JobForTest", on_delete=models.CASCADE,null=True,blank=True, related_name='eptest_job_for_test_bug',verbose_name="料号名称")
    bug=models.CharField(max_length=200, validators=[validators.MinLengthValidator(limit_value=1)],null=True,blank=True,
                            verbose_name="Bug名称")
    bug_zentao_id=models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=1)],
                            verbose_name="禅道ID")
    bug_zentao_pri = models.CharField(max_length=10, choices=(('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('none', 'none')),
                                    default='none', null=True, blank=True, verbose_name="优先级")
    bug_zentao_status = models.CharField(max_length=10, choices=(('active', '激活'), ('closed', '已关闭'), ('resloved', '已解决'), ('none', 'none')),
                                      default='none', null=True, blank=True, verbose_name="禅道状态")
    bug_creator = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=1)],null=True,blank=True,
                           verbose_name="创建者")
    bug_create_date = models.DateTimeField(null=True,blank=True,verbose_name='禅道创建时间')
    bug_assigned_to = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=1)],null=True,blank=True,
                                   verbose_name="指派给")

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eptest_job_for_test_bug_user', null=True, blank=True,
                               verbose_name="负责人")
    status = models.CharField(max_length=10, choices=(('draft', '草稿'), ('published', '正式')), default='draft',null=True,blank=True,verbose_name="发布状态")
    refresh_time = models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=0)],
                               null=True, blank=True, verbose_name="刷新时间戳")
    remark = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=0)],
                              verbose_name="备注", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')


    class Meta:
        db_table = 'eptest_bug'
        ordering = ('-create_time',)

    # def get_absolute_url(self):
    #     return reverse('job_manage:BugFormView', args=[self.id, ])

    def __str__(self):
        # Return a string that represents the instance
        return self.bug_zentao_id


class Vs(models.Model):
    job = models.ForeignKey(to="eptest.JobForTest", on_delete=models.CASCADE,null=True,blank=True, related_name='eptest_job_for_test_vs',verbose_name="料号名称")

    layer=models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=1)],
                            verbose_name="层名称")
    layer_org=models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=1)],null=True,blank=True,
                            verbose_name="原始层名称")
    vs_result=models.CharField(max_length=10, choices=(('passed', '通过'), ('failed', '失败'), ('none', '未比对')), default='none',null=True,blank=True,verbose_name="比对结果")
    vs_result_detail=models.CharField(max_length=1000000, validators=[validators.MinLengthValidator(limit_value=0)],
                            null=True,blank=True,verbose_name="比对详细信息")

    vs_method = models.CharField(max_length=10, choices=(('ep', '悦谱'), ('g', 'G软件'), ('none', 'none')),
                                    default='none', null=True, blank=True, verbose_name="比对方法")
    layer_file_type=models.CharField(max_length=100, choices=(('gerber274X', 'Gerber274-X'), ('gerber274D', 'Gerber274-D'), ('excellon2', 'Excellon2'),
                                                         ('excellon1', 'Excellon1'),('dxf', 'DXF'),
                                                             ('else', '其它')), default='else',verbose_name="层文件类型")

    layer_type = models.CharField(max_length=100, choices=(('signal_outter', '外层'),  ('signal_inner', '内层'),('solder', '防焊'),('silk', '丝印'),('paste', '锡膏'),
    ('drill', '孔层'), ('rout', 'Rout'), ('slot', '槽孔'), ('else', '其它')), default='else', verbose_name="层类型")
    features_count=models.IntegerField(default=0,null=True,blank=True,
                                     validators=[validators.MaxValueValidator(100000000), validators.MinValueValidator(0)],verbose_name="物件数")



    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eptest_job_for_test_vs_user', null=True, blank=True,
                               verbose_name="负责人")
    STATUS_CHOICES = (('draft', '草稿'), ('published', '正式'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    vs_time_ep=models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=0)],
                            null=True, blank=True,verbose_name="悦谱比对时间戳")
    vs_time_g = models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=0)],
                                  null=True, blank=True, verbose_name="G比对时间戳")

    remark = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=0)],
                              verbose_name="备注", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    class Meta:
        db_table = 'vs'
        ordering = ('-create_time',)
    # def get_absolute_url(self):
    #     return reverse('job_manage:JobFormView', args=[self.id, ])
    def __str__(self):
        # Return a string that represents the instance
        return self.layer


