import requests
import json

FCM_SERVER_KEY = "ضع_مفتاح_FCM_هنا"
FCM_URL = "https://fcm.googleapis.com/fcm/send"

def send_fcm_notification(user, title, message, sent_at):
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "to": f"/topics/user_{user.id}",  # إرسال الإشعار لكل الأجهزة المشتركة في توبك المستخدم
        "notification": {
            "title": title,
            "body": message
        },
        "data": {
            "sent_at": str(sent_at)  # تضمين وقت الإرسال في البيانات
        }
    }

    response = requests.post(FCM_URL, headers=headers, data=json.dumps(data))
    return response.json()
