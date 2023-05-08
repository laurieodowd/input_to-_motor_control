import cv2
import numpy as np
from random import randint
import subprocess
import time
screen = (600,400)
"""
cv2.namedWindow("fullscreen", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("fullscreen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
"""
cam = cv2.VideoCapture(0)

out_dim_x, out_dim_y = 800,600

def init_camera():
    cmd = "gphoto2 --capture-movie --stdout"
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=10**8)
camera_process = init_camera()

def read_mjpeg_stream(stream):
    buffer = b''
    while True:
        data = stream.read(2048)
        buffer += data
        jpg_start = buffer.find(b'\xff\xd8')
        jpg_end = buffer.find(b'\xff\xd9')

        if jpg_start != -1 and jpg_end != -1:
            jpg_data = buffer[jpg_start:jpg_end + 2]
            buffer = buffer[jpg_end + 2:]

            if jpg_data:  # Check if the JPEG data is not empty
                frame = cv2.imdecode(np.frombuffer(jpg_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                return frame

def create_gradient_colormap(input_colours, no_out_colours):
    # initialize outputs list with empty lists
    outputs = [[] for _ in range(no_out_colours)]

    # add darkest and lightest colours
    outputs[0] = input_colours[0]
    outputs[-1] = input_colours[-1]

    # create list of intervals
    interval_size = (np.array(input_colours[-1]) - np.array(input_colours[0])) / (no_out_colours - 1)
    intervals = [tuple(np.array(input_colours[0]) + i*interval_size) for i in range(no_out_colours)]

    # sort remaining input colours into output list
    used_indices = {0, no_out_colours - 1}  # keep track of indices already used
    for colour in input_colours[1:-1]:
        tone = sum(colour) / 3
        idx = np.abs([sum(intervals[i])/3 - tone for i in range(1, no_out_colours-1)]).argmin() + 1
        while idx in used_indices:
            idx += 1
        outputs[idx] = colour
        used_indices.add(idx)

    # fill in empty lists with gradient values
    last_index = 0
    for i in range(no_out_colours):
        if outputs[i]:
            last_index = i
        else:
            # find closest neighbours with defined values
            left_index = last_index
            while not outputs[left_index]:
                left_index -= 1
            right_index = i
            while not outputs[right_index]:
                right_index += 1
            # calculate gradient
            left_col = np.array(outputs[left_index])
            right_col = np.array(outputs[right_index])
            step_size = (right_col - left_col) / (right_index - left_index)
            for j in range(left_index+1, right_index):
                outputs[j] = tuple(left_col + (j-left_index)*step_size)
    outputs = [[int(c) for c in out] if out else out for out in outputs]
    return outputs

def play_frames_fullscreen(frames):
    # Initialize OpenCV video window
    cv2.namedWindow("fullscreen", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("fullscreen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Loop through frames and display them
    for frame in frames:
        # Resize frame to fit screen
        
        resized_frame = cv2.resize(frame, (1000,550))

        # Display frame in fullscreen window
        cv2.imshow("fullscreen", resized_frame)
        cv2.waitKey(1)

    # Clean up window and exit
    cv2.destroyAllWindows()
   
def show_frames(*frame):
    for i in frame:
        cv2.imshow('wdw', i)
        cv2.waitKey(10)

def linel_messi_v2(img, scalar_x, scalar_y, tones, line_width=None, background=None, line_color = None, canvas_color = None):
    img = cv2.resize(img, (100,100))
    canvas_color = (255,255,255) if canvas_color is None else canvas_color
    
    line_color = (0,0,0) if line_color is None else line_color

    # Set line_width to 1 if not provided, otherwise use the provided value
    line_width = 1 if line_width is None else line_width

    # Set canvas to the provided background or create a new one with the canvas_color
    canvas = cv2.resize(background, (img.shape[:2])) if background is not None else np.full((img.shape), canvas_color, dtype=np.uint8)

    list_tone_incs = np.linspace(0, 255, tones + 1)[1:]

    # Resizing image to desired dimensions
    
    input = cv2.resize(img, (int(out_dim_x / scalar_x), int(out_dim_y / scalar_y)))

    for i in range(input.shape[1]):
        for j in range(input.shape[0]):
            avg_tone = int(np.mean(input[j,i]))
            tone = np.argmin(np.abs(list_tone_incs - avg_tone))

            a1, a2, a3, a4 = i * scalar_x, j * scalar_y, ((i + 1) * scalar_x) - 1, ((j + 1) * scalar_y) - 1

            wedges = np.arange(1, tones - tone + 1)
            x_coords = (a1 + ((a3 - a1) / (tones - tone + 1)) * wedges).astype(int)
            y_coords = (a2 + ((a4 - a2) / (tones - tone + 1)) * wedges).astype(int)

            for x, y in zip(x_coords, y_coords):
                
                cv2.line(canvas, (a1, y), (a3, y), line_color, line_width)
                cv2.line(canvas, (x, a2), (x, a4), line_color, line_width)

    canvas = cv2.resize(canvas,(1000,1000), interpolation = cv2.INTER_NEAREST)
    return canvas

first_color = [255,0,0]
first_color_2 = [255,0,0]
"""
while True:
    
    last_color = [randint(2,255),randint(2,255),randint(2,255)]
    last_color_2 = [randint(2,255),randint(2,255),randint(2,255)]
    colors = create_gradient_colormap([first_color,last_color], 40)
    colors_back = create_gradient_colormap([first_color_2,last_color_2], 40)
    for i in range(len(colors)):
        
        ret, img = cam.read()
        output = linel_messi_v2(img, 400, 20,10, line_width = 2, line_color = colors[i], canvas_color = colors_back[i])
        #output = cv2.resize(output, (2000,1500), interpolation = cv2.INTER_NEAREST)
        show_frames(output)
    first_color = last_color
    first_color_2 = last_color_2
"""
while True:
    cam = cv2.VideoCapture(0)
    ret,img = cam.read()
    out = linel_messi_v2(img, 5,5,2)
    cv2.imshow('wdw', out)
    cv2.waitKey(1)    
        