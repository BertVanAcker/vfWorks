#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
class Standard:
    def __init__(self, name, purpose, domain,DOI=""):
        self.name = name
        self.purpose = purpose
        self.domain = domain
        self.DOI = DOI

    def create_neo4j_node(self):
        return {
            'label': 'Standard',
            'properties': {
                'name': self.name,
                'purpose': self.purpose,
                'domain': self.domain,
                'DOI': self.DOI
            }
        }




class Paragraph:
    def __init__(self, name):
        self.name = name

    def create_neo4j_node(self):
        return {
            'label': 'Paragraph',
            'properties': {
                'name': self.name
            }
        }

class Lifecycle:
    def __init__(self, name):
        self.name = name

    def create_neo4j_node(self):
        return {
            'label': 'Lifecycle',
            'properties': {
                'name': self.name
            }
        }

class Phase:
    def __init__(self, name):
        self.name = name

    def create_neo4j_node(self):
        return {
            'label': 'Phase',
            'properties': {
                'name': self.name
            }
        }

class Process:
    def __init__(self, name, objective, method):
        self.name = name
        self.objective = objective
        self.method = method

    def create_neo4j_node(self):
        return {
            'label': 'Process',
            'properties': {
                'name': self.name,
                'objective': self.objective,
                'method': self.method
            }
        }

class Metric:
    def __init__(self, name, description, target_value):
        self.name = name
        self.description = description
        self.target_value = target_value

    def create_neo4j_node(self):
        return {
            'label': 'Metric',
            'properties': {
                'name': self.name,
                'description': self.description,
                'target_value': self.target_value
            }
        }

class Property:
    def __init__(self, name, description, expected_value):
        self.name = name
        self.description = description
        self.expected_value = expected_value

    def create_neo4j_node(self):
        return {
            'label': 'Property',
            'properties': {
                'name': self.name,
                'description': self.description,
                'expected_value': self.expected_value
            }
        }

class VerificationAndValidation:
    def __init__(self, criteria, methods):
        self.criteria = criteria
        self.methods = methods

    def create_neo4j_node(self):
        return {
            'label': 'VerificationAndValidation',
            'properties': {
                'criteria': self.criteria,
                'methods': self.methods
            }
        }

class Role:
    def __init__(self, name, description, responsibility):
        self.name = name
        self.description = description
        self.responsibility = responsibility

    def create_neo4j_node(self):
        return {
            'label': 'Role',
            'properties': {
                'name': self.name,
                'description': self.description,
                'responsibility': self.responsibility
            }
        }

class Artifact:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def create_neo4j_node(self):
        return {
            'label': 'Artifact',
            'properties': {
                'name': self.name,
                'description': self.description
            }
        }

class Tool:
    def __init__(self, name, purpose, qualification_required):
        self.name = name
        self.purpose = purpose
        self.qualification_required = qualification_required

    def create_neo4j_node(self):
        return {
            'label': 'Tool',
            'properties': {
                'name': self.name,
                'purpose': self.purpose,
                'qualification_required': self.qualification_required
            }
        }
