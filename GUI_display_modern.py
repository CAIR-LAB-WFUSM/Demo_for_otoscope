import os
import customtkinter as ctk
from tkinter import Label
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkVideoPlayer import TkinterVideo

# Set theme
# ## --- MODIFIED --- ##: Changed appearance to "light"
ctk.set_appearance_mode("light")  # Options: "light", "dark", "system"
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
        ## --- MODIFIED --- ##: Increased window size for better layout and set light blue background
        self.geometry("900x600")
        self.configure(bg="#e0f0ff")

        # Handle close event (Clicking 'X' button)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Image Index
        self.img_index = 0
        self.current_img_name = selected_images[self.img_index]

        # Navigation Bar with Full-Width Logo
        ## --- MODIFIED --- ##: Changed frame color to match the light theme
        self.nav_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#cce5ff")
        self.nav_frame.pack(pady=5, fill="x")

        self.prev_btn = ctk.CTkButton(self.nav_frame, text="⟨ Previous", command=self.previous_image)
        self.prev_btn.pack(side="left", padx=10, pady=5)

        # Full-width logo
        ## --- MODIFIED --- ##: Changed label background color
        self.logo_label = Label(self.nav_frame, bg="#cce5ff")
        self.logo_label.pack(side="left",fill="both", expand=True)

        self.next_btn = ctk.CTkButton(self.nav_frame, text="Next ⟩", command=self.next_image)
        self.next_btn.pack(side="right", padx=10, pady=5)
        # Load and resize logo
        self.load_logo()

        # Video Player Section
        self.video_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#e0f0ff")
        self.video_frame.pack(side="top", pady=5, fill="both", expand=True)  # <-- Modified: Allow the frame to expand
        self.video_player = TkinterVideo(master=self.video_frame, scaled=True)
        self.video_player.configure(bg="#e0f0ff")
        self.video_player.pack(fill="both", expand=True)  # <-- Modified: Allow video to expand fully
        self.video_player.config(width=300, height=250)  # <-- Added: Set a larger default size
        self.play_video(self.current_img_name)

        ## --- ADDED --- ##: Added a text description for the video player
        self.video_description = ctk.CTkLabel(self.video_frame, text="Otoscope videos collected from clinics.",
                                              text_color="#333333", font=("Arial", 18))
        self.video_description.pack(pady=5)

        ## --- ADDED --- ##: This entire block is new. It creates a main frame for the features
        ## to enable grid layout for proper alignment.
        self.features_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#e0f0ff")
        self.features_frame.pack(pady=5, padx=20, fill="both", expand=True)
        self.features_frame.grid_columnconfigure((0, 1, 2, 3), weight=1) # Configure columns to be of equal width
        
        ## --- ADDED --- ##: A dedicated frame for the "Select Frame" button and its image label.
        ## This ensures the button is directly above the label.
        self.frame1 = ctk.CTkFrame(self.features_frame, fg_color="transparent")
        self.frame1.grid(row=0, column=0, padx=10, pady=5, sticky="n")
        self.select_frame_btn = ctk.CTkButton(self.frame1, text="Select Frame", command=self.show_image)
        self.select_frame_btn.pack(pady=5)
        ## --- MODIFIED/ADDED --- ##: Set a fixed size and placeholder color for the image label.
        self.placeholder_img = ctk.CTkFrame(self.frame1, width=200, height=200, fg_color="#d0e0f0", corner_radius=10)
        self.placeholder_img.pack()
        self.placeholder_img.pack_propagate(False)
        self.img_label = Label(self.placeholder_img, bg="#d0e0f0")
        self.img_label.pack()
        ## --- MODIFIED/ADDED--- ##: Set a Image description 
        self.selecte_frame_description = ctk.CTkLabel(self.frame1, text="The AI picks the best frame for making a diagnosis here.",
                                              text_color="#333333", font=("Arial", 16),wraplength=200, # Set a fixed width in pixels for wrapping
                                                justify="center")
        self.selecte_frame_description.pack(pady=5)

        ## --- ADDED --- ##: A dedicated frame for the "Segmentation" button and its image label.
        self.frame2 = ctk.CTkFrame(self.features_frame, fg_color="transparent")
        self.frame2.grid(row=0, column=1, padx=10, pady=5, sticky="n")
        self.segmentation_btn = ctk.CTkButton(self.frame2, text="Segmentation", command=self.show_mask)
        self.segmentation_btn.pack(pady=5)
        ## --- MODIFIED/ADDED --- ##: Set a fixed size and placeholder color for the image label.
        self.placeholder_seg = ctk.CTkFrame(self.frame2, width=200, height=200, fg_color="#d0e0f0", corner_radius=10)
        self.placeholder_seg.pack()
        self.placeholder_seg.pack_propagate(False)
        self.segmentation_label = Label(self.placeholder_seg, bg="#d0e0f0")
        self.segmentation_label.pack(fill="both", expand=True)
        ## --- MODIFIED/ADDED--- ##: Set a Image description 
        self.segmentation_description = ctk.CTkLabel(self.frame2, text="The AI is trying to pinpoint the exact area of the eardrum here.",
                                              text_color="#333333", font=("Arial", 16),wraplength=200, # Set a fixed width in pixels for wrapping
                                                justify="center")
        self.segmentation_description.pack(pady=5)

        ## --- ADDED --- ##: A dedicated frame for the "Diagnose" button and its plot label.
        self.frame3 = ctk.CTkFrame(self.features_frame, fg_color="transparent")
        self.frame3.grid(row=0, column=2, padx=10, pady=5, sticky="n")
        self.diagnose_btn = ctk.CTkButton(self.frame3, text="Diagnose", command=self.show_diagnose)
        self.diagnose_btn.pack(pady=5)
        ## --- MODIFIED/ADDED --- ##: Set a fixed size and placeholder color for the diagnosis plot label.
        self.placeholder_diag = ctk.CTkFrame(self.frame3, width=200, height=200, fg_color="#d0e0f0", corner_radius=10)
        self.placeholder_diag.pack()
        self.placeholder_diag.pack_propagate(False)
        self.diagnosis_label = Label(self.placeholder_diag, bg="#d0e0f0")
        self.diagnosis_label.pack()
        ## --- MODIFIED/ADDED--- ##: Set a Image description 
        self.diagnosis_description = ctk.CTkLabel(self.frame3, text="The AI figures out which medical diagnosis is the most likely.",
                                              text_color="#333333", font=("Arial", 16),wraplength=200, # Set a fixed width in pixels for wrapping
                                                justify="center")
        self.diagnosis_description.pack(pady=5)

        ## --- ADDED --- ##: A dedicated frame for the "Grad-CAM" button and its image label.
        self.frame4 = ctk.CTkFrame(self.features_frame, fg_color="transparent")
        self.frame4.grid(row=0, column=3, padx=10, pady=5, sticky="n")
        self.gradcam_btn = ctk.CTkButton(self.frame4, text="Grad-CAM", command=self.show_gradcam)
        self.gradcam_btn.pack(pady=5)
        ## --- MODIFIED/ADDED --- ##: Set a fixed size and placeholder color for the image label.
        self.placeholder_grad = ctk.CTkFrame(self.frame4, width=200, height=200, fg_color="#d0e0f0", corner_radius=10)
        self.placeholder_grad.pack()
        self.placeholder_grad.pack_propagate(False)
        self.gradcam_label = Label(self.placeholder_grad, bg="#d0e0f0")
        self.gradcam_label.pack(fill="both", expand=True)
        ## --- MODIFIED/ADDED--- ##: Set a Image description 
        self.gradcam_description = ctk.CTkLabel(self.frame4, text="The AI shows which areas it focused on to make this diagnosis, going from red to blue(most important to least important).",
                                              text_color="#333333", font=("Arial", 16), wraplength=200, # Set a fixed width in pixels for wrapping
                                                justify="center")
        self.gradcam_description.pack(pady=5)



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
                self.video_player.configure(bg="#e0f0ff")  # <-- Ensure dark background
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
        fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor='#d0e0f0')

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
