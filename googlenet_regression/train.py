caffe_root = '../../caffe-master/'  # this file should be run from {caffe_root}/examples (otherwise change this line)

import sys
sys.path.insert(0, caffe_root + 'python')
import caffe
from create_solver import create_solver
from do_solve import do_solve
import os


caffe.set_device(0)
caffe.set_mode_gpu()

weights = '../../../datasets/SocialMedia/models/pretrained/bvlc_googlenet.caffemodel'
assert os.path.exists(weights)

niter = 10001111
base_lr = 0.001 #Starting from 0.01 (from quick solver) -- Working 0.001
display_interval = 200 #200

#number of validating images  is  test_iters * batchSize
test_interval = 1000 #1000
test_iters = 100 #80

#Name for training plot and snapshots
training_id = 'SM_Inception_frozen_word2vec_tfidf'

#Set solver configuration
solver_filename = create_solver('prototxt/train_frozen_word2vec_tfidf_SM.prototxt', 'prototxt/val_frozen_word2vec_tfidf_SM.prototxt', training_id, base_lr=base_lr)
#Load solver
solver = caffe.get_solver(solver_filename)

#Copy init weights
solver.net.copy_from(weights)

print 'Running solvers for %d iterations...' % niter
solvers = [('my_solver', solver)]
_, _, _ = do_solve(niter, solvers, display_interval, test_interval, test_iters, training_id)
print 'Done.'

