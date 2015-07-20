import os
commands=[]
data_dir='/Users/sunxiaofei/workspace/TMPDATA/jd_data/matrixes/mallet/data.mallet'
commands.append("bin/mallet import-file --token-regex '[0-9]+' --input %s --output data.mallet"%data_dir)
commands.append("bin/mallet train-classifier --input data.mallet --trainer MaxEnt --trainer NaiveBayes --training-portion 0.9 --num-trials 10")
for command in commands:
    os.system(command)
