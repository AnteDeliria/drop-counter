## Add a way to exit program

import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('clipboard_monitor')
install('Pillow')
install('opencv-python')

import clipboard_monitor 
from PIL import Image, ImageGrab
import cv2
import numpy as np
import json


## Load drop table
with open('drops.json', 'r') as file:
    drop_table = json.load(file)


## Format drop selection message
select_drop_message = ''
newline_counter = 0
drop_table_indextokey = {}
for i, key in enumerate(drop_table.keys()):
    ## Assign values to indexes for drop selection
    drop_table_indextokey[i] = key

    padding = 30 - (len(str(i)) + 3 + len(key))
    select_drop_message += f'{i} : {key}' + ' ' * padding
    newline_counter += 1
    if newline_counter >= 3:
        newline_counter = 0
        select_drop_message += '\n'


## Drop selection
print('\n' + select_drop_message + '\n')
while True:
    try:
        drop_table_index = int(input('Input the number corresponding to enemy of interest: '))
        if 0 <= drop_table_index < len(drop_table.keys()):
            break
        else:
            print("\nInvalid input. Please enter a valid integer.")
    except ValueError:
        print("\nInvalid input. Please enter a valid integer.")
    except KeyboardInterrupt:
        print("\nUser interrupted the program.")
        exit(1)

## Copy template names to list
template_name_list = drop_table[drop_table_indextokey[drop_table_index]]
template_name_list


## Target detection size selection
print('\n\nInput the width in pixels of the detected sprite as it appears on your screen. If you play on default 100% window scaling leave this blank.')
while True:
    try:
        user_input = input('\nInput detected sprite width: ')
        if user_input == '':
            detection_size = 48
            break
        if 0 < int(user_input):
            detection_size = int(user_input)
            break
        else:
            print("\nInvalid input. Please enter a valid number between 0 and 1.")
    except ValueError:
        print("\nInvalid input. Please enter a valid number between 0 and 1.")
    except KeyboardInterrupt:
        print("\nUser interrupted the program.")
        exit(1)


template_list = []
for template_name in template_name_list:

    ## Read template and resize to specified dimensions via nearest neighbor
    base_template = cv2.imread('Templates\\' + template_name + '.png', flags = cv2.IMREAD_UNCHANGED)
    if base_template is None:
        print("\nInvalid template files.")
        exit(1)
    base_template = cv2.resize(base_template, dsize=(detection_size, detection_size), interpolation = cv2.INTER_NEAREST_EXACT)

    ## Split template into channels and apply the alpha value to each channel
    blue_channel, green_channel, red_channel, alpha_channel = cv2.split(base_template)
    blue_channel_scaled = blue_channel * (alpha_channel / 255.0)
    green_channel_scaled = green_channel * (alpha_channel / 255.0)
    red_channel_scaled = red_channel * (alpha_channel / 255.0)

    ## Merge channels and convert from float to int array
    template = cv2.merge((blue_channel_scaled, green_channel_scaled, red_channel_scaled, alpha_channel/1))
    template = template.astype(np.uint8)

    ## Crop template to non-transparent pixels
    x, y, w, h = cv2.boundingRect(alpha_channel)
    template = template[y:y+h, x:x+w]
    template = template[:,:,:3]
    template_list.append(template)


## Keep track of template count and total count
template_count = {}
for template_name in template_name_list:
    template_count[template_name] = 0

total_count = 0


## Matching threshold selection
print('\n\nInput template matching threshold. The value must be between 0 and 1.\nHigher values will increase stringency. Leave blank for default.')
while True:
    try:
        user_input = input('\nInput template matching threshold: ')
        if user_input == '':
            threshold = 0.95
            break
        if 0 <= int(user_input) <= 1:
            threshold = int(user_input)
            break
        else:
            print("\nInvalid input. Please enter a valid number between 0 and 1.")
    except ValueError:
        print("\nInvalid input. Please enter a valid number between 0 and 1.")
    except KeyboardInterrupt:
        print("\nUser interrupted the program.")
        exit(1)


## On clipboard update
def process():

    ## Grab image from clipboard and convert to int array
    img = ImageGrab.grabclipboard()
    if img is None:
        return
    global total_count
    total_count += 1
    print('Processing...')
    img = np.array(img, dtype=np.uint8)

    ## Switch channels from RGB to BGR
    img = img[:, :, [2, 1, 0]]
    # print(img.shape)
    

    ## Match template and extract maximum matching value
    ## Extract number of matches above threshold matching value
    global threshold
    for i, template in enumerate(template_list):
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, maxVal, _, maxLoc = cv2.minMaxLoc(result)
        n_matches = np.where(result >= threshold)[0].size
        if n_matches > 0:
            template_count[template_name_list[i]] += 1
            print(f'Detected {template_name_list[i]} ({maxVal})    Total: {template_count[template_name_list[i]]}')
    print(f'Total kills: {total_count}')
    print('Done')
    
## Setup clipboard monitor
clipboard_monitor.on_update(print)
clipboard_monitor.on_image(process)


## Run clipboard monitor
print('\n\nPress PrintScreen to detect drops. Each press will be counted as a kill\n')
clipboard_monitor.wait()




### Debug and unused code

## Display the 10 highest values for result match

# indices = np.argpartition(result.ravel(), -10)[-10:]
# highest_values = result.ravel()[indices]
# highest_values


## Match template applied on a range of scaling values

# found = (0, 0, 1)
# threshold = .8
# for scale in np.linspace(1.0, 4.0, 13):
#     resized_template = cv2.resize(template, dsize=None, fx=scale, fy=scale, interpolation = cv2.INTER_NEAREST_EXACT)
#     if resized_template.shape[0] > img.shape[0] or resized_template.shape[1] < template.shape[1]:
#         break
#     scale_ratio = resized_template.shape[0] / template.shape[0]
#     result = cv2.matchTemplate(img, resized_template, cv2.TM_CCOEFF_NORMED)
#     _, maxVal, _, maxLoc = cv2.minMaxLoc(result)
#     n_matches = np.where(result >= threshold)[0].size
#     print(maxVal, n_matches, scale_ratio)
#     cv2.imwrite(f'resize{scale}.png', resized_template)
#     if maxVal > found[0]:
#         found = (maxVal, n_matches, scale_ratio)
	
# found
