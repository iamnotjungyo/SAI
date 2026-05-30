from django.db import models
from django.contrib.auth.models import User


class Interest(models.Model):
    """
    관심 친구 등록 모델 (CRUD 핵심)
    - from_user가 to_user에게 관심을 표시
    - 양방향 관심 등록 시 → 서로 연락처 공개
    """
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='interests_sent',
        verbose_name='관심 보낸 유저',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='interests_received',
        verbose_name='관심 받은 유저',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')

    class Meta:
        # 동일한 (from, to) 쌍은 중복 불가
        unique_together = ('from_user', 'to_user')
        verbose_name = '관심 친구'
        verbose_name_plural = '관심 친구 목록'

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}"

    @staticmethod
    def is_mutual(user_a, user_b):
        """두 유저가 서로 관심 등록했는지 확인"""
        a_to_b = Interest.objects.filter(from_user=user_a, to_user=user_b).exists()
        b_to_a = Interest.objects.filter(from_user=user_b, to_user=user_a).exists()
        return a_to_b and b_to_a
