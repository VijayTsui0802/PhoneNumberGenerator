# backend/app/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Number
from .serializers import NumberSerializer
import random
import string

class NumberViewSet(viewsets.ModelViewSet):
    queryset = Number.objects.all()
    serializer_class = NumberSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        prefixes = request.data.get('prefixes', [])
        length = int(request.data.get('length', 10))
        count = int(request.data.get('count', 1))

        numbers = set()
        max_attempts = 1000  # 最大尝试次数
        exhausted_prefixes = []

        for prefix in prefixes:
            attempts = 0
            while len(numbers) < count and attempts < max_attempts:
                num_length = length - len(prefix)
                number = prefix + ''.join(random.choices(string.digits, k=num_length))
                if not Number.objects.filter(number=number).exists():
                    Number.objects.create(prefix=prefix, number=number)
                    numbers.add(number)
                else:
                    attempts += 1
            if attempts >= max_attempts:
                exhausted_prefixes.append(prefix)

        if len(numbers) < count:
            return Response({"message": "部分前缀段已无新号码可以生成", "exhausted_prefixes": exhausted_prefixes, "numbers": list(numbers)}, status=207)

        return Response(list(numbers))
