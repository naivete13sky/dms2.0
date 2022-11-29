from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Job,MyTag
from account.models import QueryData


class JobListView(ListView):
    queryset = Job.objects.all()
    context_object_name = 'jobs'
    paginate_by = 5
    # ordering = ['-publish']
    template_name = 'JobListView2.html'

    def get_context_data(self, **kwargs):  # 重写get_context_data方法
        # 很关键，必须把原方法的结果拿到
        context = super().get_context_data(**kwargs)
        context['job_field_verbose_name'] = [Job._meta.get_field('id').verbose_name,
                                             Job._meta.get_field('job_name').verbose_name,
                                             Job._meta.get_field('file_compressed').verbose_name,
                                             Job._meta.get_field('from_object_pcb_factory').verbose_name,
                                             Job._meta.get_field('status').verbose_name,
                                             Job._meta.get_field('updated').verbose_name,
                                             Job._meta.get_field('author').verbose_name,
                                             Job._meta.get_field('remark').verbose_name,
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


        # 加载当前用户的筛选条件
        try:
            current_query_data = QueryData.objects.get(author=self.request.user)
            # print(current_query_data)
        except:
            print("此用户无QueryData信息，此时要新建一下")
            new_query_data = QueryData(author=self.request.user)
            new_query_data.save()
        current_query_data = QueryData.objects.get(author=self.request.user)



        #默认根据历史值筛选
        # 料号名称筛选
        context['query_job_job_name'] = current_query_data.query_job_job_name
        if context['query_job_job_name'] == None:
            context['query_job_job_name'] = ""
            current_query_data.query_job_job_name=""
            current_query_data.save()
        context['jobs']= Job.objects.filter(job_name__contains = context['query_job_job_name'])

        # 料号负责人筛选
        context['query_job_author'] = current_query_data.query_job_author
        # 先把本次筛选条件存储起来
        context['jobs'] = context['jobs'].filter(author__username__contains=context['query_job_author'])

        # 料号来源-板厂
        context['query_job_from_object_pcb_factory'] = current_query_data.query_job_from_object_pcb_factory
        if context['query_job_from_object_pcb_factory'] == None:
            context['query_job_from_object_pcb_factory'] = ""
            current_query_data.query_job_from_object_pcb_factory = ""
            current_query_data.save()
        if context['query_job_from_object_pcb_factory'] != "":
            context['jobs'] = context['jobs'].filter(
                from_object_pcb_factory__name_simple__contains=context['query_job_from_object_pcb_factory'])

        # 料号状态
        context['query_job_status'] = current_query_data.query_job_status
        # print("query_job_file_usage_type:",context['query_job_file_usage_type'])
        if context['query_job_status'] == 'all':
            pass
        if context['query_job_status'] == 'draft':
            context['jobs'] = context['jobs'].filter(status="draft")
        if context['query_job_status'] == 'published':
            context['jobs'] = context['jobs'].filter(status="published")

        # 每页显示行数
        context['query_job_paginator_page'] = current_query_data.query_job_paginator_page







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
            context['jobs'] = Job.objects.filter(job_name__contains=context['query_job_job_name'])

            # 料号负责人筛选
            query_job_author = self.request.GET.get('query_job_author', False)
            context['query_job_author'] = query_job_author
            # 先把本次筛选条件存储起来
            if query_job_author != None:
                current_query_data.query_job_author = query_job_author
                current_query_data.save()
            context['jobs'] = context['jobs'].filter(author__username__contains = query_job_author)

            # 料号来源-板厂筛选
            query_job_from_object_pcb_factory = self.request.GET.get("query_job_from_object_pcb_factory", False)
            context['query_job_from_object_pcb_factory'] = query_job_from_object_pcb_factory
            # 先把本次筛选条件存储起来
            current_query_data = QueryData.objects.get(author=self.request.user)
            if query_job_from_object_pcb_factory != None:
                current_query_data.query_job_from_object_pcb_factory = query_job_from_object_pcb_factory
                current_query_data.save()
            if context['query_job_from_object_pcb_factory'] != "":
                context['jobs'] = context['jobs'].filter(
                    from_object_pcb_factory__name_simple__contains=context['query_job_from_object_pcb_factory'])

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
                context['jobs'] = context['jobs'].filter(status="draft")
            if context['query_job_status'] == 'published':
                context['jobs'] = context['jobs'].filter(status="published")

            #每页显示行数
            query_job_paginator_page = self.request.GET.get('query_job_paginator_page', False)
            context['query_job_paginator_page'] = query_job_paginator_page
            # 把每页显示多少行存储起来
            if query_job_paginator_page != None:
                current_query_data.query_job_paginator_page = query_job_paginator_page
                current_query_data.save()




        # 料号很多时，要多页显示，但是在修改非首页内容时，比如修改某个料号，这个料号在第3页，如果不记住页数，修改完成后只能重定向到固定页。为了能记住当前页，用了下面的方法。
        if self.request.GET.__contains__("page"):
            current_page = self.request.GET["page"]
            print("current_page", current_page)
            context['current_page'] = current_page
        else:
            context['current_page'] = 1

        # 分页
        page = self.request.GET.get('page')
        paginator = Paginator(context['jobs'], context['query_job_paginator_page'])  # 每页显示3篇文章
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


def job_list(request,tag_slug=None):
    if request.POST.__contains__("page_jump"):
        pass
        print("post")
        return HttpResponse("post")


    object_list = Job.objects.all()
    tag = None
    if tag_slug:
        # tag = get_object_or_404(Tag, slug=tag_slug)
        tag = get_object_or_404(MyTag, slug=tag_slug)

        object_list = Job.objects.filter(tags__in=[tag])
    # object_list = Job.published.all()
    paginator = Paginator(object_list, 20)  # 每页显示5篇文章
    page = request.GET.get('page')

    if page==None:
        page=1

    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        # 如果page参数不是一个整数就返回第一页
        jobs = paginator.page(1)
    except EmptyPage:
        # 如果页数超出总页数就返回最后一页
        jobs = paginator.page(paginator.num_pages)

    field_verbose_name=["ID","料号名称","标签","发布人","创建时间","更新时间"]
    return render(request, 'list.html', {'page': page, 'jobs': jobs,'tag': tag,"field_verbose_name":field_verbose_name,})