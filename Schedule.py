import pandas as pd
from pathlib import Path
import numpy as np
from datetime import date
from math import ceil

class Schedule:

 def __init__(self, _path_string, _magic_number = 1.8, _first_date_str = "2018-03-29", _valid_num_of_days = 1000, _times_of_pratice = 10):

  self.path = _path_string
  self.magic_number = _magic_number
  self.first_date_str = _first_date_str
  self.valid_num_of_days = _valid_num_of_days
  self.times_of_pratice = _times_of_pratice

  if not Path(self.path).is_file():
   self.data = Schedule.__initialize(self.first_date_str, self.valid_num_of_days)
   print("No current file. Created schedule.csv")
  else:
   self.data = pd.read_csv(self.path)
   self.data = self.data.set_index(pd.DatetimeIndex(self.data['Date']))
   print("Loaded" + "path_string")
   self.data = Schedule.__pre_process_for_exists(self.data, self.first_date_str, self.valid_num_of_days)
   self.data_bak = pd.DataFrame.copy(self.data)


 def __initialize(first_date_str, valid_num_of_days):
  first_date = pd.to_datetime(first_date_str, format='%Y-%m-%d').date()
  dates = first_date + np.array([pd.DateOffset(days = date_offset) for date_offset in range(valid_num_of_days)])
  empty_lists = [[] for _ in dates]
  schedule = pd.DataFrame(data = {"Date" : dates, "Problems" : empty_lists, "Todo": empty_lists})
  schedule = schedule.set_index('Date')
  return schedule


 def __pre_process(schedule):
  schedule.Problems = schedule.Problems.apply(lambda x : x[1: -1])
  schedule.Problems = schedule.Problems.apply(lambda x : x.split(", ") if len(x) else [])
  schedule.Problems = schedule.Problems.apply(lambda n : [int(x) for x in n] if len(n) else [])
  schedule.Todo = schedule.Todo.apply(lambda x : x[1: -1])
  schedule.Todo = schedule.Todo.apply(lambda x : x.split(", ") if len(x) else [])
  schedule.Todo = schedule.Todo.apply(lambda n : [int(x) for x in n] if len(n) else [])
  return  schedule


 def __pre_process_for_exists(schedule, first_date_str, valid_num_of_days):
  dummy_schedule = Schedule.__initialize(first_date_str, valid_num_of_days)
  dummy_schedule = dummy_schedule.join(schedule, lsuffix='_a', rsuffix='_b')
  dummy_schedule['Problems_b'] = dummy_schedule['Problems_b'].apply(lambda x : [] if pd.isnull(x) else x)
  dummy_schedule['Todo_b'] = dummy_schedule['Todo_b'].apply(lambda x : [] if pd.isnull(x) else x)
  dummy_schedule.drop(columns = ['Problems_a', 'Todo_a', 'Date'], inplace = True)
  dummy_schedule.rename(lambda x : x[:-2], axis='columns', inplace = True)
  return dummy_schedule


 def __post_process(schedule):
  return schedule[(np.vectorize(len)(schedule["Problems"]) != 0) | (np.vectorize(len)(schedule["Todo"]) != 0)]


 def __put(schedule, problems, day, magic_number, times_of_pratice):
  date_offsets = [ceil(magic_number ** i) for i in range(times_of_pratice)]
  todo_days = day + np.array([pd.DateOffset(days = date_offset) for date_offset in date_offsets])
  Schedule.__insert(schedule, day, problems, 'Problems')
  for day in todo_days:
   Schedule.__insert(schedule,day, problems, 'Todo')


 def __insert(schedule, day, problems, field):
  if not schedule.loc[day.strftime('%Y-%m-%d'), field]:
   schedule.loc[day.strftime('%Y-%m-%d'), field] = list(problems)
  else:
   cur = [schedule.loc[day.strftime('%Y-%m-%d'), field]]
   for problem in problems:
    cur.append(problem)
   cur = set([int(n) for n in Schedule.__flatten(cur)])
   schedule.loc[day.strftime('%Y-%m-%d'), field] = list(cur)
  print(day.strftime('%Y-%m-%d'), 'added')


 def __get_problems():
  try:
   adds = input("Input problems to add (separated by spaces): e.g. 234 or 3 13 23: \n").split()
   adds = [int(add) for add in adds]
  except ValueError:
   print("Sorry, I didn't understand that.")
   return Schedule.__get_problems()
  return adds


 def __get_date():
  try:
   day = input("Input date (Enter for today): e.g. 2018-04-03: \n")
   if day == "":
    day = pd.to_datetime(date.today())
   else:
    day = pd.to_datetime(day, infer_datetime_format = True)
  except ValueError:
   print("Sorry, I didn't understand that.")
   return Schedule.__get_date()
  return day


 def __flatten(nums):
  if type(nums) == int:
   return [nums]
  ans = []
  for num in nums:
   ans += Schedule.__flatten(num)
  return ans


 def work_flow(self):
  self.data = Schedule.__pre_process(self.data)
  while True:
   problems = Schedule.__get_problems()
   day = Schedule.__get_date()
   input_key = input("Enter to complete. If you made some mistakes, press anykey to re-enter \n")
   if input_key == "":
    break
  Schedule.__put(self.data, problems, day, self.magic_number, self.times_of_pratice)
  self.data = Schedule.__post_process(self.data)
  if Path(self.path).is_file():
   self.data_bak = Schedule.__post_process(self.data_bak)
   self.data_bak.to_csv(self.path + '.bak')
  self.data.to_csv(self.path)
