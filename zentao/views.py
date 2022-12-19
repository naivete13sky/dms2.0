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
        kwargs['name'] = 'BugView'
        kwargs['title'] = "BugView"

        engine = create_engine("mysql+mysqlconnector://chencheng:hWx9pWk5d5J@10.97.80.36:3336/zentao")
        sql = '''SELECT a.*,b.name productname,c.realname createbywho,d.realname assignedtowho from zt_bug a
                LEFT JOIN zt_product b on a.product=b.id
                LEFT JOIN zt_user c on a.openedBy=c.account
                LEFT JOIN zt_user d on a.assignedTo=d.account
                where a.deleted='0'
                '''
        bug_pd = pd.read_sql_query(sql, engine)
        # print(bug_pd)
        # bug_pd.to_excel(r'C:\Users\Administrator\Desktop\pd.xlsx')


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



        sql = '''SELECT * from zt_module
        '''
        bug_moudle_pd = pd.read_sql_query(sql, engine)
        # print(bug_moudle_pd)

        sql = '''SELECT * from zt_module a
        where a.grade=1 
        '''


        return kwargs
