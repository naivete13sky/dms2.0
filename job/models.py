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

class MyTag(TagBase):
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


class TaggedWhatever(GenericTaggedItemBase):
    # 把我们自定义的模型类传进来，它就能知道如何处理
    tag = models.ForeignKey(
        MyTag,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )



# Create your models here.
class Job(models.Model):
    job_name = models.CharField(max_length=20, validators=[validators.MinLengthValidator(limit_value=3)],
                                                                help_text='料号名称,有可能有重复名字', verbose_name="料号名称")
    file_compressed = models.FileField(upload_to='files', blank=True, null=True,
                                       help_text='原始文件,rar压缩包', verbose_name="原始文件")

    has_file_type = MultiSelectField(choices=(('gerber274x', 'Gerber274X'),('gerber274d', 'Gerber274D'), ('dxf', 'DXF'),
                                                ('dwg', 'DWG'), ('odb', 'ODB'), ('pcb', 'PCB')),
                                     blank=True,null=True, max_choices=20, max_length=200,
                                     verbose_name="包含文件类型")

    status = models.CharField(max_length=10, choices=(('draft', '草稿'), ('published', '正式')), default='draft',
                              help_text='草稿表示未经人工确认', verbose_name="状态")

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_jobs', null=True, blank=True,
                               help_text='料号上传人', verbose_name="负责人")
    from_object_pcb_factory = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                                related_name='job_job_account_customer_pcb_factory', null=True,
                                                blank=True,
                                                                               help_text='料号来源-板厂', verbose_name="料号来源-板厂")
    from_object_pcb_design = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                        related_name='job_job_account_customer_pcb_design', null=True, blank=True,
                                        help_text='料号来源-设计端', verbose_name="料号来源-设计端")
    publish = models.DateTimeField(default=timezone.now, null=True, blank=True, verbose_name='发布时间')
    create_time = models.DateTimeField(auto_now_add=True,blank=True,null=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')


    tags=TaggableManager()
    # 声明这个manager也是基于我们自定义的模型类
    tags = TaggableManager(through=TaggedWhatever,help_text='必填')
    remark = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=0)], blank=True,
                              null=True, help_text='料号的说明备注', verbose_name="备注")

    class Meta:
        db_table = 'job_job'
        ordering = ('-create_time',)
    # def get_absolute_url(self):
    #     return reverse('job_manage:job_detail', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])
    def get_absolute_url(self):
        return reverse('job:JobDetailViewForm', args=[self.id, ])
        # return reverse('job_manage:job_detail', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])
    def __str__(self):
        # Return a string that represents the instance
        return self.job_name

    def to_dict(self):
        data = {}
        for f in self._meta.concrete_fields:
            data[f.name] = f.value_from_object(self)
        return data







class MyTagForJobInfoForDevTest(TagBase):
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


class TaggedWhateverForJobInfoForDevTest(GenericTaggedItemBase):
    # 把我们自定义的模型类传进来，它就能知道如何处理
    tag = models.ForeignKey(
        MyTagForJobInfoForDevTest,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )



class JobInfoForDevTest(models.Model):
    job = models.ForeignKey(to="job.Job", on_delete=models.CASCADE, null=True, blank=True,
                            related_name='job_job_job_info_for_dev_test', verbose_name="父料号名称")

    job_name = models.CharField(null=True, blank=True,max_length=20, validators=[validators.MinLengthValidator(limit_value=3)],
                                help_text='料号名称,有可能有重复名字', verbose_name="料号名称")

    status = models.CharField(max_length=10, choices=(('draft', '草稿'), ('published', '正式')), default='draft',
                              help_text='草稿表示未经人工确认', verbose_name="状态")

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_job_info_for_dev_test_user', null=True, blank=True,
                               help_text='负责人', verbose_name="负责人")
    # ------------------------------------------------整理好的料号信息-------------------------------------------
    file = models.FileField(upload_to='files', blank=True, null=True, help_text='整理好的资料,确认过是对的',
                                verbose_name="整理好的资料")

    file_type = models.CharField(max_length=10,
                                 choices=(('odb', 'ODB'),('eps', 'EPS'),('pcb', 'PCB'), ('else', 'Else')), default='else',
                                 help_text='料号文件类型', verbose_name="料号文件类型")

    has_step_multi = MultiSelectField(choices=(('orig', 'orig'), ('net', 'net'),('pre', 'pre'), ('pcs', 'pcs'),
                                               ('set', 'set'),('panel', 'panel')),
                                      blank=True,null=True, max_choices=20, max_length=200,verbose_name="包含step")



    #------------------------------------------------所有层相关的-------------------------------------------
    job_type_1 = models.CharField(max_length=20, choices=(('through_hole', '通孔板'), ('non_through_hole', '非通孔板'), ('else', '其它')), default='else',
                                blank=True,null=True,help_text='料号的类型-维度1', verbose_name="料号类型-维度1")
    job_type_2 = models.CharField(max_length=20,
                                  choices=(('rigid', '硬板'), ('flex', '软板'),('rigid_flex', '软硬结合板'), ('else', '其它')),
                                  default='else',
                                  blank=True, null=True, help_text='料号的类型-维度2', verbose_name="料号类型-维度2")
    job_type_3 = models.CharField(max_length=20,
                                  choices=(('ic', 'IC载板'), ('led', 'LED灯板'), ('car', '汽车板'), ('server', '服务器板'), ('else', '其它')),
                                  default='else',
                                  blank=True, null=True, help_text='料号的类型-维度3', verbose_name="料号类型-维度3")
    pcsSize = models.FloatField(null=True, blank=True, help_text='pcs的profile线外接正矩形的对角线长度(单位:inch)',
                                verbose_name='pcs对角线尺寸')
    matrixRowNum = models.IntegerField(null=True, blank=True,
                                       validators=[validators.MaxValueValidator(1000), validators.MinValueValidator(0)],
                                       help_text="所有层数(包括任意层)", verbose_name='所有层数')
    totalFeatureNum = models.IntegerField(null=True, blank=True,
                                          validators=[validators.MaxValueValidator(100000000),
                                                      validators.MinValueValidator(0)], help_text="总物件数",
                                          verbose_name='总物件数')

    # ------------------------------------------------线路层相关的-------------------------------------------
    copperLayerNum = models.IntegerField(null=True, blank=True,validators=[validators.MaxValueValidator(1000),validators.MinValueValidator(0)],
                                         help_text="信号层数量(含地电层)",verbose_name='信号层数')
    pgLayerNum = models.IntegerField(null=True, blank=True, validators=[validators.MaxValueValidator(1000),
                                                                            validators.MinValueValidator(0)],
                                         help_text="地电层数量", verbose_name='地电层数')
    hasPGlayer = models.CharField(max_length=10, choices=(('yes', '是'), ('no', '否'), ('none', 'None')), default='none',
                                  help_text="是否有地电层(负片层)", verbose_name="是否有地电层(负片层)")
    linedCopper = models.CharField(max_length=10, choices=(('yes', '是'), ('no', '否'), ('none', 'None')), default='none',
                                   help_text="线路层是否为线铜", verbose_name="线路层是否为线铜")

    bgaNumTop = models.IntegerField(null=True, blank=True,
                                 validators=[validators.MaxValueValidator(100000000), validators.MinValueValidator(0)],
                                 help_text="正面BGA总数", verbose_name='正面BGA总数')

    bgaNumBottom = models.IntegerField(null=True, blank=True,
                                 validators=[validators.MaxValueValidator(100000000), validators.MinValueValidator(0)],
                                 help_text="背面BGA总数", verbose_name='背面BGA总数')


    bgaNum = models.IntegerField(null=True, blank=True,
                                 validators=[validators.MaxValueValidator(100000000), validators.MinValueValidator(0)],
                                 help_text="BGA总数", verbose_name='BGA总数')
    impLineNum = models.IntegerField(null=True, blank=True,
                                     validators=[validators.MaxValueValidator(100000), validators.MinValueValidator(0)],
                                     help_text="阻抗线数", verbose_name='阻抗线数')

    minLineWidth4outerTop = models.FloatField(null=True, blank=True, help_text='正面外层的最小线宽(单位:mil)', verbose_name='正面外层最小线宽')
    minLineSpace4outerTop = models.FloatField(null=True, blank=True, help_text='正面外层的最小线距(单位:mil)', verbose_name='正面外层最小线距')

    minLineWidth4outerBottom = models.FloatField(null=True, blank=True, help_text='背面外层的最小线宽(单位:mil)', verbose_name='背面外层最小线宽')
    minLineSpace4outerBottom = models.FloatField(null=True, blank=True, help_text='背面外层的最小线距(单位:mil)', verbose_name='背面外层最小线距')


    minLineWidth4outer = models.FloatField(null=True, blank=True, help_text='外层的最小线宽(单位:mil)', verbose_name='外层最小线宽')
    minLineSpace4outer = models.FloatField(null=True, blank=True, help_text='外层的最小线距(单位:mil)', verbose_name='外层最小线距')

    # ------------------------------------------------防焊层相关的-------------------------------------------
    solderWindowNumTop = models.IntegerField(null=True, blank=True,
                                                        validators=[validators.MaxValueValidator(100000000),
                                                                    validators.MinValueValidator(0)],
                                                        help_text="正面防焊层物件数,如果有多层，填写总数）", verbose_name='正面防焊层物件数（总数）')
    solderWindowNumBottom = models.IntegerField(null=True, blank=True,
                                             validators=[validators.MaxValueValidator(100000000),
                                                         validators.MinValueValidator(0)],
                                             help_text="底面防焊层物件数,如果有多层，填写总数）", verbose_name='底面防焊层物件数（总数）')
    solderMaxWindowNum4singleSide = models.IntegerField(null=True, blank=True,
                                                        validators=[validators.MaxValueValidator(100000000),
                                                                    validators.MinValueValidator(0)],
                                                        help_text="单面最多防焊开窗数量", verbose_name='单面最多防焊开窗数量')
    hasSMlayer = models.CharField(max_length=10, choices=(('yes', '是'), ('no', '否'), ('none', 'None')), default='none',
                                  help_text="是否有防焊层?", verbose_name="是否有防焊层")

    # ------------------------------------------------孔层相关的-------------------------------------------
    pcsDrlNum = models.IntegerField(null=True, blank=True,
                                    validators=[validators.MaxValueValidator(100000000),
                                                validators.MinValueValidator(0)], help_text="所有孔层的所有孔数量(包括槽孔,镭射孔等)",
                                    verbose_name='pcs所有孔数')

    hdiLevel = models.IntegerField(null=True, blank=True,
                                   validators=[validators.MaxValueValidator(99), validators.MinValueValidator(0)],
                                   help_text="孔阶数，HDI介数", verbose_name='孔阶数')


    # ------------------------------------------------梅需要的其它字段-------------------------------------------
    usage=models.CharField(null=True,blank=True,max_length=200, validators=[validators.MinLengthValidator(limit_value=0)],help_text="料号用途",verbose_name='用途')
    impCouponStepName=models.CharField(null=True,blank=True,max_length=50, validators=[validators.MinLengthValidator(limit_value=0)],help_text="阻抗测试条的step名",verbose_name='阻抗step')
    routLayerName=models.CharField(null=True,blank=True,max_length=50, validators=[validators.MinLengthValidator(limit_value=0)],help_text="rout层的名字",verbose_name='Rout层')
    panelSize=models.FloatField(null=True,blank=True,help_text='panel的profile线外接正矩形的对角线长度(单位:inch)',verbose_name='panel对角线尺寸')



    # <------------------------------------------------------常用字段--------------------------------------------------->
    publish = models.DateTimeField(default=timezone.now, null=True, blank=True, verbose_name='发布时间')
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    tags = TaggableManager(through=TaggedWhateverForJobInfoForDevTest, help_text='必填')
    remark = models.CharField(max_length=100, validators=[validators.MinLengthValidator(limit_value=0)], blank=True,
                              null=True, help_text='料号的说明备注', verbose_name="备注")

    class Meta:
        db_table = 'job_job_info_for_dev_test'
        ordering = ('-create_time',)


#     # def get_absolute_url(self):
#     #     return reverse('job:JobDetailViewForm', args=[self.id, ])
#
#
#     def __str__(self):
#         # Return a string that represents the instance
#         return self.job







    # # ------------------------------------------------基础字段，主要为了导入测试用的-------------------------------------------
    # file_usage_type = models.CharField(max_length=50,
    #                                    choices=(('input_test', '导入测试'), ('customer_job', '客户资料'),
    #                                             ('test', '测试'), ('else', '其它')), default='else', help_text='料号使用类型',
    #                                    verbose_name="料号使用类型")

    # # ------------------------------------------------基础字段，主要为了导入测试用的-------------------------------------------
    # file_usage_type = models.CharField(max_length=50,
    #                                    choices=(('input_test', '导入测试'), ('customer_job', '客户资料'),
    #                                             ('test', '测试'), ('else', '其它')), default='else', help_text='料号使用类型',
    #                                    verbose_name="料号使用类型")
    # 当我们想设置最小长度的时候，但是在字段中没有的话，可以借助自定义验证器MinLengthValidator
    # FileField 为文件上传功能upload_to:对应的files创建的文件夹目录
#     file_compressed = models.FileField(upload_to='files', blank=True, null=True,
#                                        help_text='整理过的原始文件.若是导入测试类型,则是rar压缩包,压缩包中只有一层文件夹.也可以是.tgz|.eps', verbose_name="整理过的原始文件")
#     job_name = models.CharField(max_length=20, validators=[validators.MinLengthValidator(limit_value=3)],
#                                 help_text='料号名称,有可能有重复名字', verbose_name="料号名称")
#     file_odb_g = models.FileField(upload_to='files', blank=True, null=True, help_text='G软件转图的结果,导入测试类型需要填写此字段',
#                                   verbose_name="G-ODB++")
#     file_compressed_org = models.FileField(upload_to='files', blank=True, null=True, help_text='未整理的原始文件,rar压缩包',verbose_name="原始文件")
#     file_org_type = models.CharField(max_length=10,
#                                      choices=(('gerber274X', 'Gerber274-X'), ('gerber274D', 'Gerber274-D'),
#                                               ('odb++', 'ODB++'), ('eps', 'EPS'),('else', '其它')), default='else',
#                                      help_text='原始文件类型', verbose_name="原始文件类型")
#     from_object = models.CharField(max_length=20, validators=[validators.MinLengthValidator(limit_value=2)], null=True,
#                                    blank=True, help_text='料号从哪来的', verbose_name="料号来源")
#     from_object_pcb_factory = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='job_manage_job_account_customer_pcb_factory', null=True, blank=True,
#                                help_text='料号来源-板厂', verbose_name="料号来源-板厂")
#     from_object_pcb_design = models.ForeignKey(Customer, on_delete=models.CASCADE,
#                                         related_name='job_manage_job_account_customer_pcb_design', null=True, blank=True,
#                                         help_text='料号来源-设计端', verbose_name="料号来源-设计端")
#     status = models.CharField(max_length=10, choices=(('draft', '草稿'), ('published', '正式')), default='draft',
#                               help_text='草稿表示未经人工确认', )
#     # tags=TaggableManager()
#     # 声明这个manager也是基于我们自定义的模型类
#     tags = TaggableManager(through=TaggedWhatever,help_text='必填')

#
#     file_odb_current = models.FileField(upload_to='files', blank=True, null=True, help_text='最新一次的悦谱转图结果,不需要手工录入,可在线自动生成',verbose_name="最新-EP-ODB++")
#     vs_result_ep=models.CharField(max_length=10, choices=(('passed', '成功'), ('failed', '失败'), ('none', '未比对')), default='none',help_text='导入测试管理员负责填写',verbose_name="悦谱比图结果")
#     vs_result_g = models.CharField(max_length=10, choices=(('passed', '成功'), ('failed', '失败'), ('none', '未比对')),
#                                     default='none',help_text='导入测试管理员负责填写',verbose_name="G软件比图结果")
#     bug_info = models.CharField(max_length=20, validators=[validators.MinLengthValidator(limit_value=0)],blank=True, null=True,help_text='Bug信息',verbose_name="Bug信息")
#     bool_layer_info = models.CharField(max_length=10, choices=(('true', 'true'), ('false', 'false')), default='false',
#                                        null=True, blank=True, help_text='不需要人工填写,系统用', verbose_name="是否有层别信息")
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_manage_jobs', null=True, blank=True,
#                                help_text='料号上传人', verbose_name="负责人")
#     publish = models.DateTimeField(default=timezone.now, null=True, blank=True, verbose_name='发布时间')
#     create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
#     updated = models.DateTimeField(auto_now=True, verbose_name='更新时间')
#     vs_time_ep = models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=0)],
#                                   null=True, blank=True, help_text='系统生成', verbose_name="悦谱比对时间戳")
#     vs_time_g = models.CharField(max_length=10, validators=[validators.MinLengthValidator(limit_value=0)],
#                                  null=True, blank=True, help_text='系统生成', verbose_name="G比对时间戳")

