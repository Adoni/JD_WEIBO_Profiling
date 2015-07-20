data_dir=/mnt/data1/adoni/jd_data/matrixes/mallet/data.mallet
bin/mallet import-file --input $data_dir --output data.mallet --token-regex '[0-9]'
bin/mallet train-classifier --input data.mallet --trainer MaxEnt --training-portion 0.9 --num-trials 10
bin/mallet train-classifier --input data.mallet --trainer NaiveBayes --training-portion 0.9 --num-trials 10
#bin/mallet train-classifier --input data.mallet --trainer "MaxEntGETrainer,gaussianPriorVariance=0.1,constraintsFile=\"review.constraints\"" --training-portion 0.9 --num-trials 10
#bin/mallet train-classifier --training-file unlabeled_data.mallet --testing-file unlabeled_data_test.mallet --trainer "MaxEntGETrainer,gaussianPriorVariance=0.1,constraintsFile=\"review.constraints\"" --report test:accuracy
