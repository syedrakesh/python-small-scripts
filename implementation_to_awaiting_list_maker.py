def extract_ids(file_path):
    with open(file_path, 'r') as file:
        wo_ids = [line.strip() for line in file if line.strip()]  # Remove empty lines and trim whitespace

    # Extract the numeric part from each damWoId
    ids = [int(wo_id[2:]) for wo_id in wo_ids]  # Remove 'WO' prefix and convert to integer
    return ids


# Example usage
input_file = "implementation_to_awaiting_list_input.txt"  # Replace with your text file containing damWoId
ids = extract_ids(input_file)

# Print the list in the desired format
print("ids = [", end="")
print(", ".join(map(str, ids)), end="")
print("]")
