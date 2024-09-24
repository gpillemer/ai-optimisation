from pyomo.environ import *
from prettytable import PrettyTable

def create_and_solve_timetable_model(data):
    # Create a model
    model = ConcreteModel()

    # Sets
    model.Classes = Set(initialize=data['Classes'])
    model.TimeSlots = Set(initialize=data['TimeSlots'])
    model.Teachers = Set(initialize=data['Teachers'])
    model.Classrooms = Set(initialize=data['Classrooms'])

    # Mappings
    class_teacher = {entry['classId']: entry['teacher'] for entry in data['ClassTeacherMapping']}
    class_room = {entry['classId']: entry['room'] for entry in data['ClassRoomMapping']}
    
    # Decision Variables
    model.x = Var(model.Classes, model.TimeSlots, domain=Binary)

    # Constraints
    
    # 1. Each class must be assigned exactly one time slot
    if data['Constraints']['OneTimeSlotPerClass']:
        def one_time_slot_per_class_rule(model, c):
            return sum(model.x[c, t] for t in model.TimeSlots) == 1
        model.one_time_slot_per_class = Constraint(model.Classes, rule=one_time_slot_per_class_rule)

    # 2. No two classes that share a common teacher can be in the same time slot
    if data['Constraints']['TeacherConflict']:
        def teacher_conflict_rule(model, t, teacher):
            classes_with_teacher = [c for c in model.Classes if class_teacher[c] == teacher]
            return sum(model.x[c, t] for c in classes_with_teacher) <= 1
        model.teacher_conflict = Constraint(model.TimeSlots, model.Teachers, rule=teacher_conflict_rule)

    # 3. No two classes that share a common classroom can be in the same time slot
    if data['Constraints']['RoomConflict']:
        def room_conflict_rule(model, t, room):
            classes_in_room = [c for c in model.Classes if class_room[c] == room]
            return sum(model.x[c, t] for c in classes_in_room) <= 1
        model.room_conflict = Constraint(model.TimeSlots, model.Classrooms, rule=room_conflict_rule)

    # 4. Force specific classes into specific time slots
    if 'ForcedAssignments' in data and data['ForcedAssignments']:
        def force_assignment_rule(model, c, t):
            forced_assignments = {entry['classId']: entry['timeslot'] for entry in data['ForcedAssignments']}
            if c in forced_assignments and forced_assignments[c] == t:
                return model.x[c, t] == 1
            else:
                return Constraint.Skip
        model.force_assignment = Constraint(model.Classes, model.TimeSlots, rule=force_assignment_rule)

    # Objective: Minimize the total number of time slots used
    def dummy_objective_rule(model):
        return 0  # A feasible solution is the main goal

    model.objective = Objective(rule=dummy_objective_rule)

    # Solve the model
    solver = SolverFactory('glpk')
    solver.solve(model)

    # Display results in a terminal table grid
    print("Class Timetable:")

    # Create a PrettyTable object
    room_table = PrettyTable()

    # Dynamically add room columns based on the number of classrooms
    room_names = sorted(list(model.Classrooms))
    room_table.field_names = ["Time Slot"] + room_names

    # Populate the table with class schedules
    for t in model.TimeSlots:
        row = [t]
        for room in room_names:
            room_class = ""
            for c in model.Classes:
                if model.x[c, t].value == 1 and class_room[c] == room:
                    room_class = c
                    break
            row.append(room_class)
        room_table.add_row(row)

    print(room_table)

    teacher_table = PrettyTable()

    # Dynamically add room columns based on the number of classrooms
    teacher_table.field_names = ["Time Slot"] + room_names

    # Populate the table with teacher schedules
    for t in model.TimeSlots:
        row = [t]
        for room in room_names:
            room_teacher = ""
            for c in model.Classes:
                if model.x[c, t].value == 1 and class_room[c] == room:
                    room_teacher = class_teacher[c]
                    break
            row.append(room_teacher)
        teacher_table.add_row(row)

    print(teacher_table)
    return {
        "room_table": room_table.get_string(),
        "teacher_table": teacher_table.get_string()
    }


# Example usage with the updated data structure:
if __name__ == "__main__":
    data = {
    "Classes": ["C1", "C2", "C3"],
    "TimeSlots": ["T1", "T2", "T3"],
    "Teachers": ["Teacher1", "Teacher2"],
    "Classrooms": ["Room1", "Room2"],
    "Teachers": ["Teacher1", "Teacher2"],
    "ClassTeacherMapping": [
        {"classId": "C1", "teacher": "Teacher1"},
        {"classId": "C2", "teacher": "Teacher2"},
        {"classId": "C3", "teacher": "Teacher1"}
    ],
    "ClassRoomMapping": [
        {"classId": "C1", "room": "Room1"},
        {"classId": "C2", "room": "Room1"},
        {"classId": "C3", "room": "Room2"}
    ],
    "Constraints": {
        "OneTimeSlotPerClass": True,
        "TeacherConflict": True,
        "RoomConflict": True
    },
    "ForcedAssignments": [
        {"classId": "C1", "timeslot": "T1"},  # Force C1 to be in T1
        {"classId": "C2", "timeslot": "T2"}   # Force C2 to be in T2
    ]
    }

    # Call the function with the data
    create_and_solve_timetable_model(data)

