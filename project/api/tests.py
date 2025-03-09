from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import User, Child, LocationRequest, Notification

class ChildTests(TestCase):

    def setUp(self):
        # إعداد بيانات المستخدم
        self.client = APIClient()
        self.user_data = {
            "name": "Ahmed",
            "phone_number": "1234567890",
            "gender": "Male",
            "email": "testuser@example.com",
            "password": "password123",
        }
        self.client.post(reverse('sign-up'), self.user_data, format='json')  # إنشاء المستخدم
        
        # تسجيل الدخول للحصول على التوكن
        signin_data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        signin_response = self.client.post(reverse('sign-in'), signin_data, format='json')
        self.token = signin_response.data['token']

        self.child_data = {
            "name": "Ali",
            "age": 5,
            "medical_info": "No medical conditions",
            "qr_code": "1234567890",
        }

    def test_add_child(self):
        # اختبار إضافة طفل
        url = reverse('add-child')
        response = self.client.post(url, self.child_data, HTTP_AUTHORIZATION=f"Bearer {self.token}", format='json')
        
        # تحقق من الاستجابة
        self.assertEqual(response.status_code, 201)  # تحقق من أنه تم الإنشاء بنجاح
        self.assertEqual(response.data['message'], 'Child added successfully')
        self.assertEqual(Child.objects.count(), 1)  # تحقق من أن الطفل تم إضافته إلى قاعدة البيانات

class LocationRequestTests(TestCase):

    def setUp(self):
        # إعداد بيانات المستخدم
        self.client = APIClient()
        self.user_data = {
            "name": "Ahmed",
            "phone_number": "1234567890",
            "gender": "Male",
            "email": "testuser@example.com",
            "password": "password123",
        }
        self.client.post(reverse('sign-up'), self.user_data, format='json')  # إنشاء المستخدم
        
        # تسجيل الدخول للحصول على التوكن
        signin_data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        signin_response = self.client.post(reverse('sign-in'), signin_data, format='json')
        self.token = signin_response.data['token']

        # إعداد بيانات الطفل
        self.child = Child.objects.create(
            name="Ali", age=5, medical_info="No medical conditions", qr_code="1234567890", user=self.user
        )

        self.location_data = {
            "latitude": 30.033,
            "longitude": 31.233,
            "map_link": "https://maps.google.com",
            "child": self.child.id
        }

    def test_location_request(self):
        # اختبار إرسال طلب الموقع
        url = reverse('location-request')
        response = self.client.post(url, self.location_data, HTTP_AUTHORIZATION=f"Bearer {self.token}", format='json')

        # تحقق من الاستجابة
        self.assertEqual(response.status_code, 201)  # تحقق من أنه تم الإنشاء بنجاح
        self.assertEqual(response.data['message'], 'Location request created successfully')


class NotificationTests(TestCase):

    def setUp(self):
        # إعداد بيانات المستخدم
        self.client = APIClient()
        self.user_data = {
            "name": "Ahmed",
            "phone_number": "1234567890",
            "gender": "Male",
            "email": "testuser@example.com",
            "password": "password123",
        }
        self.client.post(reverse('sign-up'), self.user_data, format='json')  # إنشاء المستخدم
        
        # تسجيل الدخول للحصول على التوكن
        signin_data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        signin_response = self.client.post(reverse('sign-in'), signin_data, format='json')
        self.token = signin_response.data['token']

        # إعداد بيانات الإشعار
        self.notification_data = {
            "title": "Emergency Alert",
            "message": "Test emergency message",
            "token": "some_device_token",
            "status": "Sent",
            "response": "Pending",
        }

    def test_send_notification(self):
        # اختبار إرسال إشعار
        url = reverse('send-notification')
        response = self.client.post(url, self.notification_data, HTTP_AUTHORIZATION=f"Bearer {self.token}", format='json')

        # تحقق من الاستجابة
        self.assertEqual(response.status_code, 200)  # تحقق من أنه تم الإرسال بنجاح
        self.assertEqual(response.data['message'], 'Notification sent successfully')
