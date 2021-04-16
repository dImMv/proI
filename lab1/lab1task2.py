import sys
n = input("enter n:")
b = n.isdigit()
if b == False:
	sys.exit("n aren't a number")
n = int(n)
if n <= 0:
	sys.exit("n should be more or equal 1")
Z = 1
for i in range(1,n + 1):
	Z *= i
print(Z)