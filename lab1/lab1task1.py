import sys
x = input("enter x:")
b = x.isdigit()
if b == False:
	sys.exit("x aren't a number")
x = int(x)
y = input("enter y:")
b = y.isdigit()
if b == False:
	sys.exit("y aren't a number")
y = int(y)
z = 0
if int(x) > 8:
	z = 3 + y
else:
	z = 9 * x * y
print(z)