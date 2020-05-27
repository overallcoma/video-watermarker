import csv
import os
import subprocess
from PIL import ImageDraw, Image, ImageFont


script_path = os.path.dirname(os.path.realpath(__file__))
files_path = os.path.join(script_path, "files")
ffmpeg = os.path.join(files_path, "ffmpeg.exe")
font_file_name = os.path.join(files_path, "freemon.ttf")
video_folder = os.path.join(script_path, "video")
video_extension = ".mp4"
output_folder = os.path.join(script_path, "output")
student_list_csv = os.path.join(script_path, "student_list.csv")


def create_watermark_image(image_output, font, text):
    image_image = Image.new('RGBA', (700, 100), (255, 255, 255, 0))
    image_font = ImageFont.truetype(font, 20)
    image_text = text
    image_color = (255, 255, 255, 50)
    image_draw = ImageDraw.Draw(image_image)
    image_draw.text((10, 10), image_text, font=image_font, fill=image_color)
    image_image.save(image_output)


def import_csv_rows(csv_input):
    csv_data = open(csv_input, 'r')
    csv_reader = csv.reader(csv_data)
    line_count = 0
    return_array = []
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            return_array.append(row[0] + "  --  " + row[1])
            line_count += 1
    return return_array


def get_video_list():
    if not os.path.exists(video_folder):
        print("Excpected to find video folder at:")
        print("--- " + video_folder + " ---")
        print("But did not find the folder")
        print("exiting")
        exit(1)
    video_files = os.listdir(video_folder)
    video_file_list = []
    for video_file in video_files:
        if video_file.endswith(video_extension):
            video_path = os.path.join(video_folder, video_file)
            video_file_list.append(video_path)
    if video_file_list == []:
        print("No " + video_extension + " files found in " + video_folder)
        print("Please make sure your input videos are present in the proper directory")
        exit(1)
    return video_file_list


def create_student_dir(student_name):
    output_folder_path = os.path.join(output_folder, student_name)
    try:
        os.mkdir(output_folder_path)
    except Exception as e:
        print("Student folder already exists - skipping creation")
    return output_folder_path


def workflow():
    student_list = import_csv_rows(student_list_csv)
    video_list = get_video_list()
    # Creates output folder
    try:
        os.mkdir(output_folder)
    except Exception as e:
        print("Output Path already exists - skipping creation")
    for student_watermarktext in student_list:
        student_name = (student_watermarktext.split(" --")[0]).strip()
        student_output_folder = create_student_dir(student_name)
        watermark_path = os.path.join(student_output_folder, "wm.png")
        create_watermark_image(watermark_path, font_file_name, student_watermarktext)
        for video in video_list:
            output_file = os.path.join(student_output_folder, os.path.basename(video))
            print("Generating " + os.path.basename(video) + " for " + student_name)
            subprocess.run([ffmpeg, "-loglevel", "warning", "-i", video, "-i", watermark_path, "-filter_complex",
                            "overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2", output_file, "-y"])
        os.remove(watermark_path)
        print(student_name + " is complete")


workflow()
print("yay")
