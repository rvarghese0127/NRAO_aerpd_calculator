#Created by Ryan Varghese!
#2026 NRAO Summer Student

import pandas as pd
import glob
import os

# --- Auto PFD calculator ---

# Load the PFD limits spreadsheet
file_path = "PFD_limits.xlsx"
df = pd.read_excel(file_path)

def get_pfd_limit(f_mhz):
    for i in range(0, len(df)-1, 2):
        f1 = df.iloc[i]['Freq. (MHz)']
        f2 = df.iloc[i+1]['Freq. (MHz)']
        if f1 <= f_mhz <= f2:
            val1 = df.iloc[i]['NRQZ Limit (W/m2)']
            val2 = df.iloc[i+1]['NRQZ Limit (W/m2)']
            if val1 == 'formula':
                f_ghz = f_mhz / 1000.0
                return (f_ghz ** 2) * 1e-17
            else:
                if f1 == f2: 
                    return val1
                return val1 + (val2 - val1) * (f_mhz - f1) / (f2 - f1)
                
    if f_mhz > df.iloc[-1]['Freq. (MHz)']:
        f_ghz = f_mhz / 1000.0
        return (f_ghz ** 2) * 1e-17
    return None


# --- Constants for calculation ---
FREQ_MHZ = 2110
BW_MHZ = 10
PFD_LIM = get_pfd_limit(FREQ_MHZ)



# --- Folder and File Paths ---
INPUT_FOLDER = f"./{FREQ_MHZ}_raw_coordinates_data"

# The output file will automatically generate
OUTPUT_FILE = f"./{FREQ_MHZ}_aerpd_output.csv"

def process_and_combine_files(input_folder, output_file):
    # Find all CSV files in the raw data folder
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    
    if not csv_files:
        print(f"Error: Could not find any CSV files in '{input_folder}'.")
        return

    print(f"Found {len(csv_files)} files. Processing and combining...")
    processed_data_list = []

    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        print(f"Loading {file_name}...")
        
        df = pd.read_csv(file_path, low_memory=False)
        
        # The exact headers from TAP output
        required_columns = ['Tx Latitude', 'Tx Longitude', 'Total Path Loss (dB)']
        
        #verification - Check if the columns exist in this specific file
        if not all(col in df.columns for col in required_columns):
            print(f"  -> Warning: Missing columns in {file_name}. Skipping.")
            continue
            
        # Calculate AERPd using the 'Total Path Loss (dB)' column using TAP's TPA value
        bw_factor = BW_MHZ * 50
        df['AERPd_W'] = (
            4359.45 * bw_factor * PFD_LIM * (10 ** (df['Total Path Loss (dB)'] / 10)) / 
            (FREQ_MHZ ** 2)
        )
        
        # Filter down to the 3 columns you want for your map
        final_df = df[['Tx Latitude', 'Tx Longitude', 'AERPd_W']]
        
        # Renaming columns so kepler can read it
        final_df = final_df.rename(columns={
            'Tx Latitude': 'Latitude',
            'Tx Longitude': 'Longitude'
        })
        
        #Add to our master list
        processed_data_list.append(final_df)

    # Combine all processed dataframes into one massive dataframe to output on kepler
    if processed_data_list:
        print("\nMerging all data into a single master file...")
        master_df = pd.concat(processed_data_list, ignore_index=True)
        
        # Save the combined data to a single CSV in personal file
        master_df.to_csv(output_file, index=False)
        print(f"Success! Saved a total of {len(master_df)} coordinates to {output_file}.")
    else:
        print("\nNo data was processed. Please check the terminal for errors.")

if __name__ == "__main__":
    process_and_combine_files(INPUT_FOLDER, OUTPUT_FILE)