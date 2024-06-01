from django.urls import path
from . import views

urlpatterns =[
    path('',views.home,name="home"),
    path('login/sentinel/',views.senAI,name="sentinel"),
    path('register/',views.register,name="register"),
    path('login/',views.login,name="login"),
    path('logout/',views.logout_page,name="logout"),
]

