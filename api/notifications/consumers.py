import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 그룹 이름 생성 (유저 ID 기반)
        self.group_name = f"user_{self.scope['user'].id}"

        # 그룹에 유저 추가
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 그룹에서 유저 제거
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    # 메시지 수신 시 실행
    async def send_notification(self, event):
        message = event["message"]

        # 클라이언트로 메시지 전송
        await self.send(text_data=json.dumps(message))
