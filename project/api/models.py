from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# موديل المستخدم
class User(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # استخدم CharField لتخزين كلمات المرور المشفرة
    medical_info = models.TextField(null=True, blank=True)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="children")
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    medical_info = models.TextField(null=True, blank=True)
    qr_code = models.CharField(max_length=255)


# موديل السوار
class Bracelet(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name="bracelet")
    battery_level = models.FloatField()
    bracelet_status = models.CharField(max_length=50)
    last_known_location = models.CharField(max_length=255, null=True, blank=True)


# موديل مكان الطفل الأخير
class RecentPlace(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="recent_places")
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()


# موديل طلبات الموقع
class LocationRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="location_requests")
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="location_requests")
    request_timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    map_link = models.CharField(max_length=255)


# موديل الإشعار
class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField(default="")  # إضافة قيمة افتراضية للحقل message
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    response = models.CharField(max_length=255, default="Pending")
    token = models.CharField(max_length=500)

    def __str__(self):
        return f"Notification {self.title} - Status: {self.status}"


# دالة لحفظ الإشعار في قاعدة البيانات
def save_notification(title, message, token, status, response):
    Notification.objects.create(
        title=title,
        message=message,
        token=token,
        status=status,
        response=response
    )
