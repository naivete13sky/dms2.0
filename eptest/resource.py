from import_export import resources
from .models import JobForTest

class JobForTestResource(resources.ModelResource):

    class Meta:
        model = JobForTest
        # fields = ('job_name', 'file_compressed',)