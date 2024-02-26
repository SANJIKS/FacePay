from rest_framework import views, status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
import face_recognition
import numpy as np
import json

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class UserCreateView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            face_image = request.FILES.get('face_image')
            if face_image:
                image = face_recognition.load_image_file(face_image)
                face_encodings = face_recognition.face_encodings(image)

                if face_encodings:
                    serializer.validated_data['face_encoding'] = face_encodings[0].tolist()
                else:
                    return Response({'Error': 'На изображении не найдено лиц'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Face image is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FindUserByFaceView(views.APIView):
    def post(self, request):
        face_image = request.FILES.get('face_image')
        if not face_image:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image = face_recognition.load_image_file(face_image)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            return Response({'Error': 'На изображении не найдено лиц'}, status=status.HTTP_400_BAD_REQUEST)

        for user in User.objects.all():
            if user.face_encoding:
                user_face_encoding_list = json.loads(user.face_encoding)
                user_face_encoding = np.array(user_face_encoding_list)

                matches = face_recognition.compare_faces([user_face_encoding], face_encodings[0])
                if matches[0]:
                    return Response({'id': user.id, 'name': f"{user.first_name} {user.last_name}"}, status=status.HTTP_200_OK)

        return Response({'Error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
    

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

                matches = face_recognition.compare_faces([user_face_encoding], face_encodings[0])
                if matches[0]:
                    user.state = 'waiting_for_pin'
                    user.save()
                    return Response({'id': user.id, 'name': f"{user.first_name} {user.last_name}"}, status=status.HTTP_200_OK)

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
        user = User.objects.get(pk=pk)
        input_pin_code = request.data.get('pin_code')
        amount = float(request.data.get('amount'))

        if user.state != 'waiting_for_pin':
            return Response({'Error': 'Невозможно провести оплату'})
        
        if input_pin_code == user.pin_code:
            if user.balance >= amount:    
                user.balance -= amount
                user.state = 'waiting_for_scan'
                user.save()
                
                return Response({'message': 'Оплата прошла успешно!'})
            
            user.state = 'waiting_for_scan'
            user.save()
            return Response({'Error': 'Недостаточно средств'})
        
        return Response({'Error': 'Неверный пин-код', 'user_id': user.id})
