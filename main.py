from flask import Flask, render_template, render_template, request, jsonify

import numpy as np
import pandas as pd
import json
import sqlite3

from math import degrees
from random import choice




app = Flask(__name__)

PART_NAMES = ['nose', 'leftEye',  'rightEye', 'leftEar', 'rightEar', 'leftShoulder', 'rightShoulder', 'leftElbow', 'rightElbow', 'leftWrist', 'rightWrist', 'leftHip', 'rightHip', 'leftKnee', 'rightKnee', 'leftAnkle', 'rightAnkle']
cond1 = np.array([])
cond2 = np.array([])
prev_state = -1
curr_state = -1
success_count = 0
mistake_count = 0
flag = -1
checking_cond1 = []
start_index = 0
end_index = 1
feedback = ''
sound_file = 'none'
side = 'left'
feedback_success = 'Excellent!'

#===========================================#
def get_keypoints(data):
  parts = {}
  for index, part in enumerate(PART_NAMES):
    parts[part] = np.array([data['data-uri'][index]['position']['x'], data['data-uri'][index]['position']['y']])
  return parts

def angle_cal(vector1, vector2):
  vector1_unit = vector1 / np.linalg.norm(vector1)
  vector2_unit = vector2 / np.linalg.norm(vector2)
  angle = round(degrees(np.arccos(np.clip(np.dot(vector1_unit, vector2_unit), -1.0, 1.0))))
  return angle

#===========================================#
def bicep_curls(parts):
  global cond1, cond2, checking_cond1, prev_state, curr_state, mistake_count, success_count, flag, start_index, end_index, feedback, sound_file
  mid_thres = 130
  cond1_thres = 55
  cond2_thres = 15

  # calculate neccessary vectors
  UpperArm_vec = parts[side + 'Shoulder'] - parts[side + 'Elbow']
  ForeArm_vec = parts[side + 'Wrist'] - parts[side + 'Elbow']
  Torso_vec =  parts[side + 'Shoulder'] - parts[side + 'Hip']

  # calculate angle between vectors
  UpperArm_ForeArm_angle = angle_cal(UpperArm_vec, ForeArm_vec)
  UpperArm_Torso_angle = angle_cal(Torso_vec, UpperArm_vec,)
  cond1 = np.append(cond1, UpperArm_ForeArm_angle)
  cond2 = np.append(cond2, UpperArm_Torso_angle)
  
  # converse angles list to moving average angles
  ma_cond1 = pd.Series(cond1).rolling(5).mean().dropna().round().tolist()
  ma_cond2 = pd.Series(cond2).rolling(5).mean().dropna().round().tolist()


  if ma_cond1[0] <= mid_thres:
    flag = 0
  if ma_cond1[-1] <= mid_thres and ma_cond1[-2] > mid_thres:
    curr_state = 0
    start_index = len(ma_cond1)
  elif ma_cond1[-1] >= mid_thres and ma_cond1[-2] < mid_thres:  
    curr_state = 1
    end_index = len(ma_cond1)

  if curr_state != prev_state:
    flag = (flag + 1)%2
  prev_state = curr_state

  if flag == 1:
    checking_cond1 = ma_cond1[start_index:end_index]
    checking_cond2 = ma_cond2[start_index:end_index]
    try:
      if min(checking_cond1) < cond1_thres and (max(checking_cond2) - min(checking_cond2) <= cond2_thres):
        success_count += 1
        feedback = 'Excellent!'
        sound_file = choice(['excellent1', 'excellent2', 'excellent3', 'excellent4'])
        
      if max(checking_cond2) - min(checking_cond2) > cond2_thres:
        mistake_count += 1
        feedback = 'Your upper arm shows significant rotation around the shoulder when curling.'
        sound_file = 'bicep_curls_2'
        
      if min(checking_cond1) >= cond1_thres:
        mistake_count += 1
        feedback = 'You are not curling the weight all the way up.'    
        sound_file = 'bicep_curls_1'
    except:
      print('waiting')

    flag = -1
    checking_cond1 = []
    checking_cond2 = []
  return ma_cond1[-1], ma_cond2[-1],  flag, mistake_count, success_count, feedback, sound_file

#===========================================#
def front_raise(parts):
  global cond1, cond2, checking_cond1, prev_state, curr_state, mistake_count, success_count, flag, start_index, end_index, feedback, sound_file
  mid_thres = 30
  cond1_thres = 65
  cond2_thres = 12

  # calculate neccessary vectors
  UpperArm_vec = parts[side + 'Elbow'] - parts[side + 'Shoulder']
  Torso_vec = parts[side + 'Hip'] - parts[side + 'Shoulder']
  Thigh_vec = parts[side + 'Hip'] - parts[side + 'Knee']

  # calculate angle between vectors
  UpperArm_Torso_angle = angle_cal(Torso_vec, UpperArm_vec,)
  Torso_Thigh_angle = angle_cal(Torso_vec, Thigh_vec)
  cond1 = np.append(cond1, UpperArm_Torso_angle)
  cond2 = np.append(cond2, Torso_Thigh_angle)
  
  # converse angles list to moving average angles
  ma_cond1 = pd.Series(cond1).rolling(5).mean().dropna().round().tolist()
  ma_cond2 = pd.Series(cond2).rolling(5).mean().dropna().round().tolist()
  
  if ma_cond1[0] >= mid_thres:
    flag = 0

  if ma_cond1[-1] >= mid_thres and ma_cond1[-2] < mid_thres:  
    curr_state = 1
    start_index = len(ma_cond1)
  elif ma_cond1[-1] <= mid_thres and ma_cond1[-2] > mid_thres:
    curr_state = 0
    end_index = len(ma_cond1)

  if curr_state != prev_state:
    flag = (flag + 1)%2
  prev_state = curr_state

  if flag == 1:
    checking_cond1 = ma_cond1[start_index:end_index]
    checking_cond2 = ma_cond2[start_index:end_index]
    try:
      if (max(checking_cond1) >= cond1_thres) and (max(checking_cond2) - min(checking_cond2) <= cond2_thres):
        success_count += 1
        feedback = 'Excellent!'
        sound_file = choice(['excellent1', 'excellent2', 'excellent3', 'excellent4'])
      if max(checking_cond2) - min(checking_cond2) > cond2_thres:
        mistake_count += 1
        feedback = 'Your back is not straight when you lift the weight.'
        sound_file = 'front_raise_2'
      if max(checking_cond1) < cond1_thres:
        mistake_count += 1
        feedback = 'You are not lifting the weight all the way up.'    
        sound_file = 'front_raise_1'
    except:
      print('waiting')
    print (checking_cond1)

    flag = -1
    checking_cond1 = []
    checking_cond2 = []
  return ma_cond1[-1], ma_cond2[-1],  flag, mistake_count, success_count, feedback, sound_file

#===========================================#
def lateral_raise(parts):
  global cond1, cond2, checking_cond1, prev_state, curr_state, mistake_count, success_count, flag, start_index, end_index, feedback, sound_file
  mid_thres = 40
  cond1_thres = 80
  cond2_thres = 80

  # calculate neccessary vectors
  right_UpperArm_vec = parts['rightElbow'] - parts['rightShoulder']
  right_Torso_vec =  parts['rightHip'] - parts['rightShoulder']
  left_UpperArm_vec = parts['leftElbow'] - parts['leftShoulder']
  left_Torso_vec =  parts['leftHip'] - parts['leftShoulder']

  # calculate angle between vectors
  right_UpperArm_Torso_angle = angle_cal(right_UpperArm_vec, right_Torso_vec)
  left_UpperArm_Torso_angle = angle_cal(left_UpperArm_vec, left_Torso_vec)
  cond1 = np.append(cond1, right_UpperArm_Torso_angle)
  cond2 = np.append(cond2, left_UpperArm_Torso_angle)
  
  # converse angles list to moving average angles
  ma_cond1 = pd.Series(cond1).rolling(5).mean().dropna().round().tolist()
  ma_cond2 = pd.Series(cond2).rolling(5).mean().dropna().round().tolist()

  if ma_cond1[0] >= mid_thres:
    flag = 0

  if ma_cond1[-1] >= mid_thres and ma_cond1[-2] < mid_thres:
    curr_state = 1
    start_index = len(ma_cond1)
  elif ma_cond1[-1] <= mid_thres and ma_cond1[-2] > mid_thres:  
    curr_state = 0
    end_index = len(ma_cond1)

  if curr_state != prev_state:
    flag = (flag + 1)%2
  prev_state = curr_state

  if flag == 1:
    checking_cond1 = ma_cond1[start_index:end_index]
    checking_cond2 = ma_cond2[start_index:end_index]
    try:
      if max(checking_cond1) >= cond1_thres and max(checking_cond2) >= cond2_thres:
        success_count += 1
        feedback = 'Excellent!'
        sound_file = choice(['excellent1', 'excellent2', 'excellent3', 'excellent4'])
      if max(checking_cond2) < cond2_thres:
        mistake_count += 1
        feedback = 'Raise your left arm higher.'
        sound_file = 'lateral_raise_2'
      if max(checking_cond1) < cond1_thres:
        mistake_count += 1
        feedback = 'Raise your right arm higher.'
        sound_file = 'lateral_raise_1'
    except:
      print('waiting')

    flag = -1
    checking_cond1 = []
    checking_cond2 = []
  return ma_cond1[-1], ma_cond2[-1],  flag, mistake_count, success_count, feedback, sound_file

#===========================================#
def squat(parts):
  global cond1, cond2, checking_cond1, prev_state, curr_state, mistake_count, success_count, flag, start_index, end_index, feedback, sound_file
  mid_thres = 150
  cond1_thres = 70
  cond2_thres = 120

  # calculate neccessary vectors
  Thigh_vec = parts[side + 'Hip'] - parts[side + 'Knee']
  Leg_vec = parts[side + 'Ankle'] - parts[side + 'Knee']

  # calculate angle between vectors
  Thigh_Leg_angle = angle_cal(Thigh_vec, Leg_vec)
  cond1 = np.append(cond1, Thigh_Leg_angle)
  
  
  # calculate distance between parts
  Knee_Ankle_distX = abs(parts[side + 'Knee'][0] - parts[side + 'Ankle'][0])
  cond2 = np.append(cond2, Knee_Ankle_distX)

  # converse angles list to moving average angles
  ma_cond1 = pd.Series(cond1).rolling(5).mean().dropna().round().tolist()
  ma_cond2 = pd.Series(cond2).rolling(5).mean().dropna().round().tolist()


  if ma_cond1[0] <= mid_thres:
    flag = 0
  if ma_cond1[-1] <= mid_thres and ma_cond1[-2] > mid_thres:
    curr_state = 0
    start_index = len(ma_cond1)
  elif ma_cond1[-1] >= mid_thres and ma_cond1[-2] < mid_thres:  
    curr_state = 1
    end_index = len(ma_cond1)

  if curr_state != prev_state:
    flag = (flag + 1)%2
  prev_state = curr_state

  if flag == 1:
    checking_cond1 = ma_cond1[start_index:end_index]
    checking_cond2 = ma_cond2[start_index:end_index]
    try:
      if min(checking_cond1) <= cond1_thres and max(checking_cond2) <= cond2_thres:
        success_count += 1
        feedback = 'Excellent!'
        sound_file = choice(['excellent1', 'excellent2', 'excellent3', 'excellent4'])
      if max(checking_cond2) > cond2_thres:
        mistake_count += 1
        feedback = 'Your knee is moving far forward.' 
        sound_file = 'squat_2'
      if min(checking_cond1) > cond1_thres:
        mistake_count += 1
        feedback = 'You should lower your hip more.'    
        sound_file = 'squat_1'
    except:
      print('waiting')

    flag = -1
    checking_cond1 = []
    checking_cond2 = []
  return ma_cond1[-1], ma_cond2[-1],  flag, mistake_count, success_count, feedback, sound_file
#===========================================#

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/training')
def training():
  sound_file_dict = {'excellent1':'static/audio/excellent1.mp3', 'excellent2':'static/audio/excellent2.mp3', 'excellent3':'static/audio/excellent3.mp3', 'excellent4':'static/audio/excellent4.mp3', "bicep_curls_1":"static/audio/bicep_curls_mistake1.mp3", "bicep_curls_2":"static/audio/bicep_curls_mistake2.mp3", "front_raise_1":"static/audio/front_raise_mistake1.mp3", "front_raise_2":"static/audio/front_raise_mistake2.mp3", "lateral_raise_1":"static/audio/lateral_raise_mistake1.mp3", "lateral_raise_2":"static/audio/lateral_raise_mistake2.mp3", "squat_1":"static/audio/squat_mistake1.mp3", "squat_2":"static/audio/squat_mistake2.mp3"}
  return render_template('training.html', sound_file_dict = sound_file_dict)

@app.route('/progress')
def progress():
  with sqlite3.connect("database.db") as con:
    cur = con.cursor()
    query = """
          SELECT SUM(bicep_curls), SUM(front_raise), SUM(lateral_raise), SUM(squat) FROM record
          WHERE user = 'andang'
          GROUP BY DATE(create_at);
          """
    result = cur.execute(query).fetchall()[0]
  return render_template('progress.html', result = result)

@app.route('/saveData/', methods=['POST'])
def save_data():
  global cond1, cond2, checking_cond1, prev_state, curr_state, mistake_count, success_count, flag, start_index, end_index, feedback, sound_file
  data = request.get_json()
  val_list = ['andang',0, 0, 0, 0]
  if data['type-exercise'] == 'bicep_curls':
    val_list[1] = data['count']
  elif data['type-exercise'] == 'front_raise':
    val_list[2] = data['count']
  elif data['type-exercise'] == 'lateral_raise':
    val_list[3] = data['count']
  elif data['type-exercise'] == 'squat':
    val_list[4] = data['count']

  with sqlite3.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("INSERT INTO record(user, bicep_curls, front_raise, lateral_raise, squat) VALUES (?,?,?,?,?)",(val_list))
    con.commit()
  print('saved')

  cond1 = np.array([])
  cond2 = np.array([])
  prev_state = -1
  curr_state = -1
  success_count = 0
  mistake_count = 0
  flag = -1
  checking_cond1 = []
  start_index = 0
  end_index = 1
  feedback = ''
  sound_file = 'none'
  side = 'left'
  return ({'save':1})

@app.route('/predict/', methods=['POST'])
def predict():
  global sound_file
  data = request.get_json()
  parts = get_keypoints(data)
  type_exercise = data['type-exercise']
  if type_exercise == 'bicep_curls':
   cond1, cond2, flag, mistake_count, success_count, feedback, sound_file = bicep_curls(parts)
  elif type_exercise == 'front_raise':
    cond1, cond2, flag, mistake_count, success_count, feedback, sound_file = front_raise(parts)
  elif type_exercise == 'lateral_raise':
    cond1, cond2, flag, mistake_count, success_count, feedback, sound_file = lateral_raise(parts)
  elif type_exercise == 'squat':
    cond1, cond2, flag, mistake_count, success_count, feedback, sound_file = squat(parts)
    
  result = jsonify({'cond1':cond1, 'cond2':cond2,'flag':flag, 'mistake_count': mistake_count, 'success_count': success_count, 'feedback': feedback, 'sound_file': sound_file})
  sound_file = 'none' 
  return result

if __name__ == '__main__':
  app.run(host='localhost', port=5000, debug=True)


