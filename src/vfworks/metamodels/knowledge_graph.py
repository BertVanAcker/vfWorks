#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from neo4j import GraphDatabase
from typing import Dict, Any, Optional

class KnowledgeGraph:
    def __init__(self, uri, user, password):
        """Initialize Neo4j driver connection."""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._node_registry = {}  # Track {(label, key_prop): node_id}

    def add_node(self, node_data: Dict[str, Any]) -> str:
        """
        Create or update a node.
        
        Args:
            node_data: Dict with keys 'label' and 'properties'
                      Example: {'label': 'Monitor', 'properties': {'name': 'M1', 'status': 'VALID'}}
        
        Returns:
            Node identifier (for later relationship creation)
        """
        label = node_data['label']
        props = node_data['properties']
        
        with self.driver.session() as session:
            # MERGE ensures idempotency (no duplicates)
            # Assumes 'name' is unique identifier; adjust based on your entity types
            query = f"""
            MERGE (n:`{label}` {{name: $name}})
            SET n += $props
            RETURN elementId(n) as node_id, n
            """
            result = session.run(query, name=props.get('name'), props=props)
            record = result.single()
            node_id = record['node_id']
            
            # Store mapping for relationship lookups
            registry_key = (label, props.get('name'))
            self._node_registry[registry_key] = node_id
            
            return node_id

    def add_relationship(self, from_node_data: Dict, rel_type: str, to_node_data: Dict) -> None:
        """
        Create relationship between two nodes.
        
        Args:
            from_node_data: Source node dict
            rel_type: Relationship type (e.g., "OBSERVES")
            to_node_data: Target node dict
        """
        from_label = from_node_data['label']
        from_props = from_node_data['properties']
        to_label = to_node_data['label']
        to_props = to_node_data['properties']
        
        with self.driver.session() as session:
            query = f"""
            MATCH (from:`{from_label}` {{name: $from_name}})
            MATCH (to:`{to_label}` {{name: $to_name}})
            MERGE (from)-[r:{rel_type}]->(to)
            """
            session.run(
                query,
                from_name=from_props.get('name'),
                to_name=to_props.get('name')
            )

    def close(self):
        """Close the Neo4j connection."""
        self.driver.close()