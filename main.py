import tkinter as tk
from tkinter import ttk
from excel_tab import ExcelDuplicateRemoverTab
from tts_tab import TextToSpeechConverterTab
from audio_denoiser_tab import AudioDenoiserTab
from powerpoint_text_extractor_tab import PowerPointTextExtractorTab
from audio_splitter_tab import AudioSplitterTab

class OmniToolSuite:
    def __init__(self, root):
        self.root = root
        self.root.title("OmniTool Suite")
        self.root.geometry("900x700")
        self.build_gui()

    def build_gui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=1, fill="both")

        self.excel_tab = ExcelDuplicateRemoverTab(self.notebook)
        self.notebook.add(self.excel_tab.frame, text="Excel Duplicate Remover")

        self.tts_tab = TextToSpeechConverterTab(self.notebook)
        self.notebook.add(self.tts_tab.frame, text="Text-to-Speech Converter")

        self.audio_denoiser_tab = AudioDenoiserTab(self.notebook)
        self.notebook.add(self.audio_denoiser_tab.frame, text="Audio Denoiser")

        self.pptx_extractor_tab = PowerPointTextExtractorTab(self.notebook)
        self.notebook.add(self.pptx_extractor_tab.frame, text="PPTX Text Extractor")

        self.audio_splitter_tab = AudioSplitterTab(self.notebook)
        self.notebook.add(self.audio_splitter_tab.frame, text="Audio Splitter")

def main():
    root = tk.Tk()  # Create the main application window
    app = OmniToolSuite(root)
    root.mainloop()  # Run the event loop

if __name__ == "__main__":
    main()
