from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
import os
import random


class MemoryGame:
    def __init__(self, root):
        self.root = root;
        self.root.title("Memory Game");

        # Center and format the title
        title_label: tk.Label = tk.Label(
            root,
            text="Welcome To Memory Game!",
            font=("Helvetica", 16, "bold"),
            pady=10,
            relief="groove",
            bd=4,
            bg="lightpink",
            fg="gray20"
        )
        title_label.pack(side="top", fill="x");

        # Create a frame to hold the grid of buttons
        self.grid_frame: tk.Frame = tk.Frame(self.root, relief="groove", bd=4)
        self.grid_frame.pack(padx=10, pady=10, expand=True, fill="both")

        # Create a label to display messages to the user
        self.message_label: tk.Label = tk.Label(self.grid_frame, text="", font=("Helvetica", 14));
        self.message_label.grid(row=0, column=0, columnspan=5);  # Place the label at the top of the grid

        # Use relative path to images directory
        self.image_path: str = os.path.join(os.path.dirname(__file__), "images")

        # List of image file names located in the same directory as the script
        self.image_files: list[str] = ["bear.jfif", "cat.jfif", "cow.jfif", "fox.jfif",
                                       "giraffe.jfif", "lion.jfif", "monkey.jfif",
                                       "pig.jfif", "tiger.jfif", "zebra.jfif"];

        # Duplicate the list to create pairs and shuffle them
        self.image_files = self.image_files * 2;
        random.shuffle(self.image_files);

        # Desired size for all images
        self.desired_width: int = 100;
        self.desired_height: int = 100;

        # Load the images and prepare the game
        self.photos: list[ImageTk.PhotoImage] = self.load_images();
        # Create a blank image of the same size as the images
        self.blank_photo: ImageTk.PhotoImage = self.create_blank_image();
        self.buttons: list[tk.Button] = [];
        self.revealed: list[int] = [];
        self.matches_found: int = 0;  # Initialize a counter for matches found
        self.create_grid();

        # Disable all buttons initially
        self.disable_buttons();

        # Show the initial prompt to the player
        self.prompt_choice_or_exit();

    def load_images(self) -> list[ImageTk.PhotoImage]:
        """Load and resize the images."""
        photos: list[ImageTk.PhotoImage] = [];
        for img_file in self.image_files:
            full_path: str = os.path.join(self.image_path, img_file);
            img: Image.Image = Image.open(full_path);
            img = img.resize((self.desired_width, self.desired_height), Image.Resampling.LANCZOS);
            photo: ImageTk.PhotoImage = ImageTk.PhotoImage(img);
            photos.append(photo);
        return photos;

    def create_blank_image(self) -> ImageTk.PhotoImage:
        """Create a blank image (transparent) to set as the initial button image."""
        blank_image: Image.Image = Image.new('RGBA', (self.desired_width, self.desired_height));
        return ImageTk.PhotoImage(blank_image);

    def create_grid(self) -> None:
        """Create the grid of buttons with blank images initially."""
        for i in range(len(self.photos)):
            button = tk.Button(
                self.grid_frame,
                image=self.blank_photo,
                command=lambda i=i: self.on_button_click(i),
                relief="groove",
                bd=4
            )
            # Shift rows by +1 to leave space for the label
            button.grid(row=(i // 5) + 1, column=i % 5, padx=5, pady=5, sticky="nsew");
            self.buttons.append(button);

    def on_button_click(self, index: int) -> None:
        """Handle button clicks, revealing images."""
        if len(self.revealed) < 2 and index not in self.revealed:
            self.buttons[index].config(image=self.photos[index], state="active");  # Reveal the clicked card
            self.revealed.append(index);

            if len(self.revealed) == 2:
                self.root.after(1000, self.check_match);  # check for a match

    def check_match(self) -> None:
        """Check if the two revealed images match."""
        if self.image_files[self.revealed[0]] == self.image_files[self.revealed[1]]:

            # If they match, disable the buttons to keep the images visible
            for index in self.revealed:
                self.buttons[index].config(state="disabled");

            self.matches_found += 1  # Increment the match counter

            # Check if all pairs have been matched
            if self.matches_found == len(self.image_files) // 2:
                self.message_label.config(text="Congratulations for winning the game!");
                self.ask_play_again();  # Ask to play again only when all pairs are matched
            else:
                self.message_label.config(text="Great, you've found a pair! Keep going!");

        else:
            # If they don't match, reset the buttons to the blank image
            for index in self.revealed:
                self.buttons[index].config(image=self.blank_photo, state="normal");
            self.message_label.config(text="The pair was not found, try again!");

        self.disable_buttons()  # Ensure buttons are disabled while the prompt is active

        # Clear the message after 2 seconds
        self.root.after(1000, self.clear_message);

        # Clear the revealed list
        self.revealed.clear();

    def clear_message(self) -> None:
        """Clear the message label."""
        if self.message_label.winfo_exists():
            self.message_label.config(text="");

        # Prompt the user again to choose cards or exit
        self.prompt_choice_or_exit();

    def prompt_choice_or_exit(self) -> None:
        """Prompt the player to choose two cards or exit."""
        choice: bool = messagebox.askokcancel("Your Move",
                                              "Please choose two cards or press Exit to quit the game.");
        if choice:
            self.enable_buttons();  # Re-enable the buttons if the player chooses to continue
        else:
            self.root.destroy();  # Exit the game if the player presses "Exit"

    def disable_buttons(self) -> None:
        """Disable all buttons in the grid."""
        for button in self.buttons:
            button.config(state="disabled");

    def enable_buttons(self) -> None:
        """Enable all buttons in the grid."""
        for button in self.buttons:
            if button['image'] == str(self.blank_photo):  # Only enable buttons with the blank image
                button.config(state="normal");

    def ask_play_again(self) -> None:
        """Ask the player if they want to play again or not."""
        play_again = messagebox.askyesno("Play Again?", "Do you want to play again?");
        if play_again:
            self.reset_game();
        else:
            self.root.destroy();  # Destroy the grid frame to completely remove it

    def reset_game(self) -> None:
        """Reset the game to play again."""
        self.matches_found = 0;  # Reset match counter
        random.shuffle(self.image_files);
        self.photos = self.load_images();  # Re-load the images according to the shuffled order

        for button in self.buttons:
            button.config(image=self.blank_photo, state="normal");
        self.message_label.config(text="New game started! Good luck!");


if __name__ == "__main__":
    root = tk.Tk();
    game = MemoryGame(root);
    root.mainloop();
