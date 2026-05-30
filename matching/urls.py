from django.urls import path
from .views import (
    RecommendListView,
    InterestListView,
    InterestDeleteView,
    InterestByUserDeleteView,
    MutualInterestListView,
    ReceivedInterestListView,
)

urlpatterns = [
    # 친구 추천 목록
    path('recommend/', RecommendListView.as_view(), name='recommend-list'),

    # 관심 친구 CRUD
    path('interests/', InterestListView.as_view(), name='interest-list-create'),   # GET(목록), POST(등록)
    path('interests/<int:interest_id>/', InterestDeleteView.as_view(), name='interest-delete'),        # DELETE(id 기반)
    path('interests/user/<int:user_id>/', InterestByUserDeleteView.as_view(), name='interest-delete-by-user'),  # DELETE(user_id 기반)

    # 상호 관심 (연락처 공개)
    path('mutual/', MutualInterestListView.as_view(), name='mutual-list'),

    # 받은 관심
    path('received/', ReceivedInterestListView.as_view(), name='received-list'),
]
