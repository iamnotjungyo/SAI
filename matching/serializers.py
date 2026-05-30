from rest_framework import serializers
from django.contrib.auth.models import User

from accounts.models import Profile
from .models import Interest


class RecommendProfileSerializer(serializers.ModelSerializer):
    """
    친구 추천 목록 — 이미지의 카드 항목
    (이름, 국적, 전공, 학년, 관심사, 매칭률, 나의 관심 여부)
    """
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    match_rate = serializers.SerializerMethodField()
    is_interested = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'user_id', 'username',
            'role', 'nationality', 'major', 'grade',
            'language', 'interests',
            'match_rate', 'is_interested',
        ]

    def get_match_rate(self, obj):
        """
        관심사 겹침 기반 단순 매칭률 계산.
        interests 필드는 쉼표 구분 텍스트로 저장한다고 가정.
        """
        request_user = self.context.get('request').user
        try:
            my_profile = request_user.profile
        except Exception:
            return 0

        my_interests = {i.strip() for i in my_profile.interests.split(',') if i.strip()}
        their_interests = {i.strip() for i in obj.interests.split(',') if i.strip()}

        if not my_interests or not their_interests:
            return 0

        overlap = my_interests & their_interests
        total = my_interests | their_interests
        return round(len(overlap) / len(total) * 100)

    def get_is_interested(self, obj):
        """내가 이 유저에게 관심 등록했는지"""
        request_user = self.context.get('request').user
        return Interest.objects.filter(from_user=request_user, to_user=obj.user).exists()


class InterestSerializer(serializers.ModelSerializer):
    """관심 친구 목록 — 상대 프로필 + 상태 정보"""
    user_id = serializers.IntegerField(source='to_user.id', read_only=True)
    username = serializers.CharField(source='to_user.username', read_only=True)
    nationality = serializers.SerializerMethodField()
    major = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()
    match_rate = serializers.SerializerMethodField()
    is_mutual = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%y.%m.%d', read_only=True)

    class Meta:
        model = Interest
        fields = [
            'id',
            'user_id', 'username',
            'nationality', 'major', 'grade', 'interests',
            'match_rate', 'is_mutual', 'created_at',
        ]

    def _get_profile(self, obj):
        try:
            return obj.to_user.profile
        except Exception:
            return None

    def get_nationality(self, obj):
        p = self._get_profile(obj)
        return p.nationality if p else ''

    def get_major(self, obj):
        p = self._get_profile(obj)
        return p.major if p else ''

    def get_grade(self, obj):
        p = self._get_profile(obj)
        return p.grade if p else None

    def get_interests(self, obj):
        p = self._get_profile(obj)
        return p.interests if p else ''

    def get_match_rate(self, obj):
        request_user = self.context.get('request').user
        try:
            my_profile = request_user.profile
            their_profile = obj.to_user.profile
        except Exception:
            return 0

        my_interests = {i.strip() for i in my_profile.interests.split(',') if i.strip()}
        their_interests = {i.strip() for i in their_profile.interests.split(',') if i.strip()}

        if not my_interests or not their_interests:
            return 0

        overlap = my_interests & their_interests
        total = my_interests | their_interests
        return round(len(overlap) / len(total) * 100)

    def get_is_mutual(self, obj):
        """상대도 나에게 관심을 보냈는지 (= 상호 관심)"""
        request_user = self.context.get('request').user
        return Interest.objects.filter(from_user=obj.to_user, to_user=request_user).exists()


class MutualInterestSerializer(serializers.ModelSerializer):
    """
    상호 관심 친구 — 연락처 포함 공개
    """
    user_id = serializers.IntegerField(source='to_user.id', read_only=True)
    username = serializers.CharField(source='to_user.username', read_only=True)
    nationality = serializers.SerializerMethodField()
    major = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    interests = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    match_rate = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%y.%m.%d', read_only=True)

    class Meta:
        model = Interest
        fields = [
            'id',
            'user_id', 'username',
            'nationality', 'major', 'grade', 'interests',
            'phone', 'match_rate', 'created_at',
        ]

    def _get_profile(self, obj):
        try:
            return obj.to_user.profile
        except Exception:
            return None

    def get_nationality(self, obj):
        p = self._get_profile(obj)
        return p.nationality if p else ''

    def get_major(self, obj):
        p = self._get_profile(obj)
        return p.major if p else ''

    def get_grade(self, obj):
        p = self._get_profile(obj)
        return p.grade if p else None

    def get_interests(self, obj):
        p = self._get_profile(obj)
        return p.interests if p else ''

    def get_phone(self, obj):
        # 상호 관심 목록에서만 사용하는 시리얼라이저이므로 항상 공개
        p = self._get_profile(obj)
        return p.phone if p else ''

    def get_match_rate(self, obj):
        request_user = self.context.get('request').user
        try:
            my_profile = request_user.profile
            their_profile = obj.to_user.profile
        except Exception:
            return 0

        my_interests = {i.strip() for i in my_profile.interests.split(',') if i.strip()}
        their_interests = {i.strip() for i in their_profile.interests.split(',') if i.strip()}

        if not my_interests or not their_interests:
            return 0

        overlap = my_interests & their_interests
        total = my_interests | their_interests
        return round(len(overlap) / len(total) * 100)
