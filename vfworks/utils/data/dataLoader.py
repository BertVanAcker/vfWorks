#***************************************************************************************
# * Copyright (C) 2024-present Bert Van Acker (UAntwerpen) <Bert.VanAcker@uantwerpen.be>
# *
# * This file is part of the vfWorks project.
# *
# * vfWorks can not be copied and/or distributed without the express
# * permission of Bert Van Acker
# **************************************************************************************
import pandas as pd
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


    def loadData(self,experimentLabel=None,prefix=""):
        """Load the data as pandas DataFrame"""
        _data = None
        activeMS = self._validityframe.activeModelStructure
        _inputs_reference = []
        for inport in activeMS.inports:
            #fetch measurements related to the input
            _input_data_ref = None
            _input_poi = inport.mapping
            for experiment in self._validityframe.experiments:
                if experimentLabel == experiment.label:                            #TODO: if multiple experiments have the same label, we need to concat the datapoints?
                    for measurement in experiment.measurements:
                        if measurement.poi ==_input_poi:
                            self._validityframe.logger.info(msg="Loaded data from experiment {"+experiment.name+","+experiment.GUID+"} measurement {"+measurement.name+","+measurement.GUID+"}, for PoI {"+_input_poi+"}")
                            _input_data_ref = prefix+measurement.reference

            if _input_data_ref is not None:
                _inputs_reference.append(_input_data_ref)

        _data = merge_csv_files_to_dataframe(_inputs_reference)
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

    for file in csv_files:
        df = pd.read_csv(file, header=None)  # Assumes no headers in CSV files

        if df.shape[1] > 1:
            raise ValueError(f"CSV file '{file}' has more than one column, expected only one.")

        dataframes.append(df.squeeze())  # Convert single-column DataFrame to Series
        column_names.append(file)

    merged_df = pd.concat(dataframes, axis=1)
    merged_df.columns = column_names  # Use filenames as column names

    return merged_df

# Example usage:
# df = merge_csv_files_to_dataframe("/path/to/csv_directory")
# print(df)
