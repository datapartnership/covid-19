"""
Module to do inference based on the age gender prediction model using the pipeline
from https://github.com/HSE-asavchenko/HSE_FaceRec_tf/tree/master/age_gender_identity
Developed by :
    Louis Owen (http://louisowen6.github.io/)
"""

import os
import pandas as pd
import argparse
import tensorflow as tf
import numpy as np
import json
from PIL import Image
import cv2
from tqdm import tqdm
from scipy.spatial.distance import euclidean
import face_recognition

use_GPU=False
use_tf_trt=False #if False then use .pb model


if use_tf_trt:
    import tensorflow.contrib.tensorrt as trt
    MODEL_PATH='/mnt/louis/Demographic_Prediction/model/age_gender_tf2_224_deep_fn-10-0.61-0.95.pbx'
else:
    MODEL_PATH='/mnt/louis/Demographic_Prediction/model/age_gender_tf2_224_deep_fn-10-0.61-0.95.pb'


def get_args():
    parser = argparse.ArgumentParser(description='Data Preprocessing')
    parser.add_argument('--data', choices=['twitter','instagram'], required=True, help='data source')
    return parser.parse_args()


def load_graph_def(frozen_graph_filename):
    graph_def=None
    with tf.gfile.GFile(frozen_graph_filename, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    return graph_def


def classify_gender(x):
    if x[0]>0.5:
        return 1  #1 male, 0 female
    else:
        return 0

def get_bbox_centroid(b):
    return np.asarray(
        [b[0] + (b[2] - b[0])/2,b[3] + (b[1] - b[3])/2],
        dtype=np.float32)


def get_most_center_bbox(bboxes, img_shape):
    centroids = [get_bbox_centroid(b) for b in bboxes]
    img_c = np.asarray(
        [img_shape[0] / 2, img_shape[1] / 2],
        np.float32)
    distances = [euclidean(c, img_c) for c in centroids]
    return bboxes[np.argmin(distances)]


def extract_face(img,bbox):
    return img[max(0,bbox[0]-int(np.round(bbox[0]*0.35))):bbox[2]+int(np.round(bbox[2]*0.35)),max(0,bbox[3]-int(np.round(bbox[3]*0.35))):bbox[1]+int(np.round(bbox[1]*0.35))]


if __name__=='__main__':
    args = get_args()

    if args.data=='twitter':
        df = pd.DataFrame(columns=['username','age_class','gender_class'])

        with open('/mnt/kiran/twitter_age_gender.txt','r') as f:
            for line in tqdm(f):
                lst = line.split('\t')
                df = df.append({
                    'username': lst[0],
                    'age_class': lst[2],
                    'gender_class': lst[1]
                    },ignore_index=True)

        print('Twitter Demographic')
        print('#Unique Users: {}'.format(len(df['username'].unique())))
        print(df['age_class'].value_counts())
        print(df['gender_class'].value_counts())

    else:
        DATA_SOURCE_PATH_ROOT='/mnt/profile_pictures_indonesia_louis_instagram/'

        if not use_GPU:
            os.environ['CUDA_VISIBLE_DEVICES']='-1'

        print('========== Loading Model... ==========')
        with tf.Graph().as_default() as full_graph:
            tf.import_graph_def(load_graph_def(MODEL_PATH), name='')

        _config = tf.ConfigProto(
                allow_soft_placement=True)
        _config.gpu_options.allow_growth = True

        sess= tf.Session(graph=full_graph,config=_config)

        age_out=full_graph.get_tensor_by_name('age_pred/Softmax:0')
        gender_out=full_graph.get_tensor_by_name('gender_pred/Sigmoid:0')
        in_img=full_graph.get_tensor_by_name('input_1:0')

        print('========== Start Predicting... ==========')

        if not os.path.exists('/mnt/louis/{}_demographic_100.csv'.format(args.data)):
            df = pd.DataFrame(columns=['username','age_class','gender_class'])
        else:
            df = pd.read_csv('/mnt/louis/{}_demographic_100.csv'.format(args.data))
            print('Use Checkpoint!')

        processed_username_set = set(df['username'])

        _, _, filenames = next(os.walk(DATA_SOURCE_PATH_ROOT))
        for filename in tqdm(filenames):
            try:
                if filename.split('.jpg')[0] not in processed_username_set:
                    face_image_np = np.array(Image.open(DATA_SOURCE_PATH_ROOT+'/'+filename).convert('RGB'))
                    face_image_np_shape = face_image_np.shape
                    face_locations = face_recognition.face_locations(face_image_np, model='hog')
                    if len(face_locations)>0:
                        if len(face_locations)>1:
                            most_centered_bbox = get_most_center_bbox(face_locations,face_image_np_shape)
                        else:
                            most_centered_bbox = face_locations[0]
                        img = extract_face(face_image_np,most_centered_bbox)
                        img = np.array([cv2.resize(img,(192,192))])

                        age_preds,gender_preds = sess.run([age_out,gender_out], feed_dict={in_img: img})

                        df = df.append({
                            'username':filename.split('.jpg')[0],
                            'age_class': np.argmax(age_preds),
                            'gender_class': classify_gender(gender_preds)},ignore_index=True)

            except Exception as e:
                print(e)

    df.to_csv('/mnt/louis/{}_demographic_100.csv'.format(args.data),index=False)



