import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from devices.models import Device  # <-- 1. Importa el nuevo modelo Device
from .models import Location     # <-- 2. Importa el modelo Location

User = get_user_model()


class LocationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        # El grupo de este usuario (para que él mismo vea sus dispositivos)
        self.room_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Unirse a los grupos de las personas que este usuario confía
        # (para que pueda ver sus ubicaciones)
        self.trusted_contacts_groups = []
        trusted_contacts = await self.get_trusted_contacts()
        for contact in trusted_contacts:
            group_name = f'user_{contact.id}'
            self.trusted_contacts_groups.append(group_name)
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )
            
        await self.accept()
    
    async def disconnect(self, close_code):
        # Descartar de su propio grupo
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        # Descartar de los grupos de contactos
        if hasattr(self, 'trusted_contacts_groups'):
            for group_name in self.trusted_contacts_groups:
                await self.channel_layer.group_discard(
                    group_name,
                    self.channel_name
                )
    
    async def receive(self, text_data):
        """
        Esta función se llama cuando el SERVIDOR recibe un mensaje
        (por ejemplo, desde la app móvil de Kotlin).
        """
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'location_update':
            # --- 3. Lógica de guardado (¡NUEVO!) ---
            # Guarda la ubicación en la BD y obtén la info del dispositivo
            device_info = await self.save_location(data)
            
            if not device_info:
                # El dispositivo no se encontró o no pertenece al usuario
                return

            # --- 4. Lógica de transmisión (Corregida) ---
            # Obtener la lista de usuarios que confían en este usuario
            trusted_by_users = await self.get_trusted_by_users()
            
            # Crear la lista de grupos a los que se enviará la ubicación
            # (los que confían en él + él mismo)
            broadcast_groups = [f'user_{user.id}' for user in trusted_by_users]
            broadcast_groups.append(self.room_group_name) # Añadir su propio grupo
            
            # Prepara el mensaje que se enviará a los grupos
            message = {
                'type': 'location_message', # Llama al handler 'location_message'
                'user_id': self.user.id,
                'user_name': self.user.nombre,
                'device_id': device_info['id'], # ID del dispositivo (de la BD)
                'device_name': device_info['name'], # Nombre del dispositivo
                'latitude': data.get('latitude'),
                'longitude': data.get('longitude'),
                'accuracy': data.get('accuracy'),
            }

            for group_name in set(broadcast_groups): # set() para evitar duplicados
                await self.channel_layer.group_send(group_name, message)
    
    async def location_message(self, event):
        """
        Esta función se llama cuando un GRUPO recibe un mensaje.
        Envía el mensaje final al cliente (la app web de React).
        """
        # --- 5. Mensaje al Cliente (Actualizado) ---
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'device_id': event['device_id'],     # <-- Nuevo campo
            'device_name': event['device_name'], # <-- Nuevo campo
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'accuracy': event['accuracy'],
        }))
    
    # --- 6. Nuevas funciones de Base de Datos ---
    
    @database_sync_to_async
    def get_trusted_contacts(self):
        """Obtiene los usuarios en los que ESTE usuario confía (para VERLOS)"""
        return list(self.user.trusted_contacts.all())

    @database_sync_to_async
    def get_trusted_by_users(self):
        """Obtiene los usuarios que confían en ESTE usuario (para que lo VEAN)"""
        return list(self.user.trusted_by.all())

    @database_sync_to_async
    def save_location(self, data):
        """
        Guarda la ubicación en la base de datos.
        Actualiza el Device y crea un registro en el historial (Location).
        """
        try:
            # 1. Encontrar el dispositivo basado en el ID y el usuario
            device = Device.objects.get(
                user=self.user,
                device_identifier=data.get('device_identifier')
            )
            
            lat = data.get('latitude')
            lon = data.get('longitude')
            acc = data.get('accuracy')
            
            # 2. Actualizar la "última ubicación" en el dispositivo
            device.latitude = lat
            device.longitude = lon
            device.accuracy = acc
            device.save() # Esto también actualiza 'last_seen'
            
            # 3. Crear un registro en el historial
            Location.objects.create(
                device=device,
                latitude=lat,
                longitude=lon,
                accuracy=acc
            )
            
            # Devuelve la info del dispositivo para transmitirla
            return {'id': device.id, 'name': device.name}
            
        except Device.DoesNotExist:
            print(f"Error: Dispositivo no encontrado para el usuario {self.user.email}")
            return None