import os

from import_export import resources,fields
from .models import JobForTest
from django.core.files import File

class JobForTestResource(resources.ModelResource):
    file = fields.Field(attribute='file', column_name='file')
    standard_odb = fields.Field(attribute='standard_odb', column_name='standard_odb')

    def __init__(self):
        super().__init__()
        self.file_object = None
        self.standard_odb_object = None
        self.is_preview = True

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.is_preview = dry_run  # 标记当前是否为预览模式



    def before_import_row(self, row, **kwargs):
        if not self.is_preview:  # 只在确认导入时执行附件上传逻辑,即非预览时才上传附件
            # file_path = row.get('file')
            file_path = os.path.join(r'C:\cc\share\upload', row.get('file')).replace("\\", "/")
            print('file_path:', file_path)
            if file_path:
                self.file_object = open(file_path, 'rb')
                file_name = file_path.split('/')[-1]
                django_file = File(self.file_object, name=file_name)
                row['file'] = django_file
            else:
                row['file'] = None

            # standard_odb_path = row.get('standard_odb')
            standard_odb_path = os.path.join(r'C:\cc\share\upload', row.get('standard_odb')).replace("\\", "/")
            print('standard_odb_path:', standard_odb_path)
            if standard_odb_path:
                self.standard_odb_object = open(standard_odb_path, 'rb')
                standard_odb_path_name = standard_odb_path.split('/')[-1]
                django_standard_odb = File(self.standard_odb_object, name=standard_odb_path_name)
                row['standard_odb'] = django_standard_odb
            else:
                row['standard_odb'] = None


    def after_import_row(self, row, row_result, **kwargs):
        # 清理导入后的文件对象，避免文件积累
        if self.file_object and not self.file_object.closed:
            self.file_object.close()

        if self.standard_odb_object and not self.standard_odb_object.closed:
            self.standard_odb_object.close()

        if self.is_preview:  # 如果是预览模式，清除文件字段
            row['file'] = None
            row['standard_odb'] = None

    class Meta:
        model = JobForTest
        # fields = ('job_name', 'file_compressed',)