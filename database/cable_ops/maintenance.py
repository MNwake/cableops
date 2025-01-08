from enum import Enum

from mongoengine import EmbeddedDocument, StringField, BooleanField, ListField, DateTimeField, EmbeddedDocumentField, \
    UUIDField, GenericEmbeddedDocumentField, IntField, Document, FloatField, ReferenceField


class MaintenanceServiceType(str, Enum):
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    ANNUAL = "Annual"
    INSPECTION = "Inspection"
    EMERGENCY_REPAIR = "Emergency Repair"
    NON_EMERGENCY_REPAIR = "Non-Emergency Repair"
    WATERWORK = "Waterwork"
    OTHER = "Other"



class EqualizeMaintenance(EmbeddedDocument):
    number_of_splices = IntField()
    distance_between_cables = IntField()
    images = ListField(StringField())  # URLs to images


class AnnualInspection(EmbeddedDocument):
    cables_inspected = BooleanField(default=True)
    cable_connections_inspected = BooleanField(default=True)
    ground_anchors_inspected = BooleanField(default=True)
    rigging_cables_inspected = BooleanField(default=True)
    shackles_inspected = BooleanField(default=True)
    carriers_inspected = BooleanField(default=True)


class TowerInspection(EmbeddedDocument):
    tower_id = StringField()
    liners_inspected = BooleanField(default=True)
    top_pulley_greased = BooleanField(default=True)
    bottom_pulley_greased = BooleanField(default=True)


class MotorTowerInspection(EmbeddedDocument):
    universal_joint_greased = BooleanField(default=True)
    ball_joints_greased = BooleanField(default=True)
    running_cable_splices_inspected = BooleanField(default=True)


class QuarterlyMaintenance(EmbeddedDocument):
    tower_inspections = ListField(EmbeddedDocumentField(TowerInspection))
    motor_tower_inspection = EmbeddedDocumentField(MotorTowerInspection)


class CarrierCheck(EmbeddedDocument):
    carrier_number = StringField()
    diagonals_pass = BooleanField(default=True)
    safety_pins_pass = BooleanField(default=True)
    clutch_strength_pass = BooleanField(default=True)
    clutch_ball_gap_pass = BooleanField(default=True)
    other_issues = StringField()
    actions_taken = StringField()
    images = ListField(StringField())  # URLs to images


class FunctionCheck(EmbeddedDocument):
    fork_catch_pass = BooleanField(default=True)
    decoupling_rail_pass = BooleanField(default=True)
    magazine_load_pass = BooleanField(default=True)
    emergency_stop_function_pass = BooleanField(default=True)


class LubricationCheck(EmbeddedDocument):
    loading_rod_oiled = BooleanField(default=True)
    fork_tube_oiled = BooleanField(default=True)
    fork_bolts_oiled = BooleanField(default=True)
    decoupling_rail_oiled = BooleanField(default=True)
    elevator_assembly_oiled = BooleanField(default=True)


class OtherActionCheck(EmbeddedDocument):
    counterweight_adjusted = BooleanField(default=True)
    rope_count_checked = BooleanField(default=True)
    egrab_tension_checked = BooleanField(default=True)
    turn_buoys_checked = BooleanField(default=True)
    images = ListField(StringField())  # URLs to other images


class MonthlyMaintenance(EmbeddedDocument):
    carrier_checks = ListField(EmbeddedDocumentField(CarrierCheck))
    function_checks = EmbeddedDocumentField(FunctionCheck)
    lubrication_checks = EmbeddedDocumentField(LubricationCheck)
    other_actions_checks = EmbeddedDocumentField(OtherActionCheck)

class ServiceLog(Document):
    id = UUIDField(binary=False, primary_key=True)  # Unique identifier for the log entry
    date_of_service = DateTimeField()
    service_type = StringField(choices=[m.value for m in MaintenanceServiceType])  # Store the service type as a string

    technician_name = StringField()
    notes = StringField()
    images = ListField(StringField())  # URLs to related images

    # Store service-specific details
    service_details = GenericEmbeddedDocumentField()
    running_hours = FloatField()

    # New references to the Park and Cable documents
    park = ReferenceField('Park', required=True)
    cable = ReferenceField('Cable', required=True)

    meta = {'db_alias': 'cable'}

class Maintenance(Document):
    park = ReferenceField('Park', required=True)
    last_service = DateTimeField()
    next_service = DateTimeField()
    last_reported_running_hours = IntField(default=0)
    current_estimated_running_hours = IntField(default=0)

    # Change service_logs to ReferenceField
    service_logs = ListField(ReferenceField(ServiceLog), default=list)

    meta = {'db_alias': 'cable'}