from vfworks.metamodels.experiment import Experiment, Measurement
from vfworks.metamodels.model_structure import Inport, ModelStructure, Outport
from vfworks.metamodels.monitors import Monitor
from vfworks.metamodels.properties import InfluenceFactor, PropertyofInterest
from vfworks.metamodels.specification import Specification
from vfworks.metamodels.validity_frame import ValidityFrame
from vfworks.utils.constants import DataType, DomainType, MonitorTime, PropertyType, UnitType

VF = ValidityFrame(name='VF_Forklift', description="Validity Frame for the forklift use case", VFPackage="VF_FORKLIFT")

EXP1 = Experiment(name='Initial_experiment', description="initial dataset for model training")
measurement = Measurement(name='images', dataPoints=[], reference="dataset_metadata.yaml")
EXP1.addMeasurement(measurement)

VF.addExperiment(EXP1)

# =============================================================================
# SPECIFICATIONS
# =============================================================================
#
# The specifications below correspond to REQ_1 ... REQ_19 in the DSL.
#
# PROPERTY_MIN / PROPERTY_MAX are used when the VFWorks property can naturally
# represent the requirement.
#
# PROPERTY_CUSTOM is used where the requirement contains additional semantics
# (ODD coverage, MMD, DINOv2, IoU, Cohen's Kappa, calibration method, etc.)
# that are not represented by the current VFWorks Specification API shown in
# the screw example.
#
# =============================================================================


# -----------------------------------------------------------------------------
# Accuracy
# -----------------------------------------------------------------------------

# REQ_1
#
# DSL:
#   accuracy >= 60 at validation
#
# Assuming the VF metric is normalized to [0,1], 60% is represented as 0.60.
# If "60" in the DSL is intended as the literal value 60, remove this
# normalization.
spec_model_accuracy = Specification(name="ModelAccuracy", description="REQ_1: Model accuracy >= 60% during validation", feature="accuracy", type=PropertyType.PROPERTY_MIN, valueMin=0.60)
# REQ_2
spec_pedestrian_recall = Specification(name="PedestrianRecall", description="REQ_2: Pedestrian detection recall >= 99% on validation data", feature="pedestrian_recall", type=PropertyType.PROPERTY_MIN, valueMin=0.99)
# REQ_3
spec_pedestrian_precision = Specification(name="PedestrianPrecision", description="REQ_3: Pedestrian detection precision >= 95% on validation data", feature="pedestrian_precision", type=PropertyType.PROPERTY_MIN, valueMin=0.95)
# -----------------------------------------------------------------------------
# Completeness
# -----------------------------------------------------------------------------
# REQ_4
spec_dataset_completeness = Specification(name="DatasetCompleteness", description="REQ_4: At least 100 samples for each detection class (forklift, goods, palletjack and person)", feature="dataset_class_sample_count", type=PropertyType.PROPERTY_MIN, valueMin=100)
# REQ_5
#
# The current VFWorks Specification interface does not have an explicit
# ODD-coverage property type, so keep this as a custom specification.
spec_odd_coverage = Specification(name="ODDCoverage", description="REQ_5: At least 95% of the defined WarehouseODD state space is represented in the CameraDataset", feature="odd_coverage", type=PropertyType.PROPERTY_CUSTOM)
# -----------------------------------------------------------------------------
# Representativeness
# -----------------------------------------------------------------------------
# REQ_6
spec_odd_representativeness = Specification(name="ODDRepresentativeness", description="REQ_6: At least 100 pedestrian instances shall be available for the represented ODD states in CameraDataset", feature="pedestrian_samples_per_odd_state", type=PropertyType.PROPERTY_MIN, valueMin=100)
# -----------------------------------------------------------------------------
# Independence
# -----------------------------------------------------------------------------
# REQ_7
spec_recording_separation = Specification(name="RecordingSeparation", description="REQ_7: Training, validation and test datasets must originate from separate recording sessions", feature="recording_session_separation", type=PropertyType.PROPERTY_CUSTOM)
# REQ_8
spec_cross_dataset_similarity = Specification(name="CrossDatasetSimilarity", description="REQ_8: DINOv2 embeddings across dataset partitions shall have cosine similarity <= 0.95", feature="cross_dataset_embedding_similarity", type=PropertyType.PROPERTY_CUSTOM)
# REQ_9
spec_dataset_leakage = Specification(name="DatasetLeakage", description="REQ_9: Maximum Mean Discrepancy (MMD) shall provide no statistically significant evidence of dataset leakage", feature="dataset_leakage", type=PropertyType.PROPERTY_CUSTOM)


# -----------------------------------------------------------------------------
# Correctness
# -----------------------------------------------------------------------------

# REQ_10
spec_annotation_audit = Specification(name="AnnotationAudit", description="REQ_10: Independently review 10% of annotations with an error rate <= 0.5%", feature="annotation_error_rate", type=PropertyType.PROPERTY_MAX, valueMax=0.005)
# REQ_11
spec_bounding_box_quality = Specification(name="BoundingBoxIoU", description="REQ_11: Mean bounding-box IoU shall be >= 0.95", feature="bounding_box_iou", type=PropertyType.PROPERTY_MIN, valueMin=0.95)
# REQ_12
spec_inter_annotator_agreement = Specification(name="InterAnnotatorAgreement", description="REQ_12: Cohen's Kappa shall be >= 0.90", feature="cohen_kappa", type=PropertyType.PROPERTY_MIN, valueMin=0.90)


# -----------------------------------------------------------------------------
# Robustness
# -----------------------------------------------------------------------------
# REQ_13
spec_shadow_recall = Specification(name="ShadowRecall", description="REQ_13: Pedestrian recall shall be >= 95% under the WarehouseODD.shadow condition", feature="pedestrian_recall", type=PropertyType.PROPERTY_MIN, valueMin=0.95)
# REQ_14
spec_pallet_proximity_recall = Specification(name="PalletProximityRecall", description="REQ_14: Pedestrian recall shall be >= 95% under the WarehouseODD.palletProximity condition", feature="pedestrian_recall", type=PropertyType.PROPERTY_MIN, valueMin=0.95)
# REQ_15
spec_shelf_proximity_recall = Specification(name="ShelfProximityRecall", description="REQ_15: Pedestrian recall shall be >= 95% under the WarehouseODD.shelfProximity condition", feature="pedestrian_recall", type=PropertyType.PROPERTY_MIN, valueMin=0.95)
# REQ_16
spec_partial_occlusion_recall = Specification(name="PartialOcclusionRecall", description="REQ_16: Pedestrian recall shall be >= 95% under the WarehouseODD.occlusion condition", feature="pedestrian_recall", type=PropertyType.PROPERTY_MIN, valueMin=0.95)
# -----------------------------------------------------------------------------
# Uncertainty / calibration
# -----------------------------------------------------------------------------
# REQ_17
#
# The DSL currently specifies FalsePositiveRate <= 0.05, even though the
# prose requirement calls for confidence calibration / ECE.
#
# Therefore this population faithfully represents the CURRENT DSL rather than
# silently changing it to ECE.
spec_confidence_calibration = Specification(name="ConfidenceCalibration", description=("REQ_17: False-positive rate shall be <= 5% " "(current DSL representation of confidence calibration)"), feature="false_positive_rate", type=PropertyType.PROPERTY_MAX, valueMax=0.05)
# -----------------------------------------------------------------------------
# Runtime monitoring
# -----------------------------------------------------------------------------
# REQ_18
#
# The DSL currently says "monitor accuracy", although the requirement name
# indicates image quality monitoring.
#
# Keep the actual semantic intent in the specification description and use a
# custom property.
spec_image_quality_monitoring = Specification(name="ImageQualityMonitoring", description=("REQ_18: Runtime image quality shall be monitored, including " "brightness, blur, overexposure, saturation and camera health"), feature="image_quality", type=PropertyType.PROPERTY_CUSTOM)
# REQ_19
spec_distribution_shift_monitoring = Specification(name="DistributionShiftMonitoring", description=("REQ_19: Runtime distribution shift shall be monitored using " "embedding/distribution-shift analysis"), feature="distribution_shift", type=PropertyType.PROPERTY_CUSTOM)
# Add all specifications to the VF
for spec in [
    spec_model_accuracy,
    spec_pedestrian_recall,
    spec_pedestrian_precision,
    spec_dataset_completeness,
    spec_odd_coverage,
    spec_odd_representativeness,
    spec_recording_separation,
    spec_cross_dataset_similarity,
    spec_dataset_leakage,
    spec_annotation_audit,
    spec_bounding_box_quality,
    spec_inter_annotator_agreement,
    spec_shadow_recall,
    spec_pallet_proximity_recall,
    spec_shelf_proximity_recall,
    spec_partial_occlusion_recall,
    spec_confidence_calibration,
    spec_image_quality_monitoring,
    spec_distribution_shift_monitoring
]:
    VF.addSpecification(spec)
# =============================================================================
# PROPERTIES OF INTEREST
# =============================================================================
#
# These represent measurable quantities that are relevant to validity.
#
# A particularly important distinction from the screw example:
#
#   - recall is a POI
#   - precision is a POI
#   - accuracy is a POI
#   - image / labels / detections are runtime POIs
#   - ODD variables are InfluenceFactors, not POIs
#
# =============================================================================
# -----------------------------------------------------------------------------
# Runtime POIs
# -----------------------------------------------------------------------------
poi_image = PropertyofInterest(name="Image", description="Input image from the ceiling camera", domain=DomainType.NONE, unit=UnitType.UNIT_none)
poi_detections = PropertyofInterest(name="Detections", description="Pedestrian and obstacle detections produced by the model", domain=DomainType.NONE, unit=UnitType.UNIT_none)
poi_confidence = PropertyofInterest(name="Confidence", description="Model confidence associated with detections", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64, min=0, max=1)
# -----------------------------------------------------------------------------
# Design-time / validation POIs
# -----------------------------------------------------------------------------
poi_accuracy = PropertyofInterest(name="Accuracy", description="Overall model accuracy during validation", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64, min=0, max=1, satisfies=[spec_model_accuracy])
poi_pedestrian_recall = PropertyofInterest(name="PedestrianRecall", description="Pedestrian detection recall", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64, min=0, max=1, satisfies=[spec_pedestrian_recall, spec_shadow_recall, spec_pallet_proximity_recall, spec_shelf_proximity_recall, spec_partial_occlusion_recall])
poi_pedestrian_precision = PropertyofInterest(name="PedestrianPrecision", description="Pedestrian detection precision", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64, min=0, max=1, satisfies=[spec_pedestrian_precision])
poi_dataset_completeness = PropertyofInterest(name="DatasetClassSampleCount", description="Number of samples available for each detection class", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.INTEGER_16, min=0, satisfies=[spec_dataset_completeness])
poi_odd_coverage = PropertyofInterest(name="ODDCoverage", description="Fraction of the defined WarehouseODD represented by the dataset", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64, min=0, max=1, satisfies=[spec_odd_coverage])
poi_odd_representativeness = PropertyofInterest(name="PedestrianSamplesPerODDState", description="Pedestrian instances available per represented ODD state", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.INTEGER_16, min=0, satisfies=[spec_odd_representativeness])
poi_annotation_error = PropertyofInterest(name="AnnotationErrorRate", description="Observed annotation error rate", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64, min=0, max=1, satisfies=[spec_annotation_audit])
poi_bounding_box_iou = PropertyofInterest(name="BoundingBoxIoU", description="Bounding box intersection-over-union", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64, min=0, max=1, satisfies=[spec_bounding_box_quality])
poi_cohen_kappa = PropertyofInterest(name="CohenKappa", description="Inter-annotator agreement measured using Cohen's Kappa", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64, min=-1, max=1, satisfies=[spec_inter_annotator_agreement])
poi_false_positive_rate = PropertyofInterest(name="FalsePositiveRate", description="False-positive rate used by the current REQ_17 DSL representation", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64, min=0, max=1, satisfies=[spec_confidence_calibration])
# Runtime monitoring-related POIs
poi_image_quality = PropertyofInterest(name="ImageQuality", description="Runtime image quality information including brightness, blur, overexposure and saturation", domain=DomainType.NONE, unit=UnitType.UNIT_none, satisfies=[spec_image_quality_monitoring])
poi_distribution_shift = PropertyofInterest(name="DistributionShift", description="Runtime distribution shift score", domain=DomainType.NONE, unit=UnitType.UNIT_none, satisfies=[spec_distribution_shift_monitoring])
# Add POIs to VF
for poi in [
    poi_image,
    poi_detections,
    poi_confidence,
    poi_accuracy,
    poi_pedestrian_recall,
    poi_pedestrian_precision,
    poi_dataset_completeness,
    poi_odd_coverage,
    poi_odd_representativeness,
    poi_annotation_error,
    poi_bounding_box_iou,
    poi_cohen_kappa,
    poi_false_positive_rate,
    poi_image_quality,
    poi_distribution_shift
]:
    VF.addProperty(poi)
# =============================================================================
# INFLUENCE FACTORS -- WAREHOUSE ODD
# =============================================================================
#
# These are deliberately NOT specifications.
#
# They describe dimensions of the operating environment that can influence
# model validity.
#
# The current VFWorks API shown in the screw example does not demonstrate
# categorical/enum values, so the categorical factors are represented as
# custom/unbounded influence factors with the state space captured in their
# descriptions.
#
# =============================================================================
if_light = InfluenceFactor(name="Lighting", description="Warehouse lighting state: Normal or Dark", domain=DomainType.NONE, unit=UnitType.UNIT_none)
if_sunlight = InfluenceFactor(name="Sunlight", description="Sunlight state: Absent or Present", domain=DomainType.NONE, unit=UnitType.UNIT_none)
if_shadow = InfluenceFactor(name="Shadow", description="Shadow state: Absent or Present", domain=DomainType.NONE, unit=UnitType.UNIT_none)
if_pedestrian_count = InfluenceFactor(name="PedestrianCount", description="Pedestrian count state: One or Multiple", domain=DomainType.NONE, unit=UnitType.UNIT_none)
if_occlusion = InfluenceFactor(name="Occlusion", description="Pedestrian occlusion state: None or Partial", domain=DomainType.NONE, unit=UnitType.UNIT_none)
if_pedestrian_location = InfluenceFactor(name="PedestrianLocation", description="Pedestrian location state: Centre or Edge", domain=DomainType.NONE, unit=UnitType.UNIT_none)
if_pallet_proximity = InfluenceFactor(name="PalletProximity", description="Pedestrian/pallet proximity state: Near/Far", domain=DomainType.NONE, unit=UnitType.UNIT_none)
if_shelf_proximity = InfluenceFactor(name="ShelfProximity", description="Pedestrian/shelf proximity state: Near/Far", domain=DomainType.NONE, unit=UnitType.UNIT_none)
if_door_state = InfluenceFactor(name="DoorState", description="Warehouse door state: Open or Closed", domain=DomainType.NONE, unit=UnitType.UNIT_none)
if_forklift_speed = InfluenceFactor(name="ForkliftSpeed", description="Forklift speed, validated ODD range 0..1.5 m/s", domain=DomainType.NONE, unit=UnitType.UNIT_none, datatype=DataType.FLOAT_64, min=0, max=1.5)
# Add ODD influence factors
for factor in [
    if_light,
    if_sunlight,
    if_shadow,
    if_pedestrian_count,
    if_occlusion,
    if_pedestrian_location,
    if_pallet_proximity,
    if_shelf_proximity,
    if_door_state,
    if_forklift_speed
]:
    VF.addProperty(factor)
# =============================================================================
# POI -> EXPERIMENT MEASUREMENT LINKING
# =============================================================================
#
# These measurement names are placeholders until the actual experiment/data
# schema is known.
#
# =============================================================================

VF.assign_poi2measurement(poi=poi_image,measurementName="images")
VF.assign_poi2measurement(poi=poi_detections,measurementName="detections")
VF.assign_poi2measurement(poi=poi_confidence,measurementName="confidence")
# =============================================================================
# MODEL STRUCTURE
# =============================================================================

IN1 = Inport(name="image", description="Input image from ceiling camera")
IN1.add_mapping_relation(type="poi",poi=poi_image)
OUT1 = Outport(name="detections", unit=UnitType.UNIT_none)
OUT1.add_mapping_relation(type="poi",poi=poi_detections)
OUT2 = Outport(name="confidence", unit=UnitType.UNIT_none)

OUT2.add_mapping_relation(type="poi",poi=poi_confidence)


SM = ModelStructure(name="ForkliftDetectionModel", inports=[IN1], outports=[OUT1, OUT2], modelType="monitoredModel", modelRef="best.pt")

VF.addModelStructure(SM)


# =============================================================================
# MONITORS
# =============================================================================
#
# Important distinction:
#
#   DATA_VALIDATION:
#       dataset properties such as sample count, coverage, representativeness
#
#   MODEL_VALIDATION:
#       accuracy / recall / precision / annotation quality
#
#   RUN_TIME:
#       actual runtime-observable quantities
#
# ODD variables such as "occlusion" are NOT automatically given runtime
# monitors simply because they appear in the ODD.
#
# =============================================================================


# -----------------------------------------------------------------------------
# Dataset validation
# -----------------------------------------------------------------------------
monitor_dataset_completeness = Monitor(name="DatasetCompletenessMonitor", description="Checks class sample-count requirements", observes=[spec_dataset_completeness], monitor_time=MonitorTime.DATA_VALIDATION)
monitor_odd_coverage = Monitor(name="ODDCoverageMonitor", description="Checks coverage of the defined WarehouseODD", observes=[spec_odd_coverage], monitor_time=MonitorTime.DATA_VALIDATION)
monitor_odd_representativeness = Monitor(name="ODDRepresentativenessMonitor", description="Checks pedestrian samples available for represented ODD states", observes=[spec_odd_representativeness], monitor_time=MonitorTime.DATA_VALIDATION)
monitor_recording_separation = Monitor(name="RecordingSeparationMonitor", description="Checks that recording sessions are separated between partitions", observes=[spec_recording_separation], monitor_time=MonitorTime.DATA_VALIDATION)
monitor_cross_dataset_similarity = Monitor(name="CrossDatasetSimilarityMonitor", description=("Checks cross-partition image embedding similarity using DINOv2 " "and cosine similarity"), observes=[spec_cross_dataset_similarity], monitor_time=MonitorTime.DATA_VALIDATION, custom_code_file="cross_dataset_similarity_monitor.py")
monitor_dataset_leakage = Monitor(name="DatasetLeakageMonitor", description="Checks dataset leakage using Maximum Mean Discrepancy (MMD)", observes=[spec_dataset_leakage], monitor_time=MonitorTime.DATA_VALIDATION, custom_code_file="mmd_dataset_leakage_monitor.py")
monitor_annotation_audit = Monitor(name="AnnotationAuditMonitor", description="Checks annotation audit error rate", observes=[spec_annotation_audit], monitor_time=MonitorTime.DATA_VALIDATION)
monitor_bounding_box_iou = Monitor(name="BoundingBoxIoUMonitor", description="Checks bounding-box IoU quality", observes=[spec_bounding_box_quality], monitor_time=MonitorTime.DATA_VALIDATION)
monitor_inter_annotator_agreement = Monitor(name="InterAnnotatorAgreementMonitor", description="Checks Cohen's Kappa", observes=[spec_inter_annotator_agreement], monitor_time=MonitorTime.DATA_VALIDATION)
# -----------------------------------------------------------------------------
# Model validation
# -----------------------------------------------------------------------------
monitor_model_accuracy = Monitor(name="ModelAccuracyMonitor", description="Checks overall model accuracy", observes=[spec_model_accuracy], monitor_time=MonitorTime.MODEL_VALIDATION)
monitor_pedestrian_performance = Monitor(name="PedestrianPerformanceMonitor", description="Checks pedestrian recall and precision requirements", observes=[spec_pedestrian_recall, spec_pedestrian_precision], monitor_time=MonitorTime.MODEL_VALIDATION)
monitor_shadow_recall = Monitor(name="ShadowRecallMonitor", description="Checks pedestrian recall under shadow conditions", observes=[spec_shadow_recall], monitor_time=MonitorTime.MODEL_VALIDATION, custom_code_file="odd_condition_monitor.py")
monitor_pallet_proximity_recall = Monitor(name="PalletProximityRecallMonitor", description="Checks pedestrian recall under pallet proximity conditions", observes=[spec_pallet_proximity_recall], monitor_time=MonitorTime.MODEL_VALIDATION, custom_code_file="odd_condition_monitor.py")
monitor_shelf_proximity_recall = Monitor(name="ShelfProximityRecallMonitor", description="Checks pedestrian recall under shelf proximity conditions", observes=[spec_shelf_proximity_recall], monitor_time=MonitorTime.MODEL_VALIDATION, custom_code_file="odd_condition_monitor.py")
monitor_partial_occlusion_recall = Monitor(name="PartialOcclusionRecallMonitor", description="Checks pedestrian recall under occlusion conditions", observes=[spec_partial_occlusion_recall], monitor_time=MonitorTime.MODEL_VALIDATION, custom_code_file="odd_condition_monitor.py")
monitor_confidence_calibration = Monitor(name="ConfidenceCalibrationMonitor", description="Checks the current DSL representation of the confidence requirement", observes=[spec_confidence_calibration], monitor_time=MonitorTime.MODEL_VALIDATION, custom_code_file="confidence_calibration_monitor.py")
# -----------------------------------------------------------------------------
# Runtime
# -----------------------------------------------------------------------------
#
# REQ_18 and REQ_19 are intentionally represented as custom monitors because
# the current DSL's "monitor accuracy" syntax does not capture the actual
# metrics named in the safety requirement.
# -----------------------------------------------------------------------------
monitor_image_quality = Monitor(name="ImageQualityRuntimeMonitor", description="Continuously monitors runtime image brightness, blur, overexposure, saturation and camera health", observes=[spec_image_quality_monitoring], monitor_time=MonitorTime.RUN_TIME, custom_code_file="image_quality_monitor.py")
monitor_distribution_shift = Monitor(name="DistributionShiftRuntimeMonitor", description="Continuously monitors runtime distribution shift using image embeddings and a distribution-shift/OOD metric", observes=[spec_distribution_shift_monitoring], monitor_time=MonitorTime.RUN_TIME, custom_code_file="distribution_shift_monitor.py")
monitor_runtime_confidence = Monitor(name="RuntimeConfidenceMonitor", description="Monitors runtime model confidence", observes=[spec_confidence_calibration], monitor_time=MonitorTime.RUN_TIME, custom_code_file="confidence_monitor.py")
# Add monitors
for monitor in [
    monitor_dataset_completeness,
    monitor_odd_coverage,
    monitor_odd_representativeness,
    monitor_recording_separation,
    monitor_cross_dataset_similarity,
    monitor_dataset_leakage,
    monitor_annotation_audit,
    monitor_bounding_box_iou,
    monitor_inter_annotator_agreement,

    monitor_model_accuracy,
    monitor_pedestrian_performance,
    monitor_shadow_recall,
    monitor_pallet_proximity_recall,
    monitor_shelf_proximity_recall,
    monitor_partial_occlusion_recall,
    monitor_confidence_calibration,

    monitor_image_quality,
    monitor_distribution_shift,
    monitor_runtime_confidence
]:
    VF.addMonitor(monitor)


# =============================================================================
# EXPORT
# =============================================================================

packageName = "VF_FORKLIFT"

VF.export(packageName=packageName)
VF.export_graph_json()

print("Successfully generated " + packageName)
