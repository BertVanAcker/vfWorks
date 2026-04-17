#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from py2neo import Node
class Standard:
    def __init__(self, name, purpose, domain,DOI=""):
        self.name = name
        self.purpose = purpose
        self.domain = domain
        self.DOI = DOI

    def create_neo4j_node(self):
        return Node("Standard", name=self.name, purpose=self.purpose, domain=self.domain, DOI=self.DOI, viz_color="#3A86FF")




class Paragraph:
    def __init__(self, name):
        self.name = name

    def create_neo4j_node(self):
        return Node("Paragraph", name=self.name, viz_color="#4361EE")

class Lifecycle:
    def __init__(self, name):
        self.name = name

    def create_neo4j_node(self):
        return Node("Lifecycle", name=self.name, viz_color="#4CC9F0")

class Phase:
    def __init__(self, name):
        self.name = name

    def create_neo4j_node(self):
        return Node("Phase", name=self.name, viz_color="#4895EF")

class Process:
    def __init__(self, name, objective, method):
        self.name = name
        self.objective = objective
        self.method = method

    def create_neo4j_node(self):
        return Node("Process", name=self.name, objective=self.objective, method=self.method, viz_color="#560BAD")

class Metric:
    def __init__(self, name, description, target_value):
        self.name = name
        self.description = description
        self.target_value = target_value

    def create_neo4j_node(self):
        return Node("Metric", name=self.name, description=self.description, target_value=self.target_value, viz_color="#B5179E")

class Property:
    def __init__(self, name, description, expected_value):
        self.name = name
        self.description = description
        self.expected_value = expected_value

    def create_neo4j_node(self):
        return Node("Property", name=self.name, description=self.description, expected_value=self.expected_value, viz_color="#F4A261")

class VerificationAndValidation:
    def __init__(self, criteria, methods):
        self.criteria = criteria
        self.methods = methods

    def create_neo4j_node(self):
        return Node("VerificationAndValidation", criteria=self.criteria, methods=self.methods, viz_color="#2A9D8F")

class Role:
    def __init__(self, name, description, responsibility):
        self.name = name
        self.description = description
        self.responsibility = responsibility

    def create_neo4j_node(self):
        return Node("Role", name=self.name, description=self.description, responsibility=self.responsibility, viz_color="#FF006E")

class Artifact:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def create_neo4j_node(self):
        return Node("Artifact", name=self.name, description=self.description, viz_color="#FB8500")

class Tool:
    def __init__(self, name, purpose, qualification_required):
        self.name = name
        self.purpose = purpose
        self.qualification_required = qualification_required

    def create_neo4j_node(self):
        return Node("Tool", name=self.name, purpose=self.purpose, qualification_required=self.qualification_required, viz_color="#8338EC")
