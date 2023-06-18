import sys

# Open a file for writing
with open('asr_user_update_output.txt', 'w') as f:
    # Redirect the standard output to the file
    sys.stdout = f

    # Print some output
    print("UPDATE t_asset_service_requests tasr\nSET tasr.user_id = 327\nWHERE")
    # Open the file for reading
    with open("asr_user_update_input.txt", "r") as file:
        # Read all lines of the file into a list
        lines = file.readlines()

        # Loop through each line in the file
        for line in lines:

            # If this is not the last line, just print the line
            if line != lines[-1]:
                line = line.strip()
                query = "(tasr.dam_asr_id = '{}') OR".format(line)
                print(query)

            # If this is the last line, print "hello" and then the line
            else:
                print("(tasr.dam_asr_id = '{}');".format(line))

    # Restore the standard output
    sys.stdout = sys.__stdout__
print("Query Successfully Generated In asr_user_update_output.txt")
