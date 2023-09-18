import os

# Get the current directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the directory where the files should be removed
target_directory = os.path.join(script_dir, "files")

try:
    # List all items in the target directory (files and subdirectories)
    items = os.listdir(target_directory)

    # Flag to track whether any files were found
    files_found = False

    # Loop through the items and remove files (skip directories)
    for item in items:
        item_path = os.path.join(target_directory, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
            files_found = True
        else:
            print(f"Skipping {item_path} as it is not a file.")

    if files_found:
        print("All files have been removed from the 'files' directory.")
    else:
        print("No files to remove in the 'files' directory.")
except FileNotFoundError:
    print("The 'files' directory does not exist.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
