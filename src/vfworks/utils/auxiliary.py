import pickle
from threading import Timer, Condition
import threading
import csv
from skl2onnx import to_onnx,convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

class perpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      #self.thread = Timer(self.t,self.handle_function)
      self.thread = Timer(self.t, self.handle_function)
      x=1

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

   def isAlive(self):
      return self.thread.is_alive()


def save_lists_to_csv(file_name, *lists, headers=None):
  """
  Saves multiple lists as columns in a single CSV file. Each list is treated as a column.

  Parameters:
  - file_name: str, name of the output CSV file
  - *lists: variable number of lists to store as columns in the CSV file
  - headers: list of str, optional, column headers for the CSV file

  Returns:
  - None
  """
  # Determine the maximum length of the lists
  max_length = max(len(lst) for lst in lists)

  # Pad shorter lists with empty strings to match the maximum length
  padded_lists = [list(lst) + [""] * (max_length - len(lst)) for lst in lists]

  # Transpose the lists so rows can be written correctly
  rows = zip(*padded_lists)

  # Write the rows to a CSV file
  with open(file_name, "w", newline="", encoding="utf-8") as file:
      writer = csv.writer(file)

      # Write headers if provided
      if headers:
          writer.writerow(headers)

      # Write the rows
      writer.writerows(rows)

def store_as_onnx(model, file_name,modelType="torch"):
    """Storing the model as a ONNX file"""

    if modelType == "torch":
        initial_type = [("input", FloatTensorType([None, 1]))]
        onnx_model = convert_sklearn(model=model,
                                    initial_types=initial_type,
                                    target_opset={"": 15,"ai.onnx.ml": 3})
        with open(file_name, "wb") as f:
            f.write(onnx_model.SerializeToString())
    else:
        print("Unsupported modelType {}".format(modelType))


def store_as_pickled(model, file_name,modelType="torch"):
    """Storing the model as a pickled object"""

    if modelType == "torch":
        with open(file_name, "wb") as f:
            pickle.dump(model, f)
    else:
        print("Unsupported modelType {}".format(modelType))

def load_model_from_pickle(file_name,modelType="torch"):

    """Loading the pickled model from file location"""
    if modelType == "torch":
        try:
            with open(file_name, "rb") as f:
                _loaded_model = pickle.load(f)
            return _loaded_model
        except:
            print("Failed to load model")
            return -1
    else:
        print("Unsupported modelType {}".format(modelType))
        return -1
