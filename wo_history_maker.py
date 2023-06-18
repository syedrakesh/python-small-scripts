import sys
import re

# Open a file for writing
with open('wo_history_maker_output.txt', 'w') as f:
    # Redirect the standard output to the file
    sys.stdout = f

    # Open the file for reading
    with open("wo_history_maker_input.txt", "r") as file:
        # Loop through each line in the file
        for line in file:
            # Parsing only numerical value
            wo_id = re.findall(r'\d+', line)[0]
            wo_id = wo_id.lstrip('0')
            query = "INSERT INTO t_wo_status_his (`id`, `wo_id`, `wo_status_id`, `wo_status_ch_by`, " \
                    "`wo_auto_remarks`, `created_at`, `updated_at`) VALUES (NULL, '{wo_id}', '6', '328', 'Cancelled " \
                    "by Admin Manually', now(), now());"

            print(query.format(wo_id=wo_id))

    # Restore the standard output
    sys.stdout = sys.__stdout__
print("Query Successfully Generated In wo_history_maker_output.txt")
