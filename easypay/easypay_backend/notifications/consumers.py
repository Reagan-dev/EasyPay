import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PaymentNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id
        self.group_name = f"user_{self.user_id}"
        
        # Join a private group for this specific user
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def payment_update(self, event):
        # This sends the message to the phone
        await self.send(text_data=json.dumps({
            "status": event["status"],
            "amount": event["amount"],
            "message": event["message"]
        }))