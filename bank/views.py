import json
from datetime import datetime

import face_recognition
import numpy as np
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import User, Transaction
from .serializers import UserSerializer


class UserCreateView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            face_image = request.FILES.get('face_image')
            if face_image:
                image = face_recognition.load_image_file(face_image)
                face_encodings = face_recognition.face_encodings(image)

                if face_encodings:
                    serializer.validated_data['face_encoding'] = face_encodings[0].tolist(
                    )
                else:
                    return Response({'Error': 'На изображении не найдено лиц'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Face image is required'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentByFaceViewSet(ViewSet):
    @action(detail=False, methods=['post'])
    def process_face_scan(self, request):
        face_image = request.FILES.get('face_image')
        if not face_image:
            return Response({'Error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image = face_recognition.load_image_file(face_image)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            return Response({'Error': 'На изображении не найдено лиц'}, status=status.HTTP_400_BAD_REQUEST)

        for user in User.objects.all():
            if user.face_encoding:
                user_face_encoding_list = json.loads(user.face_encoding)
                user_face_encoding = np.array(user_face_encoding_list)

                matches = face_recognition.compare_faces(
                    [user_face_encoding], face_encodings[0])
                if matches[0]:
                    transaction = Transaction.objects.create(user=user)
                    return Response({
                        'user': {
                            'name': f"{user.first_name} {user.last_name}",
                            'age': user.date_of_birth.year - datetime.now().year,
                        },
                        'transaction': {
                            'id': transaction.id,
                        }
                    }, status=status.HTTP_200_OK)

        return Response({'Error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'pin_code': openapi.Schema(type=openapi.TYPE_STRING),
                'amount': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['pin_code', 'amount']
        ))
    @action(detail=True, methods=['post'])
    def verify_pin_code(self, request, pk=None):
        transation = Transaction.objects.get(pk=pk)
        user = transation.user
        input_pin_code = request.data.get('pin_code')
        amount = float(request.data.get('amount'))

        if transation.state != 'waiting_for_pin':
            return Response({'Error': 'Невозможно провести оплату'})

        if input_pin_code == user.pin_code:
            if user.balance >= amount:
                user.balance -= amount
                transation.state = 'payment_confirmed'
                transation.save()
                return Response({'message': 'Оплата прошла успешно!'})
            else:
                transation.state = 'error'
                transation.save()
                return Response({'Error': 'Недостаточно средств'})
        return Response({'Error': 'Неверный пин-код', 'user_id': user.id})
