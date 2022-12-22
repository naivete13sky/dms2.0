import datetime
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic.base import View, TemplateView
from sqlalchemy import create_engine
import pandas as pd
from zentao.GL import GL


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


        kwargs['field_verbose_name'] = ['日期','新增','解决','关闭']



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
        # print('active_bug_group_by_who_pd：',type(active_bug_group_by_who_pd), active_bug_group_by_who_pd)
        active_bug_group_by_who_dict = dict(active_bug_group_by_who_pd.items())
        for each in active_bug_group_by_who_dict:
            # print(each,':',bug_active_priority_distribution_dict[each])
            one_dict = {'name': each, 'score': active_bug_group_by_who_dict[each]}
            active_bug_group_by_who_list.append(one_dict)
        # print('active_bug_group_by_who_list:',active_bug_group_by_who_list)
        kwargs['active_bug_group_by_who_list'] = active_bug_group_by_who_list
        # </editor-fold>

        # <editor-fold desc="每日新增Bug数">
        new_bug_group_by_day_list = []
        new_bug_group_by_day_pd = bug_pd.groupby('create_date')["id"].count().sort_index(ascending=False)[:30]
        # print('new_bug_group_by_day_pd：', type(new_bug_group_by_day_pd), new_bug_group_by_day_pd)
        new_bug_group_by_day_dict = dict(new_bug_group_by_day_pd.items())
        for each in new_bug_group_by_day_dict:
            pass
            one_dict = {'day': each, 'count': new_bug_group_by_day_dict[each]}
            new_bug_group_by_day_list.append(one_dict)
        # print('new_bug_group_by_day_list:', new_bug_group_by_day_list)
        x_list = []
        y_list = []
        for key in new_bug_group_by_day_dict:
            # print(key)
            # x_list.append(str(datetime.date(key["day"])))
            # x_list.append(key)
            x_list.append(str(key))
            y_list.append(new_bug_group_by_day_dict[key])
        x_list.reverse()
        y_list.reverse()
        # print(x_list)
        # print(y_list)
        kwargs['statics_bug_by_day_x'] = json.dumps(x_list)
        kwargs['statics_bug_by_day_y'] = y_list
        # 下面这个没用着好像
        kwargs['new_bug_group_by_day_list'] = new_bug_group_by_day_list





        # </editor-fold>

        # <editor-fold desc="每月新增Bug数">
        new_bug_group_by_month_list = []
        bug_pd['create_year'] = pd.to_datetime(bug_pd['openedDate']).dt.year
        bug_pd['create_month'] = pd.to_datetime(bug_pd['openedDate']).dt.month
        bug_pd['create_year_month'] = bug_pd.create_year.map(str) + '-' + bug_pd.create_month.map("{:02}".format)
        # bug_pd.to_excel(r'C:\Users\Administrator\Desktop\pdc5.xlsx')
        new_bug_group_by_month_pd = bug_pd.groupby('create_year_month')["id"].count().sort_index(ascending=False)[:12]
        # print('new_bug_group_by_day_pd：', type(new_bug_group_by_day_pd), new_bug_group_by_day_pd)
        new_bug_group_by_month_dict = dict(new_bug_group_by_month_pd.items())
        for each in new_bug_group_by_month_dict:
            pass
            one_dict = {'day': each, 'count': new_bug_group_by_month_dict[each]}
            new_bug_group_by_month_list.append(one_dict)
        # print('new_bug_group_by_day_list:', new_bug_group_by_day_list)
        x_list = []
        y_list = []
        for key in new_bug_group_by_month_dict:
            # print(key)
            # x_list.append(str(datetime.date(key["day"])))
            # x_list.append(key)
            x_list.append(str(key))
            y_list.append(new_bug_group_by_month_dict[key])
        x_list.reverse()
        y_list.reverse()
        print(x_list)
        print(y_list)
        kwargs['statics_bug_by_month_x'] = json.dumps(x_list)
        kwargs['statics_bug_by_month_y'] = y_list
        # 下面这个没用着好像
        kwargs['new_bug_group_by_month_list'] = new_bug_group_by_month_list

        # </editor-fold>


        # <editor-fold desc="模块分布">


        sql = '''SELECT * from zt_module                '''
        bug_moudle_pd = pd.read_sql_query(sql, engine)
        bug_moudle_pd = bug_moudle_pd[(bug_moudle_pd.deleted == '0')]

        bug_pd_active = bug_pd[(bug_pd.status == 'active')]
        bug_pd_active_with_module = pd.merge(left=bug_pd_active, right=bug_moudle_pd, left_on='module', right_on='id',
                                             how='left')
        print('bug_pd_active_with_module.shape[0]:', bug_pd_active_with_module.shape[0])
        bug_pd_active_with_module_group_by_module = bug_pd_active_with_module.groupby('module')["id_x"].count()

        data_list_1 = []
        for tup in zip(
                bug_moudle_pd['id'], bug_moudle_pd['root'], bug_moudle_pd['name'], bug_moudle_pd['parent'],
                bug_moudle_pd['grade'], bug_moudle_pd['type']
        ):
            try:
                current_count = bug_pd_active_with_module_group_by_module[tup[0]]
            except Exception as e:
                current_count = 0

            # print(tup[0],'|',tup[2],'|','count:',current_count)
            current_dict = {'module_id': tup[0], 'module_name': tup[2], 'module_parent_id': tup[3],
                            '$count': current_count}
            data_list_1.append(current_dict)
        # print(data_list_1)
        data_bug_module_distribution_json=self.list2tree_dict(data_list_1)
        # print(data_bug_module_distribution_json)
        GL.data_bug_module_distribution_json=data_bug_module_distribution_json

        # </editor-fold>





        return kwargs

    def list2tree_dict(self,data: list) -> list:
        # 转成ID为Key的字典
        mapping = dict(zip([i['module_id'] for i in data], data))
        # print('mapping:',mapping)
        # 树容器
        # container: list = []
        container: dict = {}

        # print('data:', data)
        for d in data:
            # print("d:",d)
            # 如果找不到父级项，则是根节点
            parent: dict = mapping.get(d['module_parent_id'])
            # print('parent:',parent)
            if parent is None:
                # d['$count']=0
                # container.append(d)
                temp_module_name = d['module_name']
                d.pop('module_name', None)
                container[temp_module_name] = d

            else:
                children: list = parent.get('children')
                # children: dict = parent.get('children')
                if not children:
                    children = []
                    # children = {}
                # d['$count']=0
                # children.append(d)
                temp_module_name = d['module_name']
                d.pop('module_name', None)
                # children[temp_module_name] = d
                children.append(d)

                # parent.update({'children': children})
                # parent.update({d['module_name']: children})
                parent.update({temp_module_name: children})
        container = str(container).replace('[', '').replace(']', '')
        container = eval(container)
        container = json.dumps(container, ensure_ascii=False)
        return container




class TestView(TemplateView):
    template_name = r'TestView.html'


class TestJsonView(View):
    def get(self, request, *args, **kwargs):

        with open(r'C:\Users\Administrator\Desktop\data.json', encoding='utf-8') as f:
            data_from_json = json.load(f)
        # print(data_from_json)
        # return HttpResponse('hello,cc')
        return HttpResponse(json.dumps(data_from_json))

class TestJsonView2(View):
    def get(self, request, *args, **kwargs):

        with open(r'C:\Users\Administrator\Desktop\data2.json', encoding='utf-8') as f:
            data_from_json = json.load(f)
        # print(data_from_json)
        # return HttpResponse('hello,cc')
        return HttpResponse(json.dumps(data_from_json))

class BugModuleDistributionJsonView(View):
    def get(self, request, *args, **kwargs):

        # <editor-fold desc="模块分布">



        data_from_json = GL.data_bug_module_distribution_json


        with open(r'C:\Users\Administrator\Desktop\data2.json', encoding='utf-8') as f:
            data_from_json = json.load(f)


        # </editor-fold>
        print('data_from_json:',data_from_json)

        return HttpResponse(json.dumps(data_from_json))