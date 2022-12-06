import os
import shutil
import time

import rarfile
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse

from cc.cc_method import CCMethod
from .models import JobForTest,EpcamModule,Layer,Bug,Vs
from mptt.admin import MPTTModelAdmin
from django.utils.safestring import mark_safe


# 更改管理后台名称
admin.site.site_header = '料号管理系统'
admin.site.site_title = '料号管理系统'
# admin.site.index_title = '3'



@admin.register(JobForTest)
class JobForTestAdmin(admin.ModelAdmin):
    list_display = ('id','job_parent_link','job_name','get_layer_info_link','file','file_type','test_usage_for_epcam_module','get_standard_odb_link','vs_result_ep','get_vs_info_g_link','bug_info','status','author','updated','tag_list','remark')
    list_filter = ('tags','file_type','author','test_usage_for_epcam_module',)
    search_fields = ('id','job_parent__job_name','job_name','author__username','vs_result_ep','vs_result_g',)
    prepopulated_fields = {'remark': ('job_name',)}
    raw_id_fields = ('author','job_parent',)
    # date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10
    list_display_links = ('job_name',)

    exclude = ('author', 'publish')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
    def tag_list(self, obj):
        return ",".join(o.name for o in obj.tags.all())


    def job_parent_link(self, obj):
        return mark_safe(f'<a href="../../job/job/{obj.job_parent_id}/change/">{obj.job_parent} </a>')
    job_parent_link.short_description = '父料号'

    def get_layer_info_link(self, obj):
        if obj.bool_layer_info == 'true':
            return mark_safe(f'<a href="../../../../eptest/layer/?q=one_job_layer/{obj.id}/">查看</a>')
        else:
            return mark_safe(f'<a href="../../../../eptest/get_layer_name_from_org/{obj.id}/">生成</a>')
    get_layer_info_link.short_description = '层别'


    def get_vs_info_g_link(self, obj):
        if obj.vs_result_g == 'passed':
            return mark_safe(f'<a href="../../../../eptest/view_vs_g/{obj.id}/">通过</a>')
        elif obj.vs_result_g == 'failed':
            return mark_safe(f'<a href="../../../../eptest/view_vs_g/{obj.id}/">失败</a>')
        else:
            return mark_safe(f'<a href="../../../../eptest/view_vs_g/{obj.id}/">未比对</a>')
    get_vs_info_g_link.short_description = 'G软件VS详情'


    '''保存时自动设置author为当前登录用户'''
    def save_model(self, request, obj, form, change):
        # If creating new article, associate request.user with author.
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_test_file_link(self, obj):
        if obj.file:
            return mark_safe(f'<a href="../../../../media/{obj.file}" title=" {obj.file} ">下载</a>')
    get_test_file_link.short_description = '测试料号'

    def get_standard_odb_link(self, obj):
        if obj.standard_odb:
            return mark_safe(f'<a href="../../../../media/{obj.standard_odb}" title=" {obj.standard_odb} ">下载</a>')
    get_standard_odb_link.short_description = '标准料号'




class EpcamModuleAdmin(MPTTModelAdmin):
    list_display = ('name','lft','rght','tree_id','level','parent_id',)
    search_fields = ('name',)
    list_per_page = 20
    # specify pixel amount for this ModelAdmin only:
    # default is 10 pixels
    mptt_level_indent = 20
admin.site.register(EpcamModule, EpcamModuleAdmin)


@admin.register(Layer)
class LayerAdmin(admin.ModelAdmin):
    list_display = ('id','job_link','job','layer','layer_org','vs_result_manual','vs_result_ep','vs_result_g','layer_file_type','layer_type','units','zeroes_omitted',
                    'number_format_A','number_format_B','tool_units_ep','tool_units_g',)

    list_display_links = ('layer',)
    list_filter = ( 'layer_file_type','layer_type',)
    search_fields = ('id','job__job_name','layer',)
    prepopulated_fields = {'remark': ('layer',)}
    # ordering = ('recipe_status', 'receive_date',)

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
        print("queryset:",queryset)
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
class BugAdmin(admin.ModelAdmin):
    list_display = ('job','bug','bug_zentao_id','bug_zentao_pri','bug_zentao_status','bug_creator','bug_create_date','bug_assigned_to',
                    'author','status','refresh_time','remark','create_time','updated',)

    search_fields = ('job','bug','bug_zentao_pri','status')
    prepopulated_fields = {'remark': ('bug',)}
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10


@admin.register(Vs)
class VsAdmin(admin.ModelAdmin):
    list_display = ('job','layer','layer_org','vs_result','vs_result_detail','vs_method','layer_file_type','layer_type',)

    search_fields = ('job','layer','layer_file_type','layer_type')
    prepopulated_fields = {'remark': ('layer',)}
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10