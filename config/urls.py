from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def page(template):
    return lambda request: render(request, template)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/matching/', include('matching.urls')),

    path('', page('login.html'), name='login'),
    path('home/', page('home.html'), name='home'),
    path('join/', page('join.html'), name='join'),
    path('recommend/', page('recommend.html'), name='recommend'),
    path('friend/', page('friend.html'), name='friend'),
    path('chat/', page('chat.html'), name='chat'),
    path('likesme/', page('likesme.html'), name='likesme'),
    path('profile/', page('profile.html'), name='profile'),
]
