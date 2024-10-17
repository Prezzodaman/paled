import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import tkinter.font

def get_md_colours(colour_md):
	red = (colour_md & 0xf) >> 1
	green = ((colour_md & 0xf0) >> 1) >> 4
	blue = ((colour_md & 0xf00) >> 1) >> 8
	return red, green, blue

def set_sliders(colour_md):
	red, green, blue = get_md_colours(colour_md)
	sliders_variables[0].set(red)
	sliders_variables[1].set(green)
	sliders_variables[2].set(blue)

def set_colour_label_bg(index, colour_md):
	red, green, blue = get_md_colours(colour_md)
	conversion = 255 / 7
	red_bg = int(red * conversion) << 16
	green_bg = int(green * conversion) << 8
	blue_bg = int(blue * conversion)

	colour_bg = "#" + hex(red_bg | green_bg | blue_bg)[2:].rjust(6, "0")
	colour_labels[index].configure(bg=colour_bg)

def colour_label_click(colour):
	for a in range(0, palette_length):
		if a == colour:
			colour_labels[a].configure(relief="sunken")
		else:
			colour_labels[a].configure(relief="raised")
	colour_index_selected.set(colour)
	set_sliders(palette_lines[palette_line_current.get()][colour])

def slider_change(rgb):
	red = sliders_variables[0].get()  # mega drive uses BGR instead of the usual RGB
	green = sliders_variables[1].get()
	blue = sliders_variables[2].get()

	red_md = (red << 1)
	green_md = (green << 1) << 4
	blue_md = (blue << 1) << 8
	colour_md = red_md | green_md | blue_md

	set_colour_label_bg(colour_index_selected.get(), colour_md)
	palette_lines[palette_line_current.get()][colour_index_selected.get()] = colour_md

def palette_line_change(line):
	for a in range(0, palette_length):
		set_colour_label_bg(a, palette_lines[line][a])
	set_sliders(palette_lines[line][colour_index_selected.get()])

def palette_open_line_dialog(palette, lines, even_length):
	def import_palette():
		dialog_win.grab_release()
		dialog_win.destroy()
		palette_open(palette, dialog_win_line.get())
	dialog_win = tk.Toplevel(kint)
	dialog_win_frame = tk.Frame(dialog_win)
	dialog_win_frame.pack(padx=(16, 16), pady=(8, 8))
	dialog_win.attributes("-topmost", True)
	dialog_win.attributes("-topmost", False)
	dialog_win.resizable(width=False, height=False)
	dialog_win_line = tk.IntVar(dialog_win, -1)
	if not even_length:
		lines += 1
	tk.Label(dialog_win_frame, text=f"Palette file contains {lines} lines, import which one into current line?", font=tk.font.Font(size=12, weight="bold")).grid(row=0, column=0, columnspan=lines + 1, pady=(0, 8))
	tk.Radiobutton(dialog_win_frame, text="All lines", value=-1, variable=dialog_win_line).grid(row=1, column=0)
	for a in range(0, lines):
		if even_length:
			incomplete = ""
		else:
			if a == lines - 1:
				incomplete = " (incomplete)"
			else:
				incomplete = ""
		tk.Radiobutton(dialog_win_frame, text=f"Line {a + 1}{incomplete}", value=a, variable=dialog_win_line).grid(row=1, column=a + 1)
	tk.Button(dialog_win_frame, text="Import", command=import_palette).grid(row=2, column=0, columnspan=5, pady=(8, 0))

	dialog_win.grab_set()
	dialog_win.mainloop()

def palette_open(palette, line):
	if line == -1:  # all lines
		for index_no in range(0, len(palette), 2):
			index_temp = (index_no // 2) % 16
			line_temp = (index_no // 2) // 16
			byte = (palette[index_no] << 8) | palette[index_no + 1]
			palette_lines[line_temp][index_temp] = byte
		palette_line_change(palette_line_current.get())
	else:  # one specified line
		for index_no in range(line * 32, (line * 32) + 32, 2):
			if index_no < len(palette):
				index_temp = (index_no // 2) % 16
				line_temp = palette_line_current.get()
				byte = (palette[index_no] << 8) | palette[index_no + 1]
				palette_lines[line_temp][index_temp] = byte
		palette_line_change(palette_line_current.get())

def palette_open_dialog():
	file_open = tk.filedialog.askopenfile(title="Select a file:", filetypes=[("Binary files", "*.bin")], mode="rb")
	if file_open:
		palette_file = file_open.read()
		if len(palette_file) > 128:
			tk.messagebox.showwarning("Error", "Palette spans more than 4 lines!")
		else:
			if len(palette_file) % 32 != 0:
				tk.messagebox.showwarning("Warning", "Palette length isn't a multiple of 16!")
			if len(palette_file) > 32:  # more than one line?
				palette_open_line_dialog(palette_file, len(palette_file) // 32, len(palette_file) % 32 == 0)
			else:
				palette_open(palette_file, -1)
		file_open.close()

def palette_save_clear_dialog(clear):
	def do_thing(all_lines):
		dialog_win.grab_release()
		dialog_win.destroy()
		if clear:
			if all_lines:
				for line_no in range(0, palette_line_amount):
					for index_no in range(0, palette_length):
						palette_lines[line_no][index_no] = 0
			else:
				for index_no in range(0, palette_length):
					palette_lines[palette_line_current.get()][index_no] = 0
			palette_line_change(palette_line_current.get())  # doesn't exactly matter, since they'll all be black :P
		else:
			yes_no_cancel = True
			if all_lines:
				palette_blank = [False] * palette_line_amount
				for line_no, line in enumerate(palette_lines):
					blank_entries = 0
					for index in line:
						if index == 0:
							blank_entries += 1
					if blank_entries == palette_length:
						palette_blank[line_no] = True
				if all(palette_blank):
					yes_no_cancel = tkinter.messagebox.askyesnocancel(message="Entire palette is blank! Continue?")
				elif palette_blank[1] and palette_blank[2] and palette_blank[3]:  # I'm sure there's a better way of doing this, but I can't think right now!
					yes_no_cancel = tkinter.messagebox.askyesnocancel(message="Palette lines 2, 3 and 4 appear blank. Include them?")
				elif palette_blank[2] and palette_blank[3]:
					yes_no_cancel = tkinter.messagebox.askyesnocancel(message="Palette lines 3 and 4 appear blank. Include them?")
				elif palette_blank[3]:
					yes_no_cancel = tkinter.messagebox.askyesnocancel(message="Palette line 4 appears blank. Include them?")

			if yes_no_cancel != None:
				palette_file_pre = []
				if all_lines:
					for line_no, line in enumerate(palette_lines):
						if not palette_blank[line_no]:
							for index in line:
								palette_file_pre.append(index)
				else:
					for index_no in range(0, palette_length):
						byte = palette_lines[palette_line_current.get()][index_no]
						palette_file_pre.append(byte)

				concurrent_blacks = 0
				concurrent_blacks_start = 0
				index_last = 0
				for index_no, index in enumerate(palette_file_pre):
					if index != index_last:
						concurrent_blacks_start = index_no
					if index == index_last and index == 0:
						concurrent_blacks += 1
					else:
						concurrent_blacks = 0
					index_last = index
				if concurrent_blacks > 0:
					yes_no_cancel_incomplete = tkinter.messagebox.askyesnocancel(message="Palette appears incomplete, save all entries?")
				else:
					yes_no_cancel_incomplete = True

				if yes_no_cancel_incomplete != None:
					file_save = tk.filedialog.asksaveasfile(title="Select a file:", filetypes=[("Binary files", "*.bin")], mode="wb")
					if file_save:
						if yes_no_cancel_incomplete == False:
							palette_file_pre = palette_file_pre[:concurrent_blacks_start]
						palette_file = bytearray()
						for index in palette_file_pre:
							palette_file.append(index >> 8)
							palette_file.append(index & 0xff)
						file_save.write(palette_file)
						file_save.close()
	def do_current_palette():
		do_thing(False)
	def do_all_palettes():
		do_thing(True)
	dialog_win = tk.Toplevel(kint)
	dialog_win_frame = tk.Frame(dialog_win)
	dialog_win_frame.pack(padx=(16, 16), pady=(8, 8))
	dialog_win.attributes("-topmost", True)
	dialog_win.resizable(width=False, height=False)
	dialog_win_all_lines = tk.BooleanVar(dialog_win, False)
	if clear:
		action="Clear"
	else:
		action="Save"
	tk.Label(dialog_win_frame, text=f"{action} current line or all lines?", font=tk.font.Font(size=12, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 8))
	tk.Button(dialog_win_frame, text="Current line", command=do_current_palette).grid(row=1, column=0)
	tk.Button(dialog_win_frame, text="All lines", command=do_all_palettes).grid(row=1, column=1)
	dialog_win.grab_set()
	dialog_win.mainloop()

def palette_save_dialog():
	palette_save_clear_dialog(False)
def palette_clear_dialog():
	palette_save_clear_dialog(True)

def about_dialog():
	def close():
		about_win.grab_release()
		about_win.destroy()
	about_win = tk.Toplevel(kint)
	about_win.resizable(width=False, height=False)
	about_frame = tk.Frame(about_win)
	about_frame.pack(padx=(16, 16), pady=(8, 8))
	tk.Label(about_frame, text="Paled", font=tk.font.Font(size=24)).pack()
	tk.Label(about_frame, text="v1.0, by Presley Peters (Prezzo), 2024", font=tk.font.Font(size=12)).pack()
	tk.Label(about_frame, text="4-line palette editor for the Sega Mega Drive").pack()
	tk.Button(about_frame, text="ok", command=close).pack(pady=(8, 0))
	about_win.grab_set()
	about_win.mainloop()

kint = tk.Tk()
kint.resizable(width=False, height=False)
kint.title("Paled")

palette_length = 16
palette_line_amount = 4
palette_lines = []
palette_line_temp = [0] * palette_length
for a in range(0, palette_line_amount):
	palette_lines.append(palette_line_temp.copy())

colours_frame = tk.LabelFrame(text="Entries")
colours_frame.grid(row=0, column=0, sticky="ns")

colour_labels = []
for a in range(0, palette_length):
	temp_label = tk.Label(colours_frame, width=4, height=2, borderwidth=2, relief="raised", bg="#000", text="", cursor="hand2")  # width and height is in characters, not pixels...
	temp_label.grid(row=0, column=a, padx=(2, 2), pady=(2, 2))  # frames have their own grid space!
	temp_label.bind("<Button-1>", lambda e, a=a: colour_label_click(a))
	colour_labels.append(temp_label)
colour_labels[0].configure(relief="sunken")
colour_index_selected = tk.IntVar()  # 0 - 15

sliders_frame = tk.LabelFrame(text="Red, Green and Blue")
sliders_frame.grid(row=1, column=0)
sliders_variables = []
for a in range(0, 3):
	temp_variable = tk.IntVar()
	sliders_variables.append(temp_variable)
	temp_slider = tk.Scale(sliders_frame, variable=temp_variable, from_=0, to=7, orient="horizontal")
	temp_slider.bind("<ButtonRelease-1>", lambda e, a=a: slider_change(a))
	temp_slider.grid(row=0, column=a)

palette_line_current = tk.IntVar()
palette_lines_frame = tk.LabelFrame(text="Palette Line")
palette_lines_frame.grid(row=0, column=1, sticky="ns")
for a in range(0, palette_line_amount):
	temp_button = tk.Radiobutton(palette_lines_frame, text=str(a + 1), value=a, variable=palette_line_current)
	temp_button.bind("<Button-1>", lambda e, a=a: palette_line_change(a))
	temp_button.grid(row=a // 2, column=a % 2)

file_op_frame = tk.Frame()
file_op_frame.grid(row=1, column=1)

import_icon = tk.PhotoImage(file="import.png")
save_icon = tk.PhotoImage(file="save.png")
rubbish_icon = tk.PhotoImage(file="rubbish.png")
help_icon = tk.PhotoImage(file="help.png")
tk.Button(file_op_frame, image=import_icon, command=palette_open_dialog).grid(row=0, column=0)
tk.Button(file_op_frame, image=save_icon, command=palette_save_dialog).grid(row=0, column=1)
tk.Button(file_op_frame, image=rubbish_icon, command=palette_clear_dialog).grid(row=1, column=0)
tk.Button(file_op_frame, image=help_icon, command=about_dialog).grid(row=1, column=1)

tk.mainloop()