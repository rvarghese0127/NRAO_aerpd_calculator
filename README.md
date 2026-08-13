# NRAO AERPd Calculator

A script for computing AERPd (Adjusted Equivalent Radiated Power density) from
TAP (Terrain Analysis Package) coverage run output, using NRQZ PFD limits. It
combines a folder of raw coordinate CSVs into a single output CSV suitable for
mapping in [kepler.gl](https://kepler.gl/).

Built as part of a 2026 NRAO summer student project.

## What it does

1. Loads NRQZ PFD limits from `PFD_limits.xlsx` and interpolates (or applies
   the frequency-squared formula for higher frequencies) to find the PFD limit
   for a given frequency.
2. Reads every `*.csv` file in the input folder (TAP coverage run exports).
3. Computes `AERPd_W` per row from each file's `Total Path Loss (dB)` column:

   ```
   AERPd_W = 4359.45 * (BW_MHZ * 50) * PFD_LIM * 10^(Total Path Loss (dB) / 10) / FREQ_MHZ^2
   ```

4. Keeps only `Latitude`, `Longitude`, and `AERPd_W` (renamed from `Tx
   Latitude` / `Tx Longitude`) and concatenates all files into one master CSV.

## Requirements

- Python 3
- `pandas`
- `openpyxl` (for reading `.xlsx` via pandas)

```bash
pip install pandas openpyxl
```

## Usage

1. Make sure `PFD_limits.xlsx` is in the same directory as the script.
2. Set `FREQ_MHZ` and `BW_MHZ` near the top of `aerpd_calculator.py` to match
   the run you're processing. The script expects a matching input folder
   named `./{FREQ_MHZ}_raw_coordinates_data/`.

   This repo includes `617_raw_coordinates_data/` as sample input, so to
   reproduce that run, set:

   ```python
   FREQ_MHZ = 617
   BW_MHZ = 10  # adjust to your actual channel bandwidth
   ```

3. Each CSV in the input folder must contain the columns `Tx Latitude`,
   `Tx Longitude`, and `Total Path Loss (dB)` (standard TAP export headers).
   Files missing these columns are skipped with a warning.
4. Run it:

   ```bash
   python3 aerpd_calculator.py
   ```

5. Output is written to `./{FREQ_MHZ}_aerpd_output.csv` in the working
   directory, with columns `Latitude`, `Longitude`, `AERPd_W` — ready to drop
   into kepler.gl or another mapping tool.

## Files

- `aerpd_calculator.py` — the calculator script
- `PFD_limits.xlsx` — NRQZ PFD limit table by frequency, required input
- `617_raw_coordinates_data/` — sample raw TAP coverage run CSVs (617 MHz)
