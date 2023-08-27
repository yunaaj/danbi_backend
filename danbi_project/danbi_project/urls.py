"""
URL configuration for danbi_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from danbi_app.views import tasks_handler, task_handler, subtask_handler


urlpatterns = [
    path('admin/', admin.site.urls),
    path('tasks/', tasks_handler),
    path('tasks/<int:task_id>', task_handler),
    path('subtasks/<int:subtask_id>/complete/', subtask_handler)
    # path('test/<str:username>', test_user, name='test'),
    # path('test_post/', test_post)
]
