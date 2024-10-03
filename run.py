import subprocess
import argparse
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

def run_main_on_folder(folder_path):
    # Ensure the folder path exists
    if not os.path.exists(folder_path):
        return f"Folder does not exist: {folder_path}"
    
    try:
        # Execute main.py with the folder path as an argument
        result = subprocess.run(['python', 'main.py', folder_path], check=True, capture_output=True, text=True)
        return f"Successfully processed folder: {folder_path}\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Error processing folder {folder_path}: {e.stderr}"

def main():
    # Set up argument parser to accept multiple folder paths
    parser = argparse.ArgumentParser(description="Run main.py on multiple folder paths using multiprocessing.")
    parser.add_argument("folder_paths", nargs='+', help="Paths to the folders")

    args = parser.parse_args()

    # Use ProcessPoolExecutor for multiprocessing
    with ProcessPoolExecutor(max_workers=4) as executor:  # Use 4 workers (one per vCPU)
        futures = {executor.submit(run_main_on_folder, folder): folder for folder in args.folder_paths}

        # Iterate over the completed tasks
        for future in as_completed(futures):
            folder = futures[future]
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"Exception occurred while processing {folder}: {e}")

if __name__ == "__main__":
    main()

