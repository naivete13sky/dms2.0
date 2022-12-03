from django.contrib import admin
from .models import Job,JobInfoForDevTest


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_name','file_compressed','has_file_type','status','author','from_object_pcb_factory','from_object_pcb_design','publish','create_time','tags')

    search_fields = ('job_name',)
    list_filter = ('has_file_type', 'status', 'author','from_object_pcb_factory','from_object_pcb_design','tags')
    prepopulated_fields = {'remark': ('job_name',)}
    raw_id_fields = ('author','from_object_pcb_factory','from_object_pcb_design')
    date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10


@admin.register(JobInfoForDevTest)
class JobInfoForDevTestAdmin(admin.ModelAdmin):
    list_display = ('job','status','author','file_odb','has_step_multi','job_type_1','job_type_2','job_type_3','publish','updated','remark')

    search_fields = ('job','status','author','has_step_multi',)
    list_filter = ('job', 'status', 'author',  'job_type_1', 'job_type_2', 'job_type_3')
    prepopulated_fields = {'remark': ('job',)}
    raw_id_fields = ('author','job')
    date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10