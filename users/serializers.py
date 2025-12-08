from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from datetime import date

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """커스텀 JWT 토큰 시리얼라이저 - 사용자 정보 포함"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # 토큰에 추가 정보 포함
        token['username'] = user.username
        token['first_name'] = user.first_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # 응답에 사용자 정보 추가
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'last_name': self.user.last_name,
            'first_name': self.user.first_name,
            'birth_date': str(self.user.birth_date) if self.user.birth_date else None,
            'gender': self.user.gender,
            'mbti': self.user.mbti,
        }
        # 임시 비밀번호로 로그인한 경우 플래그 추가
        data['must_change_password'] = self.user.must_change_password
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    """회원가입 시리얼라이저"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    birth_hour = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    birth_minute = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 'last_name', 'first_name',
            'birth_date', 'calendar_type', 'gender',
            'birth_hour', 'birth_minute',
            'mbti', 'personal_color', 'chinese_name'
        ]
        extra_kwargs = {
            'last_name': {'required': True},
            'first_name': {'required': True},
            'birth_date': {'required': True},
            'gender': {'required': True},
            'calendar_type': {'required': False, 'default': 'solar'},
            'mbti': {'required': False},
            'personal_color': {'required': False},
            'chinese_name': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': '비밀번호가 일치하지 않습니다.'})

        # 생년월일 검증
        birth_date = attrs.get('birth_date')
        if birth_date:
            today = date.today()
            min_date = date(1900, 1, 1)
            if birth_date > today:
                raise serializers.ValidationError({'birth_date': '미래 날짜는 선택할 수 없습니다.'})
            if birth_date < min_date:
                raise serializers.ValidationError({'birth_date': '1900년 이후 날짜를 선택해주세요.'})

        return attrs

    def create(self, validated_data):
        # 비밀번호2, birth_hour, birth_minute 제거
        validated_data.pop('password2')
        birth_hour = validated_data.pop('birth_hour', None)
        birth_minute = validated_data.pop('birth_minute', None)

        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)

        # 태어난 시각 설정
        if birth_hour is not None and birth_minute is not None:
            from datetime import time
            user.birth_time = time(hour=birth_hour, minute=birth_minute)

        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 시리얼라이저"""
    age = serializers.ReadOnlyField()
    zodiac_sign = serializers.ReadOnlyField()
    chinese_zodiac = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'last_name', 'first_name', 'email',
            'birth_date', 'calendar_type', 'gender', 'birth_time',
            'mbti', 'personal_color', 'chinese_name',
            'phone_number', 'profile_image',
            'age', 'zodiac_sign', 'chinese_zodiac',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """사용자 정보 수정 시리얼라이저"""
    birth_hour = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    birth_minute = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'last_name', 'first_name', 'email',
            'birth_date', 'calendar_type', 'gender',
            'birth_hour', 'birth_minute',
            'mbti', 'personal_color', 'chinese_name',
            'phone_number', 'profile_image'
        ]

    def update(self, instance, validated_data):
        birth_hour = validated_data.pop('birth_hour', None)
        birth_minute = validated_data.pop('birth_minute', None)

        # 태어난 시각 설정
        if birth_hour is not None and birth_minute is not None:
            from datetime import time
            instance.birth_time = time(hour=birth_hour, minute=birth_minute)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """비밀번호 변경 시리얼라이저"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': '새 비밀번호가 일치하지 않습니다.'})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('현재 비밀번호가 올바르지 않습니다.')
        return value
