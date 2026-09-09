#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import pandas as pd
import numpy as np

from vfworks.metamodels.model_structure import Inport, Outport
from vfworks.utils.constants import *


class DataLoader(object):
    def __init__(self,name="customLoader",validityframe = None,verbose=False):
        """Initialize a dataLoader component.

                Parameters
                ----------
                name : string
                    name of the property components

                verbose : bool
                    component verbose execution

                See Also
                --------
                ..

                Examples
                --------
                >> data_loader = dataLoader(verbose=False)

                """

        # --- dataLoader configuration ---
        self._name = name
        self._verbose = verbose
        self._validityframe = validityframe


    def loadData(self,experimentLabel=None,prefix="",type="pandas",shuffle=True):            #pandas dataframe | numpy | ...
        """Load the data as pandas DataFrame"""
        _data = None
        activeMS = self._validityframe.activeModelStructure
        _inputs_reference = []
        for port in activeMS.inports + activeMS.outports:
            #fetch measurements related to the input
            _input_data_ref = None
            _input_poi = port.mapping
            _poi_reference = []
            for experiment in self._validityframe.experiments:
                if experimentLabel == experiment.label or experimentLabel=="all" :                            #TODO: if multiple experiments have the same label, we need to concat the datapoints?
                    for measurement in experiment.measurements:
                        if measurement.poi ==_input_poi:
                            self._validityframe.logger.info(msg="Loaded data from experiment {"+experiment.name+","+experiment.GUID+"} measurement {"+measurement.name+","+measurement.GUID+"}, for PoI {"+_input_poi+"}")
                            _input_data_ref = prefix+measurement.reference
                            if _input_data_ref is not None:
                                _poi_reference.append(_input_data_ref)
            if len(_poi_reference) > 0:
                _inputs_reference.append(_poi_reference)

            #if _input_data_ref is not None:
            #    _inputs_reference.append(_input_data_ref)

        if type == "prepared_data_yaml":
            return _inputs_reference[0][0]
        if type == "pandas":
            _data = merge_csv_files_to_dataframe(_inputs_reference)
        if type == "numpy":
            _data = merge_csv_files_to_numpy_vstack(csv_files = _inputs_reference,shuffle=shuffle)
        return _data




def merge_csv_files_to_dataframe(csv_files=[]):
    """
    Reads multiple CSV files and merges them into a single Pandas DataFrame.
    Each file's content is placed in a separate column.

    :param csv_files: List of paths to the CSV files.
    :return: A Pandas DataFrame with each file as a separate column.
    """

    if not csv_files:
        raise ValueError("No CSV files found in the specified directory.")

    dataframes = []
    column_names = []

    for file_list in csv_files:
        df = pd.concat([pd.read_csv(path) for path in file_list], axis=0, ignore_index=True)  # Assumes header line in CSV files

        if df.shape[1] > 1:
            raise ValueError(f"CSV file '{file_list}' has more than one column, expected only one.")

        dataframes.append(df.squeeze())  # Convert single-column DataFrame to Series
        # column_names.append(file)

    merged_df = pd.concat(dataframes, axis=1)
    #merged_df.columns = column_names  # Use filenames as column names

    return merged_df

def merge_csv_files_to_numpy_vstack(csv_files=[],shuffle=True):
    """
    Reads multiple CSV files and merges them into a numpy vstack.

    :param csv_files: List of paths to the CSV files.
    :return: A Pandas DataFrame with each file as a separate column.
    """

    if not csv_files:
        raise ValueError("No CSV files found in the specified directory.")

    dataframes = []
    column_names = []

    dataset = []
    for file in csv_files:
        poi_dataset = []
        for data in file:
            _data = np.genfromtxt(data, delimiter=",", dtype="float64", filling_values=None)
            _data = np.delete(_data, 0)
            _data = np.array([np.array([row], dtype=object) for row in _data], dtype=object)
            poi_dataset.append(_data.data)
        poi_dataset = np.vstack(poi_dataset)
        dataset.append(poi_dataset.data)

    _data_stacked = np.hstack(dataset)
    if shuffle: np.random.shuffle(_data_stacked)  # Shuffle the dataset

    return _data_stacked.astype(np.float32)