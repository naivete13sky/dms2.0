from django.contrib import admin
from .models import Job,JobInfoForDevTest


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id','job_name','file_compressed','has_file_type','status','author','from_object_pcb_factory','from_object_pcb_design','publish','create_time','tag_list')

    search_fields = ('=id','job_name',)
    list_filter = ('has_file_type', 'status', 'author__username','from_object_pcb_factory','from_object_pcb_design','tags')
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
    exclude = ('author', 'publish')

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