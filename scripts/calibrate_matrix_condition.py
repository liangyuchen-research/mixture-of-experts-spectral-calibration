"""Fit a selected metal calibration curve within a Na/Ca/K/Mg matrix condition."""

def run():
    from project_paths import create_output_directory
    OUTPUT_DIR = create_output_directory("calibrate_matrix_condition")
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import tkinter as tk
    from tkinter import filedialog
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score

    # Initialize Tkinter
    root = tk.Tk()
    print('Please import your training data in CSV format (Concat.csv).')
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    root.withdraw()

    # Read the data
    data_original = pd.read_csv(file_path)
    col = list(data_original.columns)

    # Dynamically identify wavelength columns
    wavelength_cols = []
    info_cols = []
    for c in col:
        try:
            float(c)
            wavelength_cols.append(c)
        except ValueError:
            info_cols.append(c)

    # Extract Wavelengths & Data
    wavelength = np.array([float(j) for j in wavelength_cols])
    data_condition_df = data_original[info_cols]
    data = data_original[wavelength_cols].values.astype(float)

    # Extract Condition Columns (Na, Ca, K, Mg)
    try:
        na_col = data_original['Na'].values
        ca_col = data_original['Ca'].values
        k_col = data_original['K'].values
        mg_col = data_original['Mg'].values
    except KeyError as e:
        print(f"Error: Column {e} not found in the CSV.")
        raise SystemExit


    metal_line = ['368.677', '406.104', '214.158', '232.280','324.954','327.591']
    metal_name = {'368.677': 'Pb-368nm', '406.104': 'Pb-406nm', '214.158': 'Zn-214nm','232.280':'Ni-232nm','324.954':'Cu-324nm','327.591':'Cu-327nm'}
    metal_background = {
        '368.677': ['367.480', '369.873'],
        '406.104': ['405.273', '406.768'],
        '214.158': ['212.859', '215.642'],
        '232.280': ['230.621', '233.201'],
        '324.954': ['323.017', '326.185'],
        '327.591': ['327.239', '328.469']
    }

    #%%

    print("Wavelength range:", wavelength[0], "~", wavelength[-1])
    def find_idx(target_wl, wavelength_array):
        return (np.abs(wavelength_array - float(target_wl))).argmin()

    a = int(input("Do you want to normalize\n[1:No] [2:Cu-327nm] [3:Ni-236nm] [4:Ni-323nm] [5:Zn-214nm] [6:Hr] [7:Area]: "))

    if a == 1:
        spectrum = data
    elif a == 7:
        # Area Normalization
        data0 = data.copy()
        def get_indices(start_wl, end_wl, wl_arr):
            idx_start = find_idx(start_wl, wl_arr)
            idx_end = find_idx(end_wl, wl_arr)
            return np.arange(min(idx_start, idx_end), max(idx_start, idx_end) + 1)

        ranges_to_zero = [
            ('240.007', '329.873'), ('360.102', '375.499'), ('400.609', '410.415'),
            ('323.017', '340.015'), ('230.621', '240.007'), ('335.476', '360.102'),
            ('468.907', '500.126')
        ]
        for start_w, end_w in ranges_to_zero:
            if float(start_w) >= wavelength[0] and float(end_w) <= wavelength[-1]:
                indices = get_indices(start_w, end_w, wavelength)
                data0[:, indices] = 0
        area = np.trapz(data0, wavelength, axis=1)
        spectrum = data / area.reshape(len(data), 1)
    else:

        target_map = {
            2: '327.396', # Cu-327nm
            3: '236.330', # Ni-236nm
            4: '323.546', # Ni-323nm
            5: '213.856', # Zn-214nm
            6: '434.331'  # Hr
        }
        if a in target_map:
            target_wl = target_map[a]
            idx = find_idx(target_wl, wavelength)
            intensity = data[:, idx]
            spectrum = data / intensity.reshape(len(data), 1)
        else:
            spectrum = data

    results_df = pd.DataFrame(spectrum, columns=wavelength_cols)

    #%%
    # Background correction
    valid_metals = []
    for metal in metal_line:
        bg = metal_background[metal]
        if (float(metal) >= wavelength[0] and float(metal) <= wavelength[-1] and
            float(bg[0]) >= wavelength[0] and float(bg[1]) <= wavelength[-1]):
            valid_metals.append(metal)

    for metal in valid_metals:
        bg_wavelengths = metal_background[metal]
        col1 = wavelength_cols[find_idx(bg_wavelengths[0], wavelength)]
        col2 = wavelength_cols[find_idx(bg_wavelengths[1], wavelength)]
        col_peak = wavelength_cols[find_idx(metal, wavelength)]

        slope = (results_df[col1] - results_df[col2]) / (float(col1) - float(col2))
        intercept = results_df[col2] - (slope * float(col2))
        background = slope * float(metal) + intercept
        corrected_prediction = results_df[col_peak] - background

        results_df[metal_name[metal] + '_predict'] = corrected_prediction

    #%%

    b = int(input("Which metal peak you want to use for calibration\n[1:Cu-327nm] [2:Ni-232nm] [3:Zn-214nm]: "))


    peak_map = {
        1: ('Cu-327nm', 'Cu'),
        2: ('Ni-232nm', 'Ni'),
        3: ('Zn-214nm', 'Zn')
    }

    target_peak_name = ""
    target_element = ""
    metal_int = np.zeros(len(data))
    concentration = np.zeros(len(data))

    if b in peak_map:
        target_peak_name, target_element = peak_map[b]
        print(f"Selected Peak: {target_peak_name}, Target Element: {target_element}")


        if target_peak_name + '_predict' in results_df.columns:
            metal_int = results_df[target_peak_name + '_predict']
        else:
            print(f"Error: Intensity data for {target_peak_name} not found.")


        if target_element in data_original.columns:
            concentration = data_original[target_element].values
        else:
            print(f"Error: Concentration column '{target_element}' not found in CSV.")
    else:
        print("Invalid Selection.")


    calibration_int = []
    calibration_label = []

    c = 0
    while c < 1 and len(metal_int) > 0:
        try:
            na_val = float(input("What is your Na concentration: "))
            ca_val = float(input("What is your Ca concentration: "))
            k_val  = float(input("What is your K concentration: "))
            mg_val = float(input("What is your Mg concentration: "))

            found_count = 0
            for i in range(len(concentration)):
                if (na_col[i] == na_val and
                    ca_col[i] == ca_val and
                    k_col[i] == k_val and
                    mg_col[i] == mg_val):

                    calibration_int.append(metal_int[i])
                    calibration_label.append(concentration[i])
                    found_count += 1

            print(f"Found {found_count} matching data points.")
            if found_count > 0:
                c = c + 1
            else:
                print("No data found matching criteria. Try again.")
                retry = input("Retry? (y/n): ")
                if retry.lower() != 'y':
                    break
        except ValueError:
            print("Invalid input. Please enter numbers.")

    #%%
    # Plot and Test
    test_conc_num = str(input("Do you want to predict testing data(Y/N): "))

    def plot_calibration(labels, ints, metal_n, matrix_info, is_test=False, model=None):
        labels = np.array(labels).reshape(-1, 1)
        ints = np.array(ints).reshape(-1, 1)
        unique_labels = np.unique(labels)
        mean_int = []; std_int = []

        for label in unique_labels:
            mask = (np.abs(labels - label) < 1e-9).flatten()
            int_values = ints[mask]
            mean_int.append(np.mean(int_values))
            std_int.append(np.std(int_values))

        plt.figure(figsize=(8, 6))
        plt.errorbar(unique_labels, mean_int, yerr=std_int, fmt='o', capsize=5, label='Data Mean')

        if not is_test:
            mdl = LinearRegression()
            mdl.fit(labels, ints)
            predict = mdl.predict(labels)
            plt.plot(labels, predict, c="green", lw=2, label='Fit')

            slope = mdl.coef_[0][0]
            intercept = mdl.intercept_[0]
            r_squared = r2_score(ints, predict)

            first_label_mask = (np.abs(labels - unique_labels[0]) < 1e-9).flatten()
            if len(ints[first_label_mask]) > 1:
                STD = np.std(ints[first_label_mask])
            else:
                STD = 0

            LOD = 3 * STD / slope if slope != 0 else 0

            legend_text = f"Slope: {slope:.3f}\nIntercept: {intercept:.3f}\nR²: {r_squared:.4f}\nSTD: {STD:.3f}\nLOD: {LOD:.3f}"
            print(legend_text)
            plt.legend([legend_text], loc='lower right', prop={'size': 10})
            plt.title(f"{metal_n} calibration ({matrix_info})")
            plt.xlabel("Concentration (ppm)")
            plt.ylabel("Intensity (a.u.)")
            plt.show()
            return mdl, slope, intercept
        else:
            return None, 0, 0

    matrix_info = f"Na={na_val}, Ca={ca_val}, K={k_val}, Mg={mg_val}"

    if test_conc_num.upper() == 'N':
        if len(calibration_label) > 0:
            plot_calibration(calibration_label, calibration_int, target_peak_name, matrix_info)
        else:
            print("No data to plot.")

    else:
        # Train First
        if len(calibration_label) > 0:
            model, slope, intercept = plot_calibration(calibration_label, calibration_int, target_peak_name, matrix_info)

            # Test Data Import
            root = tk.Tk()
            print('Please import your testing data in CSV format (Concat.csv).')
            file_path_test = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            root.withdraw()

            data_original_test = pd.read_csv(file_path_test)
            col_test = list(data_original_test.columns)
            wavelength_cols_test = [c for c in col_test if c.replace('.','',1).isdigit()]
            wavelength_test = np.array([float(j) for j in wavelength_cols_test])
            data_test = data_original_test[wavelength_cols_test].values.astype(float)

            # Test conditions
            try:

                concentration_test = data_original_test[target_element].values / 10
                na_test = data_original_test['Na'].values
                ca_test = data_original_test['Ca'].values
                k_test = data_original_test['K'].values
                mg_test = data_original_test['Mg'].values
            except KeyError as e:
                print(f"Error reading test data: {e}")
                raise SystemExit

            # Process Test Data
            if a == 1:
                spectrum_test = data_test
            elif a == 7:
                limit_idx = 400 if 400 < data_test.shape[1] else data_test.shape[1]
                area_test = np.trapz(data_test[:, 0:limit_idx], wavelength_test[0:limit_idx], axis=1)
                spectrum_test = data_test / area_test.reshape(len(data_test), 1)
            else:
                if a in target_map:
                    idx = find_idx(target_map[a], wavelength_test)
                    spectrum_test = data_test / data_test[:, idx].reshape(len(data_test), 1)
                else:
                    spectrum_test = data_test

            results_df_test = pd.DataFrame(spectrum_test, columns=wavelength_cols_test)

            # Test Background Correction
            for metal in valid_metals:
                bg = metal_background[metal]
                if float(metal) >= wavelength_test[0] and float(metal) <= wavelength_test[-1]:
                    c1 = wavelength_cols_test[find_idx(bg[0], wavelength_test)]
                    c2 = wavelength_cols_test[find_idx(bg[1], wavelength_test)]
                    cp = wavelength_cols_test[find_idx(metal, wavelength_test)]

                    s = (results_df_test[c1] - results_df_test[c2]) / (float(c1) - float(c2))
                    ic = results_df_test[c2] - (s * float(c2))
                    bg_val = s * float(metal) + ic
                    results_df_test[metal_name[metal] + '_predict'] = results_df_test[cp] - bg_val

            # Filter Test Data
            calibration_int_test = []
            calibration_label_test = []

            if target_peak_name + '_predict' in results_df_test.columns:
                metal_int_test = results_df_test[target_peak_name + '_predict']

                c = 0
                while c < 1:
                    found_count = 0
                    for i in range(len(concentration_test)):
                        if (na_test[i] == na_val and
                            ca_test[i] == ca_val and
                            k_test[i] == k_val and
                            mg_test[i] == mg_val):

                            calibration_int_test.append(metal_int_test[i])
                            calibration_label_test.append(concentration_test[i])
                            found_count += 1
                    if found_count > 0:
                        c += 1
                    else:
                        print("No matching test data found.")
                        break

                if found_count > 0:
                    calibration_int_test = np.array(calibration_int_test)
                    calibration_label_test = np.array(calibration_label_test)
                    X_predicted = (calibration_int_test - intercept) / slope

                    unique_labels_test = np.unique(calibration_label_test)
                    X_mean = []; X_std = []
                    for label in unique_labels_test:
                        mask = (np.abs(calibration_label_test - label) < 1e-9)
                        vals = X_predicted[mask]
                        X_mean.append(np.mean(vals))
                        X_std.append(np.std(vals))

                    plt.figure(figsize=(8, 6))
                    plt.errorbar(X_mean, model.predict(np.array(X_mean).reshape(-1, 1)), xerr=X_std, fmt='o', capsize=5, label='Test Data')

                    for i, mean_val in enumerate(X_mean):
                        y_pos = model.predict(np.array([[mean_val]]))[0]
                        plt.annotate(f"{mean_val:.2f}", xy=(mean_val, y_pos), ha='center', va='bottom',
                                     fontsize=12, bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.5))

                    plt.xlabel("Predicted Concentration (ppm)")
                    plt.ylabel("Intensity (a.u.)")
                    plt.title(f"Test Data Prediction ({matrix_info})")
                    plt.show()
        else:
            print("Skipping testing because calibration failed (no data).")


if __name__ == "__main__":
    run()
