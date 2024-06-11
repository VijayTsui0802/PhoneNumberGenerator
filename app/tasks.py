# Django后端/app/tasks.py
import os
import random
import string
from celery import shared_task
from celery.utils.log import get_task_logger
from .models import Number, Task

logger = get_task_logger(__name__)

@shared_task(bind=True)
def generate_numbers(self, prefixes, length, count, task_id):
    try:
        task = Task.objects.get(task_id=task_id)
        total_numbers = len(prefixes) * count
        generated_numbers = 0
        max_attempts = 1000  # 设置最大尝试次数
        logger.info(f"Task {task_id} started. Generating {total_numbers} numbers.")

        numbers = set()  # 使用集合存储生成的号码
        for prefix in prefixes:
            attempts = 0
            while len(numbers) < count and attempts < max_attempts:
                number = prefix + ''.join(random.choices(string.digits, k=length - len(prefix)))
                if number not in numbers and not Number.objects.filter(number=number).exists():
                    Number.objects.create(prefix=prefix, number=number)
                    generated_numbers += 1
                    task.progress = (generated_numbers / total_numbers) * 100
                    task.save()
                    numbers.add(number)  # 添加到集合中
                attempts += 1

            if attempts >= max_attempts:
                logger.warning(f"Max attempts reached for prefix {prefix}. Some numbers may not be unique.")

        task.status = 'completed'
        result_file = f'results/task_{task_id}_result.txt'
        result_file_path = os.path.join('results', f'task_{task_id}_result.txt')
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
        with open(result_file_path, 'w') as f:
            f.write('\n'.join(numbers))

        task.result = result_file  # 确保这里仅保存文件路径，而不是内容
        task.save()

        logger.info(f"Task {task_id} completed successfully. Result file path: {result_file_path}")
    except Exception as e:
        task.status = 'failed'
        task.result = str(e)
        task.save()
        logger.error(f"Task {task_id} failed with error: {e}")
