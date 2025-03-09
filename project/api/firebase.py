import firebase_admin
from firebase_admin import credentials, messaging

# تهيئة Firebase باستخدام ملف الاعتماد
cred = credentials.Certificate(r'D:\last data\ITI-Python\Projects\APIS-fin\new-d734b-firebase-adminsdk-fbsvc-d8dad00290.json')
firebase_admin.initialize_app(cred)

def send_emergency_notification(title, message, token):
    # إعداد إشعار
    notification = messaging.Notification(
        title=title,
        body=message,
    )
    
    # إعداد الرسالة
    message = messaging.Message(
        notification=notification,
        token=token,  # تأكد من أن هذا هو التوكن الصحيح للجهاز المستهدف
    )
    
    # إرسال الإشعار
    response = messaging.send(message)
    
    # إرجاع استجابة Firebase (مثل ID الرسالة أو حالة الإرسال)
    return response
