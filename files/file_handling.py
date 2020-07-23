import os
import pickle

from gym_files.gym_objects import Routine


def write_file(file, contents):
    with open(file, "wb") as f:
        pickle.dump(contents, f)


def read_file(file):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        with open(file, "rb") as f:
            contents = pickle.load(f)
            return contents
    return None


def save_new_routine(file, contents, old_routine=None, overwrite=False):
    routines = []
    number = 0
    if os.path.exists(file) and not overwrite and os.path.getsize(file) > 0:
        routines = read_file(file)
        if old_routine is not None:
            number = old_routine.number
            for routine in routines:
                if routine.number == old_routine.number:
                    routines.remove(routine)
                    break

        else:
            number = 0
            largest_number = 0
            for routine in routines:
                if routine.number > largest_number:
                    largest_number = routine.number
            if largest_number == 0:
                number = 1
            else:
                for i in range(0, largest_number + 2):
                    number_used = False
                    for routine in routines:
                        if routine.number == i:
                            number_used = True
                            break
                    if not number_used:
                        number = i
                        break
    if old_routine:
        routines.insert(number, Routine(number, contents[0], contents[1]))
    else:
        routines.append(Routine(number, contents[0], contents[1]))
    write_file(file, routines)
