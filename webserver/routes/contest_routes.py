import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from mongoengine import DoesNotExist

from database import ServerMemory
from database.base_models import ContestCarrierBase, RiderStatsBase, ScorecardBase
from database.CWA_Events import ContestCarrier, RiderCompStats
from database.utils import calculate_stats, replace_nan
from webserver import ResponseHandler


def find_carrier_by_session(session_id: str):
    return ContestCarrier.objects(session=session_id).first()


class ContestRoutes:
    def __init__(self, connection_manager, server_memory: ServerMemory):
        self.router = APIRouter(tags=["Cable"])
        self.manager = connection_manager
        self.memory = server_memory
        self.contest_carrier_base = ContestCarrierBase
        self.define_routes()

    def define_routes(self):
        # WebSocket route for real-time data if needed

        @self.router.websocket("/ws")
        async def contest_carrier_websocket(websocket: WebSocket):
            await self.manager.connect(websocket)
            path = "/contest/ws"
            user_uuid = None
            is_connected = True  # Flag to keep track of connection status

            try:
                while is_connected:
                    message = await websocket.receive_text()
                    message_data = json.loads(message)
                    print(f"Received WebSocket message: {message_data.get('type')}")

                    request_type = message_data.get("type")

                    if request_type == "connect":
                        user_uuid = message_data.get("data")
                        await self.manager.register(websocket, user_uuid, path)
                        await websocket.send_json(ResponseHandler.success("User registered"))

                    elif request_type == 'carrier':
                        update_result = await self.handle_carrier(message_data.get("data"))
                        await websocket.send_json(update_result)
                        # Here you would handle the 'carrier' message and send a structured response
                    elif request_type == 'scorecard':
                        update_result = await self.handle_scorecard(message_data.get("data"))
                        await websocket.send_json(update_result)
                    # elif request_type == 'session':
                    #     print('session received')
                    #     update_result = await self.handle_session(message_data.get("data"))
                    #     await websocket.send_json(update_result)
                    elif request_type == 'ping':
                        await websocket.send_json(ResponseHandler.success("That tickles!"))
                    else:
                        await websocket.send_json(ResponseHandler.error("Invalid request format"))

            except WebSocketDisconnect:
                print('WebSocket disconnected:', websocket.client)
                is_connected = False
                if user_uuid:
                    await self.manager.disconnect(user_uuid)
            except Exception as e:
                print(f"Error: {e}")
                is_connected = False
            finally:
                if is_connected:
                    await websocket.close()

        @self.router.get("/carriers")
        async def get_contest_carriers() -> dict[str, list[Any]]:
            try:
                return {"data": self.memory.carriers}

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

    async def handle_scorecard(self, scorecard_data: str) -> dict:
        try:
            print("hanlde Scorecard")
            scorecard_data = json.loads(scorecard_data)

            # Process the scorecard data
            if not scorecard_data.get('landed', True):
                carrier = self.remove_rider_from_carrier(scorecard_data.get('session'))
                await self.manager.broadcast(type="carrier", data=carrier)

            # Convert attributes
            scorecard_data['spin_direction'] = scorecard_data.pop('spinDirection', '').lower()
            scorecard_data['trick_type'] = scorecard_data.pop('trickType', '').lower()

            # Create ScorecardBase instance
            pydantic_scorecard = ScorecardBase(**scorecard_data)

            # Save scorecard
            scorecard_id = pydantic_scorecard.save()

            # Convert ObjectId to string
            str_scorecard_id = str(scorecard_id)

            # Assign the string ID to the Pydantic model
            pydantic_scorecard.id = str_scorecard_id


            self.memory.add_scorecard(pydantic_scorecard)
            pydantic_stats = await self.update_rider_stats(pydantic_scorecard.rider)

            # Convert Pydantic model to dict and replace NaN values®
            stats_dict = replace_nan(pydantic_stats.dict())

            # broadcast updates
            await self.manager.broadcast(type="scorecard", data=pydantic_scorecard.json())
            await self.manager.broadcast(type="stats", data=stats_dict)

            return ResponseHandler.success("Scorecard processed")
        except Exception as e:
            print(f"Error occurred: {e}")
            return ResponseHandler.error(str(e))

    async def handle_carrier(self, carrier_data: str):
        try:
            data = json.loads(carrier_data)
            carrier = self.find_carrier(data['number'])
            if not carrier:
                return ResponseHandler.error(f"Carrier with number {data['number']} not found")

            if not data.get('rider_id'):
                print("removing rider")
                carrier.rider_id = None
                carrier.bib_color = None
                carrier.session = None
                print('removed')
            else:

                carrier.rider_id = data.get('rider_id')
                carrier.bib_color = data.get('bib_color')
                carrier.session = data.get('session')

            carrier.save()

            pydantic_carrier = self.memory.update_carriers(carrier)

            await self.manager.broadcast(type="carrier", data=pydantic_carrier)

            return ResponseHandler.success("Carrier updated successfully")
        except Exception as e:
            return ResponseHandler.error(str(e))

    def find_carrier(self, carrier_number):
        return ContestCarrier.objects(number=carrier_number).first()

    async def update_rider_stats(self, rider_id: str):
        new_stats = calculate_stats(rider_id)

        # Update MongoDB document
        try:
            mongo_stats = RiderCompStats.objects.get(rider=rider_id)
        except DoesNotExist:
            mongo_stats = RiderCompStats(rider=rider_id)

        for key, value in new_stats.items():
            setattr(mongo_stats, key, value)
        mongo_stats.save()

        # Create a new Pydantic model instance with updated data
        pydantic_stats = RiderStatsBase.from_orm(mongo_stats)

        await self.memory.update_stats(pydantic_stats)
        return pydantic_stats

    def remove_rider_from_carrier(self, session_id):
        carrier = find_carrier_by_session(session_id)
        if carrier:
            carrier.rider_id = None
            carrier.bib_color = None
            carrier.session = None
            carrier.save()
            return self.memory.update_carriers(carrier)

