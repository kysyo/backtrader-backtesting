import tkinter as tk
from tkinter import filedialog

'''
ui 창을 띄워 파일을 업로드 하거나 파일을 생성
'''


def select_csv_file():
    root = tk.Tk()
    root.withdraw()

    root.filename = filedialog.askopenfilename(initialdir='/',
                                               title='Select CSV file',
                                               filetypes=[("csv file", ".csv")], )
    file_name = root.filename
    root.destroy()
    return file_name


def save_csv_file(df):
    file_name = filedialog.asksaveasfile(initialdir='/',
                                         title='Save backtesting result CSV file',
                                         mode='w',
                                         defaultextension=".csv",
                                         filetypes=[("csv file", ".csv")], )
    df.to_csv(file_name, index=False, encoding='utf-8-sig')