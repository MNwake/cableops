from bson import ObjectId
from mongoengine import DoesNotExist
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from database.cable.maintenance import MaintenanceServiceType, Maintenance, ServiceLog
from database.cable.park import Park


# BaseModel for EqualizeMaintenance
class EqualizeMaintenanceBase(BaseModel):
    number_of_splices: int
    distance_between_cables: int
    images: Optional[List[str]] = []

    class Config:
        orm_mode = True
        from_attributes = True


# BaseModel for AnnualInspection
class AnnualInspectionBase(BaseModel):
    cables_inspected: bool = True
    cable_connections_inspected: bool = True
    ground_anchors_inspected: bool = True
    rigging_cables_inspected: bool = True
    shackles_inspected: bool = True
    carriers_inspected: bool = True

    class Config:
        orm_mode = True
        from_attributes = True


# BaseModel for TowerInspection
class TowerInspectionBase(BaseModel):
    tower_id: str
    liners_inspected: bool = True
    top_pulley_greased: bool = True
    bottom_pulley_greased: bool = True

    class Config:
        orm_mode = True
        from_attributes = True


# BaseModel for MotorTowerInspection
class MotorTowerInspectionBase(BaseModel):
    universal_joint_greased: bool = True
    ball_joints_greased: bool = True
    running_cable_splices_inspected: bool = True

    class Config:
        orm_mode = True
        from_attributes = True


# BaseModel for QuarterlyMaintenance
class QuarterlyMaintenanceBase(BaseModel):
    tower_inspections: Optional[List[TowerInspectionBase]] = []
    motor_tower_inspection: Optional[MotorTowerInspectionBase] = None

    class Config:
        orm_mode = True
        from_attributes = True


# BaseModel for CarrierCheck
class CarrierCheckBase(BaseModel):
    carrier_number: str
    diagonals_pass: bool = True
    safety_pins_pass: bool = True
    clutch_strength_pass: bool = True
    clutch_ball_gap_pass: bool = True
    other_issues: Optional[str] = None
    actions_taken: Optional[str] = None
    images: Optional[List[str]] = []

    class Config:
        orm_mode = True
        from_attributes = True


# BaseModel for FunctionCheck
class FunctionCheckBase(BaseModel):
    fork_catch_pass: bool = True
    decoupling_rail_pass: bool = True
    magazine_load_pass: bool = True
    emergency_stop_function_pass: bool = True

    class Config:
        orm_mode = True
        from_attributes = True


# BaseModel for LubricationCheck
class LubricationCheckBase(BaseModel):
    loading_rod_oiled: bool = True
    fork_tube_oiled: bool = True
    fork_bolts_oiled: bool = True
    decoupling_rail_oiled: bool = True
    elevator_assembly_oiled: bool = True

    class Config:
        orm_mode = True
        from_attributes = True


# BaseModel for OtherActionCheck
class OtherActionCheckBase(BaseModel):
    counterweight_adjusted: bool = True
    rope_count_checked: bool = True
    egrab_tension_checked: bool = True
    turn_buoys_checked: bool = True
    images: Optional[List[str]] = []

    class Config:
        orm_mode = True
        from_attributes = True


# BaseModel for MonthlyMaintenance
class MonthlyMaintenanceBase(BaseModel):
    carrier_checks: Optional[List[CarrierCheckBase]] = []
    function_checks: Optional[FunctionCheckBase] = None
    lubrication_checks: Optional[LubricationCheckBase] = None
    other_actions_checks: Optional[OtherActionCheckBase] = None

    class Config:
        orm_mode = True
        from_attributes = True


# BaseModel for ServiceLog
class ServiceLogBase(BaseModel):
    id: UUID
    date_of_service: datetime
    service_type: MaintenanceServiceType
    technician_name: str
    notes: str
    images: Optional[List[str]] = []
    service_details: Optional[dict] = None
    running_hours: float

    # References to Park and Cable
    park_id: str  # Assuming you're using string-based ObjectIds
    cable_id: str

    class Config:
        orm_mode = True
        from_attributes = True

    # Validator for ObjectId conversion
    @validator('id', 'park_id', 'cable_id', pre=True, always=True)
    def validate_object_ids(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value


# BaseModel for Maintenance
class MaintenanceBase(BaseModel):
    last_service: datetime
    next_service: datetime
    last_reported_running_hours: int = 0
    current_estimated_running_hours: int = 0

    # This will be a list of references to service logs
    service_logs: Optional[List[str]] = []  # List of ServiceLog IDs (UUID or ObjectId strings)

    class Config:
        orm_mode = True
        from_attributes = True

    # Validator for ObjectId conversion
    @validator('service_logs', pre=True, always=True)
    def validate_service_log_ids(cls, value):
        if isinstance(value, list):
            return [str(v) if isinstance(v, ObjectId) else v for v in value]
        return value

    def save(self, park_id: str):
        """
        Save the MaintenanceBase instance to MongoDB.
        """
        try:
            # Convert the Pydantic model to a dictionary
            maintenance_data = self.dict(exclude={"service_logs"})

            # Check if the park exists
            existing_park = Park.objects(id=park_id).first()
            if not existing_park:
                raise DoesNotExist(f"Park with id {park_id} not found.")

            # Handle service logs separately
            saved_service_log_ids = []
            for log_id in self.service_logs:
                service_log = ServiceLog.objects(id=log_id).first()
                if service_log:
                    saved_service_log_ids.append(str(service_log.id))

            # Now include the service logs as a list of references
            maintenance_data['service_logs'] = saved_service_log_ids

            # Check if the park has existing maintenance, if yes, update it
            if existing_park.maintenance:
                existing_park.maintenance.update(**maintenance_data)
            else:
                # If no maintenance exists, create a new maintenance record
                new_maintenance = Maintenance(**maintenance_data)
                existing_park.maintenance = new_maintenance

            # Save the updated park document
            existing_park.save()

            print(f"Maintenance for park {park_id} saved to the database successfully")
        except Exception as e:
            print(f"Failed to save maintenance for park {park_id}: {e}")
            raise e
