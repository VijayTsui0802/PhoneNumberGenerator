from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置默认的 Django settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PhoneNumberGenerator.settings')

app = Celery('PhoneNumberGenerator')

# 使用Django的settings文件中配置的broker
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的Django app中加载任务模块
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
