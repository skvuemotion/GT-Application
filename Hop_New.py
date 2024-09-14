#Comments to Run:
# . to go next
# , to go back
# 1,2,3,4 - Right down, Right Up, Left Down, Left Up
import pandas as pd
import argparse
import cv2
import os

key_list = ['RD','RU','LD','LU']

global mouseX,mouseY, foot_y_list, foot_x_list,window1,window_title, frame_number

mouseY,mouseX = 0,0
foot_x_list = []
foot_y_list = []

def update_key(current_key):
    #RD and RU
    if current_key == 0:
        return 1
    elif current_key == 1:
        return 0
    
    #LD and LU
    if current_key == 2:
        return 3
    elif current_key == 3:
        return 2
    
    
def stride_gt_creator(video_path, out_dir):
    global mouseX,mouseY, foot_y_list, foot_x_list,window1,window_title, frame_number
    
    current_key= -1


    frame_number = 0

    cam = cv2.VideoCapture(video_path)
    video_name = os.path.basename(video_path)[:-4]

    rd_list, ru_list = [], []
    ld_list, lu_list = [], []
    stf_list=[]
    fgu_list=[]

    #let's setup a window where we will show the images
    window1 = r"VML GT UpDown Annotation"
    window_title= f"Frame : {frame_number}"

    cv2.namedWindow(window1, cv2.WINDOW_NORMAL)
    cv2.setWindowTitle(window1, window_title)
    cv2.resizeWindow(window1, 1920, 1080)

    

    skip_frames = 8
    skip_frames_back = 3

    while cam.isOpened():

        ret_val, image = cam.read()

        if ret_val is False:
            break

        frame_number += 1
        #print('While L: frame:',frame_number)

        cv2.setWindowTitle(window1, f"Frame : {frame_number} (1:RD, 2:RU, 3:LD, 4:LU, 0:Continue Mode), Cursor(x,y)={mouseX},{mouseY}")
        cv2.imshow(window1, image)
        k = cv2.waitKey(0)

        if k == 46:  # . KEY Go Fwd 1 frame
            continue
        
        if k == 44:  # , KEY Go back 1 frame
           if frame_number - 2 < 0:
               print("Cannot Go Back - Not Enough Frames")
           else:
               cam.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 2)
               frame_number -= 2
        
        #skipping multiple frames
        if k== 108 or k==76: #key l or L - jump ahead skip frames
            for skip in range(0,skip_frames):
                ret_val, image = cam.read()
                if ret_val is False:
                    break
                frame_number += 1
            
        
        if k== 107 or k==75: #key k or K - jump back
            target_framenum = max(0,frame_number-skip_frames_back)
            #print('Target Frame',target_framenum)
            frame_number=0
            cam = cv2.VideoCapture(video_path)
            ret_val, image = cam.read()
            if ret_val is False:
                break
            frame_number += 1
            #print('frame:',frame_number)
            for skip in range(0,target_framenum):
                ret_val, image = cam.read()
                if ret_val is False:
                    break
                frame_number += 1
                #print('frame:',frame_number)

        if k== 106 or k==74: #key j or J - jump back
            target_framenum = max(0,frame_number-13)
            #print('Target Frame',target_framenum)
            frame_number=0
            cam = cv2.VideoCapture(video_path)
            ret_val, image = cam.read()
            if ret_val is False:
                break
            frame_number += 1
            #print('frame:',frame_number)
            for skip in range(0,target_framenum):
                ret_val, image = cam.read()
                if ret_val is False:
                    break
                frame_number += 1
                #print('frame:',frame_number)

        
        if k==55:            #key 7 - stf frame
            stf_list.append(frame_number)

        if k==57:            #key 9 - fgu frame
            fgu_list.append(frame_number)

        ['RD','RU','LD','LU']
        
        if k == 48:  #0 KEY
            if current_key==-1: #not reset
                print('Please start with 1,2,3,4 keys to register the leg')
            else:
                if current_key==0:
                    rd_list.append(frame_number)
                    print(f"Assigning {frame_number} as Right Down")
                if current_key==1:
                    ru_list.append(frame_number)
                    print(f"Assigning {frame_number} as Right Up")

                if current_key==2:
                    ld_list.append(frame_number)
                    print(f"Assigning {frame_number} as Left Down")
                if current_key==3:
                    lu_list.append(frame_number)
                    print(f"Assigning {frame_number} as Left Up")
                current_key = update_key(current_key)

        if k == 49:  # 1 KEY
            if current_key==-1: #not reset
                current_key = 0
            current_key = update_key(current_key)

            rd_list.append(frame_number)
            print(f"Assigning {frame_number} as Right Down")
            
        if k == 50:  # 2 KEY
            if current_key==-1: #not reset
                current_key = 1
            current_key = update_key(current_key)

            ru_list.append(frame_number)
            print(f"Assigning {frame_number} as Right Up")
            

        if k == 51:  # 3 KEY
            if current_key==-1: #not reset
                current_key = 2
            current_key = update_key(current_key)

            ld_list.append(frame_number)
            print(f"Assigning {frame_number} as Left Down")
            

        if k == 52:  # 4 KEY
            if current_key==-1: #not reset
                current_key = 3
            current_key = update_key(current_key)
            lu_list.append(frame_number)
            print(f"Assigning {frame_number} as Left Up")
            

        if k == 27:  # ESC KEY
            cv2.destroyAllWindows()
            print("EXITING")
            break

    gt_strides_df = pd.DataFrame(columns=["Foot", "GD", "GU","X","Y"],dtype=object)

    right_total_list = sorted(rd_list + ru_list)

    left_total_list = sorted(ld_list + lu_list)

    total_list = sorted(right_total_list + left_total_list)

    gd_list = []
    gu_list = []
    foot_list = []

    for gt_frame in total_list:

        if gt_frame in rd_list:
            gd_list.append(gt_frame)
        if gt_frame in ru_list:
            gu_list.append(gt_frame)
            if len(gd_list) == 0:
                gd_list.append(
                    None
                )  # If somehow the very first thing in the video is right up
        if gt_frame in ld_list:
            gd_list.append(gt_frame)
        if gt_frame in lu_list:
            gu_list.append(gt_frame)
            if len(gd_list) == 0:
                gd_list.append(
                    None
                )  # If somehow the very first thing in the video is left up

    if len(total_list) > 0:

        if (
            total_list[-1] in rd_list or total_list[-1] in ld_list
        ):  # If the last thing in the video is a ground down frame but we don't see it going up - so to equalize the number of rows
            gu_list.append(None)

        assert len(gd_list) == len(gu_list)

        gt_strides_df["GD"] = gd_list
        gt_strides_df["GU"] = gu_list
        if (len(foot_x_list)==len(gd_list)):
            gt_strides_df["X"] = foot_x_list
            gt_strides_df["Y"] = foot_y_list

        gt_strides_df.to_csv(
            os.path.join(out_dir, f"GT_{video_name}-stats.csv"), index=False
        )

        for gd, gu in zip(gd_list, gu_list):
            if gd is not None:
                if gd in rd_list:
                    foot_list.append("Right")
                if gd in ld_list:
                    foot_list.append("Left")
            elif gu is not None:
                if gu in ru_list:
                    foot_list.append("Right")
                if gu in lu_list:
                    foot_list.append("Left")
            else:
                print("Please check the CSV - Both GD AND GU SHOULDN'T BE NONE")

        assert len(foot_list) == len(gd_list) == len(gu_list)

        gt_strides_df["Foot"] = foot_list

        if len(stf_list)!=0:
            stf_list=[stf_list[0] for i in range(len(foot_list))]
            gt_strides_df["STF"] = stf_list

        if len(fgu_list)!=0:
            fgu_list=[fgu_list[0] for i in range(len(foot_list))]
            gt_strides_df["FGU"] = fgu_list

        gt_strides_df.to_csv(
            os.path.join(out_dir, f"GT_{video_name}-stats.csv"), index=False
        )
        print('output written:',os.path.join(out_dir, f"GT3Column_{video_name}-stats.csv"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--video_path",
        type=str,
        help="Enter path to video",
        required=True
    )
    parser.add_argument("--out_dir", type=str, help="Path to Output Directory")
    opt = parser.parse_args()

    video_path = opt.video_path
    out_dir = opt.out_dir

    if out_dir==None:
        out_dir=os.path.dirname(video_path)
    print('Writing Output to:', out_dir)
    stride_gt_creator(video_path, out_dir)





