from threading import Timer, Condition
import threading
import csv
import struct

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
