from rest_framework import serializers
from .models import User, Child, Bracelet, RecentPlace, LocationRequest, Notification

# Serializer لموديل المستخدم

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'gender', 'age', 'email', 'medical_info', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # إخفاء كلمة المرور عند الإرسال

    def create(self, validated_data):
        """تشفير كلمة المرور قبل إنشاء المستخدم"""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)  # ✅ تشفير كلمة المرور
        user.save()
        return user

    def update(self, instance, validated_data):
        """تحديث بيانات المستخدم، وتشفير كلمة المرور إذا تم تغييرها"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)  # ✅ تشفير كلمة المرور عند التحديث
        instance.save()
        return instance


    def update(self, instance, validated_data):
        # تحديث الحقول العادية
        instance.name = validated_data.get('name', instance.name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.age = validated_data.get('age', instance.age)
        instance.medical_info = validated_data.get('medical_info', instance.medical_info)
        
        # تحديث كلمة المرور إذا تم تقديمها
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
    # Serializer لموديل الطفل
class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'  

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
        fields = '__all__'  # هيحول كل الحقول تلقائيًا إلى JSON