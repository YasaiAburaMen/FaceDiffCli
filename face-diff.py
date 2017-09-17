import requests
import xml.etree.ElementTree as ET
import base64
import json
import math
import os
import subprocess
import sys

def post_img_api(img_path):
    url = 'https://api-us.faceplusplus.com/facepp/v3/detect'
    image = base64.encodestring(open(img_path, 'rb').read())
    data = {
        'api_key': 'b0TSh2bMfgb0Mm37o0RoKKhupmrrGF_Y',
        'api_secret': 'sVqSFtyAAb81T6cdMpt9QYjQaLnk3rv0',
        'image_base64': image,
        'return_landmark': '1'
    }
    
    r = requests.post(url, data=data)
    result = json.loads(r.text)
    return result

def make_rotated_img(img_path, new_img_path, landmark):
    left_eye = landmark['left_eye_center']
    right_eye = landmark['right_eye_center']
    nose = landmark['nose_tip']

    rotate_digree = 360 - get_digree(int(left_eye['x']), int(left_eye['y']),
                                     int(right_eye['x']), int(right_eye['y']))
    if rotate_digree > 360:
        rotate_digree = rotate_digree - 360
    rotate_digree = round(rotate_digree, 1)    
        
    subprocess.run(['convert', '-rotate', str(rotate_digree), img_path, new_img_path])

    center_point = get_center_point(img_path)
    cen_left_diff = (int(left_eye['x']) - center_point[0],
                     int(left_eye['y']) - center_point[1])    
    cen_right_diff = (int(right_eye['x']) - center_point[0],
                      int(right_eye['y']) - center_point[1])
    cen_nose_diff = (int(nose['x']) - center_point[0],
                     int(nose['y']) - center_point[1])
    
    new_center_point = get_center_point(new_img_path)
    new_left_eye = (new_center_point[0] + cen_left_diff[0],
                    new_center_point[1] + cen_left_diff[1])
    new_right_eye = (new_center_point[0] + cen_right_diff[0],
                     new_center_point[1] + cen_right_diff[1])
    new_nose = (new_center_point[0] + cen_nose_diff[0],
                new_center_point[1] + cen_nose_diff[1])

    rotated_left = get_rotated_point(new_left_eye, rotate_digree, new_center_point)
    rotated_right = get_rotated_point(new_right_eye, rotate_digree, new_center_point)
    rotated_nose = get_rotated_point(new_nose, rotate_digree, new_center_point)

    return (rotated_left, rotated_right, rotated_nose)
        
def get_digree(x1, y1, x2, y2):
    radian = math.atan2(y2 - y1, x2 - x1)
    digree = math.degrees(radian)
    return digree

def get_center_point(img_path):
    img_size_cmd = subprocess.run(['identify', '-format', '%w %h', img_path],
                                  stdout=subprocess.PIPE)
    img_size_str = img_size_cmd.stdout.decode('utf-8').split(' ')
    center_point = (int(img_size_str[0])/2, int(img_size_str[1])/2)
    return center_point

def get_rotated_point(point, digree, center_point):
    radian = math.radians(digree)
    x = (point[0] - center_point[0]) * math.cos(radian) - (point[1] - center_point[1]) * math.sin(radian) + center_point[0]
    y = (point[0] - center_point[0]) * math.sin(radian) + (point[1] - center_point[1]) * math.cos(radian) + center_point[1]
    return (x,y)
    
def rotate_img(img_path):
    json_data = post_img_api(img_path)
    landmark = json_data['faces'][0]['landmark']
    img_name = os.path.basename(img_path).split('.')[0]
    path_prefix = './'
    rotate_img_path = path_prefix + img_name+'_tmp.jpg'
    rotated_point = make_rotated_img(img_path, rotate_img_path , landmark)
    
    return (rotated_point, rotate_img_path)


def superimpose_img(img1, p1, img2, p2, diff_img):
    x_diff = round(p1[0][0] - p2[0][0], 2) * -1
    y_diff = round(p1[0][1] - p2[0][1], 2) * -1
    point = ''
    if x_diff > 0:
        point = point + '+'+str(x_diff)
    else:
        point = point + str(x_diff)
    if y_diff > 0:
        point = point + '+'+str(y_diff)
    else:
        point = point + str(y_diff)

    subprocess.run(['composite','-gravity','northwest',
                    '-geometry', point,
                    '-compose','difference',
                     img1, img2, diff_img])    

def main(img1, img2, diff_path):
    img_path1 = img1
    img_path2 = img2
    diff_img_path = diff_path
    
    rotated_point1 = rotate_img(img_path1)
    point1 = rotated_point1[0]
    rotate_img_path1 = rotated_point1[1]

    rotated_point2 = rotate_img(img_path2)
    point2 = rotated_point2[0]
    rotate_img_path2 = rotated_point2[1]
    
    superimpose_img(rotate_img_path1, point1,
                    rotate_img_path2, point2,
                    diff_img_path)
    print(diff_img_path)
    

args = sys.argv    
main(args[1], args[2], args[3])

