class BaseExercise:
    def __init__(self, exercise_data):
        self.number = exercise_data[0]
        self.name = exercise_data[1]
        self.type = exercise_data[2]
        self.muscle = exercise_data[3]
        self.equipment = exercise_data[4]
        each_side = exercise_data[5]
        if each_side == "True":
            self.each_side = True
        else:
            self.each_side = False
        self.start_weight = exercise_data[6]


class Exercise:
    def __init__(self, base_exercise, exercise_data):
        self.base_exercise = base_exercise
        self.reps = exercise_data[0]
        self.min_reps = exercise_data[1]
        self.max_reps = exercise_data[2]
        self.sets = exercise_data[3]
        self.weight = exercise_data[4]
        self.rest_time = exercise_data[5]


class SuperSet:
    def __init__(self, super_set_exercises, super_set_data):
        self.super_set_exercises = super_set_exercises
        self.sets = super_set_data[0]
        self.rest_time = super_set_data[1]


class SuperSetExercise:
    def __init__(self, base_exercise, exercise_data):
        self.base_exercise = base_exercise
        self.reps = exercise_data[0]
        self.min_reps = exercise_data[1]
        self.max_reps = exercise_data[2]
        self.weight = exercise_data[3]


class Routine:
    def __init__(self, number, name, exercises):
        self.number = number
        self.name = name
        self.exercises = exercises


def get_exercises():
    all_exercises = []

    with open("screens/exercises.txt") as f:
        for line1 in f:
            line2 = line1.replace("\n", "")
            line_list = line2.split(":")
            exercise = BaseExercise(line_list)
            all_exercises.append(exercise)

    all_exercise_names = []
    for exercise in all_exercises:
        all_exercise_names.append(exercise.name)

    x = sorted(all_exercise_names)
    sorted_exercises = []
    for i in x:
        for j in all_exercises:
            if i == j.name:
                sorted_exercises.append(j)
    return sorted_exercises
