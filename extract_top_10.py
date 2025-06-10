import pandas as pd

# Input and output file paths
input_file = 'clutch_output - clutch_output.csv.csv'
output_file = 'top_10_clutch_companies.csv'

try:
    # Read the CSV file
    df = pd.read_csv(input_file, nrows=10)  # Read only first 10 rows (including header)
    
    # Save to new CSV
    df.to_csv(output_file, index=False)
    print(f"Successfully saved top 10 companies to {output_file}")
    
except FileNotFoundError:
    print(f"Error: Could not find the file '{input_file}'. Please check the file path.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
