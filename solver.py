from pulp import *
import pandas as pd

schedule = pd.read_csv('schedule.csv')
date_df = schedule.set_index('Date')
MM = pd.read_csv('mile_matrix.csv')
MM = MM.set_index(['src', 'dest'])

# There are 32 NFL teams
TEAMS = ['Home', *sorted(list(schedule['Home Abbrev'].unique()))]
# There are 56 game dates in the 2024-25 season
DATES = [0, *list(schedule['Date'].unique())]

# Define Problem  

prob = LpProblem("Matrix Problem",LpMinimize)
# Creating a Set of Variables
# date, source, desetination
choices = LpVariable.dicts("Interview",(DATES,TEAMS,TEAMS), cat='Binary')

# Added arbitrary objective function
prob += 0, "Arbitrary Objective Function"

# ---------------- CONSTRAINTS ------------------------

# ensure each arena is departed from exactly 1 time
for t2 in TEAMS:
    prob += lpSum([choices[d][t1][t2] for d in DATES[1:] for t1 in TEAMS]) == 1, ""

# ensure each arena is visited exactly 1 time
for t1 in TEAMS:
    prob += lpSum([choices[d][t1][t2] for d in DATES[1:] for t2 in TEAMS]) == 1, ""

# minimize total number of visits
prob += lpSum([choices[d][t1][t2] for d in DATES[1:] for t1 in TEAMS for t2 in TEAMS if t1 != t2]) <= 33

# start from home and end at home
prob +=lpSum([choices[d]['Home'][t2] for t2 in TEAMS[1:] for d in DATES[1:4]]) == 1
prob +=lpSum([choices[d][t1]['Home'] for t1 in TEAMS[1:] for d in DATES[-1:]]) == 1

# make sure visits are played on home team dates
for d in DATES[1:]:
    for t2 in TEAMS[1:]:
        for t1 in TEAMS:
            if schedule[(schedule['Date'] == d) & (schedule['Home Abbrev'] == t2)].shape[0] == 0:
                prob += choices[d][t1][t2] == 0, ""

    prob += lpSum([choices[d][t1][t2] for t1 in TEAMS for t2 in TEAMS]) <= 1, ""

for d in DATES:
    for t1 in TEAMS[1:]:
        for t2 in TEAMS[1:]:
            if t1 == t2:
                prob += choices[d][t1][t2] == 0, ""

# Ensure that visits are sequential by dates
for i, d in enumerate(DATES[1:-1]):
    for t1 in TEAMS:
        for t2 in TEAMS[1:]:
            if t1 != t2:
                prob += choices[DATES[i]][t1][t2] <= lpSum([choices[d2][t2][t3] for d2 in DATES[i+1:i+4] for t3 in TEAMS if t3 != t2]), f""

for i, d in enumerate(DATES[2:]):
    for t1 in TEAMS[1:]:
        for t2 in TEAMS:
            if t1 != t2:
                prob += choices[DATES[i]][t1][t2] <= lpSum([choices[d2][t3][t1] for d2 in DATES[i-4:i] for t3 in TEAMS if t3 != t1]), f""

# # Objective: Minimize the total travel distance
prob += lpSum([choices[d][t1][t2] * MM.loc[(t1, t2), 'miles'] for d in DATES[1:] for t1 in TEAMS[1:] for t2 in TEAMS[1:] if t1 != t2]) <= 14000, "MinimizeTravelDistance"
# prob += lpSum([choices[d][t1][t2] * MM.loc[(t1, t2), 'miles'] for d in DATES[1:] for t1 in TEAMS[1:] for t2 in TEAMS[1:] if t1 != t2])

# The problem is solved using PuLP's choice of Solver
prob.solve()

print("Status:", LpStatus[prob.status])

# Print out the solution
debug = ""
print("\nMatrix Solution")
if LpStatus[prob.status] == 'Optimal':
    print('solved problem')
    matrix = []
    for t2 in TEAMS:
        row = []
        for t1 in TEAMS:
            value = 0
            for d in DATES:
                if choices[d][t1][t2].varValue == 1:
                    value = d
            row.append(value)

        matrix.append(row)

    matrix_df = pd.DataFrame(matrix, columns=TEAMS)
    matrix_df.index = TEAMS
    print(matrix_df)
    matrix_df.to_csv('solved_route.csv')

else:
    print('Problem is infeasible')


