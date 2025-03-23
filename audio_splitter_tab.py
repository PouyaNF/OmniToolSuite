import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pydub import AudioSegment, silence

class AudioSplitterTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=10)
        self.build_widgets()

    def build_widgets(self):
        # Input File
        ttk.Label(self.frame, text="Select Input WAV File:").grid(row=0, column=0, padx=5, pady=5)
        self.input_entry = ttk.Entry(self.frame, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        # Output Directory
        ttk.Label(self.frame, text="Select Output Directory:").grid(row=1, column=0, padx=5, pady=5)
        self.output_entry = ttk.Entry(self.frame, width=50)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        # Minimum Silence Length
        ttk.Label(self.frame, text="Min Silence Length (ms):").grid(row=2, column=0, padx=5, pady=5)
        self.silence_length_slider = tk.Scale(self.frame, from_=0, to=1000, orient=tk.HORIZONTAL)
        self.silence_length_slider.set(550)
        self.silence_length_slider.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Extend Duration at Beginning
        ttk.Label(self.frame, text="Extend Duration at Beginning (ms):").grid(row=3, column=0, padx=5, pady=5)
        self.extend_duration_begin_slider = tk.Scale(self.frame, from_=0, to=400, orient=tk.HORIZONTAL)
        self.extend_duration_begin_slider.set(200)
        self.extend_duration_begin_slider.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Extend Duration at End
        ttk.Label(self.frame, text="Extend Duration at End (ms):").grid(row=4, column=0, padx=5, pady=5)
        self.extend_duration_end_slider = tk.Scale(self.frame, from_=0, to=800, orient=tk.HORIZONTAL)
        self.extend_duration_end_slider.set(400)
        self.extend_duration_end_slider.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Volume Adjustment
        ttk.Label(self.frame, text="Volume Adjustment (dB):").grid(row=5, column=0, padx=5, pady=5)
        self.volume_scale = tk.Scale(self.frame, from_=-30, to=30, orient=tk.HORIZONTAL)
        self.volume_scale.set(0)
        self.volume_scale.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.apply_gain_var = tk.BooleanVar(value=True)
        self.apply_gain_check = ttk.Checkbutton(
            self.frame, text="Apply Volume Adjustment", variable=self.apply_gain_var
        )
        self.apply_gain_check.grid(row=5, column=2, padx=5, pady=5)

        # Silence Threshold
        ttk.Label(self.frame, text="Silence Threshold (dB):").grid(row=6, column=0, padx=5, pady=5)
        self.silence_thresh_slider = tk.Scale(self.frame, from_=-70, to=-30, orient=tk.HORIZONTAL)
        self.silence_thresh_slider.set(-50)
        self.silence_thresh_slider.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Reset and Start Processing buttons
        ttk.Button(self.frame, text="Reset to Default", command=self.reset_defaults).grid(row=7, column=1, padx=5, pady=10)
        ttk.Button(self.frame, text="Start Processing", command=self.start_processing).grid(row=8, column=1, padx=5, pady=10)

    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if file_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)

    def browse_output(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder_path)

    def reset_defaults(self):
        self.silence_length_slider.set(550)
        self.silence_thresh_slider.set(-50)
        self.extend_duration_begin_slider.set(200)
        self.extend_duration_end_slider.set(400)
        self.volume_scale.set(0)

    def process_audio(self, input_path, output_dir, min_silence_len,
                      extend_duration_begin, extend_duration_end,
                      volume_adjustment, silence_thresh):

        audio = AudioSegment.from_wav(input_path)
        silent_ranges = silence.detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
        speech_segments = []
        prev_end = 0

        for start, end in silent_ranges:
            if prev_end < start:
                # Extend backward without going below 0 and forward without exceeding the length
                seg_start = max(0, prev_end - extend_duration_begin)
                seg_end = min(len(audio), start + extend_duration_end)
                speech_segments.append(audio[seg_start:seg_end])
            prev_end = end

        if prev_end < len(audio):
            seg_start = max(0, prev_end - extend_duration_begin)
            seg_end = len(audio)  # Cannot extend beyond the end of the file
            speech_segments.append(audio[seg_start:seg_end])

        os.makedirs(output_dir, exist_ok=True)
        for i, segment in enumerate(speech_segments):
            if self.apply_gain_var.get():
                adjusted_segment = segment.apply_gain(volume_adjustment)
            else:
                adjusted_segment = segment

            segment_path = os.path.join(output_dir, f"segment_{i+1}.wav")
            adjusted_segment.export(segment_path, format="wav")

        messagebox.showinfo("Success", "Audio splitting complete!")

    def start_processing(self):
        input_path = self.input_entry.get()
        output_dir = self.output_entry.get()
        try:
            min_silence_len = int(self.silence_length_slider.get())
            extend_duration_begin = int(self.extend_duration_begin_slider.get())
            extend_duration_end = int(self.extend_duration_end_slider.get())
            silence_thresh = int(self.silence_thresh_slider.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for silence and extend duration.")
            return

        volume_adjustment = self.volume_scale.get()

        if not input_path or not output_dir:
            messagebox.showerror("Error", "Please select both input file and output directory.")
            return

        self.process_audio(input_path, output_dir, min_silence_len,
                           extend_duration_begin, extend_duration_end,
                           volume_adjustment, silence_thresh)
