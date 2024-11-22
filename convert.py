import cv2
import os
import argparse

def extract_images_from_video(video_path, output_folder, frame_interval=160):
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load the video
    video_capture = cv2.VideoCapture(video_path)

    if not video_capture.isOpened():
        print(f"Error opening video file: {video_path}")
        return

    frame_count = 0
    extracted_count = 0

    # Loop through the video frames
    while True:
        success, frame = video_capture.read()
        if not success:
            break

        # Save frames at the specified interval
        if frame_count % frame_interval == 0:
            output_filename = os.path.join(output_folder, f"frame_{extracted_count}.jpg")
            cv2.imwrite(output_filename, frame)
            print(f"Saved: {output_filename}")
            extracted_count += 1

        frame_count += 1

    video_capture.release()
    print(f"Total frames extracted from {video_path}: {extracted_count}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Extract frames from multiple videos.")
    parser.add_argument("video_paths", nargs='+', help="Paths to the input video files")
    parser.add_argument("--output_folder", required=True, help="Path to the output folder for extracted images")

    args = parser.parse_args()

    # Loop over each video provided
    for video_path in args.video_paths:

        # Call the function to extract frames for each video
        extract_images_from_video(video_path, args.output_folder)

if __name__ == "__main__":
    main()

