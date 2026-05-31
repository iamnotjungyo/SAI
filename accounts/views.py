from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .serializers import SignupSerializer, LoginSerializer, ProfileSerializer, PublicProfileSerializer
from .models import Profile
from matching.models import Interest


# ─── 회원가입 ──────────────────────────────────────────────────────────────────

class SignupView(generics.CreateAPIView):
    """POST /api/signup/ — 회원가입"""
    serializer_class = SignupSerializer


# ─── 로그인 ──────────────────────────────────────────────────────────────────

class LoginView(APIView):
    """POST /api/login/ — 로그인"""
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # 세션 기반 로그인 처리
            from django.contrib.auth import login
            login(request, user)
            return Response({
                'message': '로그인 성공',
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── 로그아웃 ────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """POST /api/logout/ — 로그아웃"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.contrib.auth import logout
        logout(request)
        return Response({'message': '로그아웃 되었습니다.'}, status=status.HTTP_200_OK)


# ─── 내 프로필 조회·수정 ──────────────────────────────────────────────────────

class MyProfileView(APIView):
    """
    GET  /api/profile/me/  — 내 프로필 조회
    PUT  /api/profile/me/  — 내 프로필 전체 수정
    PATCH /api/profile/me/ — 내 프로필 부분 수정
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── 타인 프로필 조회 ─────────────────────────────────────────────────────────

class UserProfileView(APIView):
    """
    GET /api/profile/<user_id>/
    - 상호 관심 등록 시 phone 공개, 아니면 null
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(Profile, user=target_user)

        # 자기 자신이면 phone 항상 공개
        if request.user == target_user:
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)

        show_phone = Interest.is_mutual(request.user, target_user)
        serializer = PublicProfileSerializer(profile, context={'show_phone': show_phone})
        return Response(serializer.data)
    
# ─── 회원탈퇴 ──────────────────────────────────────────────────────────────────

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()

        return Response(
            {"message": "회원탈퇴 완료"},
            status=status.HTTP_200_OK
        )
