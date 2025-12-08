import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from fortune.models import DailyFortuneCache

print(f'삭제 전: {DailyFortuneCache.objects.count()}개')
DailyFortuneCache.objects.all().delete()
print(f'삭제 후: {DailyFortuneCache.objects.count()}개')
print('운세 캐시 데이터가 모두 삭제되었습니다.')
