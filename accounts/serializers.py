from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import Profile


# ─── 회원가입 ──────────────────────────────────────────────────────────────────

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    nationality = serializers.CharField(write_only=True)
    major = serializers.CharField(write_only=True)
    grade = serializers.IntegerField(write_only=True)
    interests = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True, default='international')
    language = serializers.CharField(write_only=True, default='한국어')
    phone = serializers.CharField(write_only=True, required=False, default='')
    bio = serializers.CharField(write_only=True, required=False, default='')

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password',
            'role', 'nationality', 'major', 'grade',
            'language', 'interests', 'phone', 'bio',
        ]

    def create(self, validated_data):
        profile_fields = {
            'role': validated_data.pop('role', 'international'),
            'nationality': validated_data.pop('nationality'),
            'major': validated_data.pop('major'),
            'grade': validated_data.pop('grade'),
            'language': validated_data.pop('language', '한국어'),
            'interests': validated_data.pop('interests'),
            'phone': validated_data.pop('phone', ''),
            'bio': validated_data.pop('bio', ''),
        }

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        Profile.objects.create(user=user, **profile_fields)
        return user


# ─── 로그인 ──────────────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()  # username 대신 email
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('이메일 또는 비밀번호가 틀렸습니다.')

        user = authenticate(username=user.username, password=data['password'])
        if user is None:
            raise serializers.ValidationError('이메일 또는 비밀번호가 틀렸습니다.')

        data['user'] = user
        return data


# ─── 프로필 조회·수정 ────────────────────────────────────────────────────────

class ProfileSerializer(serializers.ModelSerializer):
    """
    내 프로필 조회·수정에 사용.
    연락처(phone)는 항상 포함 (자신의 것).
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'username', 'email',
            'role', 'nationality', 'major', 'grade',
            'language', 'interests', 'phone', 'bio',
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PublicProfileSerializer(serializers.ModelSerializer):
    """
    타인 프로필 조회 — phone은 상호 관심 등록 여부에 따라 동적으로 포함/제외.
    View에서 show_phone 파라미터를 context로 전달.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'username', 'email',
            'role', 'nationality', 'major', 'grade',
            'language', 'interests', 'phone', 'bio',
        ]

    def get_phone(self, obj):
        if self.context.get('show_phone'):
            return obj.phone
        return None  # 상호 관심 미충족 시 비공개
