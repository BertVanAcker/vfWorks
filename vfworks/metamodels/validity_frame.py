#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import os
import json
import logging
from pathlib import Path
from vfworks.package.PackageManager import PackageManager
from vfworks.metamodels.knowledge_graph import KnowledgeGraph
from vfworks.metamodels.model_structure import *
from vfworks.metamodels.monitors import Monitor
from vfworks.metamodels.specification import *
from vfworks.metamodels.experiment import *
from vfworks.metamodels.properties import *
from vfworks.metamodels.common import *
from vfworks.utils.constants import StatusType
from vfworks.logging.logger import *
from vfworks.utils.model.modelLoader import *
import networkx as nx
import matplotlib.pyplot as plt
from termcolor import colored

class ValidityFrame(baseElement):
    def __init__(self, name='tbd',description='tbd',config=None,loadExistingVF=False,VFPackage=None, location=None,verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        # VF_BLDC HIGH-LEVEL STRUCTURE
        self._metadata = MetaData(name="metadata", description="tbd")
        self._operational = Operational(name="operational", description="tbd")
        self._processes = Processes(name="processes", description="tbd")
        self._experiments = Experiments(name="experiments", description="tbd")
        self._model_loader = ModelLoader(name="VF_model_loader", validityFrame=self)

        # PACKAGE AND LOGGER
        self._package_manager = PackageManager(verbose=verbose, packageName=VFPackage if VFPackage else ".")
        if config is None:
            self.config = self._package_manager.init_config(VFPackage)
        else:
            self.config = self._package_manager.load_config(config)
        if VFPackage is None or VFPackage == "":
            self._package_manager.create(name=VFPackage, force=False, config=self.config, standalone=False, path=location)
        else:
            self._package_manager.create(name=VFPackage, force=False, config=self.config, standalone=True, path=location)
        self.logger = self.initialize_logger(VFPackage)
        # LOAD VF from package or initialize as new
        if loadExistingVF:
            if VFPackage== "":
                self.logger.info(msg="Loading validity frame from current workdir")
            else:
                self.logger.info(msg="Loading validity frame from package {" + VFPackage + "}")
            prefix = "." if VFPackage == "" else VFPackage
            if location is not None:
                prefix = location + prefix
            #load different elements
            self._metadata.json2object(fileName=Path(prefix+"/Metadata/Metadata.json"))
            self._operational.json2object(fileName=Path(prefix+"/Operational/Operational.json"), metadata=self._metadata, packageName=VFPackage)
            #self._processes.json2object(fileName=VFPackage+"Metadata/Metadata.json")
            self._experiments.json2object(fileName=Path(prefix+"/Experiments/Experiments.json"))

        else:
            self.logger.info(msg="New validityFrame initialized with GUID {"+self.GUID+"}")
            self.export(packageName=VFPackage if VFPackage else ".")

    @property
    def package_manager(self):
        return self._package_manager

    # -----------------------------------------
    #           METADATA
    # -----------------------------------------
    @property
    def specifications(self):
        return self._metadata._specifications

    @specifications.setter
    def specifications(self, value):
        self._metadata._specifications = value

    def addSpecification(self, spec):
        self._metadata._specifications.append(spec)

    @property
    def properties(self):
        return self._metadata.properties

    @properties.setter
    def properties(self, value):
        self._metadata.properties = value

    def addProperty(self, prop):
        self.logger.info(msg="Adding a property of interest to the validity frame with GUID {"+prop.GUID+"}")
        self._metadata.addProperty(prop)

    def getPropertyByGUID(self,guid):
        _prop = None
        for prop in self.properties:
            if prop.guid == guid:
                _prop = prop
        return _prop

    # -----------------------------------------
    #           EXPERIMENTS
    # -----------------------------------------
    @property
    def experiments(self):
        return self._experiments.experiments

    @experiments.setter
    def experiments(self, value):
        self._experiments.experiments = value

    def addExperiment(self, experiment):
        self._experiments.experiments.append(experiment)

    def assign_poi2measurement(self,poi,measurementName):
        for exp in self.experiments:
            for measurement in exp.measurements:
                if measurementName == measurement.name:
                    self.logger.info(msg="Assign PoI with GUID {"+poi.GUID+"} to measurement with GUID {"+measurement.GUID+"")
                    measurement.poi = poi.GUID

    # -----------------------------------------
    #           OPERATIONAL
    # -----------------------------------------
    @property
    def modelReference(self):
        return self._operational.activeModelStructure.modelRef   #CAN EITHER BE A SINGLE FILE OF A FOLDER WITH MULTIPLE FILES

    @modelReference.setter
    def modelReference(self, value):
        self.logger.info(msg="Adding a model reference ("+value+") to the active model structure of the validity frame")
        self._operational.activeModelStructure.modelRef = value

    @property
    def modelStructures(self):
        return self._operational.modelStructures
    
    def get_current_active_model(self):
        prefix = self.package_manager.packageName +"/Sources/"
        model_ref = prefix + self.modelReference
        model = self._model_loader.loadModel(model_location=model_ref, type=self._operational.activeModelStructure._modelType)
        return model
    
    def getModelStructureByGUID(self,GUID):
        _structure = None
        for structure in self.modelStructures:
            if structure.GUID == GUID:
                _structure = structure
        return _structure

    def setActiveModelStructure(self, GUID=None, name=None):
        if name is not None:
            self._operational.setActiveModelStructureByName(name=name)
        else:
            self._operational.setActiveModelStructure(GUID=GUID)


    @property
    def activeModelStructure(self):
        return self._operational.activeModelStructure

    @modelStructures.setter
    def modelStructures(self, value):
        self.logger.info(msg="Adding a set of model structures to the validity frame")
        self._operational.modelStructure = value

    def addModelStructure(self,structure):
        self.logger.info(msg="Adding a model structure with GUID {"+structure.GUID+" to the validity frame")
        self._operational.addModelStructure(structure)

    #-----------------------------------------
    #           PROCESSES
    #-----------------------------------------
    @property
    def processes(self):
        return self._processes.processes

    @processes.setter
    def processes(self, value):
        self._processes.processes = value

    def addProcess(self, process):
        self._processes.addProcess(process)

    # -----------------------------------------
    #        MONITORS
    #        Currently stored in Operational
    # -----------------------------------------

    @property
    def runtime_monitors(self):
        return self._operational.runtime_monitors

    @runtime_monitors.setter
    def runtime_monitors(self, value):
        self._operational.runtime_monitors = value

    @property
    def design_time_monitors(self):
        return self._operational.design_time_monitors

    @design_time_monitors.setter
    def design_time_monitors(self, value):
        self._operational.design_time_monitors = value

    def addMonitor(self, monitor):
        monitor.packageName = self.package_manager.packageName
        monitor.setup()
        self._operational.addMonitor(monitor)

    # ------------------------------------------------------------------------------------------------------------------
    #                                           LOGGING FUNCTIONS
    # -----------------------------------------------------------------------------------------------------------------
    def load_config(self, config_file):
        return self._package_manager.load_config(config_file)

    def initialize_logger(self, packageName):
        """Initialize the logger (same as before)."""
        log_config = self.config.get("logging", {})
        logger = logging.getLogger(self.__class__.__name__)
        log_level = log_config.get("level", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_file = log_config.get("file", None)
        if packageName:
            log_file = os.path.join(packageName, log_file)

        formatter = logging.Formatter(log_format)

        if log_file:
            try:
                file_handler = logging.FileHandler(log_file)    #LOAD FROM PACKAGE LEVEL
            except:
                file_handler = logging.FileHandler("../"+log_file)  #LOAD FROM FOLDER LEVEL (e.g. in processes)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger


    #------------------------------------------------------------------------------------------------------------------
    #                                           TRACE FUNCTIONS
    # -----------------------------------------------------------------------------------------------------------------

    def check_specifications(self):

        # 0. CHECK ALL MONITORS AND PROPAGATE
        for monitor in self.runtime_monitors + self.design_time_monitors:
            specs = monitor.observes
            _status = monitor.status
            for spec in specs:
                spec.status = _status

        # 1. PRINT STATUS OF SPECIFICATIONS
        if self._verbose:
            for spec in self._metadata.specifications:
                print("Specification " + spec.name + " - STATUS: " + str(spec.status))

    def neo4j_export(self):
        kg = KnowledgeGraph(uri="bolt://localhost:7687", user="neo4j", password="hallo123")

        for monitor in self.runtime_monitors + self.design_time_monitors:
            monitor_node_data = monitor.create_neo4j_node()
            curr_monitor_node = kg.add_node(monitor_node_data)
            for spec in monitor.observes:
                spec_node_data = spec.create_neo4j_node()
                curr_spec_node = kg.add_node(spec_node_data)
                kg.add_relationship(monitor_node_data, "OBSERVES", spec_node_data)
                for property in self.properties:
                    if spec.GUID in property.satisfies:
                        property_node_data = property.create_neo4j_node()
                        curr_property_node = kg.add_node(property_node_data)
                        kg.add_relationship(spec_node_data, "SATISFIED_BY", property_node_data)

    def graphify(self, figsize=(14, 10), align='vertical'):
        G = nx.DiGraph()

        def add_typed_node(node_name, node_type, status=None, layer=0, **attributes):
            G.add_node(node_name, type=node_type, status=status, layer=layer, **attributes)

        specification_by_guid = {spec.GUID: spec for spec in self._metadata.specifications}

        # Add specifications, properties, and monitors as nodes
        for prop in self._metadata.properties:
            add_typed_node(prop.name, 'property', layer=1, satisfies=prop.satisfies, guid=prop.GUID)
        for monitor in self.runtime_monitors + self.design_time_monitors:
            add_typed_node(monitor.name, 'monitor', status=monitor.status, layer=2, guid=monitor.GUID)
            for spec in monitor.observes:
                add_typed_node(spec.name, 'specification', status=monitor.spec_status[spec.feature], layer=0, guid=spec.GUID)  # Ensure observed specs are added as nodes
        for spec in self._metadata.specifications:
            add_typed_node(spec.name, 'specification', status=spec.status, layer=0, guid=spec.GUID)
            add_typed_node(spec.value.tostring(), 'value', layer=1, guid=spec.GUID)  # Add value as a separate node

        # Add edges based on which monitors check which specifications

        # Add edges based on wich spec is tied to which property

        # Add edges based on which monitor is tied to which property

        # Link specifications to the properties that satisfy them so descendant coloring can propagate.
        for prop in self._metadata.properties:
            for spec_guid in prop.satisfies:
                spec = specification_by_guid.get(spec_guid)
                if spec is not None:
                    G.add_edge(prop.name, spec.name)
                    G.add_edge(spec.value.tostring(), spec.name)
                for monitor in self.runtime_monitors + self.design_time_monitors:
                    if spec in monitor.observes:
                        G.add_edge(prop.name, monitor.name)
                        G.add_edge(spec.value.tostring(), monitor.name)
        
        invalid_monitors = set()
        valid_monitors = set()
        invalid_descendants = set()
        valid_descendants = set()
        for prop in self._metadata.properties:
            for spec_guid in prop.satisfies:
                for monitor in self.runtime_monitors + self.design_time_monitors:
                    if spec_guid in [s.GUID for s in monitor.observes]:
                        spec = specification_by_guid.get(spec_guid)
                        if monitor.status == StatusType.INVALID:
                            invalid_monitors.add(monitor.name)
                            invalid_descendants.add(prop.name)
                        elif monitor.status == StatusType.VALID:
                            valid_monitors.add(monitor.name)
                            valid_descendants.add(prop.name)
                        if monitor.spec_status[spec.feature] == StatusType.INVALID:
                            invalid_descendants.add(spec.name)
                            invalid_descendants.add(spec.value.tostring())
                        elif monitor.spec_status[spec.feature] == StatusType.VALID:
                            valid_descendants.add(spec.name)
                            valid_descendants.add(spec.value.tostring())

        node_colors = []
        for node_name in G.nodes:

            if node_name in invalid_monitors:
                node_colors.append('#d73027')
            elif node_name in invalid_descendants: 
                node_colors.append('#fc8d59')
            elif node_name in valid_monitors:
                node_colors.append('#1a9850')
            elif node_name in valid_descendants:
                node_colors.append('#66bd63')
            else:
                node_colors.append('#cce5ff')

        pos = nx.multipartite_layout(G, subset_key='layer', align=align)

        plt.figure(figsize=figsize)
        nx.draw(
            G,
            pos=pos,
            with_labels=True,
            node_color=node_colors,
            node_size=2200,
            font_size=9,
            arrows=True,
            arrowstyle='-|>',
            arrowsize=16,
            width=1.2,
            alpha=0.9
        )
        plt.tight_layout()
        plt.show()
        
        return G
    
    def export_graph_json(self, file_name="validity_frame_graph.json"):
        """
        Export the graph to a JSON file.
        """
        G = self.graphify()  # Ensure the graph is up-to-date before exporting
        # Convert the graph to a dictionary
        graph_dict = nx.node_link_data(G)
        
        # Write the dictionary to a JSON file
        with open(file_name, 'w') as f:
            json.dump(graph_dict, f)

    # ------------------------------------------------------------------------------------------------------------------
    #                                           IMPORT/EXPORT FUNCTIONS
    # -----------------------------------------------------------------------------------------------------------------
    def export(self,packageName=None):
        if packageName is None:
            #export called in VF_BLDC package, no prefix needed
            self._metadata.object2json("Metadata/Metadata.json")
            self._processes.object2json("Processes/Processes.json")
            self._experiments.object2json("Experiments/Experiments.json")
            self._operational.object2json("Operational/Operational.json")
            x=1
        else:
            self._metadata.object2json(Path(packageName + "/Metadata/Metadata.json"))
            self._processes.object2json(Path(packageName + "/Processes/Processes.json"))
            self._experiments.object2json(Path(packageName + "/Experiments/Experiments.json"))
            self._operational.object2json(Path(packageName + "/Operational/Operational.json"))
            x=1


class MetaData(baseElement):
    def __init__(self, name='tbd',description='tbd',specifications=None,properties=None,verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        if specifications is None:
            self._specifications = []
        else:
            self._specifications = specifications
        if properties is None:
            self._properties = []
        else:
            self._properties = properties

    @property
    def specifications(self):
        return self._specifications

    @specifications.setter
    def specifications(self, value):
        self._specifications = value

    def addSpecification(self, spec):
        self._specifications.append(spec)

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value

    def addProperty(self, spec):
        self._properties.append(spec)

    def object2json(self, fileName):
        """
           Function to generate a json file
        """
        data = json.dumps(self, default=lambda o: o.__dict__, indent=4)
        with open(fileName, 'w', encoding='utf-8') as f:
            f.write(data)

    def json2object(self, fileName):
        """
           Function to generate object from a json file
        """
        # --- read stored requirements ---
        available = False
        try:
            f = open(fileName)
            data = json.load(f)
            available = True
        except:
            print(colored('ERROR: ', 'red'), colored('Stored metadata cannot be read!', 'black'))

        if available:
            #add specifications
            for spec in data['_specifications']:
                s = Specification(name=spec['_name'], description=spec['_description'], feature=spec['_feature'])
                value = spec['_value']
                s.type = spec['_type']
                if spec["_type"] == PropertyType.PROPERTY_RANGE:
                    s.value = ValueRange(valueMin=value["_valueMin"], valueMax=value["_valueMax"], granularity=value["_granularity"])
                if spec["_type"] == PropertyType.PROPERTY_MEAN:
                    s.value = AverageValue(average=value["_average"], deviation=value["_deviation"])
                if spec["_type"] == PropertyType.PROPERTY_MIN:
                    s.value = ValueMin(valueMin=value["_valueMin"])
                if spec["_type"] == PropertyType.PROPERTY_MAX:
                    s.value = ValueMax(valueMax=value["_valueMax"])
                if spec["_type"] == PropertyType.PROPERTY_CUSTOM:
                    s.value = ValueCustom(description=value["_description"])
                s.GUID = spec['_GUID']
                s.timestamp = spec['_timestamp']
                self.addSpecification(s)
            #add properties
            for prop in data["_properties"]:
                p = PropertyofInterest(name=prop["_name"], description=prop["_description"],domain=prop["_domain"], unit=prop["_unit"], datatype=prop["_datatype"],min=prop["_min"], max=prop["_max"])
                p.GUID = prop["_GUID"]
                p.timestamp = prop["_timestamp"]
                p.satisfies = prop["_satisfies"]    #TODO: Check if this is working => list of spec GUIDs
                self.addProperty(p)

class Operational(baseElement):
    def __init__(self, name='tbd',description='tbd',modelStructures=[],runtime_monitors=[], design_time_monitors=[],verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        self._modelStructures = modelStructures
        self._activeModelStructure = None
        self._modelReference = None
        self._runtime_monitors = runtime_monitors
        self._design_time_monitors = design_time_monitors

    @property
    def modelStructures(self):
        return self._modelStructures

    @modelStructures.setter
    def modelStructures(self, ref):
        self._modelStructures = ref

    @property
    def runtime_monitors(self):
        return self._runtime_monitors

    @runtime_monitors.setter
    def runtime_monitors(self, value):
        self._runtime_monitors = value

    @property
    def design_time_monitors(self):
        return self._design_time_monitors

    @design_time_monitors.setter
    def design_time_monitors(self, value):
        self._design_time_monitors = value

    def addModelStructure(self,s):
        self._modelStructures.append(s)

    def addMonitor(self, monitor):
        if monitor.type == MonitorTime.DATA_VALIDATION or monitor.type == MonitorTime.MODEL_VALIDATION:
            self.design_time_monitors.append(monitor)
        if monitor.type == MonitorTime.RUN_TIME:
            self.runtime_monitors.append(monitor)

    @property
    def activeModelStructure(self):
        return self._activeModelStructure

    def setActiveModelStructureByName(self,name=None):
        if name is None:
            self._activeModelStructure = self._modelStructures[0]
        else:
            for ms in self._modelStructures:
                if ms.name == name:
                    self._activeModelStructure = ms

    def setActiveModelStructure(self,GUID=None):
        if GUID is None:
            self._activeModelStructure = self.modelStructures[0]
        else:
            for ms in self._modelStructures:
                if ms.GUID == GUID:
                    self._activeModelStructure = ms


    def object2json(self, fileName):
        """
               Function to generate a json file
        """
        data = json.dumps(self, default=lambda o: o.__dict__, indent=4)
        with open(fileName, 'w', encoding='utf-8') as f:
            f.write(data)

    def json2object(self, fileName, metadata, packageName):
        """
           Function to generate object from a json file
        """
        # --- read stored requirements ---
        available = False
        try:
            f = open(fileName)
            data = json.load(f)
            available = True
        except:
            print(colored('ERROR: ', 'red'), colored('Stored operational data cannot be read!', 'black'))

        if available:

            #add model structure
            for ms in data["_modelStructures"]:
                # extract inputs
                _inputs = []
                for input in ms["_inports"]:
                    _input = Inport(name=input["_name"], description=input["_description"],domain=input["_domain"], unit=input["_unit"],datatype=input["_datatype"],min=input["_min"], max=input["_max"])
                    _input.GUID = input["_GUID"]
                    _input.timestamp = input["_timestamp"]
                    _input.mapping = input["_mapping"]
                    _inputs.append(_input)

                #extract outputs
                _outputs=[]
                for output in ms["_outports"]:
                    _output = Outport(name=output["_name"], description=output["_description"],domain=output["_domain"], unit=output["_unit"],datatype=output["_datatype"],min=output["_min"], max=output["_max"])
                    _output.GUID = output["_GUID"]
                    _output.timestamp = output["_timestamp"]
                    _output.mapping = output["_mapping"]
                    _outputs.append(_output)

                #extract paramaters
                #TODO: check if we need parameters? if yes, implement

                _ms = ModelStructure(name=ms["_name"], inports=_inputs, outports=_outputs, modelType=ms["_modelType"])
                _ms.GUID = ms["_GUID"]
                _ms.timestamp = ms["_timestamp"]
                _ms.modelRef = ms["_modelRef"]
                _ms.redundancy = ms["_redundancy"]
                self.addModelStructure(_ms)

            for monitor in data["_design_time_monitors"] + data["_runtime_monitors"]:
                specs = []
                for spec in monitor["observes"]:
                    for specification in metadata.specifications:
                        if specification.GUID == spec["_GUID"]:
                            specs.append(specification)
                _monitor = Monitor(name=monitor["_name"], description=monitor["_description"], observes=specs, monitor_time=monitor["_type"], status=monitor["_status"], spec_status=monitor["spec_status"], last_observed_values=monitor["last_observed_values"], packageName=packageName, custom_code_file=monitor["_custom_code_file"])
                _monitor._require_custom_code_file = monitor["_require_custom_code_file"]
                _monitor.GUID = monitor["_GUID"]
                _monitor.timestamp = monitor["_timestamp"]
                _monitor.setup()
                self.addMonitor(_monitor)

class Processes(baseElement):
    def __init__(self, name='tbd',description='tbd',processes=None,verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        if processes is None:
            self._processes = []
        else:
            self._processes = processes

    @property
    def processes(self):
        return self._processes

    @processes.setter
    def processes(self, value):
        self._processes = value

    def addProcess(self, process):
        self._processes.append(process)

    def object2json(self,fileName):
        """
               Function to generate a json file
        """
        data = json.dumps(self, default=lambda o: o.__dict__, indent=4)
        with open(fileName, 'w', encoding='utf-8') as f:
            f.write(data)

class Experiments(baseElement):
    def __init__(self, name='tbd',description='tbd',experiments=None,verbose=False):
        super().__init__(name=name, description=description, verbose=verbose)

        if experiments is None:
            self._experiments = []
        else:
            self._experiments = experiments

    @property
    def experiments(self):
        return self._experiments

    @experiments.setter
    def experiments(self, value):
        self._experiments = value

    def addExperiment(self, experiment):
        self._experiments.append(experiment)

    def object2json(self,fileName):
        """
               Function to generate a json file
        """
        data = json.dumps(self, default=lambda o: o.__dict__, indent=4)
        with open(fileName, 'w', encoding='utf-8') as f:
            f.write(data)

    def json2object(self, fileName):
        """
           Function to generate object from a json file
        """
        # --- read stored requirements ---
        available = False
        try:
            f = open(fileName)
            data = json.load(f)
            available = True
        except:
            print(colored('ERROR: ', 'red'), colored('Stored operational data cannot be read!', 'black'))

        if available:
            for experiment in data["_experiments"]:
                _experiment = Experiment(name=experiment["_name"], description=experiment["_description"], label=experiment["_label"])
                _experiment.GUID = experiment["_GUID"]
                _experiment.timestamp = experiment["_timestamp"]
                #add conditions
                for condition in experiment["_conditions"]:
                    _condition = ExperimentCondition(name=condition["_name"],description=condition["_description"], value=condition["_value"])
                    _condition.GUID = experiment["_GUID"]
                    _condition.timestamp = experiment["_timestamp"]
                    _experiment.addCondition(_condition)
                #add measurements
                for measurement in experiment["_measurements"]:
                    _measurement = Measurement(name=measurement["_name"],description=measurement["_description"],dataPoints=measurement["_dataPoints"],reference=measurement["_reference"])
                    _measurement.GUID = measurement["_GUID"]
                    _measurement.timestamp = measurement["_timestamp"]
                    _measurement.poi = measurement["_poi"]
                    _experiment.addMeasurement(_measurement)

                self.addExperiment(_experiment)
