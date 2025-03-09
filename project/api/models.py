from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
import uuid

# موديل المستخدم

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # استخدم CharField لتخزين كلمات المرور المشفرة
    medical_info = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """تشفير كلمة المرور وتخزينها"""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """التحقق من كلمة المرور"""
        return check_password(raw_password, self.password)

    def update_user(self, **kwargs):
        """تحديث بيانات المستخدم بسهولة"""
        for key, value in kwargs.items():
            if key == "password" and value:  # إذا كان هناك كلمة مرور جديدة، يتم تشفيرها
                self.set_password(value)
            else:
                setattr(self, key, value)  # تحديث البيانات العادية
        self.save()
# موديل الطفل
class Child(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="children")
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.IntegerField()
    medical_info = models.TextField(null=True, blank=True)




# موديل السوار
class Bracelet(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name="bracelet")
    battery_level = models.FloatField()
    bracelet_status = models.CharField(max_length=50)
    last_known_location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Bracelet for {self.child.name}"

    class Meta:
        verbose_name = 'Bracelet'
        verbose_name_plural = 'Bracelets'


# موديل مكان الطفل الأخير
class RecentPlace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # أضف null=True هنا
    province = models.CharField(max_length=255, default="Unknown")  # قيمة افتراضية
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:  # التحقق من وجود user
            return f"RecentPlace {self.province} for User {self.user.id}"
        else:
            return f"RecentPlace {self.province} (No User)"
# موديل طلبات الموقع
class LocationRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="location_requests")
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="location_requests")
    request_timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    map_link = models.CharField(max_length=255)

    def __str__(self):
        return f"Location request for {self.child.name}"

    class Meta:
        verbose_name = 'Location Request'
        verbose_name_plural = 'Location Requests'

class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # أضف null=True هنا
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:  # التحقق من وجود user
            return f"Location {self.id} for User {self.user.id}"
        else:
            return f"Location {self.id} (No User)"
# موديل الإشعار
from django.db import models
from django.utils.timezone import now

class BatteryStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  # أضف null=True هنا
    battery_level = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)




from django.db import models
from django.utils.timezone import now
from django.conf import settings
class Notification(models.Model):
    

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)  # وقت إرسال الإشعار
    delivered_at = models.DateTimeField(null=True, blank=True)  # وقت تسليم الإشعار للـ Frontend
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Sent', 'Sent')], default='Pending')  # حالة الإشعار
    is_read = models.BooleanField(default=False) 
    def __str__(self):
        return f"Notification for {self.user.id}: {self.title}"
