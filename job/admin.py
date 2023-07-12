from django.contrib import admin
from .models import Job,JobInfoForDevTest
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from django.http import HttpResponse
from .resource import JobResource

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



#为了实现在admin后台可页面上设置每页显示条数，通过下面方法，要创建一个过滤器PageSizeFilter。
#还要创建一个CustomModelAdmin类，这个类实现changelist_view方法。因为在过滤器PageSizeFilter无法重写changelist_view，所以要写此类实现类似效果。
class PageSizeFilter(admin.SimpleListFilter):
    title = _('Page Size')  # 在过滤器下拉列表中显示的标题

    parameter_name = 'page_size'  # URL参数名称

    def lookups(self, request, model_admin):
        # 返回一个包含元组的列表，每个元组包含两个值：
        # - 过滤器值，将作为URL参数值传递
        # - 在过滤器下拉列表中显示的文本
        return (
            ('10', _('10')),
            ('20', _('20')),
            ('50', _('50')),
            ('100', _('100')),
        )

    def queryset(self, request, queryset):
        pass
        return queryset

class CustomModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        if 'page_size' in request.GET:
            # 获取用户选择的每页显示条数
            page_size = int(request.GET['page_size'])
            # 将每页显示条数存储到session中
            request.session['page_size'] = page_size
        else:
            # 如果用户没有选择任何值，则从session中获取上次选择的值
            page_size = request.session.get('page_size', 10)

        # 设置每页显示条数
        self.list_per_page = page_size

        return super().changelist_view(request, extra_context)






@admin.register(Job)
# class JobAdmin(admin.ModelAdmin):
class JobAdmin(ImportExportModelAdmin,ExportActionMixin,CustomModelAdmin):
    resource_class = JobResource

    list_display = ('id','job_name','file_compressed','has_file_type','status','author','from_object_pcb_factory','from_object_pcb_design','publish','create_time','tag_list')

    search_fields = ('=id','job_name',)
    list_filter = (HasFileTypeListFilter, 'status', 'author__username','from_object_pcb_factory','from_object_pcb_design','tags',PageSizeFilter)
    list_editable = ('file_compressed', )
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
        # print('request.user:',request.user)
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    # 批量导出，支持导出选定的记录
    def export_selected_objects(self, request, queryset):
        # 导出选定的记录
        selected_ids = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        selected_objects = self.get_queryset(request).filter(pk__in=selected_ids)

        # 创建导出的数据
        export_data = self.get_export_data(selected_objects)

        # 创建HTTP响应对象
        response = HttpResponse(content_type=self.get_export_content_type())
        response['Content-Disposition'] = self.get_export_filename()

        # 导出数据到HTTP响应对象
        self.write_export_data(response, export_data)

        # 返回HTTP响应
        return response

    # export_selected_objects.short_description = _('Export selected objects')
    #
    # actions = [export_selected_objects]



















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