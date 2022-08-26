from django.urls import path
from . import views

urlpatterns = [
    path('', views.Sample.as_view()),

    path('grid/organization/create', views.Organization.CreateOrganization.as_view()),
    path('grid/organization/list', views.Organization.ListOrganization.as_view()),
    path('grid/organization/update', views.Organization.UpdateOrganization.as_view()),
    path('gird/organization/show', views.Organization.ShowOrganization.as_view()),

    path('grid/role/create',views.Role.CreateRole.as_view()),
    path('grid/role/update',views.Role.UpdateRole.as_view()),
    path('grid/role/delete',views.Role.DeleteRole.as_view()),
    path('grid/role/list',views.Role.ListRole.as_view()),
    path('grid/role/show',views.Role.ShowRole.as_view()),



]
