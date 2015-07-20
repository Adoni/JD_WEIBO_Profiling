import os
commands=[]
commands.append("bin/vectors2vectors \
        --input data.mallet \
        --output unlabeled_data.mallet \
        --hide-targets")
commands.append("bin/mallet train-classifier\
        --training-file   unlabeled_data.mallet \
        --testing-file    data.mallet \
        --trainer 'MaxEntGETrainer,gaussianPriorVariance=0.1,constraintsFile=\"review.constraints\"'\
        --report test:accuracy")
for command in commands:
    os.system(command)
