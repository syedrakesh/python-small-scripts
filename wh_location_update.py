def generate_update_sql(input_file, output_file):
    """
    Reads a text file containing tab-separated data and generates SQL update statements.

    Parameters:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output SQL file.
    """
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                # Strip whitespace and skip empty lines
                line = line.strip()
                if not line:
                    continue

                # Split each line into `id` and `value` assuming tab separation
                try:
                    wo_id, location_id = line.split('\t')
                except ValueError:
                    print(f"Skipping invalid line: {line}")
                    continue

                # Generate the SQL UPDATE statement
                sql = f"UPDATE `t_workorders` SET `wo_target_location_id` = '{location_id}' WHERE `t_workorders`.`dam_wo_id` = '{wo_id}';\n"

                # Write the SQL statement to the output file
                outfile.write(sql)

        print(f"SQL statements successfully written to: {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Input and output file paths
input_file = 'wh_location_update_input.txt'   # Replace with your input text file name
output_file = 'wh_location_update_dhk.sql'  # Replace with desired output SQL file name

# Generate SQL statements
generate_update_sql(input_file, output_file)
