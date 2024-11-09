from django.urls import path
from .views import index, login_user, logout_user,faq,prediction,about

urlpatterns = [
    path('', index, name='index'),
    path('login', login_user, name='login'),
    path('logout', logout_user, name='logout'),
    path('faq', faq, name='faq'),
    path('prediction', prediction, name='prediction'),
    path('about/', about, name='about'),

]
