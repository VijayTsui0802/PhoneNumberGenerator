from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Number, Task
from .serializers import NumberSerializer
from .tasks import generate_numbers
import random
import string
import uuid

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
            return Response({"message": "部分前缀段已无新号码可以生成", "exhausted_prefixes": exhausted_prefixes, "numbers": list(numbers)}, status=207)

        return Response(list(numbers))

class TaskViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def start(self, request):
        prefixes = request.data.get('prefixes', [])
        length = int(request.data.get('length', 10))
        count = int(request.data.get('count', 1))
        task_id = str(uuid.uuid4())
        task = Task.objects.create(task_id=task_id, status='running', progress=0)
        generate_numbers.delay(prefixes, length, count, task_id)
        return Response({'task_id': task_id})

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        task = Task.objects.get(task_id=pk)
        return Response({
            'status': task.status,
            'progress': task.progress,
            'result': task.result
        })
