"""Parse raw spectrometer records, subtract background, and aggregate repeated measurements."""

def run():
    from project_paths import create_output_directory
    OUTPUT_DIR = create_output_directory("process_spectrometer_records")
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from tkinter import filedialog
    import tkinter as tk
    import os
    import itertools
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score

    class data_reader():

        # Browse the data file
        def __init__(self):
            print('Please import your data in csv format.')
            root = tk.Tk()
            self.path = filedialog.askdirectory()
            self.output_path = str(OUTPUT_DIR)
            root.withdraw()
            self.pixel_number = 1948

            self.sampling_number = 11



            self.column_index = ['Time', 'Voltage', 'Ontime', 'Offtime', 'Cycle', 'Conductivity',
                                 'Cu', 'Ni', 'Zn', 'Na', 'Ca', 'K', 'Mg']


            self.column_index_finding = ['Voltage', 'Ontime', 'Offtime', 'Cycle', 'Conductivity',
                                         'Cu', 'Ni', 'Zn', 'Na', 'Ca', 'K', 'Mg']


            self.metal_line = ['368.972', '406.410', '214.547', '232.704','328.079']
            self.metal_name = {'368.972': 'Pb-368nm', '406.410': 'Pb-406nm', '214.547': 'Zn-214nm','232.704':'Ni-232nm','328.079':'Cu-327nm'}
            self.__metal_background = {
                '368.972': ['367.942', '369.659'],
                '406.410': ['405.240', '407.245'],
                '214.547': ['212.501', '216.777'],
                '232.704': ['230.857', '234.180'],
                '328.079': ['326.669', '328.784'],
            }

        # Extract Wavelength
        def Wavelength_extraction(self):
            self.wavelength = []

            file_list = [f for f in os.listdir(self.path) if f.endswith('.txt')]
            if not file_list:
                print("No txt files found!")
                return []

            file_name = file_list[0]
            f = open(self.path + '/' + file_name , 'r')
            content = f.readlines()
            f.close()
            for i in range(self.pixel_number):
                self.wavelength += [str(content[i].split('\t')[0])]
            return self.wavelength


        def Data_transfer(self):

            file_names = sorted([f for f in os.listdir(self.path) if f.endswith('.txt')])

            data_condition = []
            data_origin = []


            if len(file_names) % self.sampling_number != 0:
                print(f"Warning: file count ({len(file_names)}) is not divisible by {self.sampling_number}; the final group may be incomplete.")


            for group_idx in range(0, len(file_names), self.sampling_number):

                current_group_files = file_names[group_idx : group_idx + self.sampling_number]


                if len(current_group_files) < self.sampling_number:
                    break


                bg_file = current_group_files[0]
                try:
                    with open(self.path + '/' + bg_file, 'r') as f:
                        content = f.readlines()

                    background_intensity = []
                    for j in range(self.pixel_number):
                        background_intensity.append(float(content[j].split('\t')[1]))
                except Exception as e:
                    print(f'Error reading background file {bg_file}: {e}')
                    continue



                data_files = current_group_files[1:]

                for file_name in data_files:
                    try:


                        fname_clean = file_name.replace('.txt', '')
                        parts = fname_clean.split('_')


                        # parts[0]: Timestamp (Time)
                        # parts[1]: Voltage
                        # parts[2]: Ontime
                        # parts[3]: Offtime
                        # parts[4]: Cycle
                        # parts[5]: Conductivity

                        # parts[7]: Na-0
                        # parts[8]: Ca-375
                        # parts[9]: K-0
                        # parts[10]: Mg-0

                        time_val = parts[0]
                        voltage = float(parts[1])
                        ontime = float(parts[2])
                        offtime = float(parts[3])
                        cycle = float(parts[4])
                        conductivity = float(parts[5])


                        conc_val = float(parts[6].split('-')[1]) # Conc -> Cu, Ni, Zn
                        na_val = float(parts[7].split('-')[1])
                        ca_val = float(parts[8].split('-')[1])
                        k_val = float(parts[9].split('-')[1])
                        mg_val = float(parts[10].split('-')[1])


                        # ['Time', 'Voltage', 'Ontime', 'Offtime', 'Cycle', 'Conductivity', 'Cu', 'Ni', 'Zn', 'Na', 'Ca', 'K', 'Mg']
                        condition_row = [
                            time_val, voltage, ontime, offtime, cycle, conductivity,
                            conc_val, conc_val, conc_val,
                            na_val, ca_val, k_val, mg_val
                        ]


                        with open(self.path + '/' + file_name, 'r') as f:
                            content = f.readlines()

                        intensity = []
                        for j in range(self.pixel_number):
                            raw_val = float(content[j].split('\t')[1])

                            intensity.append(raw_val - background_intensity[j])


                        data_condition.append(condition_row)
                        data_origin.append(intensity)

                    except Exception as e:
                        print(f'Error processing file {file_name}: {e}')



            condition = pd.DataFrame(data_condition, columns=self.column_index)


            condition['Total_on_time'] = condition['Ontime'] * condition['Cycle']

            data = pd.DataFrame(data_origin, columns=self.Wavelength_extraction())


            data = self.metal_wo_bg_all(data)


            self.data_concat = pd.concat([condition, data], axis=1)

            while True:
                action = input('Save as CSV. [y/n] ')
                if action == 'y':
                    condition.to_csv(self.output_path + '/' + 'Conditions.csv')
                    data.to_csv(self.output_path + '/' + 'Data.csv')
                    self.data_concat.to_csv(self.output_path + '/' + 'Concat.csv')
                    break
                elif action == 'n':
                    break
                else:
                    print('Wrong command. Please try again.')
            return self.data_concat


        def Data_read(self):
            file_name = os.listdir(self.path)
            if 'Concat.csv' in file_name:
                self.data_concat = pd.read_csv(self.path + '/Concat.csv', index_col=0)


                cols = self.data_concat.columns

                self.wavelength = [c for c in cols if c[0].isdigit() and 'Slope' not in c]

                print('Concat.csv file exist.')
                try:
                    self.data_mean = pd.read_csv(self.path + '/Mean.csv', index_col=0)
                    self.data_std = pd.read_csv(self.path + '/STD.csv', index_col=0)
                    self.data_rsd = pd.read_csv(self.path + '/RSD.csv', index_col=0)
                    print('Mean/ STD/ RSD.csv file exist.')
                except:
                    print('Mean, STD, and RSD files do not exist.\nTry to use All_conditions_analysis.')
            else:
                self.Data_transfer()
                print('Mean, STD, and RSD files do not exist.\nTry to use All_conditions_analysis.')
            return self.data_concat, self.wavelength

        def metal_wo_bg_all(self, dataframe):
            for i in self.metal_line:
                dataframe[self.metal_name[i] + '_slope'] = (dataframe[self.__metal_background[i][0]] - dataframe[self.__metal_background[i][1]]) / (float(self.__metal_background[i][0]) - float(self.__metal_background[i][1]))
                dataframe[self.metal_name[i] + '_intercept'] = dataframe[self.__metal_background[i][1]] - (dataframe[self.metal_name[i] + '_slope'] * float(self.__metal_background[i][1]))
                dataframe[self.metal_name[i] + '_background'] = dataframe[self.metal_name[i] + '_slope'] * float(i) +  dataframe[self.metal_name[i] + '_intercept']
                dataframe[self.metal_name[i] + '_predict'] = dataframe[i] - dataframe[self.metal_name[i] + '_background']
            return dataframe

        def All_conditions_analysis(self):
            data = []
            for i in self.column_index_finding:
                data += [sorted(self.data_concat[i].unique())]
            self.combinations = list(itertools.product(*data))
            mean1 = []; std1 = []; rsd1 = []

            spec_cols = self.Wavelength_extraction()

            for i in range(len(self.combinations)):
                spectrum = self.Condition_finding(self.combinations[i])
                if spectrum.empty:
                    pass
                else:
                    mean = np.array(spectrum.mean())
                    std  = np.array(spectrum.std())
                    rsd  = std / mean * 100

                    mean = np.concatenate((np.array(self.combinations[i]), mean))
                    std  = np.concatenate((np.array(self.combinations[i]), std))
                    rsd  = np.concatenate((np.array(self.combinations[i]), rsd))

                    mean1.append(mean)
                    std1.append(std)
                    rsd1.append(rsd)
                    print(len(mean))

            self.data_mean = pd.DataFrame(mean1, columns = self.column_index_finding + spec_cols)
            self.data_std  = pd.DataFrame(std1, columns = self.column_index_finding + spec_cols)
            self.data_rsd  = pd.DataFrame(rsd1, columns = self.column_index_finding + spec_cols)

            self.data_mean = self.metal_wo_bg_all(self.data_mean)


            self.create_mean_3_csv()

            while True:
                action = input('Save as CSV. [y/n] ')
                if action == 'y':
                    self.data_mean.to_csv(self.output_path + '/' + 'Mean.csv')
                    self.data_std.to_csv(self.output_path + '/' + 'STD.csv')
                    self.data_rsd.to_csv(self.output_path + '/' + 'RSD.csv')
                    break
                elif action == 'n':
                    break
                else:
                    print('Wrong command. Please try again.')

        def create_mean_3_csv(self):
            """
            Average consecutive groups of three observations, omitting incomplete groups.
            Save the derived means to Mean_3.csv in the experiment output directory.
            """
            print("Processing Mean_3 calculation...")
            mean3_list = []
            spec_cols = self.Wavelength_extraction()


            for i in range(len(self.combinations)):
                spectrum = self.Condition_finding(self.combinations[i])
                if spectrum.empty:
                    continue


                n_samples = len(spectrum)


                n_groups = n_samples // 3


                for j in range(n_groups):
                    start_idx = j * 3
                    end_idx = start_idx + 3


                    sub_spectrum = spectrum.iloc[start_idx:end_idx]


                    mean_val = np.array(sub_spectrum.mean())



                    row_data = np.concatenate((np.array(self.combinations[i]), mean_val))
                    mean3_list.append(row_data)


            self.data_mean_3 = pd.DataFrame(mean3_list, columns=self.column_index_finding + spec_cols)


            self.data_mean_3 = self.metal_wo_bg_all(self.data_mean_3)


            save_path = self.output_path + '/' + 'Mean_3.csv'
            self.data_mean_3.to_csv(save_path)
            print(f"Mean_3.csv saved to {save_path}")


        def Condition_finding(self, condition_array):
            data = self.data_concat
            wavelength = self.Wavelength_extraction()
            for i in range(len(condition_array)):
                data = data[data[self.column_index_finding[i]] == condition_array[i]]
            if data.empty:
                spectrum = pd.DataFrame()
            else:
                spectrum = data.loc[data.index , wavelength]
            return spectrum

    #%%
    a = data_reader()
    a.Data_read()
    a.All_conditions_analysis()

    mean = a.data_mean
    std = a.data_std
    concat = a.data_concat
    rsd = a.data_rsd


if __name__ == "__main__":
    run()
