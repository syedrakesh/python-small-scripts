import csv
import os

def split_emails_to_csv_fast(input_file, output_dir, group_email, max_rows=3000):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize variables
    file_count = 1
    row_count = 0
    output_file = os.path.join(output_dir, f"emails_part_{file_count}.csv")
    csvfile = open(output_file, 'w', newline='')
    writer = csv.writer(csvfile)
    writer.writerow(["Group Email [Required]", "Member Email", "Member Type", "Member Role"])

    # Read and process the input file line by line
    with open(input_file, 'r') as infile:
        for line in infile:
            email = line.strip()
            if email:
                writer.writerow([group_email, email, "", ""])
                row_count += 1

                # If max_rows is reached, start a new file
                if row_count >= max_rows:
                    csvfile.close()
                    file_count += 1
                    row_count = 0
                    output_file = os.path.join(output_dir, f"emails_part_{file_count}.csv")
                    csvfile = open(output_file, 'w', newline='')
                    writer = csv.writer(csvfile)
                    writer.writerow(["Group Email [Required]", "Member Email", "Member Type", "Member Role"])

    # Close the last file
    csvfile.close()
    print(f"Processed emails into {file_count} CSV file(s) in '{output_dir}'.")

# Usage example
input_file = "emails.txt"  # Replace with the path to your text file
output_dir = "output_csvs"  # Replace with your desired output directory
group_email = "fhfghfghfghfghfgh@a.bestedu.club"  # Replace with your fixed group email

split_emails_to_csv_fast(input_file, output_dir, group_email)
