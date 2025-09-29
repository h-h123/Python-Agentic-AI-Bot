def add(x, y):
   return x + y

def subtract(x, y):
   return x - y

def multiply(x, y):
   return x * y

def divide(x, y):
   if y == 0:
       return "Error! Division by zero is not allowed."
   else:
       return x / y

x = float(input("Enter first number: "))
y = float(input("Enter second number: "))

print("Select operation:")
print("1. Add")
print("2. Subtract")
print("3. Multiply")
print("4. Divide")

operation = input("Enter operation number: ")

if operation == '1':
   print(add(x, y))
elif operation == '2':
   print(subtract(x, y))
elif operation == '3':
   print(multiply(x, y))
elif operation == '4':
   print(divide(x, y))
else:
   print("Invalid input")