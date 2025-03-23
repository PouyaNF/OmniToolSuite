# tts_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gtts import gTTS
from pydub import AudioSegment
import os
from pydub.utils import which
import threading  # For running conversion in a separate thread
import time       # To simulate processing (optional, for smooth updates)


AudioSegment.converter = which("ffmpeg")  # Ensure pydub finds ffmpeg


class TextToSpeechConverterTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=10)
        self.build_widgets()

    def build_widgets(self):
        self.instruction_label = ttk.Label(
            self.frame, 
            text="Enter text (each line will be converted to a separate audio file):"
        )
        self.instruction_label.grid(row=0, column=0, sticky="w")

        self.text_box = tk.Text(self.frame, width=70, height=15)
        self.text_box.grid(row=1, column=0, pady=5, sticky="nsew")
        self.frame.rowconfigure(1, weight=1)

        self.format_label = ttk.Label(self.frame, text="Select output format:")
        self.format_label.grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.format_var = tk.StringVar(value="wav")
        self.format_options = ["wav", "m4a", "mp3"]
        self.format_menu = ttk.Combobox(
            self.frame, textvariable=self.format_var, values=self.format_options, state="readonly"
        )
        self.format_menu.grid(row=3, column=0, sticky="w", pady=5)
        self.output_folder_label = ttk.Label(self.frame, text="Output Folder:")
        self.output_folder_label.grid(row=4, column=0, sticky="w")

        self.output_folder_var = tk.StringVar()
        self.output_folder_entry = ttk.Entry(self.frame, textvariable=self.output_folder_var, width=20)
        self.output_folder_entry.grid(row=5, column=0, sticky="we", pady=5)
        self.select_folder_button = ttk.Button(self.frame, text="Browse", command=self.select_output_folder)
        self.select_folder_button.grid(row=5, column=1, padx=5)

        # the Progress Bar
        self.progress = ttk.Progressbar(self.frame, length=300, mode="determinate")
        self.progress.grid(row=6, column=0, columnspan=2,sticky="w", pady=10)

        self.convert_button = ttk.Button(self.frame, text="Convert", command=self.convert_text)
        self.convert_button.grid(row=7, column=0, pady=10)




    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder_var.set(folder)

    def convert_text(self):
        threading.Thread(target=self.convert_text_thread, daemon=True).start()



    def convert_text_thread(self):
        text = self.text_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return

        output_format = self.format_var.get().lower()
        lines = text.splitlines()
        output_dir = self.output_folder_var.get().strip()
        
        if not output_dir:
            messagebox.showwarning("Output Folder", "Please select an output folder.")
            return
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        format_params = {
            "wav": {"format": "wav", "parameters": []},
            "m4a": {"format": "mp4", "parameters": ["-acodec", "aac", "-b:a", "128k"]},
            "mp3": {"format": "mp3", "parameters": ["-acodec", "libmp3lame", "-b:a", "128k"]}
        }

        total_lines = len(lines)
        self.progress["maximum"] = total_lines  # Set max value for progress bar

        for i, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue

            words = line.split()
            if not words:
                continue

            first_word = words[0]
            index_str = f"{i:02d}"
            base_filename = f"{index_str}-{first_word}"
            temp_mp3 = os.path.join(output_dir, base_filename + ".mp3")
            final_filename = os.path.join(output_dir, f"{base_filename}.{output_format}")

            try:
                tts = gTTS(text=line, lang='de')
                tts.save(temp_mp3)
            except Exception as e:
                messagebox.showerror("Conversion Error", f"Error converting line {i}:\n{e}")
                continue

            try:
                audio = AudioSegment.from_mp3(temp_mp3)
                audio = audio.set_channels(2).set_frame_rate(44100)
                fmt_info = format_params[output_format]
                audio.export(final_filename, format=fmt_info["format"], parameters=fmt_info["parameters"])
            except Exception as e:
                messagebox.showerror("Conversion Error", f"Error converting file for line {i}:\n{e}")
                continue
            finally:
                if os.path.exists(temp_mp3):
                    os.remove(temp_mp3)

            # **Update Progress Bar**
            self.progress["value"] = i
            self.frame.update_idletasks()  # Refresh UI

            time.sleep(0.1)  # Optional: Smooth progress effect

        self.progress["value"] = 0  # Reset progress bar
        messagebox.showinfo("Success", "Conversion completed successfully.")


    '''
    def convert_text(self):
        text = self.text_box.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Input Error", "Please enter some text.")
            return

        output_format = self.format_var.get().lower()
        lines = text.splitlines()
        output_dir = self.output_folder_var.get().strip()
        if not output_dir:
            messagebox.showwarning("Output Folder", "Please select an output folder.")
            return
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        format_params = {
            "wav": {"format": "wav", "parameters": []},
            "m4a": {"format": "mp4", "parameters": ["-acodec", "aac", "-b:a", "128k"]},
            "mp3": {"format": "mp3", "parameters": ["-acodec", "libmp3lame", "-b:a", "128k"]}
        }

        if output_format not in format_params:
            output_format = "wav"

        for i, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue
            words = line.split()
            if not words:
                continue
            first_word = words[0]
            index_str = f"{i:02d}"
            base_filename = f"{index_str}-{first_word}"
            temp_mp3 = os.path.join(output_dir, base_filename + ".mp3")
            final_filename = os.path.join(output_dir, f"{base_filename}.{output_format}")

            try:
                tts = gTTS(text=line, lang='de')
                tts.save(temp_mp3)
            except Exception as e:
                messagebox.showerror("Conversion Error", f"Error converting line {i}:\n{e}")
                continue

            try:
                audio = AudioSegment.from_mp3(temp_mp3)
                audio = audio.set_channels(2).set_frame_rate(44100)
                fmt_info = format_params[output_format]
                audio.export(final_filename, format=fmt_info["format"], parameters=fmt_info["parameters"])
            except Exception as e:
                messagebox.showerror("Conversion Error", f"Error converting file for line {i}:\n{e}")
                continue
            finally:
                if os.path.exists(temp_mp3):
                    os.remove(temp_mp3)

        messagebox.showinfo("Success", "Conversion completed successfully.")
'''