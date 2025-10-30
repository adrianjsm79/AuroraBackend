import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class LocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            self.room_group_name = f'user_{self.user.id}'
            
            # Unirse al grupo del usuario
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            # Unirse a los grupos de contactos de confianza
            trusted_contacts = await self.get_trusted_contacts()
            for contact in trusted_contacts:
                await self.channel_layer.group_add(
                    f'user_{contact.id}',
                    self.channel_name
                )
            
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'location_update':
            # Enviar actualización a contactos de confianza
            trusted_contacts = await self.get_trusted_contacts()
            
            for contact in trusted_contacts:
                await self.channel_layer.group_send(
                    f'user_{contact.id}',
                    {
                        'type': 'location_message',
                        'user_id': self.user.id,
                        'nombre': self.user.nombre,
                        'latitude': data.get('latitude'),
                        'longitude': data.get('longitude'),
                        'accuracy': data.get('accuracy'),
                    }
                )
    
    async def location_message(self, event):
        # Enviar mensaje al WebSocket
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'user_id': event['user_id'],
            'nombre': event['nombre'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'accuracy': event['accuracy'],
        }))
    
    @database_sync_to_async
    def get_trusted_contacts(self):
        return list(self.user.trusted_contacts.all())