from django import forms
from .models import JobForTest


class JobForTestFormsReadOnly(forms.ModelForm):
    """
    Meta : 该类是必须继承的,但是该字段是
    model :对应的模型类
    fields : 当为‘__all__就是验证全部字段’,当只想验证其中部分的字段的时候，需要使用[]包裹起来
    """
    class Meta:
        model = JobForTest
        # fields = ['job_name','remark','slug','author','publish','status']
        # fields = ['job_name',]
        fields = '__all__'


        def __init__(self, *args, **kwargs):
            super(JobForTestFormsReadOnly, self).__init__(*args, **kwargs)
            for name, field in self.fields.iteritems():
                field.widget.attrs['readonly'] = 'true'