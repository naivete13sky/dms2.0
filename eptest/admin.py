import os
import shutil
import time

import rarfile
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.views.main import ChangeList
from django.core.paginator import Paginator
from django.http import HttpResponse

from cc.cc_method import CCMethod
from .models import JobForTest,EpcamModule,Layer,Bug,Vs
from mptt.admin import MPTTModelAdmin
from django.utils.safestring import mark_safe
from sqlalchemy import create_engine
import pandas as pd
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from django.utils.translation import gettext_lazy as _
from .resource import JobForTestResource

# 更改管理后台名称
admin.site.site_header = '料号管理系统'
admin.site.site_title = '料号管理系统'
# admin.site.index_title = '3'
from eptest.GL import GL

#为了实现在admin后台可页面上设置每页显示条数，通过下面方法，要创建一个过滤器PageSizeFilter。
#还要创建一个CustomModelAdmin类，这个类实现changelist_view方法。因为在过滤器PageSizeFilter无法重写changelist_view，所以要写此类实现类似效果。
class PageSizeFilter(admin.SimpleListFilter):
    title = _('每页显示条数')  # 在过滤器下拉列表中显示的标题

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





@admin.register(JobForTest)
# class JobForTestAdmin(admin.ModelAdmin):
class JobForTestAdmin(ImportExportModelAdmin,ExportActionMixin,CustomModelAdmin):
    resource_class = JobForTestResource

    # list_display = ('id','job_parent_link','job_name','get_layer_info_link','file','get_test_file_link','file_type','test_usage_for_epcam_module','standard_odb','get_standard_odb_link','vs_result_ep','get_vs_info_g_link','get_bug_info_link','status','author','updated','tag_list','remark',)
    list_display = (
    'id', 'job_parent_link', 'job_name', 'get_layer_info_link', 'file',  'file_type',
    'test_usage_for_epcam_module', 'standard_odb', 'vs_result_ep', 'get_vs_info_g_link',
    'get_bug_info_link', 'status', 'author', 'updated', 'tag_list', 'remark',)
    list_filter = ('tags','file_type','status','author','test_usage_for_epcam_module',PageSizeFilter)
    search_fields = ('job_name','author__username','vs_result_ep','vs_result_g',)
    prepopulated_fields = {'remark': ('job_name',)}
    raw_id_fields = ('author','job_parent',)
    # date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10
    list_display_links = ('job_name',)
    list_editable = ('file','standard_odb','test_usage_for_epcam_module',)
    # exclude = ('author', 'publish')
    exclude = ('publish',)
    # change_list_template = r'admin/eptest/JobForTest/change_list.html'

    app_id = None#本类中的全局变量



    # <editor-fold desc="处理tag,使得admin中可以显示正常的tag">
    def get_queryset(self, request):
        # 为了实现单个料号ID搜索，需要把ID传给实例。此处通过GL.py实现了全局变量传递。
        self.query = request.GET.get('search_by_app_id', False)
        # 如果查询的ID空，就返回所有。
        if self.query == "":
            print("空空空！")
            # GL.app_id = None
            self.app_id = None
        # 如果查询的ID不为空。
        if self.query:
            # GL.app_id = self.query
            self.app_id = self.query
        return super().get_queryset(request).prefetch_related('tags')
    def tag_list(self, obj):
        return ",".join(o.name for o in obj.tags.all())
    # </editor-fold>






    # <editor-fold desc="返回父料号">
    def job_parent_link(self, obj):
        return mark_safe(f'<a href="../../job/job/{obj.job_parent_id}/change/">{obj.job_parent} </a>')
    job_parent_link.short_description = '父料号'
    # </editor-fold>

    # <editor-fold desc="层别">
    def get_layer_info_link(self, obj):
        if obj.bool_layer_info == 'true':
            return mark_safe(f'<a href="../../../../admin/eptest/layer/?q=one_job_layer/{obj.id}/">查看</a>'
                             f'&nbsp; |&nbsp; '
                             f'<a href="../../../../eptest/get_layer_name_from_org/{obj.id}/">生成</a>')
        else:
            if obj.file:
                return mark_safe(f'<a href="../../../../eptest/get_layer_name_from_org/{obj.id}/">生成</a>')
            else:
                return mark_safe(f'-')
    get_layer_info_link.short_description = '层别'
    # </editor-fold>

    # <editor-fold desc="G软件VS详情">
    def get_vs_info_g_link(self, obj):
        if obj.vs_result_g == 'passed':
            return mark_safe(f'<a href="../../../../eptest/view_vs_g/{obj.id}/">通过</a>'
                             f'&nbsp; |&nbsp; '
                             f'<a href="epdms://{obj.id}">点击比对</a>'
                             )
        elif obj.vs_result_g == 'failed':
            return mark_safe(f'<a href="../../../../eptest/view_vs_g/{obj.id}/">失败</a>'
                             f'&nbsp; |&nbsp; '
                             f'<a href="epdms://{obj.id}">点击比对</a>'
                             )
        else:
            return mark_safe(f'<a href="../../../../eptest/view_vs_g/{obj.id}/">未比对</a>'
                             f'&nbsp; |&nbsp; '
                             f'<a href="epdms://{obj.id}">点击比对</a>'
                             )


    get_vs_info_g_link.short_description = 'G软件VS详情'
    # </editor-fold>

    # <editor-fold desc="保存时自动设置author为当前登录用户">
    def save_model(self, request, obj, form, change):
        # If creating new article, associate request.user with author.
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    # </editor-fold>

    # <editor-fold desc="测试料号">
    def get_test_file_link(self, obj):
        if obj.file:
            return mark_safe(f'<a href="../../../../media/{obj.file}" title=" {obj.file} ">下载</a>')
    get_test_file_link.short_description = '测试料号'
    # </editor-fold>

    # <editor-fold desc="标准料号">
    def get_standard_odb_link(self, obj):
        if obj.standard_odb:
            return mark_safe(f'<a href="../../../../media/{obj.standard_odb}" title=" {obj.standard_odb} ">下载</a>')
    get_standard_odb_link.short_description = '标准料号'
    # </editor-fold>

    # <editor-fold desc="bug">
    def get_bug_info_link(self, obj):
        return mark_safe(f'<a href="../../../../admin/eptest/bug/?q=one_job_bug/{obj.id}/">查看</a>')
    get_bug_info_link.short_description = 'Bug'
    # </editor-fold>

    # <editor-fold desc="actions,暂时没用">
    # # 增加自定义按钮
    # actions = ['make_copy', 'custom_button','message_test','custom_button_link']
    # def custom_button(self,request,queryset):
    #     pass
    # # 显示的文本，与django admin一致
    # custom_button.short_description = '测试2'
    # # icon，参考element-ui icon与https://fontawesome.com
    # custom_button.icon = 'fas fa-audio-description'
    # # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    # custom_button.type = 'danger'
    # # 给按钮追加自定义的颜色
    # custom_button.style = 'color:black;'
    # # 给按钮增加确认
    # custom_button.confirm = '你是否执意要点击这个按钮？'
    #
    # def make_copy(self,request,queryset):
    #     pass
    # make_copy.short_description = '测试1'
    #
    # def message_test(self, request, queryset):
    #     messages.add_message(request, messages.SUCCESS, '操作成功123123123123')
    # # 给按钮增加确认
    # message_test.confirm = '你是否执意要点击这个按钮？'
    #
    # def custom_button_link(self, request, queryset):
    #     pass
    # # 显示的文本，与django admin一致
    # custom_button_link.short_description = '打开公司主页'
    # # icon，参考element-ui icon与https://fontawesome.com
    # custom_button_link.icon = 'fas fa-audio-description'
    # # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    # custom_button_link.type = 'danger'
    # # 给按钮追加自定义的颜色
    # custom_button_link.style = 'color:black;'
    # # 链接按钮，设置之后直接访问该链接
    # # 3中打开方式
    # # action_type 0=当前页内打开，1=新tab打开，2=浏览器tab打开
    # # 设置了action_type，不设置url，页面内将报错
    # # 设置成链接类型的按钮后，custom_button方法将不会执行。
    # custom_button_link.action_type = 0
    # custom_button_link.action_url = 'http://www.epsemicon.com'
    # </editor-fold>


    # <editor-fold desc="自定义查询,实现ID准确搜索">
    def get_search_results(self, request, queryset, search_term):
        # print("search_term:", search_term)
        # print("request:", request)

        # 单ID查询
        search_id = None

        queryset, use_distinct = super(JobForTestAdmin, self).get_search_results(request, queryset, search_term)


        # if GL.app_id:
        if self.app_id:
            try:
                # search_id = int(GL.app_id)
                search_id = int(self.app_id)
            except Exception as e:
                print("输入非常ID！",e)
            if search_id:
                queryset = self.model.objects.filter(id=search_id)
                return queryset, use_distinct
        return queryset, use_distinct
    # </editor-fold>

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




class EpcamModuleAdmin(MPTTModelAdmin):
    list_display = ('name','lft','rght','tree_id','level','parent_id',)
    search_fields = ('name',)
    # list_per_page = 20
    # specify pixel amount for this ModelAdmin only:
    # default is 10 pixels
    mptt_level_indent = 20
admin.site.register(EpcamModule, EpcamModuleAdmin)


@admin.register(Layer)
class LayerAdmin(CustomModelAdmin):
    list_display = ('id','job_link','job','layer','vs_result_manual','vs_result_ep','vs_result_g','layer_file_type','layer_type','units','coordinates','zeroes_omitted',
                    'number_format_A','number_format_B','tool_units_ep','tool_units_g','status','remark')

    list_display_links = ('layer',)
    list_filter = ( 'layer_file_type','layer_type',PageSizeFilter,)
    search_fields = ('id','job__job_name','layer',)
    prepopulated_fields = {'remark': ('layer',)}
    # ordering = ('recipe_status', 'receive_date',)

    list_editable = ('layer_file_type','layer_type','units','coordinates','zeroes_omitted',
                    'number_format_A','number_format_B','tool_units_ep','tool_units_g','status','remark')

    list_per_page = 10


    def job_link(self, obj):
        return mark_safe(f'<a href="../../eptest/jobfortest/{obj.job_id}/change/">打开</a>')
    job_link.short_description = '所属料号'

    # 默认的查询集合
    def get_queryset(self, request):
        return super(LayerAdmin, self).get_queryset(request).all().order_by("-id")

    # 根据关键字进行查询集合,自定义查询。如果搜索内容包括了“one_job_layer/123”,则说明是要查某个料号（ID：123）的层信息
    def get_search_results(self, request, queryset, search_term):
        print("search_term:", search_term)
        queryset, use_distinct = super(LayerAdmin, self).get_search_results(request, queryset, search_term)
        # print("queryset:",queryset)
        print("use_distinct:", use_distinct)
        if "one_job_layer/" in search_term:
            print("搜索指定料号下的layer信息")
            queryset = self.model.objects.filter(job=int(search_term.split("/")[1]))
            return queryset,use_distinct
        # try:
        #     search_term_as_int = int(search_term)
        #     print("search_term_as_int:",search_term_as_int)
        #     queryset &= (self.model.objects.filter(gift_rule_id=search_term_as_int) |
        #                  self.model.objects.filter(user_id=search_term_as_int) |
        #                  self.model.objects.filter(activity_id=search_term))
        # except:
        #     pass
        return queryset, use_distinct








@admin.register(Bug)
class BugAdmin(CustomModelAdmin):
    list_display = ('job','bug','bug_zentao_id','bug_zentao_pri','bug_zentao_status','bug_creator','bug_create_date','bug_assigned_to',
                    'author','status','refresh_time','remark','create_time','updated',)

    search_fields = ('job__id','bug','bug_zentao_pri','status')
    prepopulated_fields = {'remark': ('bug',)}
    # ordering = ('recipe_status', 'receive_date',)
    raw_id_fields = ('author', 'job',)
    list_per_page = 10

    # <editor-fold desc="根据料号ID精准查询此料号下的Bug信息用">
    # 默认的查询集合
    def get_queryset(self, request):
        return super(BugAdmin, self).get_queryset(request).all().order_by("-id")



    # 根据关键字进行查询集合,自定义查询。如果搜索内容包括了“one_job_bug/123”,则说明是要查某个料号（ID：123）的Bug信息
    def get_search_results(self, request, queryset, search_term):
        # print("search_term:", search_term)
        queryset, use_distinct = super(BugAdmin, self).get_search_results(request, queryset, search_term)
        # print("queryset:", queryset)
        # print("use_distinct:", use_distinct)
        if "one_job_bug/" in search_term:
            print("搜索指定料号下的bug信息")
            queryset = self.model.objects.filter(job__id=int(search_term.split("/")[1]))
            return queryset, use_distinct
        return queryset, use_distinct
    # </editor-fold>

    # <editor-fold desc="创建Bug时，只要填入Bug的ID，其它信息自动带过来">
    def save_model(self, request, obj, form, change):
        pass
        print("保存时做点啥")
        engine = create_engine("mysql+mysqlconnector://chencheng:hWx9pWk5d5J@10.97.80.36:3336/zentao")
        sql = '''SELECT a.* from zt_bug a where a.id={}
                '''.format(int(obj.bug_zentao_id))
        bug_pd = pd.read_sql_query(sql, engine)

        obj.bug = bug_pd['title'][0]
        obj.bug_zentao_pri = bug_pd['pri'][0]
        obj.bug_zentao_status = bug_pd['status'][0]
        obj.bug_creator = bug_pd['openedBy'][0]
        obj.bug_create_date = bug_pd['openedDate'][0]
        obj.bug_assigned_to = bug_pd['assignedTo'][0]
        obj.author = request.user
        obj.refresh_time = str(int(time.time()))

        super().save_model(request, obj, form, change)
    # </editor-fold>

    # <editor-fold desc="增加自定义按钮">
    actions = ['update_bug_info_button']

    def update_bug_info_button(self, request, queryset):
        engine = create_engine("mysql+mysqlconnector://chencheng:hWx9pWk5d5J@10.97.80.36:3336/zentao")
        from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        print('selected:',selected)


        if selected:
            for each in queryset:
                print(each.id)
                current_bug = Bug.objects.get(id=int(each.id))
                print('current_bug:',current_bug)
                print('current_bug_bug_zentao_id:', current_bug.bug_zentao_id)

                sql = '''SELECT a.* from zt_bug a where a.id={}
                                        '''.format(int(current_bug.bug_zentao_id))
                bug_pd = pd.read_sql_query(sql, engine)

                current_bug.bug = bug_pd['title'][0]
                current_bug.bug_zentao_pri = bug_pd['pri'][0]
                current_bug.bug_zentao_status = bug_pd['status'][0]
                current_bug.bug_creator = bug_pd['openedBy'][0]
                current_bug.bug_create_date = bug_pd['openedDate'][0]
                current_bug.bug_assigned_to = bug_pd['assignedTo'][0]
                current_bug.author = request.user
                current_bug.refresh_time = str(int(time.time()))

                current_bug.save()
        else:
            pass

    # 显示的文本，与django admin一致
    update_bug_info_button.short_description = '更新Bug信息'
    # icon，参考element-ui icon与https://fontawesome.com
    # custom_button.icon = 'fas fa-audio-description'
    update_bug_info_button.icon = 'fas fa-refresh'

    # 指定element-ui的按钮类型，参考https://element.eleme.cn/#/zh-CN/component/button
    # custom_button.type = 'danger'
    update_bug_info_button.type = 'primary'

    # 给按钮追加自定义的颜色
    update_bug_info_button.style = 'color:black;'
    # </editor-fold>

    # def changelist_view(self, request, extra_context=None):
    #
    #     self.list_per_page = 50
    #     return super().changelist_view(request, extra_context)

    list_filter = [PageSizeFilter]  # 注册自定义的Filter


@admin.register(Vs)
class VsAdmin(admin.ModelAdmin):
    list_display = ('job','layer','layer_org','vs_result','vs_result_detail','vs_method','layer_file_type','layer_type',)

    search_fields = ('job','layer','layer_file_type','layer_type')
    prepopulated_fields = {'remark': ('layer',)}
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10