from django.urls import path
from . import views


urlpatterns = [
    path('',views.Sample.as_view()),

    path('grid/organization/create',views.OrganizationCreate.as_view()),
    path('grid/organization/list',views.OrganizationList.as_view()),
    path('grid/organization/update',views.OrganizationUpdate.as_view()),

]