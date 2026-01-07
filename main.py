import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class CodeMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Context Merger for AI")
        self.root.geometry("1000x700")

        # Configuration for styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", font=('Arial', 11), rowheight=25)
        style.configure("TButton", font=('Arial', 10))
        
        # State variables
        self.selected_dir = ""
        self.tree_items = {} # Map full path -> tree item id

        # --- Top Section: Controls ---
        control_frame = ttk.Frame(root, padding=10)
        control_frame.pack(fill="x")

        # 1. Select Project Folder
        self.btn_browse = ttk.Button(control_frame, text="1. Select Project Folder", command=self.browse_folder)
        self.btn_browse.pack(side="left", padx=5)
        
        self.lbl_path = ttk.Label(control_frame, text="No folder selected", foreground="gray", cursor="hand2")
        self.lbl_path.pack(side="left", padx=5)
        self.lbl_path.bind("<Button-1>", lambda e: self.open_project_folder())

        # 2. Extensions
        # Frame for extensions to keep it organized
        ext_frame = ttk.Frame(control_frame)
        ext_frame.pack(side="right", padx=5)
        
        ttk.Label(ext_frame, text="Ext (e.g. .swift, .py):").pack(side="left", padx=5)
        self.entry_ext = ttk.Entry(ext_frame, width=15)
        self.entry_ext.insert(0, ".swift, .py") # Default value
        self.entry_ext.pack(side="left", padx=5)
        self.entry_ext.bind("<Return>", lambda event: self.scan_files())

        # --- Middle Section: File Tree ---
        # lbl_info = ttk.Label(root, text="Select files/folders to merge (Click to toggle [x]):", font=("Arial", 10, "bold"))
        # lbl_info.pack(anchor="w", padx=10, pady=(5, 0))

        # Main frame with PanedWindow for split view
        self.paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned.pack(fill="both", expand=True, padx=10, pady=5)

        # --- Left Pane: Tree ---
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=1)

        # Scrollbar for tree
        self.vsb = ttk.Scrollbar(left_frame, orient="vertical")
        self.vsb.pack(side="right", fill="y")

        # Treeview
        # Changed selectmode to 'browse' to allow selection for preview
        self.tree = ttk.Treeview(left_frame, selectmode="browse", yscrollcommand=self.vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        self.vsb.config(command=self.tree.yview)
        
        # --- Right Pane: Preview ---
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=1)
        
        lbl_preview = ttk.Label(right_frame, text="Preview", font=("Arial", 10, "bold"))
        lbl_preview.pack(anchor="w", padx=5, pady=(0, 5))
        
        self.preview_text = scrolledtext.ScrolledText(right_frame, wrap=tk.NONE, font=("Consolas", 10))
        self.preview_text.pack(fill="both", expand=True)

        # Bind click event for toggling (existing) and selection for preview (new)
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Bind click event for toggling
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        # Heading
        self.tree.heading("#0", text="Project Structure", anchor="w")
        
        # --- Bottom Section: Generate ---
        bottom_frame = ttk.Frame(root, padding=10)
        bottom_frame.pack(fill="x")

        self.btn_generate = ttk.Button(bottom_frame, text="2. Generate & Merge Code", command=self.generate_output)
        self.btn_generate.pack(fill="x", padx=20, ipady=5)

    def browse_folder(self):
        """Open dialog to select a folder, defaulting to current working directory."""
        # Fix: Show default path
        initial_dir = os.getcwd()
        folder_selected = filedialog.askdirectory(initialdir=initial_dir)
        
        if folder_selected:
            self.selected_dir = folder_selected
            display_text = f"📁 {os.path.basename(self.selected_dir)}  ({self.selected_dir})"
            self.lbl_path.config(text=display_text, foreground="blue")
            self.root.title(f"Code Context Merger - {os.path.basename(self.selected_dir)}")
            
            # Auto-scan on select
            self.scan_files()

    def open_project_folder(self):
        """Open the selected folder in the system file explorer."""
        if self.selected_dir and os.path.exists(self.selected_dir):
            try:
                subprocess.run(["open", self.selected_dir])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {e}")

    def clear_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.tree_items = {}

    def scan_files(self):
        """Scan the selected directory and populate the tree view."""
        if not self.selected_dir:
            messagebox.showwarning("Warning", "Please select a folder first!")
            return
        
        self.clear_tree()
        
        # Get target extensions
        exts_input = self.entry_ext.get()
        target_exts = [e.strip().lower() for e in exts_input.split(',') if e.strip()]
        
        # Walk through the directory
        # We want to display the folder structure.
        # Logic:
        # 1. We always add directories if they contain relevant files (or we can just show all).
        #    "Show tree of folders" implies showing structure.
        #    To keep it clean, maybe we only show folders that match?
        #    Let's show everything but only 'check' matching files by default?
        #    Simpler: Show full structure.
        
        # Insert Root Node (invisible or represented by the folder name)
        # We will insert top-level items directly.
        
        # To handle 'os.walk' which is not strictly depth-first in a way that helps us create parents first easily without a map,
        # we can sort by path length or simply rely on the fact os.walk is top-down.
        
        # Map: path -> item_id
        # Root of the tree corresponds to self.selected_dir
        
        count_files = 0
        
        for root, dirs, files in os.walk(self.selected_dir):
            # Skip hidden folders like .git
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            # Determine parent item
            if root == self.selected_dir:
                parent_id = ""
            else:
                parent_id = self.tree_items.get(root)
                # If for some reason parent doesn't exist (shouldn't happen with walk topdown), skip
                if parent_id is None:
                    continue
            
            # Add current directory subfolders (We actually add folders as we encounter them in 'dirs' loop? 
            # No, os.walk structure: 'root' is current path. 'dirs' and 'files' are children.
            # We iterate children and add them to 'root's tree item.
            
            # Wait, 'root' needs to be in the tree first.
            # If root == selected_dir, its ID is "" (root of treeview).
            # But Treeview root is generic. We probably want a single top node?
            # Or just flat list of top-level folders?
            
            # 'os.walk' yields root. We need to make sure 'root' has an ID.
            # EXCEPT for the very first iteration where root == selected_dir.
            # We don't necessarily need to show the root folder itself as a node, or we can.
            # Let's just list contents of selected_dir as top-level items.
            
            current_dir_id = parent_id # This was set when we processed the *parent* of 'root'.
            
            # But wait, os.walk yields the directories in 'dirs'.
            # We should add the folders in 'dirs' to the tree now, so they exist when os.walk descends into them.
            
            for d in dirs:
                full_path = os.path.join(root, d)
                rel_path = d # Display name
                
                # Checkbox state: defaults to unchecked for folders
                display_text = f"[ ] 📁 {rel_path}"
                
                item_id = self.tree.insert(current_dir_id, "end", text=display_text, open=False, values=(full_path, "folder", "unchecked"))
                self.tree_items[full_path] = item_id

            for f in files:
                if f.startswith('.'): continue
                
                full_path = os.path.join(root, f)
                display_name = f
                
                # Check if matches extension
                is_match = False
                if not target_exts:
                    is_match = True
                else:
                    for ext in target_exts:
                        if f.lower().endswith(ext):
                            is_match = True
                            break
                            
                if not is_match:
                    continue
                            
                # Determine initial state (always checked since we filtered)
                state = "checked"
                box = "[x]"
                
                display_text = f"{box} 📄 {display_name}"
                
                item_id = self.tree.insert(current_dir_id, "end", text=display_text, values=(full_path, "file", state))
                self.tree_items[full_path] = item_id
                
                count_files += 1

        # Post-scan: If we wanted to expand folders containing selected files, we could do that.
        # But for now, keeping them collapsed or auto-expanding top level is fine.
        # Maybe expand root?
        # self.tree.item("", open=True) # doesn't apply to root usually in this way.
        
        if count_files == 0:
            messagebox.showinfo("Scan Info", "No files found matching criteria.")

    def on_tree_click(self, event):
        """Handle click events to toggle checkboxes."""
        region = self.tree.identify("region", event.x, event.y)
        if region == "tree":
            item_id = self.tree.identify_row(event.y)
            if item_id:
                self.toggle_item(item_id)

    def toggle_item(self, item_id):
        """Toggle state of an item and cascade to children."""
        values = self.tree.item(item_id, "values")
        if not values: return
        
        full_path, type_, current_state = values
        
        # Calculate new state
        new_state = "unchecked" if current_state == "checked" else "checked"
        new_box = "[x]" if new_state == "checked" else "[ ]"
        
        # Update text
        original_text = self.tree.item(item_id, "text")
        # Usually text is "[x] 📁 Name". We replace first 3 chars.
        # But just in case, let's reconstruct it.
        # Be careful not to lose the icon/name.
        clean_name = original_text[4:] # assume "[ ] " is 4 chars
        self.tree.item(item_id, text=f"{new_box} {clean_name}")
        
        # Update values
        self.tree.item(item_id, values=(full_path, type_, new_state))
        
        # Cascade if it's a folder
        if type_ == "folder":
            self.cascade_toggle(item_id, new_state)

    def cascade_toggle(self, parent_id, new_state):
        """Recursively toggle all children to match parent state."""
        children = self.tree.get_children(parent_id)
        new_box = "[x]" if new_state == "checked" else "[ ]"
        
        for child in children:
            child_values = self.tree.item(child, "values")
            full_path, type_, _ = child_values
            
            # Update child
            original_text = self.tree.item(child, "text")
            clean_name = original_text[4:]
            self.tree.item(child, text=f"{new_box} {clean_name}", values=(full_path, type_, new_state))
            
            if type_ == "folder":
                self.cascade_toggle(child, new_state)

    def on_tree_select(self, event):
        """Show file content in preview pane when selected."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        item_id = selected_items[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return
            
        full_path, type_, _ = values
        
        self.preview_text.delete(1.0, tk.END)
        
        if type_ == 'file':
            try:
                # Read first 8KB for preview to avoid lag on huge files
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(8192) 
                    if len(content) == 8192: content += "\n\n... (preview truncated) ..."
                    self.preview_text.insert(tk.END, content)
            except Exception as e:
                self.preview_text.insert(tk.END, f"[Error reading file: {e}]")
        else:
             self.preview_text.insert(tk.END, f"[Folder: {os.path.basename(full_path)}]")

    def get_selected_files(self):
        """Traverse tree to find all checked files."""
        selected = []
        
        # We need to iterate all items.
        # Treeview doesn't have a simple "get all" linear method easily, so we walk the dictionary or use recursive.
        # Dictionary self.tree_items has all paths. We can just check their items.
        
        for path, item_id in self.tree_items.items():
            # Check if item still exists (it should)
            if not self.tree.exists(item_id): continue
            
            values = self.tree.item(item_id, "values")
            if not values: continue
            
            path_val, type_, state = values
            if type_ == "file" and state == "checked":
                selected.append(path_val)
                
        return selected

    def generate_output(self):
        selected_files = self.get_selected_files()
        
        if not selected_files:
            messagebox.showinfo("Info", "No files selected.")
            return

        output_text = ""
        for file_path in selected_files:
            rel_path = os.path.relpath(file_path, self.selected_dir)
            
            # Required Format
            output_text += f"// {rel_path}\n\n"
            
            try:
                with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
                    output_text += f.read()
            except Exception as e:
                output_text += f"Error reading file: {e}"
            
            output_text += "\n\n" + ("-"*40) + "\n\n"

        self.show_result_window(output_text)

    def show_result_window(self, content):
        result_window = tk.Toplevel(self.root)
        result_window.title("Merged Output")
        result_window.geometry("800x600")

        # Text Area
        txt_area = scrolledtext.ScrolledText(result_window, wrap=tk.WORD, font=("Consolas", 10))
        txt_area.pack(expand=True, fill='both')
        txt_area.insert(tk.END, content)

        # Button Frame for actions
        btn_frame = ttk.Frame(result_window)
        btn_frame.pack(fill="x", pady=5, padx=10)

        # Copy Button
        btn_copy = ttk.Button(btn_frame, text="Copy to Clipboard", command=lambda: self.copy_to_clipboard(result_window, content))
        btn_copy.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Export Button
        btn_export = ttk.Button(btn_frame, text="Export as .txt", command=lambda: self.export_as_txt(content))
        btn_export.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def copy_to_clipboard(self, window, content):
        window.clipboard_clear()
        window.clipboard_append(content)
        messagebox.showinfo("Success", "Copied to clipboard!")

    def export_as_txt(self, content):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Merged Output"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeMergerApp(root)
    root.mainloop()