# print("Hello, World!");

# if 5 > 2:
#   print("Five is greater than two!") #Python uses indentation to indicate a block of code. Without them code didnt work

# """
# это
# многострочный
# комментарий
# """

# #Variables (Variable names are case-sensitive.)

# x = 5
# y = "John"
# print(x)
# print(y)

# x = 4       # x is of type int
# x = "Sally" # x is now of type str
# print(x)

# x = str(3)    # x will be '3'
# y = int(3)    # y will be 3
# z = float(3)  # z will be 3.0

# #Get the Type

# x = 5
# y = "John"
# print(type(x))
# print(type(y))

# #Legal variable names:

# myvar = "John"
# my_var = "John"
# _my_var = "John"
# myVar = "John"
# MYVAR = "John"
# myvar2 = "John"

# x, y, z = "Orange", "Banana", "Cherry"
# print(x)
# print(y)
# print(z)

# x = y = z = "Orange"
# print(x)
# print(y)
# print(z)

# fruits = ["apple", "banana", "cherry"]
# x, y, z = fruits
# print(x)
# print(y)
# print(z)


# #Slicing

# b = "Hello, World!"
# print(b[2:5])

# b = "Hello, World!"
# print(b[:5])

# b = "Hello, World!"
# print(b[2:])

# b = "Hello, World!"
# print(b[-5:-2]) #orl

def myFunc(e, i):
    return e * i


newFunc = myFunc(*(2, 3))
newFunc.extend([])

type(newFunc)
