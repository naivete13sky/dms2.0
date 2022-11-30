from django.contrib import admin
from .models import JobForTest,EpcamModule
from mptt.admin import MPTTModelAdmin

@admin.register(JobForTest)
class JobForTestAdmin(admin.ModelAdmin):
    list_display = ('job','file','test_usage_for_epcam_module','standard_odb','vs_result_ep','vs_result_g','bug_info','status','author','publish','create_time','tags','remark')

    search_fields = ('job','author__username','vs_result_ep','vs_result_g','tags',)
    prepopulated_fields = {'remark': ('job',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10


class EpcamModuleAdmin(MPTTModelAdmin):
    list_display = ('name','lft','rght','tree_id','level','parent_id',)
    search_fields = ('name',)
    list_per_page = 20
    # specify pixel amount for this ModelAdmin only:
    # default is 10 pixels
    mptt_level_indent = 20
admin.site.register(EpcamModule, EpcamModuleAdmin)


