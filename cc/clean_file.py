import os
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

def get_unuse_file():
    pass
    # 获取附件列表
    list_files_in_media_files = os.listdir(r'..\media\files')
    # print(list_files_in_media_files)
    print('media/files中的文件个数：',len(list_files_in_media_files))

    # 系统中在用的附件列表
    list_all_files = []

    engine = create_engine('postgresql+psycopg2://readonly:123456@10.97.80.119/epdms')

    # 主料号job_job
    sql = '''SELECT a.* from job_job a'''
    pd_job_job = pd.read_sql(sql=sql, con=engine)
    # print(pd_job_job['file_compressed'])
    list_job_job = [x.split('/')[-1] for x in pd_job_job['file_compressed'] if x != None]
    print("主料号job_job:",len(list_job_job))
    # print(list_job_job)
    list_all_files.extend(list_job_job)

    # 研发用的测试料号
    sql = '''SELECT a.* from job_job_info_for_dev_test a'''
    pd_job_job_info_for_dev_test = pd.read_sql(sql=sql, con=engine)
    # print(pd_job_job_info_for_dev_test['file'])
    list_job_job_info_for_dev_test = [x.split('/')[-1] for x in pd_job_job_info_for_dev_test['file'] if x != None]
    print("研发测试料号job_job_info_for_dev_test:",len(list_job_job_info_for_dev_test))
    list_all_files.extend(list_job_job_info_for_dev_test)

    # 测试部用的测试料号
    sql = '''SELECT a.* from eptest_job_for_test a'''
    pd_eptest_job_for_test = pd.read_sql(sql=sql, con=engine)
    #待测试料号
    # print(pd_eptest_job_for_test['file'])
    list_eptest_job_for_test_file = [x.split('/')[-1] for x in pd_eptest_job_for_test['file'] if x != None]
    print("测试部测试料号--待测试料号eptest_job_for_test_file:", len(list_eptest_job_for_test_file))
    list_all_files.extend(list_eptest_job_for_test_file)
    #标准料号
    # print(pd_eptest_job_for_test['standard_odb'])
    list_eptest_job_for_test_standard_odb = [x.split('/')[-1] for x in pd_eptest_job_for_test['standard_odb'] if x != None]
    print("测试部测试料号--标准料号eptest_job_for_test_standard_odb:", len(list_eptest_job_for_test_standard_odb))
    list_all_files.extend(list_eptest_job_for_test_standard_odb)

    print('总个数',len(list_all_files))
    print('要删除个数：',len(list_files_in_media_files) - len(list_all_files))

    #获取无用的附件名称
    # 使用列表推导式找到lista中存在但listb中不存在的元素
    list_unuse_files = [x for x in list_files_in_media_files if x not in list_all_files]
    print(len(list_unuse_files))

    return list_unuse_files


if __name__ == '__main__':
    pass
    cc = get_unuse_file()
    print(cc)