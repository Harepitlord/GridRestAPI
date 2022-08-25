from django.urls import path
from . import views

urlpatterns = [
    path('', views.Sample.as_view()),

    path('grid/organization/create', views.Organization.OrganizationCreate.as_view()),
    path('grid/organization/list', views.Organization.OrganizationList.as_view()),
    path('grid/organization/update', views.Organization.OrganizationUpdate.as_view()),
    path('gird/organization/show', views.Organization.OrganizationShow.as_view()),

]
