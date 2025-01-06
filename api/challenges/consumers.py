import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChallengeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.challenge_id = self.scope["url_route"]["kwargs"]["challenge_id"]
        self.group_name = f"challenge_{self.challenge_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def challenge_request(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))

    async def challenge_start(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))
