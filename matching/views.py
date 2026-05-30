from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q

from accounts.models import Profile
from .models import Interest
from .serializers import RecommendProfileSerializer, InterestSerializer, MutualInterestSerializer


# ─── 친구 추천 목록 ───────────────────────────────────────────────────────────

class RecommendListView(APIView):
    """
    GET /api/matching/recommend/
    - 나를 제외한 모든 유저를 매칭률 내림차순으로 반환
    - 이미 관심 등록한 유저도 포함 (is_interested 필드로 구분)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 자신 제외
        profiles = Profile.objects.exclude(user=request.user).select_related('user')

        serializer = RecommendProfileSerializer(
            profiles, many=True, context={'request': request}
        )
        data = serializer.data
        # 매칭률 내림차순 정렬
        data = sorted(data, key=lambda x: x['match_rate'], reverse=True)
        return Response(data)


# ─── 관심 친구 CRUD ──────────────────────────────────────────────────────────

class InterestListView(APIView):
    """
    GET  /api/matching/interests/        — 내가 관심 등록한 목록 (CREATE 시점 최신순)
    POST /api/matching/interests/        — 관심 등록 (CREATE)

    body: { "to_user_id": <int> }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        interests = (
            Interest.objects
            .filter(from_user=request.user)
            .select_related('to_user', 'to_user__profile')
            .order_by('-created_at')
        )
        serializer = InterestSerializer(interests, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        to_user_id = request.data.get('to_user_id')
        if not to_user_id:
            return Response({'error': 'to_user_id는 필수입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        to_user = get_object_or_404(User, id=to_user_id)

        # 자기 자신에게 관심 불가
        if to_user == request.user:
            return Response({'error': '자신에게 관심을 등록할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # 중복 방지 (CREATE or ignore)
        interest, created = Interest.objects.get_or_create(
            from_user=request.user,
            to_user=to_user,
        )

        if not created:
            return Response({'error': '이미 관심 등록한 유저입니다.'}, status=status.HTTP_409_CONFLICT)

        # 상호 관심 여부 확인
        is_mutual = Interest.is_mutual(request.user, to_user)
        return Response({
            'message': '관심 등록 완료',
            'interest_id': interest.id,
            'is_mutual': is_mutual,
        }, status=status.HTTP_201_CREATED)


class InterestDeleteView(APIView):
    """
    DELETE /api/matching/interests/<interest_id>/  — 관심 취소 (DELETE)
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, interest_id):
        interest = get_object_or_404(
            Interest, id=interest_id, from_user=request.user
        )
        interest.delete()
        return Response({'message': '관심 취소 완료'}, status=status.HTTP_204_NO_CONTENT)


class InterestByUserDeleteView(APIView):
    """
    DELETE /api/matching/interests/user/<user_id>/
    — user_id로 직접 관심 취소 (프론트에서 interest_id 없이 user_id만 알 때 편의용)
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        to_user = get_object_or_404(User, id=user_id)
        deleted_count, _ = Interest.objects.filter(
            from_user=request.user, to_user=to_user
        ).delete()

        if deleted_count == 0:
            return Response({'error': '관심 등록 내역이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': '관심 취소 완료'}, status=status.HTTP_204_NO_CONTENT)


# ─── 상호 관심 (매칭 완료) 목록 ──────────────────────────────────────────────

class MutualInterestListView(APIView):
    """
    GET /api/matching/mutual/
    - 내가 관심 등록 AND 상대도 나에게 관심 등록한 경우
    - 상대의 연락처(phone) 포함 공개
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 내가 관심 보낸 to_user 중 → 나에게도 관심을 보낸 유저만 필터
        my_sent = Interest.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
        mutual_qs = Interest.objects.filter(
            from_user=request.user,
            to_user__interests_sent__from_user__in=[request.user],
            to_user__in=my_sent,
        ).select_related('to_user', 'to_user__profile').distinct()

        # 쿼리가 복잡해질 수 있으니 Python-level 필터로 단순화
        my_interests = (
            Interest.objects
            .filter(from_user=request.user)
            .select_related('to_user', 'to_user__profile')
            .order_by('-created_at')
        )
        mutual_list = [
            i for i in my_interests
            if Interest.objects.filter(from_user=i.to_user, to_user=request.user).exists()
        ]

        serializer = MutualInterestSerializer(mutual_list, many=True, context={'request': request})
        return Response(serializer.data)


# ─── 관심 받은 목록 (받은 관심) ───────────────────────────────────────────────

class ReceivedInterestListView(APIView):
    """
    GET /api/matching/received/
    - 나에게 관심을 보낸 유저 목록
    - 상호 여부(is_mutual)도 포함
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        received = (
            Interest.objects
            .filter(to_user=request.user)
            .select_related('from_user', 'from_user__profile')
            .order_by('-created_at')
        )

        result = []
        for interest in received:
            try:
                profile = interest.from_user.profile
            except Exception:
                continue

            is_mutual = Interest.objects.filter(
                from_user=request.user, to_user=interest.from_user
            ).exists()

            result.append({
                'interest_id': interest.id,
                'user_id': interest.from_user.id,
                'username': interest.from_user.username,
                'nationality': profile.nationality,
                'major': profile.major,
                'grade': profile.grade,
                'interests': profile.interests,
                'is_mutual': is_mutual,
                'created_at': interest.created_at.strftime('%y.%m.%d'),
            })

        return Response(result)
