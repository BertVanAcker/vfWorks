from vfworks.metamodels.knowledge_graph import *
from vfworks.metamodels.standard import *

#----------------------------------------------------------------------------
#
#   THIS KNOWLEDGE GRAPH WILL BE GENERATED FROM THE PROVIDED EXCEL (WIP)
#
#----------------------------------------------------------------------------




kg = KnowledgeGraph(uri="bolt://localhost:7687", user="neo4j", password="hallo123")

# Create and add nodes
standard = Standard("FunctionalSafety", "Ensure functional safety in automotive systems", "Automotive")
standard_node = kg.add_node(standard.create_neo4j_node())

lifecycle = Lifecycle("Concept")
lifecycle_node = kg.add_node(lifecycle.create_neo4j_node())

phase = Phase("ConceptPhase")
phase_node = kg.add_node(phase.create_neo4j_node())

process = Process("HazardAnalysis", "Identify and evaluate potential hazards", "HARA (Hazard Analysis and Risk Assessment)")
process_node = kg.add_node(process.create_neo4j_node())

metric = Metric("RiskClassification", "Classify risks into ASIL levels", "ASIL A to D")
metric_node = kg.add_node(metric.create_neo4j_node())

property = Property("SafetyGoals", "Define safety goals for risk mitigation", "Complete and traceable safety goals")
property_node = kg.add_node(property.create_neo4j_node())

vv = VerificationAndValidation("Traceability and validation of safety goals", "Testing, Simulation, Review")
vv_node = kg.add_node(vv.create_neo4j_node())

role = Role("SafetyEngineer", "Responsible for defining and validating safety goals", "Safety goal creation, verification")
role_node = kg.add_node(role.create_neo4j_node())

artifact = Artifact("SafetyPlan", "Detailed plan for ensuring functional safety")
artifact_node = kg.add_node(artifact.create_neo4j_node())

tool = Tool("AnalysisTool", "Support hazard analysis and risk assessment", True)
tool_node = kg.add_node(tool.create_neo4j_node())

# Create relationships
kg.add_relationship(standard_node, "HAS_LIFECYCLE", lifecycle_node)
kg.add_relationship(lifecycle_node, "HAS_PHASE", phase_node)
kg.add_relationship(phase_node, "HAS_PROCESS", process_node)
kg.add_relationship(process_node, "HAS_METRIC", metric_node)
kg.add_relationship(process_node, "HAS_PROPERTY", property_node)
kg.add_relationship(standard_node, "HAS_VERIFICATION_AND_VALIDATION", vv_node)
kg.add_relationship(standard_node, "HAS_ROLE", role_node)
kg.add_relationship(standard_node, "HAS_ARTIFACT", artifact_node)
kg.add_relationship(standard_node, "HAS_TOOL", tool_node)