from rest_framework import serializers
from .models import User, Child, Bracelet, RecentPlace, LocationRequest, Notification

# Serializer لموديل المستخدم
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        password = validated_data.get('password')
        if len(password) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long.")
        user = User(**validated_data)
        user.set_password(password)  # تشفير كلمة المرور
        user.save()
        return user
        

# Serializer لموديل الطفل
class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ['id', 'user', 'name', 'age', 'medical_info', 'qr_code']

# Serializer لموديل السوار
class BraceletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bracelet
        fields = ['id', 'child', 'battery_level', 'bracelet_status', 'last_known_location']

# Serializer لموديل مكان الطفل الأخير
class RecentPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecentPlace
        fields = ['id', 'child', 'latitude', 'longitude', 'timestamp']

# Serializer لموديل طلبات الموقع
class LocationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationRequest
        fields = ['id', 'user', 'child', 'request_timestamp', 'latitude', 'longitude', 'map_link']

# Serializer لموديل الإشعار
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'sent_at', 'status', 'response', 'token']

    def create(self, validated_data):
        return Notification.objects.create(**validated_data)
