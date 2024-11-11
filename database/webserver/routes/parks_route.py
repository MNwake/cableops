import logging
import os
from typing import Any

from fastapi import APIRouter, Path, HTTPException
from pydantic import json
from fastapi.responses import FileResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from database.base_models import ParkBase
from database.webserver import ResponseHandler


class ParkRoutes:
    def __init__(self, connection_manager, server_memory):
        self.router = APIRouter(tags=["Cable"])
        self.manager = connection_manager
        self.memory = server_memory
        self.define_routes()

    def define_routes(self):
        @self.router.websocket("/ws/park")
        async def get_park_info(websocket: WebSocket):
            path = '/ws/parks/park'
            await self.manager.connect(websocket, path)
            while True:
                try:
                    message = await websocket.receive_text()
                    if message:
                        message_data = json.loads(message)
                        request_type = message_data.get("request_type")
                        if request_type:
                            await self.handle_request(websocket, request_type, message_data)
                        else:
                            await websocket.send_json({"error": "Invalid request format"})
                except WebSocketDisconnect as e:
                    print('websocketdisconnect', e)
                finally:
                    pass

        @self.router.get("")
        async def get_parks() -> dict[str, Any]:
            try:
                return {'data': self.memory.parks}
            except Exception as e:
                return ResponseHandler.error('Failed to delivery parks')

        @self.router.put("/{park_id}")
        async def update_park(park_id: str, park_data: ParkBase):
            logging.info(f"Received PUT request to update park with ID: {park_id}")
            print(f"Received PUT request to update park with ID: {park_id}")

            try:
                # Find the park in memory
                park = next((p for p in self.memory.parks if p.id == park_id), None)
                if not park:
                    logging.error(f"Park with ID {park_id} not found.")
                    raise HTTPException(status_code=404, detail="Park not found")

                # Update the park in memory
                logging.info(f"Updating park with new data: {park_data.dict()}")
                print(f"Updating park with new data: {park_data.dict()}")

                park.name = park_data.name
                park.abbreviation = park_data.abbreviation
                park.cover_photo = park_data.cover_photo
                park.logo = park_data.logo
                park.address = park_data.address
                park.maintenance = park_data.maintenance
                park.contacts = park_data.contacts
                park.cables = park_data.cables

                # Save to the database (mock this for now)
                # If you use MongoDB or SQL, this would be the place to save the park.
                # Example: db.collection.update_one({"_id": park_id}, {"$set": park.dict()})

                logging.info(f"Park {park_id} successfully updated.")
                # Instead of wrapping the park data in a dictionary, return the updated park directly
                return park.dict()
            except Exception as e:
                logging.error(f"Error updating park: {e}")
                print(f"Error updating park: {e}")
                raise HTTPException(status_code=500, detail="Failed to update park")

    async def handle_request(self, websocket, request_type, message_data):
        print('websocket', 'request_type', 'message_data')
        print(websocket, request_type, message_data)
