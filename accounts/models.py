from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = (
        ('local', '내국인'),
        ('international', '외국인'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='international')
    nationality = models.CharField(max_length=50)
    major = models.CharField(max_length=100)
    grade = models.IntegerField()
    language = models.CharField(max_length=50, default='한국어')
    interests = models.TextField()

    # 연락처 — 상호 관심 등록 시에만 상대에게 공개
    phone = models.CharField(max_length=20, blank=True, default='')
    bio = models.TextField(blank=True, default='', verbose_name='자기소개')

    def __str__(self):
        return self.user.username
