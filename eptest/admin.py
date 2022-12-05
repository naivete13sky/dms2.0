import os
import shutil
import time

import rarfile
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse

from cc.cc_method import CCMethod
from .models import JobForTest,EpcamModule,Layer,Bug
from mptt.admin import MPTTModelAdmin
from django.utils.safestring import mark_safe


# 更改管理后台名称
admin.site.site_header = '料号管理系统'
admin.site.site_title = '料号管理系统'
# admin.site.index_title = '3'



@admin.register(JobForTest)
class JobForTestAdmin(admin.ModelAdmin):
    list_display = ('id','job_parent_link','job_name','get_layer_info_link','file','file_type','test_usage_for_epcam_module','standard_odb','vs_result_ep','vs_result_g','bug_info','status','author','publish','create_time','tag_list','remark')
    list_filter = ('tags','file_type','author','test_usage_for_epcam_module',)
    search_fields = ('id','job_parent__job_name','job_name','author__username','vs_result_ep','vs_result_g',)
    prepopulated_fields = {'remark': ('job_name',)}
    raw_id_fields = ('author','job_parent',)
    # date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10
    list_display_links = ('job_name',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return ",".join(o.name for o in obj.tags.all())

    def job_parent_link(self, obj):
        return mark_safe(f'<a href="../../job/job/{obj.job_parent_id}/change/">{obj.job_parent} </a>')
    job_parent_link.short_description = '父料号'

    def get_layer_info_link(self, obj):
        return mark_safe(f'<a href="../../../../eptest/get_layer_name_from_org/{obj.id}/">生成</a>')
    get_layer_info_link.short_description = '生成层别'



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



@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):
    list_display = ('job','bug','bug_zentao_id','bug_zentao_pri','bug_zentao_status','bug_creator','bug_create_date','bug_assigned_to',
                    'author','status','refresh_time','remark','create_time','updated',)

    search_fields = ('job','bug','bug_zentao_pri','status')
    prepopulated_fields = {'remark': ('bug',)}
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10