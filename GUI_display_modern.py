import os
import customtkinter as ctk
from tkinter import Label
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkVideoPlayer import TkinterVideo

# Set theme
ctk.set_appearance_mode("dark")  # Options: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

# Define paths
BASE_DIR = "classification_results/correct"
ORI_IMG_DIR = os.path.join(BASE_DIR, "ori_img")
GRADCAM_DIR = os.path.join(BASE_DIR, "gradcam")
MASK_DIR = os.path.join(BASE_DIR, "mask")
PROB_DIR = os.path.join(BASE_DIR, "prob")
VIDEO_DIR = os.path.join(BASE_DIR, "video")
LOGO_PATH = "./logo2.png"  # Path to your logo
SELECTED_IMG_PATH = os.path.join(BASE_DIR, "select_img.txt")

# Load selected images from list
with open(SELECTED_IMG_PATH, "r") as f:
    selected_images = [line.strip() for line in f.readlines()]


class ImageViewerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Medical Image Viewer")
        self.geometry("900x600")
        self.configure(bg="#1e1e1e")

        # Handle close event (Clicking 'X' button)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Image Index
        self.img_index = 0
        self.current_img_name = selected_images[self.img_index]

        # Navigation Bar with Full-Width Logo
        self.nav_frame = ctk.CTkFrame(self, corner_radius=25)
        self.nav_frame.pack(pady=20, fill="x")

        self.prev_btn = ctk.CTkButton(self.nav_frame, text="⟨ Previous", command=self.previous_image)
        self.prev_btn.pack(side="left", padx=10, pady=5)

        # Full-width logo
        self.logo_label = Label(self.nav_frame, bg="#1e1e1e")
        self.logo_label.pack(side="left",fill="both", expand=True)

        self.next_btn = ctk.CTkButton(self.nav_frame, text="Next ⟩", command=self.next_image)
        self.next_btn.pack(side="right", padx=10, pady=5)
        # Load and resize logo
        self.load_logo()

        # Video Player Section
        self.video_frame = ctk.CTkFrame(self, corner_radius=25, fg_color="#1e1e1e")
        # self.video_frame.pack(side="top",pady=30)
        # self.video_player = TkinterVideo(master=self.video_frame, scaled=True)
        # self.video_player.pack(fill="x", expand=True)
        # self.video_player.config(width=800, height=450)  # <-- Added: Set a larger default size
        self.video_frame.pack(side="top", pady=30, fill="both", expand=True)  # <-- Modified: Allow the frame to expand
        self.video_player = TkinterVideo(master=self.video_frame, scaled=True)
        self.video_player.pack(fill="both", expand=True)  # <-- Modified: Allow video to expand fully
        self.video_player.config(width=300, height=250)  # <-- Added: Set a larger default size
        self.play_video(self.current_img_name)

        # Feature Buttons
        self.button_frame = ctk.CTkFrame(self, corner_radius=25)
        self.button_frame.pack(pady=10)

        self.select_frame_btn = ctk.CTkButton(self.button_frame, text="Select Frame", command=self.show_image)
        self.select_frame_btn.pack(side="left", padx=10, pady=5)

        self.segmentation_btn = ctk.CTkButton(self.button_frame, text="Segmentation", command=self.show_mask)
        self.segmentation_btn.pack(side="left", padx=10, pady=5)

        self.diagnose_btn = ctk.CTkButton(self.button_frame, text="Diagnose", command=self.show_diagnose)
        self.diagnose_btn.pack(side="left", padx=10, pady=5)

        self.gradcam_btn = ctk.CTkButton(self.button_frame, text="Grad-CAM", command=self.show_gradcam)
        self.gradcam_btn.pack(side="left", padx=10, pady=5)

        # Display Sections
        self.image_display_frame = ctk.CTkFrame(self, corner_radius=10)
        self.image_display_frame.pack(pady=10, fill="both", expand=True)
        # Configure grid layout to evenly distribute labels
        self.image_display_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)  # <-- Equal spacing

        # Image Label
        self.img_label = Label(self.image_display_frame, bg="#1e1e1e")
        self.img_label.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")  # <-- Use grid & center

        # Segmentation Label
        self.segmentation_label = Label(self.image_display_frame, bg="#1e1e1e")
        self.segmentation_label.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")  # <-- Centered in grid

        # Diagnosis Label
        self.diagnosis_label = Label(self.image_display_frame, bg="#1e1e1e")
        self.diagnosis_label.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")  # <-- Centered in grid

        # Grad-CAM Label
        self.gradcam_label = Label(self.image_display_frame, bg="#1e1e1e")
        self.gradcam_label.grid(row=0, column=3, padx=10, pady=5, sticky="nsew")  # <-- Centered in grid
        # self.img_label = Label(self.image_display_frame, bg="#1e1e1e")
        # self.img_label.pack(side="left", padx=10, pady=5)

        # self.segmentation_label = Label(self.image_display_frame, bg="#1e1e1e")
        # self.segmentation_label.pack(side="left", padx=10, pady=5)

        # self.diagnosis_label = Label(self.image_display_frame, bg="#1e1e1e")
        # self.diagnosis_label.pack(side="left", padx=10, pady=5)

        # self.gradcam_label = Label(self.image_display_frame, bg="#1e1e1e")
        # self.gradcam_label.pack(side="left", padx=10, pady=5)



    def on_close(self):
        """Handles the window close event (Clicking 'X' button)"""
        print("Closing application...")
        self.video_player.stop()  # Stop video player to release resources
        self.quit()  # Exit main loop
        self.destroy()  # Close the application window

    def load_logo(self):
        """Loads and resizes the logo dynamically to fill the entire row."""
        logo_img = Image.open(LOGO_PATH)
        logo_img = logo_img.resize((1000, 100))  # Ensure it extends fully
        self.logo_img = ImageTk.PhotoImage(logo_img)
        self.logo_label.configure(image=self.logo_img)
        self.logo_label.image = self.logo_img

    def play_video(self, img_name):
        """Displays the corresponding video"""
        video_path = os.path.join(VIDEO_DIR, f"{img_name.split('_')[0]}.MOV")
        # Stop the previous video safely before loading a new one
        self.video_player.stop()
        if os.path.exists(video_path):
            try:
                self.video_player.load(video_path)
                self.video_player.set_size((300, 250))  # Ensure size consistency
                self.video_player.scale = True  # Force auto-scaling
                self.video_player.configure(bg="#1e1e1e")  # <-- Ensure dark background
                self.video_player.play()
            except Exception as e:
                print(f"Error loading video {video_path}: {e}")
        else:
            print(f"Video not found: {video_path}")

    def show_image(self):
        """Displays the original image"""
        img_path = os.path.join(ORI_IMG_DIR, f"{self.current_img_name}.png")
        self.update_image(self.img_label, img_path)

    def show_mask(self):
        """Displays the segmentation mask"""
        mask_path = os.path.join(MASK_DIR, f"{self.current_img_name}.png")
        self.update_image(self.segmentation_label, mask_path)

    def show_gradcam(self):
        """Displays the Grad-CAM overlay"""
        gradcam_path = os.path.join(GRADCAM_DIR, f"{self.current_img_name}.png")
        self.update_image(self.gradcam_label, gradcam_path)

    def show_diagnose(self):
        """Displays a bar chart of probabilities with a legend"""
        prob_path = os.path.join(PROB_DIR, f"{self.current_img_name}.txt")
        with open(prob_path, "r") as f:
            lines = f.readlines()

        class_probs = {}
        for line in lines[2:]:  # Skip header lines
            class_name, prob = line.strip().split(": ")
            class_probs[class_name] = float(prob)

        # Clear previous figure
        for widget in self.diagnosis_label.winfo_children():
            widget.destroy()

        # Define colors for each class
        class_colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FFD700']
        fig, ax = plt.subplots(figsize=(3.5, 3.5))

        bars = ax.barh(list(class_probs.keys()), list(class_probs.values()), color=class_colors, edgecolor='black')

        # Remove frame, x labels, and y labels
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_title("Diagnosis Probability", fontsize=9, fontweight="bold")

        # Invert y-axis for better readability
        ax.invert_yaxis()

        # Add value labels inside bars
        for bar in bars:
            ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2, 
                    f'{bar.get_width():.2f}', ha='left', va='center', fontsize=9, fontweight="bold")

        # Add legend
        legend_labels = [f"{name}" for name in class_probs.keys()]
        ax.legend(bars, legend_labels, loc="upper right", title="Class Name", fontsize=7)

        # Embed in Tkinter
        self.diagnose_canvas = FigureCanvasTkAgg(fig, master=self.diagnosis_label)
        self.diagnose_canvas.get_tk_widget().pack()
        self.diagnose_canvas.draw()


    def update_image(self, label, img_path):
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((280, 280))
            img = ImageTk.PhotoImage(img)
            label.configure(image=img)
            label.image = img  # Keep reference to prevent garbage collection
        else:
            label.configure(image="")  # Clear label if image not found
            label.image = None


    def next_image(self):
        """Displays the next image"""
        if self.img_index < len(selected_images) - 1:
            self.img_index += 1
            self.current_img_name = selected_images[self.img_index]
            self.play_video(self.current_img_name)
            self.clear_all_labels()

    def previous_image(self):
        """Displays the previous image"""
        if self.img_index > 0:
            self.img_index -= 1
            self.current_img_name = selected_images[self.img_index]
            self.play_video(self.current_img_name)
            self.clear_all_labels()

    def clear_all_labels(self):
        """Clears all images and plots"""
        for label in [self.img_label, self.segmentation_label, self.gradcam_label, self.diagnosis_label]:
            self.clear_label(label)

    def clear_label(self, label):
        """Clears content of a label"""
        label.configure(image="")
        label.image = None
        for widget in label.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = ImageViewerApp()
    app.mainloop()
