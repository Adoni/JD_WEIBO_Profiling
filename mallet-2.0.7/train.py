import os
commands=[]
data_dir='/mnt/data1/adoni/jd_data/matrixes/mallet'

commands.append("bin/mallet import-file \
        --input %s/review_%s.mallet \
        --token-regex '[0-9]+'\
        --output train_data.mallet"%(data_dir,'train'))

commands.append("bin/mallet import-file \
        --input %s/review_%s.mallet \
        --token-regex '[0-9]+'\
        --output test_data.mallet"%(data_dir,'test'))

commands.append("bin/mallet train-classifier \
        --training-file train_data.mallet \
        --testing-file test_data.mallet \
        --trainer NaiveBayes")

for command in commands:
    os.system(command)
