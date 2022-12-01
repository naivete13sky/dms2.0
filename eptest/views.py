from django.shortcuts import render
from .models import EpcamModule
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .forms import JobForTestFormsReadOnly,JobForTestForm
from .models import JobForTest,MyTagForEptest
from account.models import QueryData, Customer
from job.models import Job

def show_genres(request):
    return render(request, "EpcamModule.html", {'epcam_module': EpcamModule.objects.all()})


class JobForTestListView(ListView):
    queryset = JobForTest.objects.all()
    context_object_name = 'jobfortest'
    paginate_by = 5
    template_name = 'JobForTestListView.html'

    def get_context_data(self, **kwargs):  # 重写get_context_data方法
        # 很关键，必须把原方法的结果拿到
        context = super().get_context_data(**kwargs)
        context['job_field_verbose_name'] = [JobForTest._meta.get_field('id').verbose_name,
                                             JobForTest._meta.get_field('job_parent').verbose_name,
                                             JobForTest._meta.get_field('job_name').verbose_name,
                                             JobForTest._meta.get_field('file').verbose_name,
                                             JobForTest._meta.get_field('file_type').verbose_name,
                                             JobForTest._meta.get_field('test_usage_for_epcam_module').verbose_name,
                                             JobForTest._meta.get_field('standard_odb').verbose_name,
                                             JobForTest._meta.get_field('vs_result_ep').verbose_name,
                                             JobForTest._meta.get_field('vs_result_g').verbose_name,
                                             JobForTest._meta.get_field('bug_info').verbose_name,
                                             JobForTest._meta.get_field('bool_layer_info').verbose_name,
                                             # JobForTest._meta.get_field('vs_time_ep').verbose_name,
                                             # JobForTest._meta.get_field('vs_time_g').verbose_name,
                                             JobForTest._meta.get_field('status').verbose_name,
                                             JobForTest._meta.get_field('updated').verbose_name,
                                             JobForTest._meta.get_field('author').verbose_name,
                                             JobForTest._meta.get_field('remark').verbose_name,
                                             "标签",
                                             "操作",
                                             ]



        # 使用分类筛选
        context['select_file_usage_type'] = [('all', '所有'), ('input_test', '导入测试'), ('customer_job', '客户资料'),
                                             ('test', '测试'), ('else', '其它')]
        context['select_author'] = [('all', '所有'), ('mine', '我的'), ]
        context['select_status'] = [('all', '所有'), ('draft', '草稿'), ('published', '正式'), ]
        context['select_page'] = [('5', '5'), ('10', '10'), ('20', '20'), ('50', '50'), ('100', '100'),
                                  ('200', '200'), ]

        # print("len of objects-no filter:", len(context['jobfortest']))


        # 加载当前用户的筛选条件
        try:
            current_query_data = QueryData.objects.get(author=self.request.user)
            # print(current_query_data)
        except:
            print("此用户无QueryData信息，此时要新建一下")
            new_query_data = QueryData(author=self.request.user)
            new_query_data.save()
        current_query_data = QueryData.objects.get(author=self.request.user)
        print("current_query_data:",current_query_data)


        #<------------------------------开始：默认根据历史值筛选---------------------------------------------------------->
        # 料号名称筛选
        context['query_job_job_name'] = current_query_data.query_job_job_name
        if context['query_job_job_name'] == None:
            context['query_job_job_name'] = ""
            current_query_data.query_job_job_name=""
            current_query_data.save()
        context['jobfortest']= JobForTest.objects.filter(job_name__contains = context['query_job_job_name'])
        print("len of objects-filter by job:", len(context['jobfortest']))

        # 料号负责人筛选
        if current_query_data.query_job_author == None:
            context['query_job_author'] = ''
        else:
            context['query_job_author'] = current_query_data.query_job_author
        print("context['query_job_author']:",context['query_job_author'])
        # 先把本次筛选条件存储起来
        context['jobfortest'] = context['jobfortest'].filter(author__username__contains=context['query_job_author'])
        # print("len of objects1:", len(context['jobfortest']))

        # 料号来源-板厂
        # context['query_job_from_object_pcb_factory'] = current_query_data.query_job_from_object_pcb_factory
        # if context['query_job_from_object_pcb_factory'] == None:
        #     context['query_job_from_object_pcb_factory'] = ""
        #     current_query_data.query_job_from_object_pcb_factory = ""
        #     current_query_data.save()
        # if context['query_job_from_object_pcb_factory'] != "":
        #     context['jobs'] = context['jobs'].filter(
        #         from_object_pcb_factory__name_simple__contains=context['query_job_from_object_pcb_factory'])

        # 料号状态
        context['query_job_status'] = current_query_data.query_job_status
        # print("query_job_file_usage_type:",context['query_job_file_usage_type'])
        if context['query_job_status'] == 'all':
            pass
        if context['query_job_status'] == 'draft':
            context['jobfortest'] = context['jobfortest'].filter(status="draft")
        if context['query_job_status'] == 'published':
            context['jobfortest'] = context['jobfortest'].filter(status="published")

        # 每页显示行数
        context['query_job_paginator_page'] = current_query_data.query_job_paginator_page

        # <------------------------------结束：默认根据历史值筛选---------------------------------------------------------->


        # <-----------------------------------开始：get方法筛选---------------------------------------------------------->
        # get方式query数据
        submit_query_get = self.request.GET.get('submit_query_get', False)
        if submit_query_get:
            # 料号名称筛选
            query_job_name = self.request.GET.get('query_job_name', False)
            context['query_job_job_name'] = query_job_name
            # 先把本次筛选条件存储起来
            if query_job_name != None:
                current_query_data.query_job_job_name = query_job_name
                current_query_data.save()
            context['jobfortest'] = JobForTest.objects.filter(job_name__contains=context['query_job_job_name'])

            # 料号负责人筛选
            query_job_author = self.request.GET.get('query_job_author', False)
            context['query_job_author'] = query_job_author
            # 先把本次筛选条件存储起来
            if query_job_author != None:
                current_query_data.query_job_author = query_job_author
                current_query_data.save()
            context['jobfortest'] = context['jobfortest'].filter(author__username__contains = query_job_author)

            # # 料号来源-板厂筛选
            # query_job_from_object_pcb_factory = self.request.GET.get("query_job_from_object_pcb_factory", False)
            # context['query_job_from_object_pcb_factory'] = query_job_from_object_pcb_factory
            # # 先把本次筛选条件存储起来
            # current_query_data = QueryData.objects.get(author=self.request.user)
            # if query_job_from_object_pcb_factory != None:
            #     current_query_data.query_job_from_object_pcb_factory = query_job_from_object_pcb_factory
            #     current_query_data.save()
            # if context['query_job_from_object_pcb_factory'] != "":
            #     context['jobs'] = context['jobs'].filter(
            #         from_object_pcb_factory__name_simple__contains=context['query_job_from_object_pcb_factory'])

            # 料号状态筛选
            query_job_status = self.request.GET.get("query_job_status", False)
            context['query_job_status'] = query_job_status
            # 先把本次筛选条件存储起来
            current_query_data = QueryData.objects.get(author=self.request.user)
            if query_job_status:
                current_query_data.query_job_status = query_job_status
                current_query_data.save()

            if context['query_job_status'] == 'all':
                pass
            if context['query_job_status'] == 'draft':
                context['jobfortest'] = context['jobfortest'].filter(status="draft")
            if context['query_job_status'] == 'published':
                context['jobfortest'] = context['jobfortest'].filter(status="published")



            #每页显示行数
            query_job_paginator_page = self.request.GET.get('query_job_paginator_page', False)
            context['query_job_paginator_page'] = query_job_paginator_page
            # 把每页显示多少行存储起来
            if query_job_paginator_page != None:
                current_query_data.query_job_paginator_page = query_job_paginator_page
                current_query_data.save()
        # <-----------------------------------结束：get方法筛选---------------------------------------------------------->


        # <--------------------------------------开始：tag筛选---------------------------------------------------------->
        tag_slug = self.kwargs.get('tag_slug', None)
        if tag_slug:
            print("tag_slug:", tag_slug)
            # 从MyTag对应的数据库表里查询tag
            tag = get_object_or_404(MyTagForEptest, slug=tag_slug)
            context['jobfortest'] = context['jobfortest'].filter(tags__in=[tag])
        # <--------------------------------------结束：tag筛选---------------------------------------------------------->


        # <--------------------------------------开始：根据料号ID精准搜索-------------------------------------------------->
        search_by_job_id = self.request.GET.get('search_by_job_id', False)
        if search_by_job_id:
            print("search_by_job_id:", search_by_job_id)
            context['jobfortest'] = JobForTest.objects.filter(Q(id=search_by_job_id))
        # <--------------------------------------结束：根据料号ID精准搜索-------------------------------------------------->



        # 料号很多时，要多页显示，但是在修改非首页内容时，比如修改某个料号，这个料号在第3页，如果不记住页数，修改完成后只能重定向到固定页。
        # 为了能记住当前页，用了下面的方法。
        if self.request.GET.__contains__("page"):
            current_page = self.request.GET["page"]
            print("current_page", current_page)
            context['current_page'] = current_page
        else:
            context['current_page'] = 1



        print("len of objects:",len(context['jobfortest']))

        # <-----------------------------------------------开始：分页----------------------------------------------------->
        page = self.request.GET.get('page')
        paginator = Paginator(context['jobfortest'], context['query_job_paginator_page'])  # 每页显示3篇文章
        print("page:::", page)
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
        # <-----------------------------------------------结束：分页----------------------------------------------------->


        return context

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


    def post(self, request):  # ***** this method required! ******
        self.object_list = self.get_queryset()
        if request.method == 'POST':
            print("POST!!!")

            #分页跳转用
            if request.POST.__contains__("page_jump"):
                print(request.POST.get("page_jump"))
                return HttpResponse(request.POST.get("page_jump"))


class JobForTestDetailViewForm(DetailView):
    model = JobForTest
    template_name = "JobForTestDetailViewForm.html"
    context_object_name = "job_for_test"
    pk_url_kwarg = "pk"  # pk_url_kwarg默认值就是pk，这里可以覆盖，但必须和url中的命名组参数名称一致


    def get_form(self):
        self.pk = self.kwargs['pk']
        # print("pk:",pk)
        job = JobForTest.objects.filter(id=self.pk).first()
        return JobForTestFormsReadOnly(instance=job)

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['form'] = self.get_form()
        context['job_id'] = self.pk
        return context


class JobForTestUpdateView(UpdateView):
    """
    该类必须要有一个pk或者slug来查询（会调用self.object = self.get_object()）
    """
    model = JobForTest
    fields = "__all__"
    template_name = 'JobForTestUpdateView.html'

    def get(self, request, *args, **kwargs):

        job_update = JobForTest.objects.get(id=self.kwargs['pk'])
        form=JobForTestForm(instance=job_update)
        self.job_id = job_update.id
        print("ccabc:", len(Job.objects.filter(id=job_update.job_parent_id)))
        if len(Job.objects.filter(id=job_update.job_parent_id)):
            self.job_parent_id = Job.objects.filter(id = job_update.job_parent_id)[0].id
            self.job_parent = job_update.job_parent
        else:
            self.job_parent_id = None
            self.job_parent = None

        current_page = self.kwargs['current_page']
        print("current_page",current_page)
        return render(request, 'JobForTestUpdateView.html', {'form':form,'job_parent_id':self.job_parent_id,'job_parent':self.job_parent})

    def get_success_url(self):
        return '../../JobForTestListView?page={}'.format(self.kwargs['current_page'])


class JobForTestCreateView(CreateView):
    model=JobForTest
    template_name = "JobForTestCreateView.html"
    fields = "__all__"
    #设置新增料号时，自动填写上当前用户
    def get_initial(self):
        # Get the initial dictionary from the superclass method
        initial = super(JobForTestCreateView, self).get_initial()
        # Copy the dictionary so we don't accidentally change a mutable dict
        initial = initial.copy()
        initial['author'] = self.request.user
        return initial
    success_url = 'JobForTestListView'



    def get_context_data(self, **kwargs):
        context = super(JobForTestCreateView, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            pass

        else:
            pass

        #暂时用不着下面的方法
        # context['get_customer_pcb_factory']=self.get_customer_pcb_factory()
        # context['get_customer_pcb_design'] = self.get_customer_pcb_design()

        return context


class JobForTestDeleteView(DeleteView):
  """
  """
  model = JobForTest
  template_name = 'JobForTestDeleteView.html'
  success_url = reverse_lazy('eptest:JobForTestListView')