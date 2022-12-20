import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic.base import View, TemplateView
from sqlalchemy import create_engine
import pandas as pd


class BugView_0(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('hello, getn')

class BugView(TemplateView):
    # 模板文件名
    template_name = 'BugView.html'

    # 获取模板中数据
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        # <editor-fold desc="拿到项目名称">
        engine = create_engine("mysql+mysqlconnector://chencheng:hWx9pWk5d5J@10.97.80.36:3336/zentao")
        sql = '''SELECT a.* from zt_product a
                where a.id <> 3              
                '''
        product_name_pd = pd.read_sql_query(sql, engine)
        product_name_select = [('all','所有'),]
        count = 0
        for tup in zip(product_name_pd['id'], product_name_pd['name']):
            # print(tup, type(tup[1:]))
            count += 1
            product_name_select.append((str(tup[0]),tup[1]))
        print('product_name_select:',product_name_select)
        # product_name_list = pd.read_sql_query(sql, engine)['name'].unique().tolist()
        kwargs['product_name_select'] = product_name_select
        # </editor-fold>

        sql = '''SELECT a.*,b.name productname,c.realname createbywho,d.realname assignedtowho from zt_bug a
                                        LEFT JOIN zt_product b on a.product=b.id
                                        LEFT JOIN zt_user c on a.openedBy=c.account
                                        LEFT JOIN zt_user d on a.assignedTo=d.account
                                        where a.deleted='0'
                                        '''
        bug_pd = pd.read_sql_query(sql, engine)
        # bug_pd.to_excel(r'C:\Users\Administrator\Desktop\pdc1.xlsx')

        # get方式query数据
        submit_query_get = self.request.GET.get('submit_query_get', False)
        if submit_query_get:
            pass
            print("submit_query_get")
            query_product_name = self.request.GET.get('query_product_name', False)
            print("query_product_name:",query_product_name)
            kwargs['query_product_name'] = query_product_name
            print(query_product_name == '1')
            if query_product_name == 'all':
                bug_pd = bug_pd
            else:
                bug_pd = bug_pd[(bug_pd['product'] == int(query_product_name))]
        else:
            bug_pd = bug_pd


        # <editor-fold desc="新增">
        # 今日新增bug
        today = datetime.date(datetime.now())
        yestoday = today - relativedelta(days=1)
        # print('yestoday:',yestoday)
        bug_pd['create_date'] = pd.to_datetime(bug_pd['openedDate']).dt.date
        bug_static_by_create_date = bug_pd.groupby('create_date')["id"].count()
        bug_static_by_create_date_pd=pd.DataFrame(
            {'create_date': bug_static_by_create_date.index, 'numbers': bug_static_by_create_date.values})
        # bug_static_by_create_date_pd.to_excel(r'C:\Users\Administrator\Desktop\pd2.xlsx')
        # print(bug_static_by_create_date_pd.columns.tolist())#查看有哪些字段
        try:
            today_new_bug_count = bug_static_by_create_date_pd[
                (bug_static_by_create_date_pd.create_date == today)]['numbers'].values[0]
        except Exception as e:
            print('今天新增bug为空',e)
            today_new_bug_count = 0
        kwargs['today_new_bug_count'] = today_new_bug_count
        try:
            yestoday_new_bug_count = bug_static_by_create_date_pd[
                (bug_static_by_create_date_pd.create_date == yestoday)]['numbers'].values[0]
        except Exception as e:
            print('昨天新增bug为空',e)
            yestoday_new_bug_count = 0
        kwargs['yestoday_new_bug_count'] = yestoday_new_bug_count
        # </editor-fold>

        # <editor-fold desc="解决">
        # 今日解决bug
        bug_pd['resolved_date'] = pd.to_datetime(bug_pd['resolvedDate']).dt.date
        bug_static_by_resolved_date = bug_pd.groupby('resolved_date')["id"].count()
        bug_static_by_resolved_date_pd = pd.DataFrame({'resolved_date': bug_static_by_resolved_date.index,
                                   'numbers': bug_static_by_resolved_date.values})
        try:
            today_resolved_bug_count = bug_static_by_resolved_date_pd[
                (bug_static_by_resolved_date_pd.resolved_date == today)]['numbers'].values[0]
        except Exception as e:
            print('今天解决bug为空',e)
            today_resolved_bug_count = 0
        kwargs['today_resolved_bug_count'] = today_resolved_bug_count
        try:
            yestoday_resolved_bug_count = bug_static_by_resolved_date_pd[
                (bug_static_by_resolved_date_pd.resolved_date == yestoday)]['numbers'].values[0]
        except Exception as e:
            print('昨天解决bug为空',e)
            yestoday_resolved_bug_count = 0
        kwargs['yestoday_resolved_bug_count'] = yestoday_resolved_bug_count
        # </editor-fold>

        # <editor-fold desc="关闭">
        # 今日关闭bug
        bug_pd['closed_date'] = pd.to_datetime(bug_pd['closedDate']).dt.date
        bug_static_by_closed_date = bug_pd.groupby('closed_date')["id"].count()
        bug_static_by_closed_date_pd = pd.DataFrame({'closed_date': bug_static_by_closed_date.index,
                                                       'numbers': bug_static_by_closed_date.values})
        try:
            today_closed_bug_count = bug_static_by_closed_date_pd[
                (bug_static_by_closed_date_pd.closed_date == today)]['numbers'].values[0]
        except Exception as e:
            print('今天解决bug为空', e)
            today_closed_bug_count = 0
        kwargs['today_closed_bug_count'] = today_closed_bug_count
        try:
            yestoday_closed_bug_count = bug_static_by_closed_date_pd[
                (bug_static_by_closed_date_pd.closed_date == yestoday)]['numbers'].values[0]
        except Exception as e:
            print('今天解决bug为空', e)
            yestoday_closed_bug_count = 0
        kwargs['yestoday_closed_bug_count'] = yestoday_closed_bug_count
        # </editor-fold>

        # 激活数
        # print(bug_pd[(bug_pd.status == 'active') & (bug_pd.productname == 'EP-CAM')]['id'].count())
        kwargs['active_count'] = bug_pd[(bug_pd.status == 'active')]['id'].count()

        # 已解决
        kwargs['resolved_count'] = bug_pd[(bug_pd.status == 'resolved')]['id'].count()




        sql = '''SELECT * from zt_module
        '''
        bug_moudle_pd = pd.read_sql_query(sql, engine)
        # print(bug_moudle_pd)
        sql = '''SELECT * from zt_module a
        where a.grade=1 
        '''



        # <editor-fold desc="优先级分布">
        # 优先级分布
        priority_distribution_list = []
        bug_active_pd = bug_pd[(bug_pd.status == 'active')]
        # print(bug_active_pd.shape[0])
        # print('bug_active_pd:',bug_active_pd)
        # bug_active_priority_distribution_pd = bug_active_pd.groupby('pri').agg('count')
        bug_active_priority_distribution_pd = bug_active_pd.groupby('pri')["id"].count()
        # print('bug_active_priority_distribution_pd：',bug_active_priority_distribution_pd)
        # print(type(bug_active_priority_distribution_pd))
        # print(list(bug_active_priority_distribution_pd.items()))
        # print(dict(bug_active_priority_distribution_pd.items()))
        bug_active_priority_distribution_dict = dict(bug_active_priority_distribution_pd.items())
        for each in bug_active_priority_distribution_dict:
            # print(each,':',bug_active_priority_distribution_dict[each])
            one_dict = {'优先级':'优先级' + str(each),'个数':bug_active_priority_distribution_dict[each]}
            priority_distribution_list.append(one_dict)
        kwargs['bug_active_priority_distribution'] = priority_distribution_list
        # </editor-fold>

        # <editor-fold desc="拥有Bug数据排行榜">
        active_bug_group_by_who_list = []
        # bug_active_pd = bug_pd[(bug_pd.status == 'active')]
        # .sort_values(ascending=False, inplace=False)[:10] 先排序，再获取前10
        active_bug_group_by_who_pd = bug_active_pd.groupby('assignedtowho')["id"].count().sort_values(ascending=False, inplace=False)[:10]
        print('active_bug_group_by_who_pd：',type(active_bug_group_by_who_pd), active_bug_group_by_who_pd)
        active_bug_group_by_who_dict = dict(active_bug_group_by_who_pd.items())
        for each in active_bug_group_by_who_dict:
            # print(each,':',bug_active_priority_distribution_dict[each])
            one_dict = {'name': each, 'score': active_bug_group_by_who_dict[each]}
            active_bug_group_by_who_list.append(one_dict)
        print('active_bug_group_by_who_list:',active_bug_group_by_who_list)
        kwargs['active_bug_group_by_who_list'] = active_bug_group_by_who_list
        # </editor-fold>



        return kwargs



