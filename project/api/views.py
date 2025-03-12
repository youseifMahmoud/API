from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, ChildSerializer, BraceletSerializer, RecentPlaceSerializer, LocationRequestSerializer, NotificationSerializer
#from .firebase import send_emergency_notification  # Firebase
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Child,Bracelet,RecentPlace,LocationRequest,Notification
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
from django.shortcuts import render
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from django.db import transaction

def index(request):
    return render(request, 'api/index.html')
def signup_view(request):
    return render(request, 'api/signup.html')
def login_view(request):
    return render(request, 'api/login.html')
def home(request):
    return render(request, 'api/home.html')
def profile_view(request):
    return render(request, 'api/profile.html')

def notification_view(request):
    return render(request, 'api/notification.html')
def child_view(request, id):
    child = get_object_or_404(Child, id=id)  # البحث عن الطفل أو إرجاع 404
    return render(request, 'api/child_detail.html', {'child': child})  # تمرير بيانات الطفل للقالب


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        print("Received Data:", data)

        if not data.get('password') or not data.get('email'):
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        if data['password'] != data.get('confirm_password'):
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=data['email']).exists():
            return Response({"detail": "Email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(data['password'])  # ✅ تشفير كلمة المرور
            user.save()  # ✅ حفظ المستخدم بعد التشفير

            # ✅ إنشاء طفل مرتبط بالمستخدم الجديد
            child = Child.objects.create(
                user=user,  # ✅ استخدام الحقل الصحيح بدلاً من parent
                name=data.get('name',''),  # تعيين اسم افتراضي
                age=data.get('age', 0),
                gender=data.get('gender','') ,
                phone_number=data.get('phone_number',''), # وضع قيمة افتراضية للعمر إذا لم يتم تحديده
                medical_info=data.get('medical_info', ''),  # وضع قيمة افتراضية
            )

            return Response({
                "message": "User created successfully",
                "user_id": str(user.id),
                "child_id": str(child.id),  # ✅ إرسال الـ child_id إلى الواجهة الأمامية
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)  # البحث عن المستخدم بواسطة البريد الإلكتروني
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.check_password(password):  # التحقق من كلمة المرور
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "message": "Login successful",
                "user_id": str(user.id),  # إرسال الـ user_id
                "token": access_token  # إرسال الـ token
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User , BatteryStatus
from .serializers import UserSerializer

class UserProfileView(APIView):
    def get(self, request):
        # استخراج الـ id من query parameters
        user_id = request.query_params.get("id")
        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user_id = request.query_params.get("id")
        if not user_id:
            return Response({"detail": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "user": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
from django.views.decorators.csrf import csrf_exempt
import json
@csrf_exempt
def save_child_id(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            child_id = data.get("child_id")

            if not user_id or not child_id:
                return JsonResponse({"success": False, "message": "بيانات ناقصة."}, status=400)

            # حفظ البيانات في قاعدة البيانات
            child, created = Child.objects.get_or_create(user_id=user_id, child_id=child_id)
            return JsonResponse({"success": True, "message": "تم حفظ معرف الطفل بنجاح."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "طلب غير صالح."}, status=400)

from .models import Location
import uuid

@csrf_exempt
def save_location(request, child_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            if not all([user_id, latitude, longitude]):
                return JsonResponse({
                    "status": "error",
                    "message": "Missing required fields"
                }, status=400)

            try:
                child_uuid = uuid.UUID(child_id)
                child = Child.objects.get(id=child_uuid, user_id=user_id)
            except Child.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Child not found"}, status=404)

            # حفظ البيانات
            location = Location.objects.create(
                user_id=user_id,
                latitude=latitude,
                longitude=longitude
            )
            RecentPlace.objects.create(
                user_id=user_id,
                child=child,
                latitude=latitude,
                longitude=longitude
            )

            return JsonResponse({
                "status": "success",
                "message": "Location saved",
                "data": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "map_link": f"https://maps.google.com/?q={latitude},{longitude}"
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

# دالة لإرجاع الطول فقط
# وظيفة لحفظ خط العرض
@csrf_exempt
def save_latitude(request, child_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            latitude = data.get("latitude")

            if latitude is None:
                return JsonResponse({"status": "error", "message": "Missing latitude"}, status=400)

            try:
                child_uuid = uuid.UUID(child_id)
                child = get_object_or_404(Child, id=child_uuid)
            except ValueError:
                return JsonResponse({"status": "error", "message": "Invalid child_id format"}, status=400)

            # الحصول على user_id من الطفل
            user_id = child.user_id

            location = Location.objects.order_by('-timestamp').first()
            if location:
                location.latitude = latitude
                location.user_id = user_id  # حفظ user_id تلقائيًا
                location.save()
            else:
                location = Location(latitude=latitude, longitude=0, user_id=user_id)
                location.save()

            return JsonResponse({
                "status": "success",
                "message": "Latitude saved",
                "latitude": latitude,
                "user_id": user_id,  # تأكيد حفظ user_id في الرد
                "child_id": child_id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

from django.shortcuts import get_object_or_404

# دالة لإرجاع العرض فقط
@csrf_exempt
def save_longitude(request, child_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            longitude = data.get("longitude")

            if longitude is None:
                return JsonResponse({"status": "error", "message": "Missing longitude"}, status=400)

            try:
                child_uuid = uuid.UUID(child_id)
                child = get_object_or_404(Child, id=child_uuid)
            except ValueError:
                return JsonResponse({"status": "error", "message": "Invalid child_id format"}, status=400)

            # الحصول على user_id من الطفل
            user_id = child.user_id

            location = Location.objects.order_by('-timestamp').first()
            if location:
                location.longitude = longitude
                location.user_id = user_id  # حفظ user_id تلقائيًا
                location.save()
            else:
                location = Location(latitude=0, longitude=longitude, user_id=user_id)
                location.save()

            return JsonResponse({
                "status": "success",
                "message": "Longitude saved",
                "longitude": longitude,
                "user_id": user_id,  # تأكيد حفظ user_id في الرد
                "child_id": child_id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

def get_child_id(request):
    user_id = request.GET.get("user_id")
    try:
        child = Child.objects.filter(user_id=user_id).first()  # إرجاع أول طفل موجود بدلاً من `get`
        if child:
            return JsonResponse({"child_id": str(child.id)})
        else:
            return JsonResponse({"error": "No child found for this user"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

from geopy.geocoders import Nominatim

from geopy.exc import GeocoderTimedOut, GeocoderServiceError
# إرجاع أحدث موقع تم تسجيله
def get_last_location(request):
    user_id = request.GET.get("user_id")  # الحصول على user_id من الطلب
    if not user_id:
        return JsonResponse({"status": "error", "message": "User ID is required"}, status=400)

    try:
        last_location = Location.objects.filter(user_id=user_id).order_by('-timestamp').first()
        if not last_location:
            return JsonResponse({"status": "error", "message": "No locations found"}, status=404)

        try:
            # إعداد Geopy
            geolocator = Nominatim(user_agent="myGeoApp")
            location_data = geolocator.reverse(
                (last_location.latitude, last_location.longitude), 
                exactly_one=True, 
                timeout=10
            )

            if not location_data:
                return JsonResponse({"status": "error", "message": "Location not found"}, status=404)

            # استخراج اسم المحافظة
            address = location_data.raw.get("address", {})
            city = address.get("city", address.get("town", address.get("village", "Unknown")))

            # 🔹 **التحقق من عدم تكرار نفس المحافظة**
            last_recent_place = RecentPlace.objects.filter(user_id=user_id).order_by('-timestamp').first()
            if not last_recent_place or last_recent_place.province != city:
                RecentPlace.objects.create(user_id=user_id, province=city)

            return JsonResponse({
                "status": "success",
                "data": {
                    "latitude": last_location.latitude,
                    "longitude": last_location.longitude,
                    "province": city,
                    "timestamp": last_location.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
            })

        except (GeocoderTimedOut, GeocoderServiceError):
            return JsonResponse({"status": "error", "message": "Geocoding service unavailable"}, status=503)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# 🔹 **دالة جلب آخر 10 مواقع**
def get_recent_places(request):
    user_id = request.GET.get("user_id")  # الحصول على user_id من الطلب
    if not user_id:
        return JsonResponse({"status": "error", "message": "User ID is required"}, status=400)

    places = RecentPlace.objects.filter(user_id=user_id).order_by('-timestamp')[:10]  # جلب آخر 10 مواقع للمستخدم
    data = [{"province": place.province, "timestamp": place.timestamp.strftime("%Y-%m-%d %H:%M:%S")} for place in places]

    return JsonResponse({"status": "success", "data": data})

def get_child_data(request, child_id):
    try:
        # تحويل `child_id` إلى UUID
        child_uuid = uuid.UUID(child_id)

        # البحث عن الطفل في قاعدة البيانات
        child = Child.objects.filter(id=child_uuid).first()

        # التحقق من وجود الطفل
        if not child:
            return JsonResponse({"status": "error", "message": "Child not found."}, status=404)

        # إرجاع بيانات الطفل
        return JsonResponse({
            "status": "success",
            "data": {
                "id": str(child.id),
                "name": child.name,
                "age": child.age,
                
                "medical_info": child.medical_info,
                "user_id": child.user.id,  # إرجاع الـ `user_id` المرتبط بالطفل
            }
        })

    except ValueError:
        return JsonResponse({"status": "error", "message": "Invalid UUID format."}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# استقبال نسبة البطارية من الهاردوير وتخزينها
@csrf_exempt
def save_battery_status(request, child_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            battery_level = data.get("battery_level")

            if battery_level is None:
                return JsonResponse({"status": "error", "message": "Battery level is required."}, status=400)

            # التأكد من أن child_id صحيح
            try:
                child_uuid = uuid.UUID(child_id)
                child = get_object_or_404(Child, id=child_uuid)
            except ValueError:
                return JsonResponse({"status": "error", "message": "Invalid child_id format"}, status=400)

            # الحصول على user_id المرتبط بالطفل
            user_id = child.user_id

            # حفظ مستوى البطارية مع user_id
            BatteryStatus.objects.create(user_id=user_id, battery_level=battery_level)

            return JsonResponse({
                "status": "success",
                "message": "Battery status saved successfully.",
                "battery_level": battery_level,
                "user_id": user_id,
                "child_id": child_id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

def get_battery_status(request, user_id):
    try:
        user = User.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({"status": "error", "message": "User not found."}, status=404)

        # استرجاع آخر نسبة بطارية تم تسجيلها لهذا المستخدم
        battery_status = BatteryStatus.objects.filter(user=user).order_by('-timestamp').first()

        if not battery_status:
            return JsonResponse({"status": "error", "message": "No battery status found."}, status=404)

        return JsonResponse({
            "status": "success",
            "battery_level": battery_status.battery_level,
            "timestamp": battery_status.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)    

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



from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from django.utils.timezone import now

# 1️⃣ API لإضافة إشعار جديد (يستخدمه الهاردوير)
@api_view(['POST'])
def add_notification(request):
    """
    API لاستقبال بيانات الإشعارات من الهاردوير وتخزينها في قاعدة البيانات.
    """
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # حفظ الإشعار في قاعدة البيانات
        return Response({"message": "Notification added successfully!"}, status=201)
    return Response(serializer.errors, status=400)
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

@api_view(['GET'])
def get_notifications(request):
    """
    API لجلب جميع الإشعارات التي لم يتم إرسالها بعد.
    """
    notifications = Notification.objects.filter(status='Pending')  # إشعارات غير مرسلة
    serializer = NotificationSerializer(notifications, many=True)

    if notifications.exists():
        # عدم تغيير الحالة إلى 'Sent' فورًا لتجنب فقدان الإشعارات
        notifications.update(delivered_at=now())

    return Response({"notifications": serializer.data})
@api_view(['POST'])
def confirm_notifications(request):
    """
    API لتأكيد استلام الإشعارات من قبل الـ Frontend.
    """
    notification_ids = request.data.get("notification_ids", [])

    if not notification_ids:
        return Response({"error": "No notification IDs provided."}, status=400)

    # تحديث حالة الإشعارات المستلمة إلى "Sent"
    Notification.objects.filter(id__in=notification_ids).update(status="Sent")

    return Response({"message": "Notifications confirmed successfully!"}, status=200)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Notification
from django.utils.timezone import now

# API to mark all notifications as read
@api_view(['POST'])
def mark_as_read(request, notification_id):
    """
    API لتحديث حالة الإشعار إلى "Read".
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read!"}, status=200)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found."}, status=404)


@api_view(['DELETE'])
def clear_notifications(request, notification_id):
    """
    API لحذف الإشعار.
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return Response({"message": "Notification deleted successfully!"}, status=200)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found."}, status=404)

@api_view(['GET'])
def get_unread_notifications_count(request):
    """
    API لجلب عدد الإشعارات الغير مقروءة.
    """
    user_id = request.GET.get('id')
    if not user_id:
        return Response({"error": "User ID is required"}, status=400)

    unread_count = Notification.objects.filter(user_id=user_id, is_read=False).count()
    return Response({"unread_count": unread_count}, status=200)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Child
from .serializers import ChildSerializer

class ChildDetailAPIView(APIView):
    def get(self, request, id):
        child = get_object_or_404(Child, id=id)  # البحث عن الطفل بناءً على `id`
        serializer = ChildSerializer(child)  # تحويل الكائن إلى JSON
        return Response(serializer.data, status=status.HTTP_200_OK)
