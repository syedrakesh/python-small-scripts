import csv
import os
import time


def split_emails_across_groups(input_emails_file, groups_file, output_dir, max_rows_per_group=3000):
    # Start the timer
    start_time = time.time()

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load group emails
    with open(groups_file, 'r') as group_file:
        group_emails = [line.strip() for line in group_file if line.strip()]

    # Read all emails from the input file
    with open(input_emails_file, 'r') as emails_file:
        emails = [line.strip() for line in emails_file if line.strip()]

    # Limit the total number of emails to process based on groups and max_rows_per_group
    total_emails_to_process = len(group_emails) * max_rows_per_group
    emails_to_use = emails[:total_emails_to_process]
    remaining_emails = emails[total_emails_to_process:]

    # Write emails for each group to individual CSV files
    for idx, group_email in enumerate(group_emails):
        # Get the emails for the current group
        start_idx = idx * max_rows_per_group
        end_idx = start_idx + max_rows_per_group
        group_emails_chunk = emails_to_use[start_idx:end_idx]

        # Create a CSV for the group
        output_file = os.path.join(output_dir, f"emails_part_{idx + 1}.csv")
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write the header row
            writer.writerow(["Group Email [Required]", "Member Email", "Member Type", "Member Role"])
            # Write the data rows
            for email in group_emails_chunk:
                writer.writerow([group_email, email, "", ""])

        print(f"Created: {output_file}")

    # Write any remaining emails to extras file
    if remaining_emails:
        extras_file = os.path.join(output_dir, "emails_extras.txt")
        with open(extras_file, 'w') as extras:
            extras.write("\n".join(remaining_emails))
        print(f"Remaining emails written to: {extras_file}")

    # Calculate and print the runtime
    end_time = time.time()
    print(f"Script completed in {end_time - start_time:.2f} seconds.")


# Usage example
input_emails_file = "emails.txt"  # Replace with the path to your email text file
groups_file = "groups.txt"  # Replace with the path to your groups text file
output_dir = "output_csvs"  # Replace with your desired output directory

split_emails_across_groups(input_emails_file, groups_file, output_dir)
