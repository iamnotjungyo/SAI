from django.urls import path
from .views import SignupView, LoginView, LogoutView, MyProfileView, UserProfileView

urlpatterns = [
    # 인증
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # 프로필
    path('profile/me/', MyProfileView.as_view(), name='my-profile'),
    path('profile/<int:user_id>/', UserProfileView.as_view(), name='user-profile'),
]
