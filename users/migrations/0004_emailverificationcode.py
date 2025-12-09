# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_must_change_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerificationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='이메일')),
                ('username', models.CharField(max_length=150, verbose_name='아이디')),
                ('code', models.CharField(max_length=6, verbose_name='인증코드')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(verbose_name='만료시간')),
                ('is_verified', models.BooleanField(default=False, verbose_name='인증완료')),
            ],
            options={
                'verbose_name': '이메일 인증코드',
                'verbose_name_plural': '이메일 인증코드들',
                'db_table': 'email_verification_codes',
            },
        ),
    ]
