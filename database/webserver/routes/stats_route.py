import json

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel

from database.events import RiderStats
from database.webserver.encoder import custom_encoder



class StatsRoute:
    def __init__(self, manager):
        self.router = APIRouter()
        self.manager = manager
        self.define_routes()

    def define_routes(self):
        @self.router.websocket("/ws/rider")
        async def get_rider_stats(websocket: WebSocket):
            path = '/ws/stats/rider'
            await self.manager.connect(websocket, path)
            try:
                while True:
                    # Wait for a message containing the rider_id
                    data = await websocket.receive_text()
                    rider_id = json.loads(data).get('rider_id')

                    # Fetch stats for the requested rider
                    if rider_id:
                        rider_stats = await RiderStats.get_rider_stats(rider_id=rider_id)
                        await websocket.send_json(rider_stats)
                    else:
                        # Handle invalid rider_id
                        await websocket.send_text("Invalid rider ID")
            except Exception as e:
                print('Exception in rider stats WebSocket:', e)
            finally:
                self.manager.disconnect(websocket, path)



    async def on_rider_stats_updated(self, stats):
        try:
            print('on rider stats updated')
            print(type(stats))

            # Convert ObjectId fields to strings
            updated_stats_data = custom_encoder(stats)
            updated_stats_data['_id'] = str(updated_stats_data['_id'])
            updated_stats_data['rider'] = str(updated_stats_data['rider'])

            print('updated stats', updated_stats_data)

            # Convert the dictionary to JSON
            message = json.dumps(updated_stats_data)

            # Broadcast the updated rider stats
            await self.manager.broadcast(message, '/ws/stats/rider')

        except Exception as e:
            print('Error in on_rider_stats_updated:', e)
