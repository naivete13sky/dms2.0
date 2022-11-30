from django.contrib import admin
from .models import JobForTest,EpcamModule
from mptt.admin import MPTTModelAdmin

@admin.register(JobForTest)
class JobForTestAdmin(admin.ModelAdmin):
    list_display = ('job','file','test_usage_for_epcam_module','standard_odb','vs_result_ep','vs_result_g','bug_info','status','author','publish','create_time','tag_list','remark')
    list_filter = ('tags',)
    search_fields = ('job','author__username','vs_result_ep','vs_result_g',)
    prepopulated_fields = {'remark': ('job',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return ",".join(o.name for o in obj.tags.all())




class EpcamModuleAdmin(MPTTModelAdmin):
    list_display = ('name','lft','rght','tree_id','level','parent_id',)
    search_fields = ('name',)
    list_per_page = 20
    # specify pixel amount for this ModelAdmin only:
    # default is 10 pixels
    mptt_level_indent = 20
admin.site.register(EpcamModule, EpcamModuleAdmin)


