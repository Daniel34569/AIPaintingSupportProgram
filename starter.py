import tkinter as tk
from tkinter import ttk, filedialog
import os
import subprocess

def browse_folder(input_var):
    folder = filedialog.askdirectory()
    input_var.set(folder)

def browse_image(input_var):
    image_path = filedialog.askopenfilename()
    input_var.set(image_path)

def process_resize():
    folder = folder_var.get()
    shrink_ratio = shrink_ratio_var.get()
    resize_to_px = resize_to_px_var.get()
    seperate_vertical = seperate_vertical_var.get()
    result_type = result_type_var.get()

    command = f"python resave.py --input_dir \"{folder}\" --shrink_ratio {shrink_ratio} --resize_to_px {resize_to_px} --seperate_vertical {seperate_vertical} --result_type {result_type}"
    print(command)
    subprocess.run(command, shell=True, check=True)

def process_watermark():
    folder = folder_var.get()
    opacity = opacity_var.get()
    ratio = ratio_var.get()
    position_x = position_x_var.get()
    position_y = position_y_var.get()
    watermark_image = watermark_image_var.get()
    result_folder = result_folder_var.get()

    command = f"python watermark.py --folder \"{folder}\" --opacity {opacity} --ratio {ratio} --position {position_x} {position_y} --watermark_image \"{watermark_image}\" --result_folder \"{result_folder}\""
    print(command)
    subprocess.run(command, shell=True, check=True)

    
def process_editor():
    folder = folder_var.get()
    command = f"python editor.py --input_dir \"{folder}\""
    print(command)
    subprocess.run(command, shell=True, check=True)
    
def process_mosaic():
    folder = folder_var.get()
    result_folder = result_folder_var.get()
    select_roi_shrink_ratio = select_roi_shrink_ratio_var.get()
    command = f"python mosaic.py --input_dir \"{folder}\" --result_folder \"{result_folder}\" --select_roi_shrink_ratio {select_roi_shrink_ratio}"
    print(command)
    subprocess.run(command, shell=True, check=True)

def process_text_transform():
    command = f"python text_transform.py"
    print(command)
    subprocess.run(command, shell=True, check=True)

def process_lora_xyplot():
    command = f"python lora_xyplot_generator.py"
    print(command)
    subprocess.run(command, shell=True, check=True)

def initialize_watermark_tab(tab):
    current_row = 1

    tk.Label(tab, text="Opacity:").grid(row=current_row, column=0, sticky="w")
    tk.Entry(tab, textvariable=opacity_var).grid(row=current_row, column=1)

    current_row += 1

    tk.Label(tab, text="Ratio:").grid(row=current_row, column=0, sticky="w")
    tk.Entry(tab, textvariable=ratio_var).grid(row=current_row, column=1)

    current_row += 1

    tk.Label(tab, text="Position:").grid(row=current_row, column=0, sticky="w")
    tk.Entry(tab, textvariable=position_x_var).grid(row=current_row, column=1)
    tk.Entry(tab, textvariable=position_y_var).grid(row=current_row, column=2)

    current_row += 1

    tk.Label(tab, text="Watermark Image:").grid(row=current_row, column=0, sticky="w")
    tk.Entry(tab, textvariable=watermark_image_var).grid(row=current_row, column=1)
    tk.Button(tab, text="Browse", command=lambda: browse_image(watermark_image_var)).grid(row=current_row, column=2)

    current_row += 1

    tk.Label(tab, text="Result Folder:").grid(row=current_row, column=0, sticky="w")
    tk.Entry(tab, textvariable=result_folder_var).grid(row=current_row, column=1)
    tk.Button(tab, text="Browse", command=lambda: browse_folder(result_folder_var)).grid(row=current_row, column=2)

    current_row += 1

    tk.Button(tab, text="Process", command=process_watermark).grid(row=current_row, columnspan=2)
    
def initialize_editor_tab(tab):
    current_row = 1

    tk.Button(tab, text="Process", command=process_editor).grid(row=current_row, columnspan=2)
    
def initialize_mosaic_tab(tab):
    current_row = 1

    tk.Label(tab, text="Result Folder:").grid(row=current_row, column=0, sticky="w")
    tk.Entry(tab, textvariable=result_folder_var).grid(row=current_row, column=1)
    tk.Button(tab, text="Browse", command=lambda: browse_folder(result_folder_var)).grid(row=current_row, column=2)

    current_row += 1

    tk.Label(tab, text="Select Roi Shrink Ratio:").grid(row=current_row, column=0, sticky="w")
    tk.Entry(tab, textvariable=select_roi_shrink_ratio_var).grid(row=current_row, column=1)

    current_row += 1

    tk.Button(tab, text="Process", command=process_mosaic).grid(row=current_row, columnspan=2)
    
def initialize_text_transform(tab):
    current_row = 1

    tk.Label(tab, text="Doesn't Need Any Input for This Mode!!").grid(row=current_row, column=0, sticky="w")

    current_row += 1

    tk.Button(tab, text="Process", command=process_text_transform).grid(row=current_row, columnspan=2)
    
def initialize_lora_xyplot(tab):
    current_row = 1

    tk.Label(tab, text="Doesn't Need Any Input for This Mode!!").grid(row=current_row, column=0, sticky="w")

    current_row += 1

    tk.Button(tab, text="Process", command=process_lora_xyplot).grid(row=current_row, columnspan=2)



app = tk.Tk()
app.title("Image Processing")

folder_var = tk.StringVar()
# Resize tab Var
shrink_ratio_var = tk.DoubleVar(value=1.0)
resize_to_px_var = tk.IntVar(value=-1)
seperate_vertical_var = tk.IntVar(value=1)
result_type_var = tk.StringVar(value="png")

# Watermark tab Var
opacity_var = tk.DoubleVar(value=0.5)
ratio_var = tk.DoubleVar(value=0.1)
position_x_var = tk.DoubleVar(value=0.8)
position_y_var = tk.DoubleVar(value=0.8)
watermark_image_var = tk.StringVar()
result_folder_var = tk.StringVar()
select_roi_shrink_ratio_var = tk.DoubleVar(value=-1)

#is_enable_var = tk.BooleanVar(value=True)



# Tab control
tab_control = ttk.Notebook(app)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab4 = ttk.Frame(tab_control)
tab5 = ttk.Frame(tab_control)
tab6 = ttk.Frame(tab_control)
tab_control.add(tab1, text="Resize")
tab_control.add(tab2, text="Watermark")
tab_control.add(tab3, text="Editor")
tab_control.add(tab4, text="Mosaic")
tab_control.add(tab5, text="Text Transform")
tab_control.add(tab6, text="Lora XYPlot")
tab_control.grid(row=1, columnspan=6)


# Resize tab
current_row = 0

tk.Label(app, text="Folder:").grid(row=current_row, column=0, sticky="w")
tk.Entry(app, textvariable=folder_var).grid(row=current_row, column=1)
tk.Button(app, text="Select Folder", command=lambda: browse_folder(folder_var)).grid(row=current_row, column=2)

current_row = 1

tk.Label(tab1, text="Shrink Ratio:").grid(row=current_row, column=0, sticky="w")
tk.Entry(tab1, textvariable=shrink_ratio_var).grid(row=current_row, column=1)

current_row += 1

tk.Label(tab1, text="Resize To px:").grid(row=current_row, column=0, sticky="w")
tk.Entry(tab1, textvariable=resize_to_px_var).grid(row=current_row, column=1)

current_row += 1

tk.Label(tab1, text="Seperate Vertical:").grid(row=current_row, column=0, sticky="w")
tk.Entry(tab1, textvariable=seperate_vertical_var).grid(row=current_row, column=1)

current_row += 1

tk.Label(tab1, text="Result Type:").grid(row=current_row, column=0, sticky="w")
tk.Entry(tab1, textvariable=result_type_var).grid(row=current_row, column=1)

current_row += 1

tk.Button(tab1, text="Process", command=process_resize).grid(row=current_row, columnspan=2)

initialize_watermark_tab(tab2)

initialize_editor_tab(tab3)

initialize_mosaic_tab(tab4)

initialize_text_transform(tab5)

initialize_lora_xyplot(tab6)

app.mainloop()
