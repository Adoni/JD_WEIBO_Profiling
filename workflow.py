import os
commands=[]
#commands.append('python knn.py')
commands.append('python deep_walk.py')
commands.append('python svm.py')
for command in commands:
    os.system(command)
