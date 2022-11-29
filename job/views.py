from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.views.generic import ListView
from .models import Job

# Create your views here.
class JobListView(ListView):
    queryset = Job.objects.all()
    # model=models.Job
    context_object_name = 'jobs'
    paginate_by = 10
    # ordering = ['-publish']
    template_name = 'JobListView.html'

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        left_has_more = False

        right_has_more = False
        current_page = page_obj.number
        if current_page <= around_count + 2:
            left_range = range(1, current_page)
        else:
            left_has_more = True
            left_range = range(current_page - around_count, current_page)

        if current_page >= paginator.num_pages - around_count - 1:
            right_range = range(current_page + 1, paginator.num_pages + 1)
        else:
            right_has_more = True
            right_range = range(current_page + 1, current_page + around_count + 1)

        pagination_data = {
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'left_range': left_range,
            'right_range': right_range
        }
        return pagination_data

    def get_context_data(self, **kwargs):  # 重写get_context_data方法
        # 很关键，必须把原方法的结果拿到
        context = super().get_context_data(**kwargs)
        context['job_field_verbose_name'] = [Job._meta.get_field('id').verbose_name,
                                  Job._meta.get_field('job_name').verbose_name,
                                  Job._meta.get_field('file_compressed').verbose_name,
                                  '层别信息',

                                  Job._meta.get_field('remark').verbose_name,
                                  Job._meta.get_field('author').verbose_name,
                                  # Job._meta.get_field('from_object').verbose_name,
                                  Job._meta.get_field('status').verbose_name,
                                  Job._meta.get_field('updated').verbose_name,
                                  "标签",
                                  "操作",
                                  ]

        # 分页
        print(context)
        page = self.request.GET.get('page')
        paginator = Paginator(context['jobs'], 3)  # 每页显示3篇文章
        # paginator=context.get('paginator')#不能用这个paginator,因为这个是所有的jobs的。而我们需要的是筛选过的jobs。
        try:
            context['jobs_page'] = paginator.page(page)
        except PageNotAnInteger:
            # 如果page参数不是一个整数就返回第一页
            context['jobs_page'] = paginator.page(1)
        except EmptyPage:
            # 如果页数超出总页数就返回最后一页
            context['jobs_page'] = paginator.page(paginator.num_pages)
        pagination_data = self.get_pagination_data(paginator, context['jobs_page'])
        context.update(pagination_data)






        return context



