from celery import shared_task
from .models import Number, Task
import random
import string
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(bind=True)
def generate_numbers(self, prefixes, length, count, task_id):
    try:
        task = Task.objects.get(task_id=task_id)
        total_numbers = len(prefixes) * count
        generated_numbers = 0
        logger.info(f"Task {task_id} started. Generating {total_numbers} numbers.")

        for prefix in prefixes:
            for _ in range(count):
                number = prefix + ''.join(random.choices(string.digits, k=length - len(prefix)))
                if not Number.objects.filter(number=number).exists():
                    Number.objects.create(prefix=prefix, number=number)
                    generated_numbers += 1
                    task.progress = (generated_numbers / total_numbers) * 100
                    task.save()
                    logger.info(f"Generated number: {number}. Progress: {task.progress}%")

        task.status = 'completed'
        task.result = '\n'.join([number.number for number in Number.objects.filter(prefix__in=prefixes)])
        task.save()
        logger.info(f"Task {task_id} completed successfully.")
    except Exception as e:
        task.status = 'failed'
        task.result = str(e)
        task.save()
        logger.error(f"Task {task_id} failed with error: {e}")
