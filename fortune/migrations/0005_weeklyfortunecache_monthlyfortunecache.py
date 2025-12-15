# Generated manually for weekly/monthly fortune cache

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fortune', '0004_dailyfortunecache_birth_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeeklyFortuneCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=255, verbose_name='세션 키 (비회원용)')),
                ('year', models.IntegerField(verbose_name='년도')),
                ('week_number', models.IntegerField(verbose_name='주차')),
                ('birth_date', models.DateField(blank=True, db_index=True, null=True, verbose_name='생년월일')),
                ('full_fortune_data', models.TextField(blank=True, default='{}', verbose_name='전체 운세 데이터 (JSON)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
            ],
            options={
                'verbose_name': '주간 운세 캐시',
                'verbose_name_plural': '주간 운세 캐시',
                'db_table': 'weekly_fortune_cache',
            },
        ),
        migrations.CreateModel(
            name='MonthlyFortuneCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, max_length=255, verbose_name='세션 키 (비회원용)')),
                ('year', models.IntegerField(verbose_name='년도')),
                ('month', models.IntegerField(verbose_name='월')),
                ('birth_date', models.DateField(blank=True, db_index=True, null=True, verbose_name='생년월일')),
                ('full_fortune_data', models.TextField(blank=True, default='{}', verbose_name='전체 운세 데이터 (JSON)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
            ],
            options={
                'verbose_name': '월간 운세 캐시',
                'verbose_name_plural': '월간 운세 캐시',
                'db_table': 'monthly_fortune_cache',
            },
        ),
    ]
