import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量 - 新增
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ 环境变量文件加载成功: {env_path}")
else:
    print(f"⚠️  未找到环境变量文件: {env_path}")
    print("请创建 .env 文件并添加 DEEPSEEK_API_KEY 等配置")

# 从环境变量获取 DeepSeek API 密钥
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if DEEPSEEK_API_KEY and DEEPSEEK_API_KEY != 'sk-test12345678901234567890':
    print(f"✅ DeepSeek API 密钥已配置")
elif DEEPSEEK_API_KEY == 'sk-test12345678901234567890':
    print(f"⚠️  使用的是测试API密钥，请替换为真实密钥")
else:
    print(f"❌ DeepSeek API 密钥未配置，请检查 .env 文件")
# 安全设置
SECRET_KEY = 'django-insecure-your-random-secret-key-here-make-it-long'
DEBUG = True
ALLOWED_HOSTS = ['*']

# 安装的app
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'users',
    'documents',
    'knowledge_graph',
    'api',
]

# 中间件
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 模板配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# REST框架配置
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

# 跨域设置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 静态文件
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

# 前端静态文件
FRONTEND_DIR = BASE_DIR.parent / "frontend" / "dist"
if FRONTEND_DIR.exists():
    STATICFILES_DIRS.append(FRONTEND_DIR)
    print(f"✅ 前端静态文件目录已添加: {FRONTEND_DIR}")
else:
    print(f"⚠️  前端静态文件目录不存在: {FRONTEND_DIR}")

# 媒体文件
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 国际化设置
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL配置
ROOT_URLCONF = 'backend.urls'

# WSGI配置
WSGI_APPLICATION = 'backend.wsgi.application'

# 使用自定义用户模型
AUTH_USER_MODEL = 'users.CustomUser'

# 密码验证
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