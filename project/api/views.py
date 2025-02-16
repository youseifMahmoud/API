from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, ChildSerializer, BraceletSerializer, RecentPlaceSerializer, LocationRequestSerializer, NotificationSerializer
from .firebase import send_emergency_notification  # Firebase
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Child,Bracelet,RecentPlace,LocationRequest,Notification,save_notification
from django.utils.timezone import now
from django.http import JsonResponse
from channels.layers import get_channel_layer
from datetime import datetime
from django.views import View
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
import requests
import asyncio
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from datetime import datetime
# View for user sign up (registration)
class SignUpView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # الحصول على البيانات من الـ request
        data = request.data
        print("Received Data:", data)  # طباعة البيانات المستلمة
        if not data.get('password') or not data.get('email'):
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # تحقق من وجود المستخدم
        if User.objects.filter(email=data['email']).exists():
            return Response({"detail": "Email is already registered."}, status=status.HTTP_400_BAD_REQUEST)
        
        # إنشاء المستخدم
        user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'])
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.save()

        # العودة بالـ response مع بيانات المستخدم بعد إنشاءه
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)

# View for user sign in (login)
class SignInView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # التحقق من صحة بيانات الدخول
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # إنشاء توكن جديد
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # إرجاع التوكن مع رسالة النجاح
            return Response({"message": "Login successful", "user_id": user.id, "token": access_token}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user  # المستخدم الحالي
        data = request.data  

        allowed_fields = ["name", "phone_number", "gender", "age", "email", "password", "medical_info"]

        # تحديث البيانات فقط إذا كانت موجودة في الطلب
        update_data = {field: data[field] for field in allowed_fields if field in data}
        
        if not update_data:
            return Response({"error": "No valid fields provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.update_user(**update_data)  # استخدام الدالة المخصصة للتحديث
            return Response({"message": "User updated successfully!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# View for creating a child (the child is linked to the user)
class ChildView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """إنشاء طفل جديد مرتبط بالمستخدم"""
        serializer = ChildSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChildDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, qr_code):
        """عرض بيانات الطفل عند مسح QR Code"""
        child = get_object_or_404(Child, qr_code=qr_code)
        user = child.user

        return render(request, "api/child_detail.html", {"child": child, "user": user})
# عرض معلومات السوار وتحديث نسبة البطارية
# جلب معلومات السوار بما في ذلك مستوى البطارية
class GetBraceletInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # الحصول على الطفل المرتبط بالمستخدم
            child = request.user.child
            bracelet = Bracelet.objects.get(child=child)

            # إرسال البيانات للسيراليزر
            serializer = BraceletSerializer(bracelet)
            battery_level = bracelet.battery_level  # جلب مستوى البطارية

            # إرسال مستوى البطارية عبر WebSocket عند الاستعلام
            self.send_websocket_battery_update(child, battery_level)

            return Response({
                "bracelet_info": serializer.data,
                "battery_level": battery_level  # تضمين مستوى البطارية في الرد
            }, status=200)

        except Child.DoesNotExist:
            return Response({"error": "No child linked to this user."}, status=404)
        except Bracelet.DoesNotExist:
            return Response({"error": "No bracelet linked to this child."}, status=404)

    def send_websocket_battery_update(self, child, battery_level):
        """
        إرسال تحديث مستوى البطارية إلى التطبيق عبر WebSocket
        """
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            f'user_{child.user.id}',
            {
                'type': 'battery_update',
                'battery_level': battery_level,
                'child_id': child.id
            }
        )

        # إرسال إشعار إذا انخفضت البطارية إلى أقل من 20%
        if battery_level < 20:
            send_emergency_notification(child.user.token, "Battery Low", "Battery level is critically low!")

class LocationRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        child_id = request.data.get('child_id')

        if not child_id:
            return Response({'error': 'Child ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # التأكد من أن الطفل موجود ومربوط بالمستخدم
        child = get_object_or_404(Child, id=child_id, user=request.user)

        # محاكاة طلب الموقع من السوار (بدلاً من API خارجي)
        location_data = self.get_bracelet_location(child_id)

        if not location_data:
            return Response({'error': 'Failed to fetch location from bracelet'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        latitude = location_data.get('latitude')
        longitude = location_data.get('longitude')
        place_name = self.get_place_name(latitude, longitude)

        # حفظ الموقع في RecentPlace
        recent_place = RecentPlace.objects.create(
            child=child,
            latitude=latitude,
            longitude=longitude,
            place_name=place_name
        )

        # إرسال الموقع إلى التطبيق عبر WebSocket
        self.send_websocket_location_update(recent_place)

        return Response({
            'status': 'success',
            'message': 'Location retrieved successfully',
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'place_name': place_name
            }
        }, status=status.HTTP_200_OK)

    def get_bracelet_location(self, child_id):
        """
        محاكاة استلام الموقع من السوار مباشرة.
        هنا يمكن استبدالها بقراءة مباشرة من الـ Hardware
        """
        # يمكن استبدال هذا بجلب الموقع من قاعدة بيانات مباشرة أو السوار
        return {
            'latitude': 30.0444,  # مثال إحداثيات القاهرة
            'longitude': 31.2357
        }

    def get_place_name(self, latitude, longitude):
        """
        جلب اسم الموقع بناءً على الإحداثيات.
        يمكن استخدام Google Maps API أو أي مصدر آخر.
        """
        return f"Location at {latitude}, {longitude}"

    def send_websocket_location_update(self, recent_place):
        """
        إرسال تحديث الموقع عبر WebSocket
        """
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            f'user_{recent_place.child.user.id}',
            {
                'type': 'location_update',
                'latitude': recent_place.latitude,
                'longitude': recent_place.longitude,
                'place_name': recent_place.place_name,
                'timestamp': recent_place.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        )

# استقبال الموقع من السوار وحفظه وإرساله فورًا
class LocationUpdateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        child_id = data.get('child_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not child_id or not latitude or not longitude:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        child = get_object_or_404(Child, id=child_id)
        place_name = self.get_place_name(latitude, longitude)

        recent_place = RecentPlace.objects.create(
            child=child,
            latitude=latitude,
            longitude=longitude,
            place_name=place_name
        )

        self.send_websocket_location_update(recent_place)
        return Response({'status': 'success', 'message': 'Location updated'}, status=status.HTTP_200_OK)

    def send_websocket_location_update(self, recent_place):
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            'location_group',
            {
                'type': 'location_update',
                'latitude': recent_place.latitude,
                'longitude': recent_place.longitude,
                'place_name': recent_place.place_name,
                'timestamp': recent_place.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        )

    def get_place_name(self, latitude, longitude):
        return f"Location at {latitude}, {longitude}"

# استقبال بيانات البطارية وإرسالها للتطبيق
class BatteryStatusView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        child_id = data.get('child_id')
        battery_level = data.get('battery_level')

        if not child_id or battery_level is None:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        child = get_object_or_404(Child, id=child_id)
        self.send_websocket_battery_update(child, battery_level)

        if battery_level < 20:
            send_emergency_notification(child.user.token, "Battery Low", "Battery level is critically low!")

        return Response({'status': 'success', 'message': 'Battery status updated'}, status=status.HTTP_200_OK)

    def send_websocket_battery_update(self, child, battery_level):
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            f'user_{child.user.id}',
            {
                'type': 'battery_update',
                'battery_level': battery_level,
                'child_id': child.id
            }
        )

# استقبال إشعارات الطوارئ من السوار
class EmergencyAlertView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        child_id = data.get('child_id')
        alert_type = data.get('alert_type')  # battery_low, fall_detected, emergency_button
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not child_id or not alert_type:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        child = get_object_or_404(Child, id=child_id)
        place_name = self.get_place_name(latitude, longitude) if latitude and longitude else "Unknown"
        recent_place = RecentPlace.objects.create(
            child=child,
            latitude=latitude,
            longitude=longitude,
            place_name=place_name
        )

        self.send_websocket_alert(child, alert_type, recent_place)
        return Response({'status': 'success', 'message': 'Emergency alert sent'}, status=status.HTTP_200_OK)

    def send_websocket_alert(self, child, alert_type, recent_place):
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            f'user_{child.user.id}',
            {
                'type': 'emergency_alert',
                'alert_type': alert_type,
                'latitude': recent_place.latitude,
                'longitude': recent_place.longitude,
                'place_name': recent_place.place_name,
                'timestamp': recent_place.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        )

# إرسال الإشعارات فورًا وحفظها في قاعدة البيانات
class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(child__user=user).order_by('-sent_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        child_id = request.data.get('child_id')
        title = request.data.get('title')
        message = request.data.get('message')
        token = request.data.get('token')

        if not child_id or not title or not message or not token:
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        child = get_object_or_404(Child, id=child_id)
        notification = Notification.objects.create(
            child=child,
            title=title,
            message=message,
            status='Sent',
            token=token,
            sent_at=timezone.now()
        )

        self.send_websocket_notification(child, title, message)
        return Response({
            'message': 'Notification sent successfully!',
            'notification': NotificationSerializer(notification).data
        }, status=status.HTTP_201_CREATED)

    def send_websocket_notification(self, child, title, message):
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            f"user_{child.user.id}",
            {
                'type': 'send_notification',
                'notification_type': title,
                'message': message,
                'child_id': child.id,
                'sent_at': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )
