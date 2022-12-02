"""
Django settings for epdms project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-en5)(qk*1p7r(lpjc7*v!4d_3$%m0xe4%x!5^ci%x94(%09g!v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = ['*']
#

# Application definition

INSTALLED_APPS = [
    'simpleui',
    'account.apps.AccountConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'back_stage.apps.BackStageConfig',
    'taggit',
    'job.apps.JobConfig',
    'multiselectfield',
    'mptt',
    'eptest.apps.EptestConfig',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'epdms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'epdms.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'epdms',
        # 'NAME': 'ep_develop',
        'USER': 'postgres',
        'PASSWORD': 'cc',
        # 'HOST': '10.97.80.118',
        'HOST': '127.0.0.1',
        # 'HOST': '10.97.80.147',

        'PORT': '5432',
    }
}




# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-Hans'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# 当运行 python manage.py collectstatic 的时候
# STATIC_ROOT 文件夹 是用来将所有STATICFILES_DIRS中所有文件夹中的文件，以及各app中static中的文件都复制过来
# 把这些文件放到一起是为了用apache等部署的时候更方便
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

# 其它 存放静态文件的文件夹，可以用来存放项目中公用的静态文件，里面不能包含 STATIC_ROOT
# 如果不想用 STATICFILES_DIRS 可以不用，都放在 app 里的 static 中也可以
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "common_static"),
    #'/path/to/others/static/',  # 用不到的时候可以不写这一行
)

# 这个是默认设置，Django 默认会在 STATICFILES_DIRS中的文件夹 和 各app下的static文件夹中找文件
# 注意有先后顺序，找到了就不再继续找了
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
)




# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#下面用的465端口，阿里云可以用的
EMAIL_USE_SSL = True
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'chen320821@163.com' # 帐号
# EMAIL_HOST_PASSWORD =  'angela123.163'  # 密码
EMAIL_HOST_PASSWORD =  'CZZLYIRGEDHOTHWA'  # 密码
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# 如果没有指定next参数，登录成功后重定向的URL
LOGIN_REDIRECT_URL = 'dashboard'
# 用户需要登录的情况下被重定向到的URL地址（例如@login_required重定向到的地址）
LOGIN_URL = 'login'
# 用户需要登出的时候被重定向到的URL地址
LOGOUT_URL = 'logout'

# 由于我们要允许用户上传图片，必须配置Django让其提供媒体文件服务，在settings.py中加入下列内容：
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# <---------------------------------------------------simpleui--------------------------------------------------------->
# 隐藏simpleui主页信息
SIMPLEUI_HOME_INFO = False

# simpleui修改logo
# 如果需要使用本地图片，需要在Lib/site-packages/simpleui/static/admin/simpleui-x/img中把原来的logo.png替换掉（图片名称不要改变）。
# SIMPLEUI_LOGO = '图片URL'

# 设置默认主题
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'

# 修改默认首页
SIMPLEUI_HOME_PAGE = 'http://127.0.0.1:8000/back_stage/'
SIMPLEUI_HOME_TITLE = '看板'
SIMPLEUI_HOME_ICON = 'fa-solid fa-gauge'


# 设置simpleui 点击首页图标跳转的地址；首页顶部首页图标默认跳转地址为/，即根目录；
# SIMPLEUI_INDEX = 'https://www.88cto.com'


# 自定义SIMPLEUI的Logo
SIMPLEUI_LOGO = 'https://avatars2.githubusercontent.com/u/13655483?s=60&v=4'
'http://127.0.0.1:8000/admin/#/admin/job/job/'
SIMPLEUI_CONFIG = {
    'system_keep': False, # 关闭系统菜单
    # 'system_keep': True, # 关闭系统菜单
    'menu_display': ['料号','任务管理', '测试', '权限认证'],
    'dynamic': True,    # 设置是否开启动态菜单, 默认为False. 如果开启, 则会在每次用户登陆时动态展示菜单内容

    'menus': [
        {
            'app': 'job',
            'name': '料号',
            'icon': 'fas fa-user-shield',
            'models': [
                {
                    'name': '料号管理',
                    'icon': 'fa fa-user',
                    'url': '/admin/job/job/'
                },
                {
                    'name': '研发测试料号',
                    'icon': 'fa fa-user',
                    'url': '/admin/job/jobinfofordevtest/'
                }
            ]
        },
        {
            'app': 'myapp',
            'name': '任务管理',
            'icon': 'fas fa-user-shield',
            'models': [{
                'name': '任务管理1',
                'icon': 'fa fa-user',
                'url': 'job_detail/'
            }]
        },
        {
            'app': 'auth',
            'name': '权限认证',
            'icon': 'fas fa-user-shield',
            'models': [{
                'name': '用户',
                'icon': 'fa fa-user',
                'url': 'auth/user/'
            }]
        },
        {
            'name': '测试',
            'icon': 'fa fa-file',
            'models': [
                {
                    'name': 'Baidu',
                    'url': 'http://baidu.com',
                    'icon': 'far fa-surprise'
                },
                {
                    'name': '内网穿透',
                    'url': 'https://www.wezoz.com',
                    'icon': 'fab fa-github'
                }
            ]
        }
    ]
}


# <---------------------------------------------------simpleui--------------------------------------------------------->