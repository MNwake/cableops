from typing import Any

from fastapi import APIRouter, HTTPException, status

from database import ServerMemory
from database.base_models import RiderBase, RiderProfileBase
from database.CWA_Events import Rider



class RiderRoutes:
    def __init__(self, connection_manager, server_memory: ServerMemory):
        self.router = APIRouter(tags=["Cable"])
        self.manager = connection_manager
        self.memory = server_memory
        self.rider_base = RiderBase
        self.define_routes()

    def define_routes(self):

        @self.router.get("")
        async def get_riders() -> dict[str, list[Any] | str]:
            try:
                # print(f"Sending batch of {len(self.pydantic_riders)} riders")
                # rider_data = [rider.serialize() for rider in self.pydantic_riders]

                return {"data": self.memory.riders}

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.router.post("/update")
        async def update_rider(rider_data: dict) -> dict:
            try:
                # Update MongoDB database and retrieve the updated rider
                updated_rider_mongo = RiderBase.update_or_create_rider(rider_data)

                # Convert the updated MongoDB document to a Pydantic model
                updated_rider_pydantic = RiderBase.from_orm(updated_rider_mongo)
                self.update_pydantic_list(updated_rider_pydantic)

                return {"success": True, "rider_id": str(updated_rider_pydantic.id)}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.router.post("/create")
        async def create_rider() -> dict:
            try:
                # Here, add your logic to create a new rider in the database.
                # For now, I'm just generating a mock UUID.
                new_rider = Rider()
                new_rider.save()

                # Save the new rider in the database and get the rider ID
                # rider = YourDatabaseModel.create(...)
                # new_rider_id = str(rider.id)

                return {"success": True, "rider_id": str(new_rider.id)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.router.get("/profile/{rider_id}", response_model=RiderProfileBase)
        async def get_rider_profile(rider_id: str):
            try:
                profile = self.memory.get_rider_profile(rider_id)
                if profile is None:
                    # If no profile found, return a 404 status code with a custom message
                    return HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Rider profile not found."
                    )
                return profile
            except Exception as e:
                # For other exceptions, return a 500 status code with the error message
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )

    def update_pydantic_list(self, updated_rider_pydantic):
        # Find and update or add the Pydantic rider in the list
        for i, pydantic_rider in enumerate(self.memory.riders):
            if pydantic_rider.id == updated_rider_pydantic.id:
                self.memory.riders[i] = updated_rider_pydantic
                break
        else:
            self.memory.riders.append(updated_rider_pydantic)
