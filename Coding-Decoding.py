# ==========================================================
#  ULTIMATE SECURITY PROJECT - SECRET CODE TRANSLATOR (FINAL)
#  Features : Modern ttkbootstrap GUI, Encode/Decode, Load/Save,
#             Preserves punctuation handling, short-word rules,
#             Inline comments and corrected issues.
#  Author : Mayank Baranwal
# ==========================================================



# ------------------------------ IMPORTS -------------------------------- #
import random
import string
import os

# ttkbootstrap is a drop-in modern styling layer for tkinter
import ttkbootstrap as ttk
# provides constants like LEFT, RIGHT if desired
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox



# ----------------------------- CORE LOGIC -------------------------------- #
# All encoding/decoding rules and simple helpers are implemented here.
# Inline comments explain behavior and corrections.


# Encoding logic
def generate_random_chars(n=3):
    """
    Generate n random alphanumeric characters (letters + digits).
    Correction: original docstring said lowercase only; we now include
    uppercase and digits for stronger variety (keeps earlier modern version).
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=n))


# Helper to split word into core and punctuation
def split_word_punctuation(word):
    """
    Separate leading/trailing non-alphanumeric characters (punctuation)
    from the 'core' word so punctuation is preserved during encode/decode.

    Returns (prefix, core, suffix).
    Example: '"Hello,"' -> ('"', 'Hello', ',')
    """
    prefix = ''
    suffix = ''


    # Move trailing punctuation to suffix
    while word and not word[-1].isalnum():
        # build suffix from right to left, so prepend is used
        suffix = word[-1] + suffix
        word = word[:-1]


    # Move leading punctuation to prefix
    while word and not word[0].isalnum():
        prefix += word[0]
        word = word[1:]

    return prefix, word, suffix


# Encoding logic
def encode_word(word):
    """
    Encode a single token (word with possible punctuation).
    Rules:
      - If core (alphanumeric part) length < 3: reverse the core
      - Else: move first char to end, then add 3 random chars at start and end
    NOTE: We preserve punctuation by reattaching prefix/suffix.
    """
    prefix, core, suffix = split_word_punctuation(word)


    # If core is empty (word was purely punctuation), return original
    if core == "":
        return prefix + core + suffix

    if len(core) < 3:
        # For words like "I", "am" -> reverse
        encoded_core = core[::-1]
    else:
        # Move first letter to end
        transformed = core[1:] + core[0]
        # Add random characters at start/end for secrecy
        encoded_core = generate_random_chars(3) + transformed + generate_random_chars(3)

    return prefix + encoded_core + suffix


# Decoding logic
def decode_word(word):
    """
    Decode a single token (word with punctuation).
    Rules:
      - If core length < 3: reverse the core
      - Else: remove first 3 and last 3 chars (random padding),
              then move last character of core to the front to restore original
    Corrections:
      - Handles empty core and short cores safely (avoids index errors).
    """
    prefix, core, suffix = split_word_punctuation(word)


    # If core empty (pure punctuation), return as-is
    if core == "":
        return prefix + core + suffix

    if len(core) < 3:
        decoded_core = core[::-1]
    else:
        # Safety: ensure core has at least 6 characters (3 prefix + transformed + 3 suffix).
        # If incoming text is malformed we attempt a best-effort decoding.
        if len(core) < 6:
            # Malformed / unexpected: try to decode gracefully by reversing encode steps if possible.
            # We'll attempt to remove whatever 3-char padding exists at ends when possible.
            # Fallback: return core as-is to avoid crashes.
            # (This is defensive coding: better than raising an exception.)
            decoded_core = core
        else:
            # Remove the 3 random characters at both ends
            inner = core[3:-3]   # this is the 'transformed' string (first-letter-moved-to-end)
            if inner == "":
                # Defensive: nothing left after stripping padding
                decoded_core = ""
            else:
                # Move last letter to the beginning to reverse the earlier transform
                decoded_core = inner[-1] + inner[:-1]

    return prefix + decoded_core + suffix


# Message-level encode/decode
def encode_message(message):
    """
    Encode an entire message. Splits on whitespace to preserve token boundaries.
    This simple split keeps multiple spaces normalized to single spaces in output.
    """
    return ' '.join(encode_word(token) for token in message.split())

def decode_message(message):
    """
    Decode an entire message. Same tokenization as encode_message.
    """
    return ' '.join(decode_word(token) for token in message.split())



# ----------------------------- GUI LOGIC -------------------------------- #
# The GUI wraps the core logic above. Inline comments explain each widget,
# event handler, and the corrections applied from the original code.



# Main Application Class
class SecretCodeApp:
    def __init__(self, root):
        """
        Initialize GUI:
          - root should be a ttkbootstrap.Window so theming is applied.
          - We use frames to structure Input -> Buttons -> Output.
        Correction notes:
          - Removed an unnecessary/self-conflicting style call from original code.
            The original had `self.style = ttk.Style("cyborg")` which isn't needed
            when using ttk.Window(themename=...).
        """
        self.root = root
        self.root.title("🔐 Secret Code Translator")
        self.root.geometry("900x650")  # initial window size; window is resizable



        # ---------------- Title ----------------
        # Title label
        title = ttk.Label(
            root,
            text="Secret Code Translator",
            font=("Segoe UI", 22, "bold"),
            bootstyle="info"  # bootstyle controls color/theme in ttkbootstrap
        )
        title.pack(pady=12)



        # ---------------- Input Section ----------------
        # Frame to contain input label and text widget
        input_frame = ttk.Frame(root, padding=(12, 6))
        input_frame.pack(fill="both", expand=False, padx=12)

        ttk.Label(input_frame, text="Input Message:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        # Use ttk.Text (ttkbootstrap provides a Text wrapper) for consistent theme
        self.input_text = ttk.Text(input_frame, height=8, font=("Consolas", 11))
        self.input_text.pack(fill="both", expand=True)



        # ---------------- Buttons ----------------
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=12, padx=12)


        # Each button executes its corresponding handler below
        # Corrections: explicit commands and consistent bootstyles used for clarity
        ttk.Button(button_frame, text="🔒 Encode", bootstyle="success-outline", width=14,
                    command=self.encode_action).grid(row=0, column=0, padx=6, pady=4)

        ttk.Button(button_frame, text="🔓 Decode", bootstyle="info-outline", width=14,
                    command=self.decode_action).grid(row=0, column=1, padx=6, pady=4)

        ttk.Button(button_frame, text="🧹 Clear", bootstyle="danger-outline", width=14,
                    command=self.clear_action).grid(row=0, column=2, padx=6, pady=4)

        ttk.Button(button_frame, text="📂 Load File", bootstyle="warning-outline", width=14,
                    command=self.load_file).grid(row=0, column=3, padx=6, pady=4)

        ttk.Button(button_frame, text="💾 Save File", bootstyle="secondary-outline", width=14,
                    command=self.save_file).grid(row=0, column=4, padx=6, pady=4)



        # ---------------- Output Section ----------------
        output_frame = ttk.Frame(root, padding=(12, 6))
        output_frame.pack(fill="both", expand=True, padx=12, pady=(0, 6))


        # Output label and text widget
        ttk.Label(output_frame, text="Output Message:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
        self.output_text = ttk.Text(output_frame, height=10, font=("Consolas", 11))
        self.output_text.pack(fill="both", expand=True)


        # Footer: simple credit line
        footer = ttk.Label(root, text="Made with ❤️ using Python & ttkbootstrap",
                           font=("Segoe UI", 10), bootstyle="secondary")
        footer.pack(side="bottom", pady=8)



    # ---------------- Handlers / Utilities ----------------


    # Encode action
    def encode_action(self):
        """
        Read input_text, encode it, and show result in output_text.
        Validation: warn if input is empty.
        """
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to encode.")
            return
        result = encode_message(text)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", result)


    # Decode action
    def decode_action(self):
        """
        Read input_text, decode it, and show result in output_text.
        Validation: warn if input is empty.
        """
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to decode.")
            return
        result = decode_message(text)
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", result)


    # Clear action
    def clear_action(self):
        """Clear both input and output text widgets."""
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")


    # Load file action
    def load_file(self):
        """
        Open file dialog, read plain text file, and put contents into input_text.
        Correction: added safe file existence checks and encoding='utf-8'
        """
        filename = filedialog.askopenfilename(title="Open Text File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file:\n{e}")
                return
            self.input_text.delete("1.0", "end")
            self.input_text.insert("end", content)
            messagebox.showinfo("File Loaded", f"Loaded file: {os.path.basename(filename)}")


    # Save file action
    def save_file(self):
        """
        Save the contents of output_text to a file chosen by the user.
        Validation: ensure there is something to save.
        """
        result = self.output_text.get("1.0", "end").strip()
        if not result:
            messagebox.showwarning("Warning", "No encoded or decoded text to save.")
            return


        # Ask for filename to save
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                                                title="Save Output As")
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(result)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
                return
            messagebox.showinfo("Saved", f"Saved to: {os.path.basename(filename)}")



# ----------------------------- RUN APP -------------------------------- #
# Correction: create ttk.Window with an explicit theme (themename). This is
# the recommended way to apply ttkbootstrap styling. The previous code used a
# stray `Style("cyborg")` call which was redundant/unnecessary.


# Run the application
if __name__ == "__main__":
    # You can change themename to: 'flatly', 'minty', 'solar', 'cyborg', 'darkly', etc.
    root = ttk.Window(themename="cyborg")
    app = SecretCodeApp(root)
    root.mainloop()
