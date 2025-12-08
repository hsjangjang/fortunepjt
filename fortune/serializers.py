from rest_framework import serializers
from .models import DailyFortuneCache, ColorMaster, MBTISpeechTemplate
import json


class FortuneSerializer(serializers.ModelSerializer):
    """운세 시리얼라이저"""
    lucky_colors = serializers.SerializerMethodField()
    saju_data = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyFortuneCache
        fields = [
            'id', 'fortune_date', 'fortune_score', 'fortune_text',
            'lucky_color', 'lucky_colors', 'lucky_number', 
            'lucky_direction', 'zodiac_sign', 'chinese_zodiac',
            'saju_data', 'created_at'
        ]
    
    def get_lucky_colors(self, obj):
        try:
            return json.loads(obj.lucky_colors_json) if obj.lucky_colors_json else []
        except:
            return []
    
    def get_saju_data(self, obj):
        try:
            return json.loads(obj.saju_data) if obj.saju_data else {}
        except:
            return {}


class FortuneCalculateSerializer(serializers.Serializer):
    """운세 계산 요청 시리얼라이저"""
    birth_date = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=['M', 'F', 'O'], required=True)
    birth_time = serializers.TimeField(required=False)
    chinese_name = serializers.CharField(max_length=100, required=False)
    mbti = serializers.CharField(max_length=4, required=False)
    calendar_type = serializers.ChoiceField(choices=['solar', 'lunar'], required=False, default='solar')


class ColorSerializer(serializers.ModelSerializer):
    """색상 시리얼라이저"""
    class Meta:
        model = ColorMaster
        fields = '__all__'
