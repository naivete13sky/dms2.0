from import_export import resources
from .models import Job

class JobResource(resources.ModelResource):

    class Meta:
        model = Job
        fields = ('job_name', 'file_compressed',)