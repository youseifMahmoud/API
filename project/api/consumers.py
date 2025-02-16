import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.room_group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception as e:
            print(f"Error during disconnect: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
            return

        notification_type = data.get("type")
        message = data.get("message", "No message provided")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if notification_type not in ["battery_low", "emergency", "fall_detected"]:
            return

        await self.channel_layer.group_send(self.room_group_name, {
            "type": "send_notification",
            "notification_type": notification_type,
            "message": message,
            "latitude": latitude,
            "longitude": longitude
        })

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event))
