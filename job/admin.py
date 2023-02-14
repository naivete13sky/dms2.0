from django.contrib import admin
from .models import Job,JobInfoForDevTest
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin


# 自定义筛选器。MultiSelectField类型的字段直接放在list_filter里有问题的。
class HasFileTypeListFilter(admin.SimpleListFilter):
    # 提供一个可读的标题
    title = _('包含文件类型')
    # 用于URL查询的参数.
    parameter_name = 'has_file_type'

    def lookups(self, request, model_admin):
        """
        返回一个二维元组。每个元组的第一个元素是用于URL查询的真实值，
        这个值会被self.value()方法获取，并作为queryset方法的选择条件。
        第二个元素则是可读的显示在admin页面右边侧栏的过滤选项。
        """
        return (
            ('gerber274x', _('gerber274x')),
            ('gerber274d', _('gerber274d')),
            ('dxf', _('dxf')),
            ('dwg', _('dwg')),
            ('odb', _('odb')),
            ('pcb', _('pcb')),

        )

    def queryset(self, request, queryset):
        """
        根据self.value()方法获取的条件值的不同执行具体的查询操作。
        并返回相应的结果。
        """
        if self.value():
            # print("self.value:",self.value)
            return queryset.filter(has_file_type__contains = self.value())



@admin.register(Job)
# class JobAdmin(admin.ModelAdmin):
class JobAdmin(ImportExportModelAdmin):
    list_display = ('id','job_name','file_compressed','has_file_type','status','author','from_object_pcb_factory','from_object_pcb_design','publish','create_time','tag_list')

    search_fields = ('=id','job_name',)
    list_filter = (HasFileTypeListFilter, 'status', 'author__username','from_object_pcb_factory','from_object_pcb_design','tags')
    prepopulated_fields = {'remark': ('job_name',)}
    raw_id_fields = ('author','from_object_pcb_factory','from_object_pcb_design')
    # date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10

    exclude = ('author','publish')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return ",".join(o.name for o in obj.tags.all())

    '''保存时自动设置author为当前登录用户'''
    def save_model(self, request, obj, form, change):
        # If creating new article, associate request.user with author.
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)






@admin.register(JobInfoForDevTest)
class JobInfoForDevTestAdmin(admin.ModelAdmin):
    list_display = ('id','job','status','author','file','has_step_multi','job_type_1','job_type_2','job_type_3','updated','tag_list','remark')

    search_fields = ('=id','job__job_name','status','author__username','has_step_multi',)
    list_filter = ( 'status', 'author',  'job_type_1', 'job_type_2', 'job_type_3','tags',)
    prepopulated_fields = {'remark': ('job',)}
    raw_id_fields = ('author','job')
    # date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10
    exclude = ('author', 'publish','solderMaxWindowNum4singleSide','origStepName','prepareStepName','pcsStepName','setStepName','panelStepName','hasPGlayer','hasSMlayer')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return ",".join(o.name for o in obj.tags.all())


    '''保存时自动设置author为当前登录用户'''
    def save_model(self, request, obj, form, change):
        # If creating new article, associate request.user with author.
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)