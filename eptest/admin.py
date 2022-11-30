from django.contrib import admin
from .models import JobForTest,EpcamModule
from mptt.admin import MPTTModelAdmin

@admin.register(JobForTest)
class JobForTestAdmin(admin.ModelAdmin):
    list_display = ('job','file','test_usage_for_epcam_module','status','author','publish','create_time','tags','remark')

    search_fields = ('job','author__username','tags',)
    prepopulated_fields = {'remark': ('job',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10

# @admin.register(EpcamModule)
# class EpcamModuleAdmin(admin.ModelAdmin):
#     list_display = ('name','lft','rght','tree_id','level','parent_id',)
#     search_fields = ('name',)
#     list_per_page = 10


# admin.site.register(EpcamModule,MPTTModelAdmin)


class EpcamModuleAdmin(MPTTModelAdmin):
    list_display = ('name','lft','rght','tree_id','level','parent_id',)
    search_fields = ('name',)
    list_per_page = 10
admin.site.register(EpcamModule, EpcamModuleAdmin)
