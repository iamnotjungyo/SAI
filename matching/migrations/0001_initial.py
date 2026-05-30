import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Interest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='등록일')),
                ('from_user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='interests_sent',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='관심 보낸 유저',
                )),
                ('to_user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='interests_received',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='관심 받은 유저',
                )),
            ],
            options={
                'verbose_name': '관심 친구',
                'verbose_name_plural': '관심 친구 목록',
                'unique_together': {('from_user', 'to_user')},
            },
        ),
    ]
