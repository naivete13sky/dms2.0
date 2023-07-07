from import_export import resources,fields
from .models import Job
from import_export.widgets import ForeignKeyWidget
from django.core.files import File


class JobResource(resources.ModelResource):
    file_compressed = fields.Field(attribute='file_compressed', column_name='file_compressed')

    def __init__(self):
        super().__init__()
        self.file_object = None
        self.is_preview = True

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.is_preview = dry_run  # 标记当前是否为预览模式

    class Meta:
        model = Job
        # fields = ('job_name', 'file_compressed',)

    def before_import_row(self, row, **kwargs):
        if not self.is_preview:  # 只在确认导入时执行附件上传逻辑,即非预览时才上传附件
            file_path = row.get('file_compressed')
            print('file_path:', file_path)


            if file_path:
                self.file_object = open(file_path, 'rb')
                file_name = file_path.split('/')[-1]
                django_file = File(self.file_object, name=file_name)
                row['file_compressed'] = django_file
            else:
                row['file_compressed'] = None



    def after_import_row(self, row, row_result, **kwargs):
        # 清理导入后的文件对象，避免文件积累
        if self.file_object and not self.file_object.closed:
            self.file_object.close()

        if self.is_preview:  # 如果是预览模式，清除文件字段
            row['file_compressed'] = None