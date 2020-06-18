import numpy as np
import math
import random
import pandas

side = 'left'

def angle_cal(vector1, vector2):
  vector1_unit = vector1 / np.linalg.norm(vector1)
  vector2_unit = vector2 / np.linalg.norm(vector2)
  angle = round(math.degrees(np.arccos(np.clip(np.dot(vector1_unit, vector2_unit), -1.0, 1.0))))
  return angle

def bicep_curls(parts):
  global cond1, cond2, checking_cond1, prev_state, curr_state, mistake_count, success_count, flag, start_index, end_index, feedback, sound_file
  mid_thres = 130
  cond1_thres = 53
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
        sound_file = random.choice(['excellent.mp3', 'excellent2.mp3', 'excellent3.mp3', 'excellent4.mp3'])
        
      if max(checking_cond2) - min(checking_cond2) > cond2_thres:
        mistake_count += 1
        feedback = 'Your upper arm shows significant rotation around the shoulder when curling.'
        sound_file = 'bicep_curls_mistake2.mp3'
        
      if min(checking_cond1) >= cond1_thres:
        mistake_count += 1
        feedback = 'You are not curling the weight all the way up.'    
        sound_file = 'bicep_curls_mistake1.mp3'
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
  cond1_thres = 75
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
        sound_file = random.choice(['excellent.mp3', 'excellent2.mp3', 'excellent3.mp3', 'excellent4.mp3'])
      if max(checking_cond2) - min(checking_cond2) > cond2_thres:
        mistake_count += 1
        feedback = 'Your back is not straight when you lift the weight.'
        sound_file = 'front_raise_mistake2.mp3'
      if max(checking_cond1) < cond1_thres:
        mistake_count += 1
        feedback = 'You are not lifting the weight all the way up.'    
        sound_file = 'front_raise_mistake1.mp3'
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
  cond1_thres = 85
  cond2_thres = 85

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
        sound_file = random.choice(['excellent.mp3', 'excellent2.mp3', 'excellent3.mp3', 'excellent4.mp3'])
      if max(checking_cond2) < cond2_thres:
        mistake_count += 1
        feedback = 'Raise your left arm higher.'
        sound_file = 'lateral_raise_mistake2.mp3'
      if max(checking_cond1) < cond1_thres:
        mistake_count += 1
        feedback = 'Raise your right arm higher.'
        sound_file = 'lateral_raise_mistake1.mp3'
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
  cond2_thres = 80

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
        sound_file = random.choice(['excellent.mp3', 'excellent2.mp3', 'excellent3.mp3', 'excellent4.mp3'])
      if max(checking_cond2) > cond2_thres:
        mistake_count += 1
        feedback = 'Your knee is moving far forward.' 
        sound_file = 'squat_mistake2.mp3'
      if min(checking_cond1) > cond1_thres:
        mistake_count += 1
        feedback = 'You should lower your hip more.'    
        sound_file = 'squat_mistake1.mp3'
    except:
      print('waiting')

    flag = -1
    checking_cond1 = []
    checking_cond2 = []
  return ma_cond1[-1], ma_cond2[-1],  flag, mistake_count, success_count, feedback, sound_file