import random
n = 4
a = [[0]*n for i in range(n)]
for i in range(n):
	for j in range(n):
		a[i][j] =  random.randrange(0,99)
for row in a:
	print(' '.join([str(elem) for elem in row]))
res = []
k = 0
for m in range(n):
	for p in range(n):
			k += int(a[m][p])
	res.append(str(k))
print(res)