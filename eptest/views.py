import json
import os
import shutil
import time
import rarfile
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from .serializers import JobForTestSerializer
from .models import EpcamModule
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .forms import JobForTestFormsReadOnly,JobForTestForm
from .models import JobForTest,MyTagForEptest,Layer,Vs
from account.models import QueryData, Customer
from job.models import Job
from cc.cc_method import CCMethod
from .filters import JobForTestFilter



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
        context['select_eptest_job_for_test_file_type'] = [ ('all', '所有'),('gerber274x', 'Gerber274X'), ('dxf', 'DXF'),('dwg', 'DWG'), ('odb', 'ODB'),
                                          ('pcb', 'PCB'), ('none', 'none'), ]
        context['select_status'] = [('all', '所有'), ('draft', '草稿'), ('published', '正式'), ]
        context['select_eptest_job_for_test_vs_result_g'] = [('all', '所有'), ('passed', '成功'), ('failed', '失败'), ('none', '未比对'), ]
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
        context['jobfortest'] = context['jobfortest'].filter(author__username__contains=context['query_job_author'])
        # print("len of objects1:", len(context['jobfortest']))

        # 模块名称筛选
        if current_query_data.query_eptest_job_for_test_test_usage_for_epcam_module == None:
            context['query_eptest_job_for_test_test_usage_for_epcam_module'] = ''
        else:
            context['query_eptest_job_for_test_test_usage_for_epcam_module'] = current_query_data.query_eptest_job_for_test_test_usage_for_epcam_module
        context['jobfortest'] = context['jobfortest'].filter(test_usage_for_epcam_module__name__contains=context['query_eptest_job_for_test_test_usage_for_epcam_module'])

        # 文件类型
        context['query_eptest_job_for_test_file_type'] = current_query_data.query_eptest_job_for_test_file_type
        if context['query_eptest_job_for_test_file_type'] == 'all':
            pass
        else:
            context['jobfortest'] = context['jobfortest'].filter(file_type=context['query_eptest_job_for_test_file_type'])



        # 料号状态
        context['query_job_status'] = current_query_data.query_job_status
        # print("query_job_file_usage_type:",context['query_job_file_usage_type'])
        if context['query_job_status'] == 'all':
            pass
        if context['query_job_status'] == 'draft':
            context['jobfortest'] = context['jobfortest'].filter(status="draft")
        if context['query_job_status'] == 'published':
            context['jobfortest'] = context['jobfortest'].filter(status="published")

        # G软件比图结果
        context['query_eptest_job_for_test_vs_result_g'] = current_query_data.query_eptest_job_for_test_vs_result_g
        if context['query_eptest_job_for_test_vs_result_g'] == 'all':
            pass
        if context['query_eptest_job_for_test_vs_result_g'] != "all":
            context['jobfortest'] = context['jobfortest'].filter(
                vs_result_g__contains=context['query_eptest_job_for_test_vs_result_g'])





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

            # 模块名称筛选
            query_eptest_job_for_test_test_usage_for_epcam_module = self.request.GET.get('query_eptest_job_for_test_test_usage_for_epcam_module', False)
            context['query_eptest_job_for_test_test_usage_for_epcam_module'] = query_eptest_job_for_test_test_usage_for_epcam_module
            # 先把本次筛选条件存储起来
            if query_eptest_job_for_test_test_usage_for_epcam_module != None:
                current_query_data.query_eptest_job_for_test_test_usage_for_epcam_module = query_eptest_job_for_test_test_usage_for_epcam_module
                current_query_data.save()
            context['jobfortest'] = context['jobfortest'].filter(test_usage_for_epcam_module__name__contains=query_eptest_job_for_test_test_usage_for_epcam_module)

            # 文件类型筛选
            query_eptest_job_for_test_file_type = self.request.GET.get("query_eptest_job_for_test_file_type", False)
            context['query_eptest_job_for_test_file_type'] = query_eptest_job_for_test_file_type
            # 先把本次筛选条件存储起来
            current_query_data = QueryData.objects.get(author=self.request.user)
            if query_eptest_job_for_test_file_type:
                current_query_data.query_eptest_job_for_test_file_type = query_eptest_job_for_test_file_type
                current_query_data.save()
            if context['query_eptest_job_for_test_file_type'] == 'all':
                pass
            else:
                context['jobfortest'] = context['jobfortest'].filter(file_type=context['query_eptest_job_for_test_file_type'])




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

            # G软件比图结果
            query_eptest_job_for_test_vs_result_g = self.request.GET.get("query_eptest_job_for_test_vs_result_g", False)
            context['query_eptest_job_for_test_vs_result_g'] = query_eptest_job_for_test_vs_result_g
            # 先把本次筛选条件存储起来
            current_query_data = QueryData.objects.get(author=self.request.user)
            if query_eptest_job_for_test_vs_result_g:
                current_query_data.query_eptest_job_for_test_vs_result_g = query_eptest_job_for_test_vs_result_g
                current_query_data.save()

            if context['query_eptest_job_for_test_vs_result_g'] == 'all':
                pass
            if context['query_eptest_job_for_test_vs_result_g'] != "all":
                context['jobfortest'] = context['jobfortest'].filter(
                    vs_result_g__contains=context['query_eptest_job_for_test_vs_result_g'])


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




def get_layer_name_from_org(request,job_id):
    print(job_id)
    # 找到job对象
    job = JobForTest.objects.get(id=job_id)
    #先删除原来已有的层信息
    layer_old=Layer.objects.filter(job=job)
    print(layer_old)
    layer_old.delete()


    print(job.job_name, job.file)

    # 先拿到原始料号，放到临时文件夹，完成解压
    temp_path = r'C:\cc\share\temp'+"_"+str(request.user)+"_"+str(job_id)
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)

    org_file_path = (os.path.join(settings.BASE_DIR, r'media', str(job.file))).replace(r'/', '\\')
    shutil.copy(org_file_path, temp_path)
    time.sleep(0.2)
    rf = rarfile.RarFile(os.path.join(temp_path, str(job.file).split("/")[1]))
    rf.extractall(temp_path)
    temp_compressed = os.path.join(temp_path, str(job.file).split("/")[1])
    if os.path.exists(temp_compressed):
        os.remove(temp_compressed)
    file_path_gerber = os.listdir(temp_path)[0]
    print(file_path_gerber)



    list = os.listdir(os.path.join(temp_path,file_path_gerber))  # 列出文件夹下所有的目录与文件
    index=1
    for i in range(0, len(list)):
        path = os.path.join(os.path.join(temp_path,file_path_gerber), list[i])
        if os.path.isfile(path):
            pass
            print(path)
            file_name=list[i]
            file_name_org=list[i]
            if CCMethod.is_chinese(path):
                pass
                os.rename(path,os.path.join(temp_path,file_path_gerber,'unknow' + str(index)))
                file_name='unknow' + str(index)
                index=index+1
            file_name=file_name.replace(' ','-')
            file_name = file_name.replace('(', '-')
            file_name = file_name.replace(')', '-')
            layer_new = Layer()
            layer_new.job=job
            layer_new.layer=file_name
            layer_new.layer_org=file_name_org
            layer_new.save()
    # 删除temp_path
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)

    job.bool_layer_info='true'
    job.save()
    # return redirect('job_manage:JobListViewVs')
    # return redirect('../../../../../admin/#/admin/eptest/jobfortest/')
    # return HttpResponse("已完成！请F5刷新页面！")
    return render(request,r'get_layer_info.html')



@csrf_exempt
def send_vs_g_local_result(request):
    if request.method == 'POST':
        print("post")
        # print(request.body)
        print(request.POST)
        body=json.loads(request.body)
        print(body,type(body))
        body_dict=json.loads(body)
        print(body_dict,type(body_dict))
        job_id = body_dict["job_id"]
        job = JobForTest.objects.get(id=job_id)
        print(job)
        vs_time_g=body_dict["vs_time_g"]
        g_vs_total_result_flag=True

        if len(body_dict["all_result_g"]) == 0:
            g_vs_total_result_flag = False


        # 原始层文件信息，最全的
        all_layer_from_org = Layer.objects.filter(job=job)
        for item in body_dict["all_result_g"].items():
            print(item[0],item[1])
            for each in all_layer_from_org:
                # print("layer:",layer,"str(each.layer_org).lower():",str(each.layer_org).lower().replace(" ","-").replace("(","-").replace(")","-"))
                if item[0] == str(each.layer_org).lower().replace(" ", "-").replace("(", "-").replace(")", "-"):
                    print("I find it!!!!!!!!!!!!!!")
                    new_vs = Vs()
                    new_vs.job = job
                    new_vs.layer = each.layer
                    new_vs.layer_org = each.layer_org
                    new_vs.vs_result_detail = str(item[1])
                    new_vs.vs_method = 'g'
                    new_vs.layer_file_type = each.layer_file_type
                    new_vs.layer_type = each.layer_type
                    new_vs.vs_time_g = vs_time_g
                    try:
                        if item[1] == '正常':
                            each.vs_result_g = 'passed'
                            new_vs.vs_result = 'passed'
                        elif item[1] == '错误':
                            each.vs_result_g = 'failed'
                            new_vs.vs_result = 'failed'
                            g_vs_total_result_flag = False
                        elif item[1] == '未比对':
                            each.vs_result_g = 'none'
                            new_vs.vs_result = 'none'
                            g_vs_total_result_flag = False
                        else:
                            each.vs_result_g = 'failed'
                            new_vs.vs_result = 'failed'
                            g_vs_total_result_flag = False
                            print("异常，状态异常！！！")

                    except:
                        pass
                        print("异常！")
                    each.vs_time_g = vs_time_g
                    # print("each:",each)
                    each.save()
                    # print("new_vs:",new_vs)
                    new_vs.save()

        if g_vs_total_result_flag == True:
            pass
            job.vs_result_g = 'passed'
        if g_vs_total_result_flag == False:
            pass
            job.vs_result_g = 'failed'
        job.vs_time_g = vs_time_g
        job.save()

        temp_path=r"C:\cc\share\temp"
        # 删除temp_path
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)

        return HttpResponse("提交完成！！！")

    return render(request,"send_vs_g_local_result.html")


def view_vs_g(request,job_id):
    pass
    #找到job对象
    job=JobForTest.objects.get(id=job_id)
    print(job.job_name,job.file)
    vs = Vs.objects.filter(job=job,vs_time_g=job.vs_time_g)

    field_verbose_name = [Vs._meta.get_field('job').verbose_name,
                          Vs._meta.get_field('layer').verbose_name,
                          Vs._meta.get_field('layer_org').verbose_name,
                          Vs._meta.get_field('vs_result').verbose_name,
                          Vs._meta.get_field('vs_result_detail').verbose_name,
                          Vs._meta.get_field('vs_method').verbose_name,
                          Vs._meta.get_field('layer_file_type').verbose_name,
                          Vs._meta.get_field('layer_type').verbose_name,
                          Vs._meta.get_field('features_count').verbose_name,
                          Vs._meta.get_field('status').verbose_name,
                          Vs._meta.get_field('vs_time_ep').verbose_name,
                          Vs._meta.get_field('vs_time_g').verbose_name,
                          Vs._meta.get_field('create_time').verbose_name,
                          Vs._meta.get_field('updated').verbose_name,
                          "标签",
                          "操作",
                          ]

    # return redirect('job_manage:LayerListView')
    return render(request, 'VsListViewOneJob.html', {'field_verbose_name': field_verbose_name, 'vs': vs,'job':job})


def test(request):
    pass
    return render(request,'test.html')


# restful-api
class CustomPagination(PageNumberPagination):
    page_size = 10
    max_page_size = None



class JobForTestListViewSet(viewsets.ModelViewSet):
    queryset = JobForTest.objects.all().order_by('-id')
    serializer_class = JobForTestSerializer
    pagination_class = CustomPagination
    # filter_backends = [filters.OrderingFilter]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filter_backends = [DjangoFilterBackend]
    search_fields = ['id', 'job_name', 'tags__name']  # 允许搜索的字段
    # filter_fields = ['test_usage_for_epcam_module','vs_result_g', 'status','author']  # 替换为你想要筛选的字段
    filterset_class = JobForTestFilter
