#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
from py2neo import Node, Relationship, Graph

class KnowledgeGraph:
    def __init__(self, uri, user, password):
        #self.graph = Graph(uri, auth=(user, password))
        self.graph = Graph(uri, user=user, password=password)

    def add_node(self, node):
        self.graph.create(node)
        return node

    def add_relationship(self, from_node, relationship_type, to_node):
        relationship = Relationship(from_node, relationship_type, to_node)
        self.graph.create(relationship)
