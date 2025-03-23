import os
import threading
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import librosa
import noisereduce as nr
import soundfile as sf
from scipy.signal import butter, filtfilt

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

class AudioDenoiserTab:
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.winfo_toplevel()
        self.frame = ttk.Frame(parent, padding=10)
        self.processing = False
        self.create_widgets()

    def create_widgets(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.main_frame = ttk.Frame(self.frame, padding=20)
        self.main_frame.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.main_frame.columnconfigure(0, weight=1)

        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=0, column=0, sticky=tk.EW, pady=5)
        ttk.Label(input_frame, text="Input Directory:").grid(row=0, column=0, padx=5)
        self.input_dir = ttk.Entry(input_frame, width=60)
        self.input_dir.grid(row=0, column=1, padx=5, sticky=tk.EW)
        ttk.Button(input_frame, text="Browse", command=self.select_input_dir).grid(row=0, column=2, padx=5)
        input_frame.columnconfigure(1, weight=1)

        output_frame = ttk.Frame(self.main_frame)
        output_frame.grid(row=1, column=0, sticky=tk.EW, pady=5)
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, padx=5)
        self.output_dir = ttk.Entry(output_frame, width=60)
        self.output_dir.grid(row=0, column=1, padx=5, sticky=tk.EW)
        ttk.Button(output_frame, text="Browse", command=self.select_output_dir).grid(row=0, column=2, padx=5)
        output_frame.columnconfigure(1, weight=1)

        noise_frame = ttk.Frame(self.main_frame)
        noise_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(noise_frame, text="Noise Sample (ms):").grid(row=0, column=0, padx=5)
        self.noise_start = ttk.Entry(noise_frame, width=8)
        self.noise_start.grid(row=0, column=1, padx=5)
        ttk.Label(noise_frame, text="to").grid(row=0, column=2, padx=5)
        self.noise_end = ttk.Entry(noise_frame, width=8)
        self.noise_end.grid(row=0, column=3, padx=5)
        self.noise_start.insert(0, "0")
        self.noise_end.insert(0, "1000")

        quality_frame = ttk.Labelframe(self.main_frame, text="Quality Settings", padding=10)
        quality_frame.grid(row=3, column=0, sticky=tk.EW, pady=10)
        quality_frame.columnconfigure(1, weight=1)
        self.bit_depth_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(quality_frame, text="Preserve Original Bit Depth (16/32-bit)", variable=self.bit_depth_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        ttk.Label(quality_frame, text="Frequency Range (Hz):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        freq_frame = ttk.Frame(quality_frame)
        freq_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        self.low_cut = ttk.Entry(freq_frame, width=5)
        self.low_cut.pack(side=tk.LEFT, padx=2)
        self.low_cut.insert(0, "80")
        ttk.Label(freq_frame, text="-").pack(side=tk.LEFT)
        self.high_cut = ttk.Entry(freq_frame, width=5)
        self.high_cut.pack(side=tk.LEFT, padx=2)
        self.high_cut.insert(0, "16000")
        ttk.Label(freq_frame, text="Hz").pack(side=tk.LEFT)

        volume_frame = ttk.Frame(self.main_frame)
        volume_frame.grid(row=4, column=0, sticky=tk.EW, pady=5)
        ttk.Label(volume_frame, text="Volume Boost (dB):").grid(row=0, column=0, padx=5)
        self.volume_boost = ttk.Scale(volume_frame, from_=0, to=15, orient=tk.HORIZONTAL)
        self.volume_boost.set(3)
        self.volume_boost.grid(row=0, column=1, padx=5, sticky=tk.EW)
        self.vol_spin = ttk.Spinbox(volume_frame, from_=0, to=15, width=4)
        self.vol_spin.set(3)
        self.vol_spin.grid(row=0, column=2, padx=5)
        self.volume_boost.config(command=lambda v: self.vol_spin.set(round(float(v))))
        self.vol_spin.config(command=lambda: self.volume_boost.set(self.vol_spin.get()))
        volume_frame.columnconfigure(1, weight=1)

        adv_frame = ttk.Labelframe(self.main_frame, text="Advanced Parameters", padding=10)
        adv_frame.grid(row=5, column=0, sticky=tk.EW, pady=10)
        ttk.Label(adv_frame, text="Noise Reduction Strength (0.0 - 1.0):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.prop_decrease = ttk.Entry(adv_frame, width=8)
        self.prop_decrease.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.prop_decrease.insert(0, "1.0")
        ttk.Label(adv_frame, text="FFT Size (n_fft):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.n_fft = ttk.Entry(adv_frame, width=8)
        self.n_fft.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        self.n_fft.insert(0, "2048")
        ttk.Label(adv_frame, text="Window Length (win_length):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.win_length = ttk.Entry(adv_frame, width=8)
        self.win_length.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        self.win_length.insert(0, "2048")
        ttk.Label(adv_frame, text="Hop Length (hop_length):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.hop_length = ttk.Entry(adv_frame, width=8)
        self.hop_length.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        self.hop_length.insert(0, "512")
        ttk.Label(adv_frame, text="Butterworth Filter Order:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.filter_order = ttk.Entry(adv_frame, width=8)
        self.filter_order.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        self.filter_order.insert(0, "6")
        ttk.Button(adv_frame, text="Help / Guide", command=self.show_help).grid(row=0, column=2, rowspan=2, padx=10, pady=2)

        self.progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.grid(row=6, column=0, sticky=tk.EW, pady=10)

        log_frame = ttk.Frame(self.main_frame)
        log_frame.grid(row=7, column=0, sticky=tk.N+tk.S+tk.E+tk.W, pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        ttk.Label(log_frame, text="Processing Log:").grid(row=0, column=0, sticky=tk.W)
        self.log = tk.Text(log_frame, height=10, width=80)
        self.log.grid(row=1, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        log_scroll = ttk.Scrollbar(log_frame, command=self.log.yview)
        log_scroll.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.log.configure(yscrollcommand=log_scroll.set)

        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=8, column=0, pady=10)
        self.start_btn = ttk.Button(btn_frame, text="Start Processing", command=self.start_processing, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exit", command=self.root.quit, width=10).pack(side=tk.RIGHT, padx=5)

        for i in range(9):
            self.main_frame.rowconfigure(i, weight=0)
        self.main_frame.rowconfigure(7, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

    def show_help(self):
        help_text = (
            "Guidelines for Advanced Parameters:\n\n"
            "Noise Reduction Strength (prop_decrease): Range 0.0 to 1.0.\n"
            "FFT Size (n_fft): e.g., 2048.\n"
            "Window Length (win_length): Typically equal to n_fft.\n"
            "Hop Length (hop_length): Commonly n_fft/4.\n"
            "Butterworth Filter Order: Typical values between 4 and 8."
        )
        messagebox.showinfo("Help / Guide", help_text)

    def select_input_dir(self):
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir.delete(0, tk.END)
            self.input_dir.insert(0, directory)

    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, directory)

    def log_message(self, message):
        self.root.after(0, lambda: (self.log.insert(tk.END, message + "\n"),
                                      self.log.see(tk.END)))

    def process_audio_file(self, input_path, output_path, noise_start, noise_end, volume_boost):
        try:
            y, sr = librosa.load(input_path, sr=None, mono=False)
            if y.ndim == 1:
                y = np.expand_dims(y, axis=0)
            start_idx = int(noise_start * sr / 1000)
            end_idx = int(noise_end * sr / 1000)
            if end_idx <= start_idx or end_idx > y.shape[1]:
                raise ValueError("Invalid noise sample indices")
            prop_decrease = float(self.prop_decrease.get())
            n_fft = int(self.n_fft.get())
            win_length = int(self.win_length.get())
            hop_length = int(self.hop_length.get())
            filter_order = int(self.filter_order.get())
            processed_channels = []
            for channel in y:
                noise_sample = channel[start_idx:end_idx]
                reduced = nr.reduce_noise(
                    y=channel,
                    y_noise=noise_sample,
                    sr=sr,
                    prop_decrease=prop_decrease,
                    n_fft=n_fft,
                    win_length=win_length,
                    hop_length=hop_length
                )
                lowcut = float(self.low_cut.get())
                highcut = float(self.high_cut.get())
                filtered = bandpass_filter(reduced, lowcut, highcut, sr, order=filter_order)
                boost_gain = 10 ** (volume_boost / 20.0)
                boosted = filtered * boost_gain
                boosted = np.clip(boosted, -1.0, 1.0)
                processed_channels.append(boosted)
            if len(processed_channels) == 1:
                processed_audio = processed_channels[0]
            else:
                processed_audio = np.stack(processed_channels, axis=-1)
            subtype = 'PCM_16'
            if self.bit_depth_var.get():
                subtype = 'PCM_32'
            sf.write(output_path, processed_audio, sr, subtype=subtype)
            return True
        except Exception as e:
            self.log_message(f"Error processing {os.path.basename(input_path)}: {str(e)}")
            return False

    def batch_process(self):
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please select both input and output directories")
            return
        try:
            noise_start = float(self.noise_start.get())
            noise_end = float(self.noise_end.get())
            volume_boost = float(self.vol_spin.get())
            if noise_start >= noise_end:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Invalid parameters")
            return
        supported_ext = ('.wav', '.mp3', '.ogg', '.flac')
        file_list = []
        for root_dir, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith(supported_ext):
                    file_list.append(os.path.join(root_dir, file))
        total_files = len(file_list)
        if total_files == 0:
            messagebox.showinfo("Info", "No supported audio files found")
            return
        self.root.after(0, lambda: self.progress.config(maximum=total_files, value=0))
        processed = 0
        for idx, input_path in enumerate(file_list):
            if not self.processing:
                break
            rel_path = os.path.relpath(input_path, input_dir)
            output_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.log_message(f"Processing: {os.path.basename(input_path)}")
            if self.process_audio_file(input_path, output_path, noise_start, noise_end, volume_boost):
                processed += 1
            self.root.after(0, lambda v=idx+1: self.progress.config(value=v))
        messagebox.showinfo("Complete", f"Processed {processed}/{total_files} files")
        self.processing = False
        self.root.after(0, lambda: self.start_btn.config(text="Start Processing"))

    def start_processing(self):
        if not self.processing:
            self.processing = True
            self.start_btn.config(text="Stop Processing")
            threading.Thread(target=self.batch_process, daemon=True).start()
        else:
            self.processing = False
            self.start_btn.config(text="Start Processing")
