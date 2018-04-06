import Schedule


def main():
 path_string = "./schedule.csv"
 schedule_obj = Schedule.Schedule(path_string)
 schedule_obj.work_flow()



if __name__ == "__main__":
    main()
