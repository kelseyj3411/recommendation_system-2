#import tensorflow as tf
#from tensorflow.keras.layers import *
#from tensorflow.keras.models import Model
#import argparse

import keras
from keras import backend as K
from keras import initializers
from keras.regularizers import l2
from keras.models import Sequential, Model
from keras.layers.core import Dense, Lambda, Activation
from keras.layers import *
from keras.constraints import maxnorm
from keras.optimizers import Adagrad, Adam, SGD, RMSprop

import numpy as np
from time import time
import theano
import sys
import argparse
import multiprocessing as mp

from Loader import Loader

#################### Arguments ####################
def parse_args():
    parser = argparse.ArgumentParser(description="Run MLP.")
    parser.add_argument('--path', nargs='?', default='Data/',
                        help='Input data path.')
    parser.add_argument('--dataset', nargs='?', default='brunch',
                        help='Choose a dataset.')
    parser.add_argument('--epochs', type=int, default=100,
                        help='Number of epochs.')
    parser.add_argument('--batch_size', type=int, default=256,
                        help='Batch size.')
    parser.add_argument('--layers', nargs='?', default='[64,32,16,8]',
                        help="Size of each layer. Note that the first layer is the concatenation of user and item embeddings. So layers[0]/2 is the embedding size.")
    parser.add_argument('--num_neg', type=int, default=4,
                        help='Number of negative instances to pair with a positive instance.')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='Learning rate.')
    parser.add_argument('--learner', nargs='?', default='adam',
                        help='Specify an optimizer: adagrad, adam, rmsprop, sgd')
    parser.add_argument('--verbose', type=int, default=1,
                        help='Show performance per X iterations')
    parser.add_argument('--out', type=int, default=1,
                        help='Whether to save the trained model.')
    return parser.parse_args()


def get_model(user_num, item_num, context_num, layers = [20,64,32,16,8]):
    num_layer = len(layers) # number of mlp layers

    ## Embedding Layer ##

    # User Embedding
    user = Input(shape=(1,), dtype='int32')
    user_embedding = Embedding(input_dim=user_num, output_dim=layers[0]/2, input_length=user_input.shape[1])(user)
    user_latent = Flatten()(user_embedding)

    # Item Embedding
    item = Input(shape=(1,), dtype='int32')
    item_embedding = Embedding(input_dim=item_num, output_dim=layers[0]/2, input_length=item_input.shape[1])(item)
    item_latent = Flatten()(item_embedding)

    # Context Embedding
    context = Input(shape=(1,), dtype='int32')
    context_embedding = Embedding(input_dim=context_num, output_dim=layers[0]/2, input_length=context_input.shape[1])(context)
    context_latent = Flatten()(context_embedding)

    ## Concatenate ##
    concat = Concatenate()[user_latent, item_latent, context_latent]
    vector = Dropout(rate=0.2)(concat)

    ## MLP  Layers ##
    # Layer1
    layer_1 = Dense(units=64, activation='relu', name='layer1')(dropout)  # (64,1)
    dropout1 = Dropout(rate=0.2, name='dropout1')(layer_1)                # (64,1)
    batch_norm1 = BatchNormalization(name='batch_norm1')(dropout1)        # (64,1)

    # Layer2
    layer_2 = Dense(units=32, activation='relu', name='layer2')(batch_norm1)  # (32,1)
    dropout2 = Dropout(rate=0.2, name='dropout2')(layer_2)                    # (32,1)
    batch_norm2 = BatchNormalization(name='batch_norm2')(dropout2)            # (32,1)

    # Layer3
    layer_3 = Dense(units=16, activation='relu', name='layer3')(batch_norm2)  # (16,1)

    # Layer4
    layer_4 = Dense(units=8, activation='relu', name='layer4')(layer_3)  # (8,1)

    ## Output Layer ##
    output_layer = Dense(1, activation = 'sigmoid',kernel_initializer='lecun_uniform', name='output_layer')(layer_4)

    # Build Model
    model = Model(input=[user, item, context],
                        output=output_layer)

    return model



###############################
##       Get train data      ##
###############################

def get_train_instances():





###############################

if __name__ == '__main__':
    args = parse_args()
    path = args.path
    dataset = args.dataset
    layers = eval(args.layers)
    num_negatives = args.num_neg
    learner = args.learner
    learning_rate = args.lr
    batch_size = args.batch_size
    epochs = args.epochs
    verbose = args.verbose

    topK = 10
    evaluation_threads = 1 #mp.cpu_count()
    print("MLP arguments: %s " %(args))
    model_out_file = 'Pretrain/%s_MLP_%s_%d.h5' %(args.dataset, args.layers, time())


###############################
##         Load Data         ##
###############################
# Load data
t1 = time()
dataset = Loader(args.path + args.dataset)
train, testRatings, testNegatives =
user_num, item_num =
print("Load data done [%.1f s]. #user=%d, #item=%d, #train=%d, #test=%d"
      %(time()-t1, num_users, num_items, ))

# Build model
model = get_model(num_users, num_items, layers)
opt = keras.optimizers.Adam(learning_rate=learning_rate)
model.compile(optimizer=opt, loss='binary_crossentropy')


###############################
##         Evaluation        ##
###############################
# Generate training instances
user, item, context, labels = get_train_instances(train, num_negatives)

# Training
hist = model.fit([np.array(user), np.array(item)],
                 np.array(labels), # labels
                 batch_size=batch_size,
                 nb_epoch=1,
                 verbose=0)
t2 = time()


# Evaluation







###############################
##            FIX
###############################
def get_train_instances(train, num_neg):
        """
        모델에 사용할 train 데이터 생성 함수
        """
        num_items =
        uids =
        iids =
        user_input, item_input, labels = [],[],[]
        zipped = set(zip(uids, iids)) # train (user, item) 세트

        for (u, i) in zip(uids, iids):

            # pos item 추가
            user_input.append(u)  # [u]
            item_input.append(i)  # [pos_i]
            labels.append(1)      # [1]

            # neg item 추가
            for t in range(num_neg):

                j = np.random.randint(num_items)      # neg_item j num_neg 개 샘플링
                while (u, j) in zipped:               # u가 j를 이미 선택했다면
                    j = np.random.randint(num_items)  # 다시 샘플링

                user_input.append(u)  # [u1, u1,  u1,  ...]
                item_input.append(j)  # [pos_i, neg_j1, neg_j2, ...]
                labels.append(0)      # [1, 0,  0,  ...]

        return user_input, item_input, labels



    # Check Init performance
    t1 = time()
    (hits, ndcgs) = evaluate_model(model, testRatings, testNegatives, topK, evaluation_threads)
    hr, ndcg = np.array(hits).mean(), np.array(ndcgs).mean()
    print('Init: HR = %.4f, NDCG = %.4f [%.1f]' %(hr, ndcg, time()-t1))


    # Train model
    best_hr, best_ndcg, best_iter = hr, ndcg, -1
    for epoch in range(epochs):
        t1 = time()

        # Generate training instances
        user, item, context, labels = get_train_instances(train, num_negatives)

        # Training
        hist = model.fit([np.array(user), np.array(item)],
                         np.array(labels), # labels
                         batch_size=batch_size,
                         nb_epoch=1,
                         verbose=0)
        t2 = time()

        # Evaluation
        if epoch %verbose == 0:
            (hits, ndcgs) = evaluate_model(model, testRatings, testNegatives, topK, evaluation_threads)
            hr, ndcg, loss = np.array(hits).mean(), np.array(ndcgs).mean(), hist.history['loss'][0]
            print('Iteration %d [%.1f s]: HR = %.4f, NDCG = %.4f, loss = %.4f [%.1f s]'
                  % (epoch,  t2-t1, hr, ndcg, loss, time()-t2))

            if hr > best_hr:
                best_hr, best_ndcg, best_iter = hr, ndcg, epoch
                if args.out > 0:
                    model.save_weights(model_out_file, overwrite=True)

    print("End. Best Iteration %d:  HR = %.4f, NDCG = %.4f. " %(best_iter, best_hr, best_ndcg))
    if args.out > 0:
        print("The best MLP model is saved to %s" %(model_out_file))
