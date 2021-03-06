# Load trained doc2vec model and infer vectors for unseen text.
# Make the train/val/test splits for CNN regression training randomly

from stop_words import get_stop_words
import string
from joblib import Parallel, delayed
import numpy as np
from random import randint
import json
import gensim

# Load data and model
text_data_path = '../../../datasets/WebVision/'
model_path = '../../../datasets/WebVision/models/doc2vec/doc2vec_model_webvision.model'

# Create output files
train_gt_path = '../../../datasets/WebVision/doc2vec_gt/' + 'train_webvision.txt'
train_file = open(train_gt_path, "w")
val_gt_path = '../../../datasets/WebVision/doc2vec_gt/' + 'myval_webvision.txt'
val_file = open(val_gt_path, "w")

model = gensim.models.Doc2Vec.load(model_path)

size = 400 # vector size
cores = 8

whitelist = string.letters + string.digits + ' '
words2filter = ['wikipedia','google', 'flickr', 'figure', 'photo', 'image', 'homepage', 'url', 'youtube', 'images', 'blog', 'pinterest']
# create English stop words list
en_stop = get_stop_words('en')

def infer(d):

        caption = d[2]
        filtered_caption = ""

        # Replace hashtags with spaces
        caption = caption.replace('#',' ')

        # Keep only letters and numbers
        for char in caption:
            if char in whitelist:
                filtered_caption += char

        filtered_caption = filtered_caption.lower()
        #Gensim simple_preproces instead tokenizer
        tokens = gensim.utils.simple_preprocess(filtered_caption)
        # remove stop words from tokens
        stopped_tokens = [i for i in tokens if not i in en_stop]

        try:
            embedding = model.infer_vector(stopped_tokens)
            embedding = embedding - min(embedding)
            if max(embedding) > 0:
                embedding = embedding / max(embedding)

        except:
            print "Tokenizer error"
            print stopped_tokens
            return

        out_string = ''
        for t in range(0,size):
            out_string = out_string + ',' + str(embedding[t])

        return d[0] + ',' + str(d[1]) + out_string



sources=['google','flickr']
former_filename = ' '
for s in sources:
    data = []
    print 'Loading data from ' + s
    data_file = open(text_data_path + 'info/train_meta_list_' + s + '.txt', "r")
    img_list_file = open(text_data_path + 'info/train_filelist_' + s + '.txt', "r")

    img_names = []
    img_classes = []
    for line in img_list_file:
        img_names.append(line.split(' ')[0])
        img_classes.append(int(line.split(' ')[1]))

    for i,line in enumerate(data_file):

        filename = line.split(' ')[0].replace(s,s+'_json')
        idx = int(line.split(' ')[1])

        if filename != former_filename:
            # print filename
            json_data = open(text_data_path + filename)
            d = json.load(json_data)
            former_filename = filename

        caption = ''

        if d[idx - 1].has_key('description'): caption = caption + d[idx - 1]['description'] + ' '
        if d[idx - 1].has_key('title'): caption = caption + d[idx - 1]['title'] + ' '
        if d[idx - 1].has_key('tags'):
            for tag in d[idx-1]['tags']:
                caption = caption + tag + ' '

        data.append([img_names[i],img_classes[i],caption])


    print "Number of elements for " + s + ": " + str(len(data))
    parallelizer = Parallel(n_jobs=cores)
    print "Infering LDA scores"
    tasks_iterator = (delayed(infer)(d) for d in data)
    r = parallelizer(tasks_iterator)
    # merging the output of the jobs
    strings = np.vstack(r)

    print "Resulting number of elements for " + s + ": " + str(len(strings))

    print "Saving results"
    for s in strings:
        # Create splits random
        try:
            split = randint(0,19)
            if split < 1:
                val_file.write(s[0] + '\n')
            else: train_file.write(s[0] + '\n')
        except:
            print "Error writing to file: "
            print s[0]
            continue

    data_file.close()
    img_list_file.close()

train_file.close()
val_file.close()

print "Done"
