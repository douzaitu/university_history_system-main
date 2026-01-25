"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls')),
    path('api/', include('api.urls')),  # 这行指向 api/urls.py
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 这行很重要！

# 添加前端静态文件服务
if settings.DEBUG:
    # 服务前端的静态资源文件
    urlpatterns += [
        # 服务前端的index.html文件
        re_path(r'^$', serve, kwargs={'path': 'index.html', 'document_root': settings.BASE_DIR.parent / "frontend" / "dist"}),
        # 服务静态资源文件
        re_path(r'^assets/(?P<path>.*)$', lambda request, path: serve(request, path, document_root=settings.BASE_DIR.parent / "frontend" / "dist" / "assets")),
        re_path(r'^HomePage/(?P<path>.*)$', lambda request, path: serve(request, path, document_root=settings.BASE_DIR.parent / "frontend" / "dist" / "HomePage")),
        re_path(r'^People/(?P<path>.*)$', lambda request, path: serve(request, path, document_root=settings.BASE_DIR.parent / "frontend" / "dist" / "People")),
        re_path(r'^Places/(?P<path>.*)$', lambda request, path: serve(request, path, document_root=settings.BASE_DIR.parent / "frontend" / "dist" / "Places")),
        re_path(r'^Organizations/(?P<path>.*)$', lambda request, path: serve(request, path, document_root=settings.BASE_DIR.parent / "frontend" / "dist" / "Organizations")),
        re_path(r'^Subjects/(?P<path>.*)$', lambda request, path: serve(request, path, document_root=settings.BASE_DIR.parent / "frontend" / "dist" / "Subjects")),
        re_path(r'^Events/(?P<path>.*)$', lambda request, path: serve(request, path, document_root=settings.BASE_DIR.parent / "frontend" / "dist" / "Events")),
        # 服务前端路由
        re_path(r'^people/(?P<id>\d+)$', lambda request, id: serve(request, 'index.html', document_root=settings.BASE_DIR.parent / "frontend" / "dist")),
        re_path(r'^people$', serve, kwargs={'path': 'index.html', 'document_root': settings.BASE_DIR.parent / "frontend" / "dist"}),
        re_path(r'^organizations/(?P<id>\d+)$', lambda request, id: serve(request, 'index.html', document_root=settings.BASE_DIR.parent / "frontend" / "dist")),
        re_path(r'^organizations$', serve, kwargs={'path': 'index.html', 'document_root': settings.BASE_DIR.parent / "frontend" / "dist"}),
        re_path(r'^places/(?P<id>\d+)$', lambda request, id: serve(request, 'index.html', document_root=settings.BASE_DIR.parent / "frontend" / "dist")),
        re_path(r'^places$', serve, kwargs={'path': 'index.html', 'document_root': settings.BASE_DIR.parent / "frontend" / "dist"}),
        re_path(r'^subjects/(?P<id>\d+)$', lambda request, id: serve(request, 'index.html', document_root=settings.BASE_DIR.parent / "frontend" / "dist")),
        re_path(r'^subjects$', serve, kwargs={'path': 'index.html', 'document_root': settings.BASE_DIR.parent / "frontend" / "dist"}),
        re_path(r'^events/(?P<id>\d+)$', lambda request, id: serve(request, 'index.html', document_root=settings.BASE_DIR.parent / "frontend" / "dist")),
        re_path(r'^events$', serve, kwargs={'path': 'index.html', 'document_root': settings.BASE_DIR.parent / "frontend" / "dist"}),
    ]