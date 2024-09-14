# Comments to Run:
# . to go next
# , to go back
# 1,2,3,4 - Right down, Right Up, Left Down, Left Up
import pandas as pd
import argparse
import cv2
import os

key_list = ["RD", "RU", "LD", "LU"]

global mouseX, mouseY, foot_y_list, foot_x_list, window1, window_title, frame_number

mouseY, mouseX = 0, 0
foot_x_list = []
foot_y_list = []


def get_cursor(event, x, y, flags, param):
    global mouseX, mouseY, foot_y_list, foot_x_list, window1, window_title, frame_number
    mouseX, mouseY = x, y
    # print('global',x,y)
    cv2.setWindowTitle(
        window1,
        f"Frame : {frame_number} Cursor(x,y)={mouseX},{mouseY}",
    )
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(x, y)
        mouseX, mouseY = x, y
        foot_x_list.append(x)
        foot_y_list.append(y)


def stride_gt_creator(video_path, out_dir, old_gt_csv_path):
    global mouseX, mouseY, foot_y_list, foot_x_list, window1, window_title, frame_number

    frame_number = 0

    cam = cv2.VideoCapture(video_path)
    video_name = os.path.basename(video_path)[:-4]

    # let's setup a window where we will show the images
    window1 = r"VML GT UpDown Annotation"
    window_title = f"Frame : {frame_number}"

    cv2.namedWindow(window1, cv2.WINDOW_NORMAL)
    cv2.setWindowTitle(window1, window_title)
    cv2.resizeWindow(window1, 1920, 1080)

    cv2.setMouseCallback(window1, get_cursor)
    old_strides_df = pd.read_csv(old_gt_csv_path)

    gd_list = list(old_strides_df["GD"])
    gu_list = list(old_strides_df["GU"])
    foot_list = list(old_strides_df["Foot"])
    if 'STF' in old_strides_df.columns:
        stf_list=list(old_strides_df["STF"])
    
    if 'FGU' in old_strides_df.columns:
        fgu_list=list(old_strides_df["FGU"])

    while cam.isOpened():

        ret_val, image = cam.read()

        if ret_val is False:
            break

        frame_number += 1
        if frame_number in gd_list:

            cv2.setWindowTitle(
                window1,
                f"Frame : {frame_number} Cursor(x,y)={mouseX},{mouseY}",
            )
            cv2.imshow(window1, image)
            k = cv2.waitKey(0)

            if k == 46:  # . KEY Go Fwd 1 frame
                continue

            if k == 27:  # ESC KEY
                cv2.destroyAllWindows()
                print("EXITING")
                break
        else:
            continue

    gt_strides_df = pd.DataFrame(columns=["Foot", "GD", "GU", "X", "Y"], dtype=object)

    gt_strides_df["GD"] = gd_list
    gt_strides_df["GU"] = gu_list
    if len(foot_x_list) == len(gd_list):
        gt_strides_df["X"] = foot_x_list
        gt_strides_df["Y"] = foot_y_list
        gt_strides_df["Foot"] = foot_list
    if 'STF' in old_strides_df.columns:
        gt_strides_df["STF"] = stf_list
    if 'FGU' in old_strides_df.columns:
        gt_strides_df["FGU"] = fgu_list
    gt_strides_df.to_csv(
        os.path.join(out_dir, f"GT_{video_name}-stats.csv"), index=False
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--video_path", type=str, help="Enter path to video", required=True
    )
    parser.add_argument("--out_dir", type=str, help="Path to Output Directory")
    parser.add_argument("--old_csv_path", type=str, help="Path to 3GT CSV")
    opt = parser.parse_args()

    video_path = opt.video_path
    out_dir = opt.out_dir
    old_csv_path = opt.old_csv_path

    if out_dir == None:
        out_dir = os.path.dirname(video_path)
    print("Writing Output to:", out_dir)

    stride_gt_creator(video_path, out_dir, old_csv_path)
