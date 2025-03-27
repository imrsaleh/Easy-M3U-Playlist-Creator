import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
import re
from urllib.parse import urlparse

class ChannelManager:
    def __init__(self):
        self.channels = []
        self.window = tk.Tk()
        self.window.title("Easy M3U Playlist Creator v1.2.0")
        self.window.resizable(False, False)
        self.setup_ui()
        self.create_context_menu()

    def validate_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def setup_ui(self):
        # Main frame setup
        main_frame = tk.Frame(self.window, borderwidth=2, relief="groove")
        main_frame.pack(padx=10, pady=10)

        # Input fields setup
        fields = [
            ("Channel Name", "entry_channel_name", 0, 0),
            ("Group Title", "entry_group_title", 0, 2),
            ("EPG TVG Name", "entry_tvg_name", 1, 0),
            ("EPG Time Shift", "combo_tvg_shift", 1, 2),
            ("EPG TVG ID", "entry_tvg_id", 2, 0),
            ("Logo Link", "entry_logo_link", 2, 2),
            ("Channel Link", "entry_channel_link", 3, 0),
            ("Manifest Type", "manifest_type_var", 3, 2),
            ("License Key", "entry_license_key", 4, 0),
            ("License Type", "license_type_var", 4, 2)
        ]

        for text, var, row, col in fields:
            label = tk.Label(main_frame, text=text)
            label.grid(row=row, column=col, padx=5, pady=5, sticky="w")
            entry = tk.Entry(main_frame, font=("Arial", 10), width=30)
            entry.grid(row=row, column=col+1, padx=5, pady=5, ipady=6)
            setattr(self, var, entry)

        # Comboboxes setup
        self.setup_comboboxes(main_frame)
        self.setup_buttons(main_frame)
        self.setup_info_display()

    def setup_comboboxes(self, parent):
        # TVG Shift combobox
        tvg_shift = ttk.Combobox(parent, values=[""] + [str(i) for i in range(-12, 13)], 
                               font=("Arial", 10), width=28, state="readonly")
        tvg_shift.grid(row=1, column=3, padx=5, pady=5)
        self.combo_tvg_shift = tvg_shift

        # License Type combobox
        license_types = ["", "clearkey", "com.widevine.alpha", 
                        "com.microsoft.playready", "org.w3.clearkey"]
        self.license_type_var = tk.StringVar()
        ttk.Combobox(parent, values=license_types, textvariable=self.license_type_var,
                    font=("Arial", 10), width=28, state="readonly").grid(row=4, column=3, padx=5, pady=5)

        # Manifest Type combobox
        manifest_types = ["", "hls", "dash", "smooth", "progressive", 
                         "wv", "ismt", "rtmp", "m3u8", "mpd", "mp4", "ts", "flv"]
        self.manifest_type_var = tk.StringVar()
        ttk.Combobox(parent, values=manifest_types, textvariable=self.manifest_type_var,
                    font=("Arial", 10), width=28, state="readonly").grid(row=3, column=3, padx=5, pady=5)

    def setup_buttons(self, parent):
        buttons = [
            ("Add Channel", self.on_add_channel, 5, 1),
            ("Clear Fields", self.on_clear_fields, 5, 3),
            ("Generate M3U", self.on_generate_m3u, 6, 2),
            ("GitHub", self.open_github, 6, 4)
        ]

        for text, command, row, col in buttons:
            if row is not None:
                btn = tk.Button(parent, text=text, command=command)
                btn.grid(row=row, column=col, padx=5, pady=10)
            else:
                btn = tk.Button(self.window, text=text, command=command)
                btn.pack(side="right" if text == "Check Updates" else "left", pady=20)

    def setup_info_display(self):
        self.channel_info = tk.Text(self.window, height=15, width=79)
        self.channel_info.pack(padx=10, pady=10)
        
        self.channel_count_var = tk.StringVar()
        tk.Label(self.window, textvariable=self.channel_count_var, 
                font=("Arial", 11)).pack(pady=10)

    def create_context_menu(self):
        context_menu = tk.Menu(self.window, tearoff=0)
        context_menu.add_command(label="Cut", command=lambda: self.window.focus_get().event_generate("<<Cut>>"))
        context_menu.add_command(label="Copy", command=lambda: self.window.focus_get().event_generate("<<Copy>>"))
        context_menu.add_command(label="Paste", command=lambda: self.window.focus_get().event_generate("<<Paste>>"))
        self.window.bind("<Button-3>", lambda e: context_menu.post(e.x_root, e.y_root))

    def update_channel_info(self):
        self.channel_info.delete(1.0, tk.END)
        for channel in reversed(self.channels):
            info = "\n".join([f"{k}: {v}" for k, v in channel.items() if v]) + "\n\n"
            self.channel_info.insert(tk.END, info)
        self.channel_count_var.set(f"Channels Added: {len(self.channels)}")

    def on_add_channel(self):
        required_fields = {
            "Channel Name": self.entry_channel_name.get(),
            "Group Title": self.entry_group_title.get(),
            "Channel Link": self.entry_channel_link.get()
        }

        if not all(required_fields.values()):
            messagebox.showerror("Error", "Please fill all required fields")
            return

        if not self.validate_url(self.entry_channel_link.get()):
            messagebox.showerror("Error", "Invalid Channel Link URL")
            return

        if self.license_type_var.get() and not self.entry_license_key.get():
            messagebox.showerror("Error", "License type requires a license key")
            return

        channel = {
            "channel_name": required_fields["Channel Name"],
            "group_title": required_fields["Group Title"],
            "channel_link": required_fields["Channel Link"],
            "tvg_id": self.entry_tvg_id.get(),
            "tvg_name": self.entry_tvg_name.get(),
            "tvg_shift": self.combo_tvg_shift.get(),
            "logo_link": self.entry_logo_link.get(),
            "license_type": self.license_type_var.get(),
            "license_key": self.entry_license_key.get(),
            "manifest_type": self.manifest_type_var.get()
        }
        
        self.channels.append(channel)
        self.update_channel_info()

    def on_clear_fields(self):
        for widget in [self.entry_channel_name, self.entry_group_title, self.entry_channel_link,
                      self.entry_tvg_id, self.entry_tvg_name, self.entry_logo_link,
                      self.entry_license_key]:
            widget.delete(0, tk.END)
        self.combo_tvg_shift.set("")
        self.license_type_var.set("")
        self.manifest_type_var.set("")

    def on_generate_m3u(self):
        if not self.channels:
            messagebox.showwarning("Warning", "No channels to export")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".m3u",
            filetypes=[("M3U files", "*.m3u"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for channel in self.channels:
                    self.write_kodiprops(f, channel)
                    self.write_extinf(f, channel)
                    f.write(f"{channel['channel_link']}\n")
            messagebox.showinfo("Success", "Playlist generated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def write_kodiprops(self, f, channel):
        if channel['license_type'] and channel['license_key']:
            f.write("#KODIPROP:inputstream.adaptive.license_type="
                   f"{channel['license_type']}\n")
            f.write("#KODIPROP:inputstream.adaptive.license_key="
                   f"{channel['license_key']}\n")
        if channel['manifest_type']:
            f.write("#KODIPROP:inputstream.adaptive.manifest_type="
                   f"{channel['manifest_type']}\n")

    def write_extinf(self, f, channel):
        extinf = "#EXTINF:-1 "
        attrs = [
            f'tvg-id="{channel["tvg_id"]}"' if channel['tvg_id'] else None,
            f'tvg-name="{channel["tvg_name"]}"' if channel['tvg_name'] else None,
            f'tvg-shift="{channel["tvg_shift"]}"' if channel['tvg_shift'] else None,
            f'tvg-logo="{channel["logo_link"]}"' if channel['logo_link'] else None,
            f'group-title="{channel["group_title"]}"' if channel['group_title'] else None
        ]
        extinf += " ".join([a for a in attrs if a]) + f",{channel['channel_name']}\n"
        f.write(extinf)

    def open_github(self):
        webbrowser.open("https://github.com/imrsaleh/Easy-M3U-Playlist-Creator")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ChannelManager()
    app.run()
