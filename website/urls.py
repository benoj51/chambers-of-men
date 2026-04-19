from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('signup/', views.signup, name='signup'),
    path('contact/', views.contact, name='contact'),
    path('styleguide/', views.styleguide, name='styleguide'),
]
