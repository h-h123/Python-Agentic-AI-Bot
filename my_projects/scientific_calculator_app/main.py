import math
import tkinter as tk
from tkinter import font

class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("400x600")
        self.root.resizable(False, False)

        self.expression = ""
        self.input_text = tk.StringVar()
        self.result_text = tk.StringVar()
        self.result_text.set("0")

        self.create_widgets()

    def create_widgets(self):
        input_frame = tk.Frame(self.root, height=100, bg="#f0f0f0")
        input_frame.pack(side=tk.TOP, fill=tk.BOTH)

        input_field = tk.Entry(
            input_frame,
            font=('Arial', 18, 'bold'),
            textvariable=self.input_text,
            bd=0,
            justify=tk.RIGHT,
            bg="#f0f0f0"
        )
        input_field.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        result_label = tk.Label(
            input_frame,
            font=('Arial', 12),
            textvariable=self.result_text,
            bd=0,
            justify=tk.RIGHT,
            bg="#f0f0f0",
            fg="#666666"
        )
        result_label.pack(fill=tk.BOTH, expand=True, padx=10)

        btn_frame = tk.Frame(self.root, bg="#333333")
        btn_frame.pack(fill=tk.BOTH, expand=True)

        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3), ('C', 1, 4),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3), ('(', 2, 4),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3), (')', 3, 4),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3), ('⌫', 4, 4),
            ('sin', 5, 0), ('cos', 5, 1), ('tan', 5, 2), ('√', 5, 3), ('x²', 5, 4),
            ('log', 6, 0), ('ln', 6, 1), ('π', 6, 2), ('e', 6, 3), ('x^y', 6, 4),
            ('!', 7, 0), ('10^x', 7, 1), ('|x|', 7, 2), ('rad', 7, 3), ('deg', 7, 4)
        ]

        for (text, row, col) in buttons:
            if text in ['=', 'C', '⌫', 'deg', 'rad']:
                bg = "#ff9500" if text == '=' else "#a6a6a6"
                fg = "white" if text == '=' else "black"
            else:
                bg = "#4d4d4d" if text in ['+', '-', '*', '/', '^'] else "#5a5a5a"
                fg = "white"

            btn = tk.Button(
                btn_frame,
                text=text,
                font=('Arial', 14, 'bold'),
                bg=bg,
                fg=fg,
                bd=0,
                activebackground="#666666",
                activeforeground="white",
                command=lambda t=text: self.on_button_click(t)
            )
            btn.grid(
                row=row,
                column=col,
                sticky=tk.NSEW,
                padx=1,
                pady=1,
                ipadx=10,
                ipady=10
            )
            btn_frame.grid_columnconfigure(col, weight=1)

        for i in range(8):
            btn_frame.grid_rowconfigure(i, weight=1)

    def on_button_click(self, char):
        if char == 'C':
            self.expression = ""
            self.input_text.set("")
            self.result_text.set("0")
        elif char == '⌫':
            self.expression = self.expression[:-1]
            self.input_text.set(self.expression)
        elif char == '=':
            try:
                result = self.evaluate_expression()
                self.result_text.set(f"={result}")
                self.expression = str(result)
                self.input_text.set(self.expression)
            except Exception as e:
                self.result_text.set("Error")
                self.expression = ""
        elif char == 'deg':
            self.result_text.set("Degree mode")
        elif char == 'rad':
            self.result_text.set("Radian mode")
        else:
            if char in ['sin', 'cos', 'tan', 'log', 'ln', '√', 'x²', 'x^y', '!', '10^x', '|x|']:
                self.handle_functions(char)
            elif char == 'π':
                self.expression += str(math.pi)
                self.input_text.set(self.expression)
            elif char == 'e':
                self.expression += str(math.e)
                self.input_text.set(self.expression)
            else:
                self.expression += str(char)
                self.input_text.set(self.expression)

    def handle_functions(self, func):
        if func == 'sin':
            self.expression += 'math.sin('
        elif func == 'cos':
            self.expression += 'math.cos('
        elif func == 'tan':
            self.expression += 'math.tan('
        elif func == 'log':
            self.expression += 'math.log10('
        elif func == 'ln':
            self.expression += 'math.log('
        elif func == '√':
            self.expression += 'math.sqrt('
        elif func == 'x²':
            self.expression += '**2'
        elif func == 'x^y':
            self.expression += '**'
        elif func == '!':
            self.expression += 'math.factorial('
        elif func == '10^x':
            self.expression += '10**'
        elif func == '|x|':
            self.expression += 'abs('

        self.input_text.set(self.expression)

    def evaluate_expression(self):
        try:
            return eval(self.expression, {'math': math, '__builtins__': None})
        except:
            raise ValueError("Invalid expression")

if __name__ == "__main__":
    root = tk.Tk()
    calculator = ScientificCalculator(root)
    root.mainloop()