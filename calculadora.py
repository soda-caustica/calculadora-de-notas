import tkinter as tk
from tkinter import messagebox
from collections import deque
import numpy as np
import random
from scipy.optimize import minimize


def validatenum(grade, min, max):
    if grade == '':
        return True
    try:
        float(grade)
    except:
        return False
    return (min <= float(grade) <= max)


def clearResults(*args):
    for i in grade_weight_pairs:
        i[0].set('')
        i[1].set('')
    a.set('')
    while len(boxes) > 1:
        remove_boxes()
    boxes[0][0].config(fg="SystemWindowText")
    boxes[0][0].config(state="normal")


def create_boxes(*args):
    addingButton.grid_forget()
    removingButton.grid_forget()
    grade = tk.StringVar()
    weight = tk.StringVar()
    gradeBox = tk.Entry(frame, textvariable=grade, width=10,
                        validate="key", validatecommand=validate_grade_wrapper)
    weightBox = tk.Entry(frame, textvariable=weight, width=10,
                         validate="key", validatecommand=validate_percentage_wrapper)
    gradeBox.grid(column=0, row=len(grade_weight_pairs)+1)
    weightBox.grid(column=1, row=len(grade_weight_pairs)+1)
    boxes.append([gradeBox, weightBox])
    grade_weight_pairs.append((grade, weight))
    addingButton.grid(column=0, row=len(grade_weight_pairs)+1)
    removingButton.grid(column=1, row=len(grade_weight_pairs)+1)


def remove_boxes(*args):
    if len(boxes) <= 1:
        return
    addingButton.grid_forget()
    removingButton.grid_forget()
    grade_weight_pairs.pop()
    gradebox, weightbox = boxes.pop()
    gradebox.destroy()
    weightbox.destroy()
    addingButton.grid(column=0, row=len(grade_weight_pairs)+1)
    removingButton.grid(column=1, row=len(grade_weight_pairs)+1)


def validateInputs(*args):
    porcentajes = 0
    missing = []
    if a.get() == '':
        messagebox.showwarning(
            'Advertencia', "No se ha ingresado una nota aprobatoria")
        return

    for i, j in grade_weight_pairs:

        if j.get() == '':
            messagebox.showwarning(
                'Advertencia', "No se han ingresado todos los porcentajes")
            return
        porcentajes += float(j.get())

    if porcentajes != 100:
        messagebox.showwarning('Advertencia', "Los porcentajes no suman 100")
        return
    startCalcs()

def recalc(*args):
    for i,box in enumerate(boxes):
        if box[0].cget("foreground") == auto_color:
            grade_weight_pairs[i][0].set('')
    validateInputs()

def startCalcs():
    missing = []

    grades = [x[0].get() for x in grade_weight_pairs]
    weights = [float(x[1].get())/100 for x in grade_weight_pairs]
    for i, grade in enumerate(grades):
        if grade == '':
            missing.append(i)
        else:
            grades[i] = float(grade)

    def objective(vars):
        variables = deque(vars)
        suma = 0
        for i in range(len(grades)):
            if i in missing:
                suma += weights[i]*variables.popleft()
            else:
                suma += weights[i]*grades[i]
        return (suma - float(a.get()))**2

    constraints = []
    for i in range(len(missing)):
        constraints.append(
            {'type': 'ineq', 'fun': lambda x, index=i: x[index] - 1})
        constraints.append(
            {'type': 'ineq', 'fun': lambda x, index=i: 7 - x[index]})

    initial_guess = np.array([random.uniform(1.7,4) for _ in range(len(missing))])
    solution = minimize(objective, initial_guess, constraints=constraints)
    for i in range(len(missing)):
        grades[missing[i]] = solution.x[i]
    suma = 0
    for i, j in zip(grades, weights):
        suma += i*j
    if suma < 3.95:
        messagebox.showwarning("Advertencia", "Es imposible de lograr 😥")
    else:
        for index, sol in zip(missing, solution.x):
            grade_weight_pairs[index][0].set(f'{round(sol, 1)}')
            boxes[index][0].config(fg=auto_color)
            boxes[index][0].config(state='readonly')



boxes = []
grade_weight_pairs = []
auto_color = "red"

root = tk.Tk()
validate_grade_wrapper = (root.register(
    (lambda min: lambda max: lambda grade: validatenum(grade, min, max))(1)(7)), "%P")
validate_percentage_wrapper = (root.register(
    (lambda min: lambda max: lambda grade: validatenum(grade, min, max))(0)(100)), "%P")

frame = tk.Frame(root, border=20)
frame.grid()

tk.Label(frame, text="NOTAS").grid(column=0, row=0)
tk.Label(frame, text="PORCENTAJE").grid(column=1, row=0)
tk.Label(frame, text="APROBATORIA").grid(column=2, row=0)
a = tk.StringVar()
aprobado = tk.Entry(frame, textvariable=a, validate="key",
                    validatecommand=validate_grade_wrapper, width=7)
aprobado.grid(column=2, row=1)
addingButton = tk.Button(frame, text="MAS NOTAS", font=(
    "Times New Roman", 7), width=10, command=create_boxes)
removingButton = tk.Button(frame, text="MENOS NOTAS", font=(
    "Times New Roman", 7), width=12, command=remove_boxes)
calcButton = tk.Button(frame, text="CALCULAR", height=3,
                       width=10, command=validateInputs)
calcButton.grid(column=2, row=2, rowspan=4, columnspan=2)

reCalc = tk.Button(frame,text="RECALCULAR",width=10, command = recalc)
reCalc.grid(column=2,row=8,columnspan=2)

cleanButton = tk.Button(frame, text="LIMPIAR",
                       width=10, command=clearResults)
cleanButton.grid(column=2, row=9, columnspan=2)
create_boxes()

root.mainloop()
