from django.urls import path
from .views import (
    SignUpView, 
    SignInView, 
    UserUpdateView, 
    ChildView, 
    GetBraceletInfoView,
    LocationUpdateView, 
    EmergencyAlertView, 
    NotificationView, 
    ChildDetailView,
    BatteryStatusView,
)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),  # تسجيل مستخدم جديد
    path('signin/', SignInView.as_view(), name='signin'),  # تسجيل الدخول
    path('update-profile/', UserUpdateView.as_view(), name='update_profile'),  # تحديث بيانات المستخدم
    path('child/', ChildView.as_view(), name='create_child'), # إضافة طفل جديد
    path('child-detail/<str:qr_code>/', ChildDetailView.as_view(), name='child_detail'),
    path('get-bracelet-info/', GetBraceletInfoView.as_view(), name='get-bracelet-info'),
    path('battery-status/', BatteryStatusView.as_view(), name='battery_status'),
    path('location-request/', LocationUpdateView.as_view(), name='location_request'),  # طلب موقع الطفل
    path('RecentPlace/', EmergencyAlertView.as_view(), name='emergency'),  # إرسال إشعار طارئ
    path('notification/', NotificationView.as_view(), name='notification'),  # إرسال إشعار
    #path('child/<str:qr_code>/', child_detail, name='child_detail'),
    #path('qrcode/<str:qr_code>/', child_detail, name='child_detail'),
]
