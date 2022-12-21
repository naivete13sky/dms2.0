from sqlalchemy import create_engine
import pandas as pd

def cc1():
    engine = create_engine("mysql+mysqlconnector://chencheng:hWx9pWk5d5J@10.97.80.36:3336/zentao")

    sql = '''SELECT a.*,b.name productname,c.realname createbywho,d.realname assignedtowho from zt_bug a
                                            LEFT JOIN zt_product b on a.product=b.id
                                            LEFT JOIN zt_user c on a.openedBy=c.account
                                            LEFT JOIN zt_user d on a.assignedTo=d.account
                                            where a.deleted='0'
                                            '''
    bug_pd = pd.read_sql_query(sql, engine)



    sql = '''SELECT * from zt_module                '''
    bug_moudle_pd = pd.read_sql_query(sql, engine)

    bug_pd_active = bug_pd[(bug_pd.status == 'active')]
    bug_pd_active_with_module = pd.merge(left=bug_pd_active,right=bug_moudle_pd,left_on='module',right_on='id',how='left')
    # bug_pd_with_module.to_excel(r'C:\Users\Administrator\Desktop\pdmodule2.xlsx')
    print(bug_pd_active_with_module.shape[0])


    data_dict_1 = {}
    for tup in zip(bug_pd_active_with_module['module'], bug_pd_active_with_module['id_y'],bug_pd_active_with_module['grade'],
                   bug_pd_active_with_module['name']):
        # print(tup)
        if tup[0] == 0:
            pass
            # print('无模块信息')
        else:
            if tup[2]:
                if str(tup[2]) != 'nan':
                    if int(tup[2]) == 1:
                        # print("grade = 1")
                        if tup[3] in data_dict_1:
                            # print('已存在')
                            current_old_dict = {}
                            # print('|',data_dict_1[tup[3]]['$count'])
                            current_old_dict['$count'] = data_dict_1[tup[3]]['$count'] + 1
                            # print('|',current_old_dict['$count'])
                            data_dict_1[tup[3]]=current_old_dict
                        else:
                            current_new_dict = {}
                            current_new_dict['$count'] = 1
                            data_dict_1[tup[3]]=current_new_dict
                    else:
                        pass
                        # print("grade = {}".format(int(tup[2])))
                        if tup[3] in data_dict_1:
                            # print('已存在')
                            current_old_dict = {}
                            # print('|',data_dict_1[tup[3]]['$count'])
                            current_old_dict['$count'] = data_dict_1[tup[3]]['$count'] + 1
                            # print('|',current_old_dict['$count'])
                            data_dict_1[tup[3]]=current_old_dict
                        else:
                            current_new_dict = {}
                            current_new_dict['$count'] = 1
                            data_dict_1[tup[3]]=current_new_dict

    print(data_dict_1)


def cc2():
    engine = create_engine("mysql+mysqlconnector://chencheng:hWx9pWk5d5J@10.97.80.36:3336/zentao")
    sql = '''SELECT * from zt_module                '''
    bug_moudle_pd = pd.read_sql_query(sql, engine)
    bug_moudle_pd = bug_moudle_pd[(bug_moudle_pd.deleted == '0')]
    # print(bug_moudle_pd)

    data_list_1 = []
    for tup in zip(
            bug_moudle_pd['id'],bug_moudle_pd['root'],bug_moudle_pd['name'],bug_moudle_pd['parent'],
            bug_moudle_pd['grade'], bug_moudle_pd['type']
                   ):
        pass
        current_dict = {'module_id':tup[0],'module_root':tup[1],'module_name':tup[2],'module_parent_id':tup[3]}
        data_list_1.append(current_dict)
    # print(data_list_1)
    return data_list_1






"""
列表转树函数
关键字：id、parent_id、children
"""
def list2tree(data: list) -> list:
    # 转成ID为Key的字典
    mapping: dict = dict(zip([i['module_id'] for i in data], data))

    # 树容器
    container: list = []

    for d in data:
        # 如果找不到父级项，则是根节点
        parent: dict = mapping.get(d['module_parent_id'])
        if parent is None:
            container.append(d)
        else:
            children: list = parent.get('children')
            if not children:
                children = []
            children.append(d)
            parent.update({'children': children})
    return container








if __name__=="__main__":
    data: list = [
        {'module_id': 1, 'module_parent_id': 0, 'name': '用户管理', 'url': 'https://www.baidu.com'},
        {'module_id': 2, 'module_parent_id': 0, 'name': '菜单管理', 'url': 'https://www.baidu.com'},
        {'module_id': 3, 'module_parent_id': 1, 'name': '新增用户', 'url': 'https://www.baidu.com'},
        {'module_id': 7, 'module_parent_id': 3, 'name': '新增用户cc', 'url': 'https://www.baidu.comcc'},
        {'module_id': 4, 'module_parent_id': 1, 'name': '删除用户', 'url': 'https://www.baidu.com'},
        {'module_id': 5, 'module_parent_id': 2, 'name': '新增菜单', 'url': 'https://www.baidu.com'},
        {'module_id': 6, 'module_parent_id': 2, 'name': '删除菜单', 'url': 'https://www.baidu.com'},
    ]


    data = cc2()



    # # 打印验证一下
    # for i in list2tree(data):
    #     print(i)
    cc = list2tree(data)
    print(type(cc))
    print(len(cc))
    for each in cc:
        print(each)
