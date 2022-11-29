from django.contrib import admin
from .models import Job

# Register your models here.
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('job_name','file_compressed','status','author','from_object_pcb_factory','from_object_pcb_design','publish','create_time','tags')

    search_fields = ('job_name','author__username','from_object',)
    prepopulated_fields = {'remark': ('job_name',)}
    raw_id_fields = ('author','from_object_pcb_factory','from_object_pcb_design')
    date_hierarchy = 'publish'
    # ordering = ('recipe_status', 'receive_date',)
    list_per_page = 10