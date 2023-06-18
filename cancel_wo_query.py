import sys

# Open a file for writing
with open('cancel_wo_query.txt', 'w') as f:
    # Redirect the standard output to the file
    sys.stdout = f

    # Print some output
    print("UPDATE t_workorders dtw\nSET dtw.wo_status = 6, dtw.wo_remarks = 'Cancelled by Admin Manually'\nWHERE")
    # Open the file for reading
    with open("wo_no.txt", "r") as file:
        # Read all lines of the file into a list
        lines = file.readlines()

        # Loop through each line in the file
        for line in lines:

            # If this is not the last line, just print the line
            if line != lines[-1]:
                line = line.strip()
                query = "(dtw.dam_wo_id = '{}') OR".format(line)
                print(query)

            # If this is the last line, print without OR
            else:
                print("(dtw.dam_wo_id = '{}');".format(line))

    # Restore the standard output
    sys.stdout = sys.__stdout__
print("Query Successfully Generated In cancel_wo_query.txt")
