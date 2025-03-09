from django.urls import path
from .views import (
    SignUpView, 
    SignInView, 
   
    ChildView, 
    #GetBraceletInfoView,
    EmergencyAlertView, 
    
    ChildDetailView,
    signup_view,
    login_view,
    home,
    profile_view,
    index,
    UserProfileView,
    notification_view,
    #receive_notification,
    save_child_id,
    mark_as_read,
    add_notification,
    confirm_notifications,
    get_notifications,
    clear_notifications,
    get_unread_notifications_count,
    save_location,
    save_battery_status,
    get_child_id,
    save_latitude, save_longitude, get_last_location , get_recent_places ,get_battery_status , get_child_data,
    child_view,
    ChildDetailAPIView,
  
)

urlpatterns = [
    path('', index, name='index'),
    path('sign-up/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('home/', home, name='home'),
    path('notification/', notification_view, name='notification'),
    path('profileuser/', profile_view, name='profile'),
    path('child_data/', child_view, name='child'),
    path('child_data/<uuid:id>/', child_view, name='child_detail'),
    path('signup/', SignUpView.as_view(), name='signup'),  # تسجيل مستخدم جديد
    path('signin/', SignInView.as_view(), name='signin'), 
    path('profile/', UserProfileView.as_view(), name='user-profile'), # تحديث بيانات المستخدم
    path('childdetail/', ChildView.as_view(), name='create_child'), # إضافة طفل جديد
    path('child-detail/<str:qr_code>/', ChildDetailView.as_view(), name='child_detail'),
   # path('get-bracelet-info/', GetBraceletInfoView.as_view(), name='get-bracelet-info'),
   # path('battery-status/', BatteryStatusView.as_view(), name='battery_status'),
   # path('location-request/', LocationUpdateView.as_view(), name='location_request'),  # طلب موقع الطفل
   # path('RecentPlace/', EmergencyAlertView.as_view(), name='emergency'),  # إرسال إشعار طارئ
    #path('receive-notification/', receive_notification, name='receive_notification'), # إرسال إشعار
    #path('child/<str:qr_code>/', child_detail, name='child_detail'),
    #path('qrcode/<str:qr_code>/', child_detail, name='child_detail'),
    path('mark_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path('delete_notification/<int:notification_id>/', clear_notifications, name='clear_notifications'),
    path('add_notification/', add_notification, name='add_notification'),
    path('get_notifications/', get_notifications, name='get_notifications'),
    path('confirm_notifications/', confirm_notifications, name='confirm_notifications'),
    path('unread_count/', get_unread_notifications_count, name='get_unread_notifications_count'),
    path("save-location/", save_location, name="save_location"),
    path('battery-status/', save_battery_status, name='save_battery_status'),
    path('get-child-id/', get_child_id, name='get-child-id'),
    path("save-child-id/", save_child_id, name="save-child-id"),
    path("save-location/", save_location, name="save_location"),
    path('save-latitude/', save_latitude, name='save_latitude'),
    path('save-longitude/', save_longitude, name='save_longitude'),
    path('get-last-location/', get_last_location, name='get_last_location'),
    path('get-recent-places/', get_recent_places, name='get_recent_places'),
    path('save-battery-status/', save_battery_status, name='save_battery_status'),
    path('get-battery-status/<uuid:user_id>/', get_battery_status, name='get_battery_status'),
    path('get-child/<uuid:child_id>/', get_child_data, name='get-child-data'),
    path('child/<uuid:id>/', ChildDetailAPIView.as_view(), name='child-detail'),
]
