import requests
import xml.etree.ElementTree as ET
import base64
import json
import math
import os
import subprocess

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
    
    subprocess.run(['convert', '-rotate', 360 - rotate_digree, img_path, new_img_path])

    center_point = get_center_point(img_path)
    cen_left_diff = (int(left_eye['x']) - center_point[0],
                     int(left_eye['y']) - center_point[1])    
    cen_right_diff = (int(right_eye['x']) - center_point[0],
                      int(right_eye['y']) - center_point[1])
    
    new_center_point = get_center_point(new_img_path)
    new_left_eye = (new_center_point[0] + cen_left_diff[0],
                    new_center_point[1] + cen_left_diff[1])
    new_right_eye = (new_center_point[0] + cen_right_diff[0],
                     new_center_point[1] + cen_right_diff[1])

    rotated_left = get_rotated_point(new_left_eye)
    rotated_right = get_rotated_point(new_right_eye)

    return (rotated_left, rotated_right)
    
#10,10     200,10
#    100,100
#10,200    200,200 
    
def get_digree(x1, y1, x2, y2):
    radian = math.atan2(y2 - y1, x2 - x2)
    digree = math.degrees(radian)
    return digree

def get_center_point(img_path):
    img_size_cmd = subprocess.run(['identify', '-format', '"%w %h"', img_path],
                                  stdout=subprocess.PIPE)
    img_size_str = img_size_cmd.stdout.decode('utf-8').split(' ')
    center_point = (int(img_size_str[0])/2, int(img_size_str[1])/2)
    return center_point

def get_rotated_point(point, digree):
    radian = math.radians(digree)
    x = point[0] * math.cos(radian) - point[1] * math.sin(radian)
    y = point[0] * math.sin(radian) + point[1] * math.con(radian)
    return (x,y)
    
def rotate_img(img_path):
    json_data = post_img_api(img_path)
    landmark = json_data['faces'][0]['landmark']
    img_name = os.path.basename(img_path).split('.')[0]
    path_prefix = ''
    rotate_img_path = path_prefix + img_name+"_tmp.jpg"
    rotated_point = make_rotated_img(img_path, rotate_img_path , landmark)

    return (rotated_point, rotate_img_name)


def superimpose_img(img1, p1, img2, p2, diff_img):
    # img1を基準に重ねる


def main():
    img_path1 = './pic1.jpg'
    img_path2 = './pic2.jpg'

    diff_img_path = './diff.jpg'
    
    rotated_point1 = rotate_img(img_path1)
    point1 = rotated_point1[0]
    rotate_img_path1 = rotated_point1[1]

    rotated_point2 = rotate_img(img_path2)
    point2 = rotated_point2[0]
    rotate_img_path2 = rotated_point2[1]

    superimpose_img(rotate_img_path1, point1,
                    rotate_img_path2, point2,
                    diff_img_path)

    
main()

