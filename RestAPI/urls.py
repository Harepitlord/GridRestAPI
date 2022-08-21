from django.urls import path
import views


urlpatterns = [
    path('',views.Sample.as_view()),
]