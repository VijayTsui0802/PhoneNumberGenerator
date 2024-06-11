import os
import uuid
import logging
from django.http import FileResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Number, Task
from .serializers import NumberSerializer
from .tasks import generate_numbers

logger = logging.getLogger(__name__)

class NumberViewSet(viewsets.ModelViewSet):
    queryset = Number.objects.all()
    serializer_class = NumberSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        prefixes = request.data.get('prefixes', [])
        length = int(request.data.get('length', 10))
        count = int(request.data.get('count', 1))

        def generate_number(prefix):
            num_length = length - len(prefix)
            number = prefix + ''.join(random.choices(string.digits, k=num_length))
            if not Number.objects.filter(number=number).exists():
                Number.objects.create(prefix=prefix, number=number)
                return number
            return None

        numbers = set()
        max_attempts = 1000
        exhausted_prefixes = []

        for prefix in prefixes:
            attempts = 0
            while len(numbers) < count and attempts < max_attempts:
                number = generate_number(prefix)
                if number:
                    numbers.add(number)
                else:
                    attempts += 1
            if attempts >= max_attempts:
                exhausted_prefixes.append(prefix)

        if len(numbers) < count:
            return Response({"message": "部分前缀段已无新号码可以生成", "exhausted_prefixes": exhausted_prefixes}, status=207)

        return Response(status=200)

class TaskViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def start(self, request):
        prefixes = request.data.get('prefixes', [])
        length = int(request.data.get('length', 10))
        count = int(request.data.get('count', 1))
        task_id = str(uuid.uuid4())  # 生成唯一的任务 ID
        task = Task.objects.create(task_id=task_id, status='running', progress=0)
        generate_numbers.delay(prefixes, length, count, task_id)
        return Response({'task_id': task_id})

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        try:
            task = Task.objects.get(task_id=pk)
            return Response({
                'status': task.status,
                'progress': task.progress,
                'result': task.result
            })
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=404)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        try:
            task = Task.objects.get(task_id=pk)
            logger.info(f"Task status: {task.status}")

            if task.status == 'completed' and task.result:
                result_file = f'results/task_{task.task_id}_result.txt'  # 从 task 对象中获取 task_id
                logger.info(f"Result file path: {result_file}")
                result_file_path = os.path.join(os.getcwd(), result_file)  # 使用相对路径
                logger.info(f"Checking if file exists: {result_file_path}")
                if os.path.exists(result_file_path):
                    logger.info(f"Serving file: {result_file_path}")
                    return FileResponse(open(result_file_path, 'rb'), as_attachment=True, filename=os.path.basename(result_file_path))
                else:
                    logger.error(f"File not found: {result_file_path}")
                    return Response({'error': 'File not found'}, status=400)
            else:
                logger.error(f"Task not completed or no result file: {task.status} - {task.result}")
                return Response({'error': 'Task not completed or result file not found'}, status=400)
        except Task.DoesNotExist:
            logger.error("Task not found")
            return Response({'error': 'Task not found'}, status=404)
        except Exception as e:
            logger.error(f"Error during file download: {e}")
            return Response({'error': str(e)}, status=500)
