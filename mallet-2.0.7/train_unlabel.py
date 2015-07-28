import os
<<<<<<< HEAD
commands=[]
commands.append("bin/vectors2vectors \
        --input data.mallet \
        --output unlabeled_data.mallet \
        --hide-targets")
commands.append("bin/mallet train-classifier\
        --training-file   unlabeled_data.mallet \
        --testing-file    data.mallet \
=======

commands=[]

commands.append("bin/vectors2vectors \
        --input train_data.mallet \
        --output unlabeled_data.mallet \
        --hide-targets")

commands.append("bin/mallet train-classifier\
        --training-file   unlabeled_data.mallet \
        --testing-file    train_data.mallet \
>>>>>>> f82e8d5f92eb2574d9101b29d7d69ce90d10ebc1
        --trainer 'MaxEntGETrainer,gaussianPriorVariance=0.1,constraintsFile=\"review.constraints\"'\
        --report test:accuracy")
for command in commands:
    os.system(command)
