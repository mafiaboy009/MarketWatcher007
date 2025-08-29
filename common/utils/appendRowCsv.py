import csv


def append_row_to_csv(filename, new_row_data, fieldnames=None):
    """
    Appends a new row to a CSV file. Creates the file if it doesn't exist.

    Args:
        filename (str): The name of the CSV file.
        new_row_data (list or dict): The data for the new row.
                                      If a list, it's appended directly.
                                      If a dict, fieldnames must be provided
                                      to use csv.DictWriter.
        fieldnames (list, optional): A list of field names (column headers)
                                     for DictWriter. Required if new_row_data
                                     is a dictionary and the file might be new.
    """

    # Determine if the file already exists to decide if headers are needed
    try:
        with open(filename, 'r') as f:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open(filename, 'a', newline='') as csvfile:
        if isinstance(new_row_data, dict):
            if fieldnames is None and not file_exists:
                raise ValueError("fieldnames must be provided for a new CSV file when using dictionary data.")

            # If file is new, write headers first
            if not file_exists and fieldnames:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

            # Use DictWriter to append the dictionary row
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames if fieldnames else new_row_data.keys())
            writer.writerow(new_row_data)
        else:
            # Use regular writer for list data
            writer = csv.writer(csvfile)
            writer.writerow(new_row_data)


# Example Usage:

# Appending a list of values
new_data_list = ['value1', 'value2', 'value3']
append_row_to_csv('my_data.csv', new_data_list)

# Appending a dictionary of values (with fieldnames for potential new file)
new_data_dict = {'Header A': 'Data A', 'Header B': 'Data B'}
# Define fieldnames explicitly if the file might be new or you want a specific order
headers = ['Header A', 'Header B']
append_row_to_csv('my_dict_data.csv', new_data_dict, fieldnames=headers)