def generate_php_syntax_from_file(file_path, group_size=10):
    # Read WO IDs from the text file
    with open(file_path, 'r') as file:
        wo_ids = [line.strip() for line in file if line.strip()]  # Remove empty lines and trim whitespace

    # Split the WO IDs into groups of specified size
    groups = [wo_ids[i:i + group_size] for i in range(0, len(wo_ids), group_size)]

    php_code = ""

    # Generate PHP code for each group
    for i, group in enumerate(groups, start=1):
        # Create a single-line array
        php_code += f"$damWoID{i} = ['" + "', '".join(group) + "'];\n\n"

        # Add update query for the current group
        php_code += f"WorkOrder::whereIn('dam_wo_id', $damWoID{i})->where('wo_status', 4)->update(['wo_status' => 30]);\n\n"

        # Add get query for verification
        php_code += f"WorkOrder::whereIn('dam_wo_id', $damWoID{i})->get('wo_status');\n\n"

    return php_code


# Example usage:
input_file = "implementation_to_awaiting_tinker_input.txt"  # Replace with your actual file name
group_size = 10  # Customize the group size if needed

# Generate PHP syntax
php_code = generate_php_syntax_from_file(input_file, group_size)

# Save the generated PHP code to a file (optional)
output_file = "implementation_to_awaiting_tinker_output.txt"
with open(output_file, "w") as file:
    file.write(php_code)

print(f"PHP code has been generated and saved to {output_file}.")
