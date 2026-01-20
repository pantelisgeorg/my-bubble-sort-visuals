"""
Algorithm Visualizer
====================
A comprehensive algorithm visualization tool using Tkinter and Matplotlib.
Run this file in VSCode, PyCharm, or any Python environment.

Requirements:
    pip install matplotlib numpy

Usage:
    python algorithm_visualizer.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
from typing import List, Callable, Generator
import colorsys

# Check for matplotlib
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not installed. Using basic visualization.")
    print("Install with: pip install matplotlib")


class AlgorithmVisualizer:
    """Main Algorithm Visualizer Application"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🔬 Algorithm Visualizer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a2e")
        
        # State variables
        self.array: List[int] = []
        self.array_size = 50
        self.speed = 50  # milliseconds delay
        self.is_running = False
        self.is_paused = False
        self.is_step_mode = False
        self.step_requested = False
        self.current_step_line = 0
        self.comparisons = 0
        self.swaps = 0
        self.current_algorithm = "Bubble Sort"
        
        # Colors
        self.colors = {
            'default': '#4361ee',
            'comparing': '#ff6b6b',
            'swapping': '#ffd93d',
            'sorted': '#6bcb77',
            'pivot': '#9b59b6',
            'minimum': '#e74c3c',
            'background': '#1a1a2e',
            'panel': '#16213e',
            'text': '#eaeaea',
            'accent': '#0f3460'
        }
        
        self.setup_ui()
        self.generate_array()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top control panel
        self.setup_control_panel(main_frame)
        
        # Content area with visualization and code tracer
        content_frame = tk.Frame(main_frame, bg=self.colors['background'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left side: Visualization area
        viz_container = tk.Frame(content_frame, bg=self.colors['background'])
        viz_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.setup_visualization_area(viz_container)
        
        # Right side: Code tracer
        tracer_container = tk.Frame(content_frame, bg=self.colors['panel'], width=350)
        tracer_container.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        tracer_container.pack_propagate(False)
        
        self.setup_code_tracer(tracer_container)
        
        # Stats panel
        self.setup_stats_panel(main_frame)
        
        # Algorithm info panel
        self.setup_info_panel(main_frame)
        
    def setup_control_panel(self, parent):
        """Setup control buttons and sliders"""
        control_frame = tk.Frame(parent, bg=self.colors['panel'], pady=15, padx=20)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(
            control_frame, 
            text="🔬 Algorithm Visualizer",
            font=("Helvetica", 24, "bold"),
            bg=self.colors['panel'],
            fg=self.colors['text']
        )
        title_label.pack(side=tk.LEFT, padx=(0, 40))
        
        # Algorithm selector
        algo_frame = tk.Frame(control_frame, bg=self.colors['panel'])
        algo_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            algo_frame, 
            text="Algorithm:",
            font=("Helvetica", 11),
            bg=self.colors['panel'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        self.algo_var = tk.StringVar(value="Bubble Sort")
        algorithms = [
            "Bubble Sort", "Selection Sort", "Insertion Sort",
            "Merge Sort", "Quick Sort", "Heap Sort",
            "Counting Sort", "Radix Sort", "Shell Sort"
        ]
        
        self.algo_dropdown = ttk.Combobox(
            algo_frame, 
            textvariable=self.algo_var,
            values=algorithms,
            state="readonly",
            width=15,
            font=("Helvetica", 10)
        )
        self.algo_dropdown.pack(side=tk.LEFT, padx=(5, 0))
        self.algo_dropdown.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        
        # Size slider
        size_frame = tk.Frame(control_frame, bg=self.colors['panel'])
        size_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(
            size_frame, 
            text="Array Size:",
            font=("Helvetica", 11),
            bg=self.colors['panel'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        self.size_var = tk.IntVar(value=50)
        self.size_slider = ttk.Scale(
            size_frame,
            from_=10,
            to=200,
            variable=self.size_var,
            orient=tk.HORIZONTAL,
            length=120,
            command=self.on_size_change
        )
        self.size_slider.pack(side=tk.LEFT, padx=5)
        
        self.size_label = tk.Label(
            size_frame, 
            text="50",
            font=("Helvetica", 11, "bold"),
            bg=self.colors['panel'],
            fg=self.colors['accent'],
            width=4
        )
        self.size_label.pack(side=tk.LEFT)
        
        # Speed slider
        speed_frame = tk.Frame(control_frame, bg=self.colors['panel'])
        speed_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(
            speed_frame, 
            text="Speed:",
            font=("Helvetica", 11),
            bg=self.colors['panel'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        self.speed_var = tk.IntVar(value=50)
        self.speed_slider = ttk.Scale(
            speed_frame,
            from_=1,
            to=100,
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            length=120,
            command=self.on_speed_change
        )
        self.speed_slider.pack(side=tk.LEFT, padx=5)
        
        self.speed_label = tk.Label(
            speed_frame, 
            text="Medium",
            font=("Helvetica", 11, "bold"),
            bg=self.colors['panel'],
            fg=self.colors['accent'],
            width=8
        )
        self.speed_label.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg=self.colors['panel'])
        button_frame.pack(side=tk.RIGHT)
        
        button_style = {
            'font': ("Helvetica", 11, "bold"),
            'width': 10,
            'height': 1,
            'bd': 0,
            'cursor': 'hand2'
        }
        
        self.generate_btn = tk.Button(
            button_frame,
            text="🔄 Generate",
            command=self.generate_array,
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            **button_style
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶️ Start",
            command=self.start_sorting,
            bg="#27ae60",
            fg="white",
            activebackground="#1e8449",
            **button_style
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = tk.Button(
            button_frame,
            text="⏸️ Pause",
            command=self.toggle_pause,
            bg="#f39c12",
            fg="white",
            activebackground="#d68910",
            state=tk.DISABLED,
            **button_style
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self.stop_sorting,
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            state=tk.DISABLED,
            **button_style
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.step_btn = tk.Button(
            button_frame,
            text="⏭️ Step",
            command=self.step_once,
            bg="#9b59b6",
            fg="white",
            activebackground="#8e44ad",
            **button_style
        )
        self.step_btn.pack(side=tk.LEFT, padx=5)
        
        # Custom array input button
        self.import_btn = tk.Button(
            button_frame,
            text="📥 Import",
            command=self.import_custom_array,
            bg="#1abc9c",
            fg="white",
            activebackground="#16a085",
            **button_style
        )
        self.import_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_visualization_area(self, parent):
        """Setup the main visualization canvas"""
        viz_frame = tk.Frame(parent, bg=self.colors['panel'], padx=10, pady=10)
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.canvas = tk.Canvas(
            viz_frame,
            bg=self.colors['background'],
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind resize event
        self.canvas.bind("<Configure>", self.on_resize)
        
    def setup_stats_panel(self, parent):
        """Setup statistics display panel"""
        stats_frame = tk.Frame(parent, bg=self.colors['panel'], pady=10, padx=20)
        stats_frame.pack(fill=tk.X, pady=5)
        
        # Stats labels
        stat_style = {
            'font': ("Helvetica", 12),
            'bg': self.colors['panel'],
            'fg': self.colors['text']
        }
        
        value_style = {
            'font': ("Helvetica", 14, "bold"),
            'bg': self.colors['panel'],
            'fg': "#4361ee"
        }
        
        # Comparisons
        tk.Label(stats_frame, text="Comparisons:", **stat_style).pack(side=tk.LEFT)
        self.comparisons_label = tk.Label(stats_frame, text="0", **value_style)
        self.comparisons_label.pack(side=tk.LEFT, padx=(5, 30))
        
        # Swaps
        tk.Label(stats_frame, text="Swaps/Writes:", **stat_style).pack(side=tk.LEFT)
        self.swaps_label = tk.Label(stats_frame, text="0", **value_style)
        self.swaps_label.pack(side=tk.LEFT, padx=(5, 30))
        
        # Time complexity
        tk.Label(stats_frame, text="Time Complexity:", **stat_style).pack(side=tk.LEFT)
        self.complexity_label = tk.Label(stats_frame, text="O(n²)", **value_style)
        self.complexity_label.pack(side=tk.LEFT, padx=(5, 30))
        
        # Space complexity
        tk.Label(stats_frame, text="Space Complexity:", **stat_style).pack(side=tk.LEFT)
        self.space_label = tk.Label(stats_frame, text="O(1)", **value_style)
        self.space_label.pack(side=tk.LEFT)
        
        # Status
        self.status_label = tk.Label(
            stats_frame, 
            text="Ready",
            font=("Helvetica", 12, "bold"),
            bg=self.colors['panel'],
            fg="#27ae60"
        )
        self.status_label.pack(side=tk.RIGHT)
        
    def setup_info_panel(self, parent):
        """Setup algorithm information panel"""
        info_frame = tk.Frame(parent, bg=self.colors['panel'], pady=10, padx=20)
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.info_text = tk.Text(
            info_frame,
            height=3,
            font=("Helvetica", 10),
            bg=self.colors['background'],
            fg=self.colors['text'],
            wrap=tk.WORD,
            bd=0,
            padx=10,
            pady=10
        )
        self.info_text.pack(fill=tk.X)
        self.info_text.config(state=tk.DISABLED)
        self.update_algorithm_info()
        
    def setup_code_tracer(self, parent):
        """Setup code tracer panel"""
        tracer_frame = tk.Frame(parent, bg=self.colors['panel'], pady=10, padx=20)
        tracer_frame.pack(fill=tk.X, pady=(5, 0))
        
        tracer_label = tk.Label(
            tracer_frame,
            text="📝 Code Tracer",
            font=("Helvetica", 12, "bold"),
            bg=self.colors['panel'],
            fg=self.colors['text']
        )
        tracer_label.pack(anchor=tk.W)
        
        self.code_tracer = tk.Text(
            tracer_frame,
            height=12,
            font=("Courier", 10),
            bg="#0d1117",
            fg="#c9d1d9",
            wrap=tk.NONE,
            bd=0,
            padx=10,
            pady=10
        )
        self.code_tracer.pack(fill=tk.X, pady=(5, 0))
        
        # Configure tags for highlighting
        self.code_tracer.tag_configure("current_line", background="#1f6feb", foreground="#ffffff")
        self.code_tracer.tag_configure("executed", foreground="#7ee787")
        self.code_tracer.tag_configure("keyword", foreground="#ff7b72")
        self.code_tracer.tag_configure("comment", foreground="#8b949e")
        self.code_tracer.tag_configure("variable", foreground="#79c0ff")
        
        self.code_tracer.config(state=tk.DISABLED)
        self.update_code_tracer()
        
    def generate_array(self):
        """Generate a new random array"""
        if self.is_running:
            return
            
        self.array_size = self.size_var.get()
        self.array = [random.randint(5, 100) for _ in range(self.array_size)]
        self.comparisons = 0
        self.swaps = 0
        self.update_stats()
        self.draw_array()
        self.status_label.config(text="Ready", fg="#27ae60")
        
    def draw_array(self, color_map: dict = None):
        """Draw the array visualization"""
        self.canvas.delete("all")
        
        if not self.array:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            return
            
        # Calculate bar dimensions
        bar_width = max(2, (canvas_width - 20) / len(self.array))
        max_val = max(self.array)
        
        for i, val in enumerate(self.array):
            # Calculate bar position and height
            x1 = 10 + i * bar_width
            x2 = x1 + bar_width - 1
            bar_height = (val / max_val) * (canvas_height - 40)
            y1 = canvas_height - 20 - bar_height
            y2 = canvas_height - 20
            
            # Determine color
            if color_map and i in color_map:
                color = color_map[i]
            else:
                # Generate gradient color based on value
                hue = 0.55 + (val / max_val) * 0.15  # Blue to cyan gradient
                r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
                color = f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'
            
            # Draw bar
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline=self.colors['background']
            )
            
    def update_stats(self):
        """Update statistics labels"""
        self.comparisons_label.config(text=str(self.comparisons))
        self.swaps_label.config(text=str(self.swaps))
        
    def on_resize(self, event):
        """Handle canvas resize"""
        self.draw_array()
        
    def on_size_change(self, val):
        """Handle array size slider change"""
        size = int(float(val))
        self.size_label.config(text=str(size))
        if not self.is_running:
            self.generate_array()
            
    def on_speed_change(self, val):
        """Handle speed slider change"""
        speed = int(float(val))
        self.speed = max(1, 101 - speed)  # Invert so higher = faster
        
        if speed < 33:
            label = "Slow"
        elif speed < 66:
            label = "Medium"
        else:
            label = "Fast"
        self.speed_label.config(text=label)
        
    def on_algorithm_change(self, event):
        """Handle algorithm selection change"""
        self.current_algorithm = self.algo_var.get()
        self.update_algorithm_info()
        self.update_code_tracer()
        
    def update_algorithm_info(self):
        """Update algorithm information display"""
        info = {
            "Bubble Sort": {
                "desc": "Repeatedly steps through the list, compares adjacent elements and swaps them if they're in wrong order. Simple but inefficient for large datasets.",
                "time": "O(n²)",
                "space": "O(1)"
            },
            "Selection Sort": {
                "desc": "Finds the minimum element and places it at the beginning. Then repeats for the remaining unsorted portion.",
                "time": "O(n²)",
                "space": "O(1)"
            },
            "Insertion Sort": {
                "desc": "Builds the sorted array one item at a time by inserting each element into its correct position. Efficient for small or nearly sorted data.",
                "time": "O(n²)",
                "space": "O(1)"
            },
            "Merge Sort": {
                "desc": "Divides the array into halves, recursively sorts them, then merges the sorted halves. Guaranteed O(n log n) but requires extra space.",
                "time": "O(n log n)",
                "space": "O(n)"
            },
            "Quick Sort": {
                "desc": "Selects a pivot and partitions elements around it. Elements smaller go left, larger go right. Very efficient in practice.",
                "time": "O(n log n)",
                "space": "O(log n)"
            },
            "Heap Sort": {
                "desc": "Builds a max heap and repeatedly extracts the maximum element. Guaranteed O(n log n) with O(1) space.",
                "time": "O(n log n)",
                "space": "O(1)"
            },
            "Counting Sort": {
                "desc": "Counts occurrences of each value and uses this to place elements directly. Very fast for integers with limited range.",
                "time": "O(n + k)",
                "space": "O(k)"
            },
            "Radix Sort": {
                "desc": "Sorts numbers digit by digit, starting from the least significant. Efficient for integers with bounded digits.",
                "time": "O(d × n)",
                "space": "O(n + k)"
            },
            "Shell Sort": {
                "desc": "Generalization of insertion sort that allows exchange of far apart elements. Uses gap sequences for efficiency.",
                "time": "O(n log n)",
                "space": "O(1)"
            }
        }
        
        algo_info = info.get(self.current_algorithm, info["Bubble Sort"])
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, f"📌 {self.current_algorithm}: {algo_info['desc']}")
        self.info_text.config(state=tk.DISABLED)
        
        self.complexity_label.config(text=algo_info['time'])
        self.space_label.config(text=algo_info['space'])
        
    def start_sorting(self):
        """Start the sorting visualization"""
        if self.is_running:
            return
            
        self.is_running = True
        self.is_paused = False
        self.comparisons = 0
        self.swaps = 0
        
        # Update button states
        self.start_btn.config(state=tk.DISABLED)
        self.generate_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.algo_dropdown.config(state=tk.DISABLED)
        self.size_slider.config(state=tk.DISABLED)
        
        self.status_label.config(text="Sorting...", fg="#f39c12")
        
        # Start sorting in a separate thread
        thread = threading.Thread(target=self.run_algorithm)
        thread.daemon = True
        thread.start()
        
    def run_algorithm(self):
        """Run the selected algorithm"""
        algorithms = {
            "Bubble Sort": self.bubble_sort,
            "Selection Sort": self.selection_sort,
            "Insertion Sort": self.insertion_sort,
            "Merge Sort": lambda: self.merge_sort(0, len(self.array) - 1),
            "Quick Sort": lambda: self.quick_sort(0, len(self.array) - 1),
            "Heap Sort": self.heap_sort,
            "Counting Sort": self.counting_sort,
            "Radix Sort": self.radix_sort,
            "Shell Sort": self.shell_sort
        }
        
        try:
            algorithms[self.current_algorithm]()
            
            if self.is_running:
                # Show completion animation
                self.completion_animation()
                self.root.after(0, lambda: self.status_label.config(
                    text="Completed!", fg="#27ae60"
                ))
        except Exception as e:
            print(f"Error during sorting: {e}")
        finally:
            self.is_running = False
            self.root.after(0, self.reset_buttons)
            
    def completion_animation(self):
        """Show completion animation"""
        for i in range(len(self.array)):
            if not self.is_running:
                break
            color_map = {j: self.colors['sorted'] for j in range(i + 1)}
            self.root.after(0, lambda cm=color_map: self.draw_array(cm))
            time.sleep(0.01)
            
    def reset_buttons(self):
        """Reset button states"""
        self.start_btn.config(state=tk.NORMAL)
        self.generate_btn.config(state=tk.NORMAL)
        self.import_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸️ Pause")
        self.stop_btn.config(state=tk.DISABLED)
        self.algo_dropdown.config(state="readonly")
        self.size_slider.config(state=tk.NORMAL)
        self.is_step_mode = False
        self.step_requested = False
        
    def toggle_pause(self):
        """Toggle pause state"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="▶️ Resume")
            self.status_label.config(text="Paused", fg="#9b59b6")
            self.step_btn.config(state=tk.NORMAL)
            self.is_step_mode = True
        else:
            self.pause_btn.config(text="⏸️ Pause")
            self.status_label.config(text="Sorting...", fg="#f39c12")
            self.step_btn.config(state=tk.DISABLED)
            self.is_step_mode = False
            
    def step_once(self):
        """Execute one step in step mode"""
        if self.is_running and self.is_paused:
            self.step_requested = True
        elif not self.is_running:
            # Start in step mode if not running
            self.start_step_mode()
            
    def start_step_mode(self):
        """Start sorting in step-by-step mode"""
        if self.is_running:
            return
            
        self.is_running = True
        self.is_paused = True
        self.is_step_mode = True
        self.step_requested = True  # Execute first step immediately
        self.comparisons = 0
        self.swaps = 0
        
        # Update button states
        self.start_btn.config(state=tk.DISABLED)
        self.generate_btn.config(state=tk.DISABLED)
        self.import_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text="▶️ Resume")
        self.stop_btn.config(state=tk.NORMAL)
        self.algo_dropdown.config(state=tk.DISABLED)
        self.size_slider.config(state=tk.DISABLED)
        
        self.status_label.config(text="Step Mode", fg="#9b59b6")
        
        # Start sorting in a separate thread
        thread = threading.Thread(target=self.run_algorithm)
        thread.daemon = True
        thread.start()
            
    def stop_sorting(self):
        """Stop the sorting process"""
        self.is_running = False
        self.is_paused = False
        self.is_step_mode = False
        self.step_requested = False
        self.status_label.config(text="Stopped", fg="#e74c3c")
        
    def import_custom_array(self):
        """Open dialog to import custom numbers"""
        if self.is_running:
            return
            
        dialog = tk.Toplevel(self.root)
        dialog.title("Import Custom Array")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors['panel'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_reqwidth()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_reqheight()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Instructions
        tk.Label(
            dialog,
            text="Enter numbers separated by commas or spaces:",
            font=("Helvetica", 11),
            bg=self.colors['panel'],
            fg=self.colors['text']
        ).pack(pady=(20, 10))
        
        # Text entry
        entry_frame = tk.Frame(dialog, bg=self.colors['panel'])
        entry_frame.pack(fill=tk.X, padx=20)
        
        self.custom_entry = tk.Text(
            entry_frame,
            height=4,
            font=("Courier", 11),
            bg="#0d1117",
            fg="#c9d1d9",
            insertbackground="#c9d1d9",
            wrap=tk.WORD
        )
        self.custom_entry.pack(fill=tk.X)
        self.custom_entry.insert(tk.END, "64, 34, 25, 12, 22, 11, 90, 45, 33, 78")
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=self.colors['panel'])
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Import",
            command=lambda: self.process_custom_array(dialog),
            bg="#27ae60",
            fg="white",
            font=("Helvetica", 10, "bold"),
            width=10,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#e74c3c",
            fg="white",
            font=("Helvetica", 10, "bold"),
            width=10,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)
        
    def process_custom_array(self, dialog):
        """Process the custom array input"""
        text = self.custom_entry.get("1.0", tk.END).strip()
        
        # Parse numbers - support comma, space, or mixed separators
        text = text.replace(",", " ")
        parts = text.split()
        
        try:
            numbers = []
            for part in parts:
                num = int(part.strip())
                if num < 1:
                    raise ValueError("Numbers must be positive")
                if num > 1000:
                    num = 1000  # Cap at 1000 for visualization
                numbers.append(num)
                
            if len(numbers) < 2:
                raise ValueError("Need at least 2 numbers")
            if len(numbers) > 200:
                numbers = numbers[:200]  # Limit to 200 elements
                
            self.array = numbers
            self.array_size = len(numbers)
            self.size_var.set(len(numbers))
            self.size_label.config(text=str(len(numbers)))
            self.comparisons = 0
            self.swaps = 0
            self.update_stats()
            self.draw_array()
            self.status_label.config(text="Array Imported", fg="#1abc9c")
            dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror(
                "Invalid Input",
                f"Please enter valid positive integers.\n\nExample: 64, 34, 25, 12, 22, 11, 90",
                parent=dialog
            )
        
    def visualize_step(self, color_map: dict = None, line_number: int = 0):
        """Visualize current step with delay"""
        # Handle step mode
        if self.is_step_mode and self.is_paused:
            self.step_requested = False
            while not self.step_requested and self.is_paused and self.is_running:
                time.sleep(0.05)
            if not self.is_running:
                return False
                
        # Handle normal pause
        while self.is_paused and self.is_running and not self.is_step_mode:
            time.sleep(0.1)
            
        if not self.is_running:
            return False
        
        # Update code tracer highlighting
        self.current_step_line = line_number
        self.root.after(0, self.highlight_code_line)
            
        self.root.after(0, lambda: self.draw_array(color_map))
        self.root.after(0, self.update_stats)
        time.sleep(self.speed / 1000)
        return True
    
    def highlight_code_line(self):
        """Highlight the current line in code tracer"""
        self.code_tracer.config(state=tk.NORMAL)
        self.code_tracer.tag_remove("current_line", "1.0", tk.END)
        
        if self.current_step_line > 0:
            line_start = f"{self.current_step_line}.0"
            line_end = f"{self.current_step_line}.end"
            self.code_tracer.tag_add("current_line", line_start, line_end)
            self.code_tracer.see(line_start)
            
        self.code_tracer.config(state=tk.DISABLED)
        
    def update_code_tracer(self):
        """Update the code tracer with algorithm pseudocode"""
        pseudocode = self.get_algorithm_pseudocode()
        
        self.code_tracer.config(state=tk.NORMAL)
        self.code_tracer.delete(1.0, tk.END)
        self.code_tracer.insert(tk.END, pseudocode)
        self.code_tracer.config(state=tk.DISABLED)
        
    def get_algorithm_pseudocode(self) -> str:
        """Get pseudocode for the current algorithm"""
        pseudocodes = {
            "Bubble Sort": """1  # Bubble Sort Algorithm
2  def bubble_sort(array):
3      n = len(array)
4      for i in range(n):
5          swapped = False
6          for j in range(0, n-i-1):
7              if array[j] > array[j+1]:  # Compare
8                  swap(array[j], array[j+1])
9                  swapped = True
10         if not swapped:
11             break  # Array is sorted""",
            
            "Selection Sort": """1  # Selection Sort Algorithm
2  def selection_sort(array):
3      n = len(array)
4      for i in range(n):
5          min_idx = i
6          for j in range(i+1, n):
7              if array[j] < array[min_idx]:  # Compare
8                  min_idx = j
9          swap(array[i], array[min_idx])""",
            
            "Insertion Sort": """1  # Insertion Sort Algorithm
2  def insertion_sort(array):
3      for i in range(1, len(array)):
4          key = array[i]
5          j = i - 1
6          while j >= 0 and array[j] > key:  # Compare
7              array[j+1] = array[j]  # Shift
8              j -= 1
9          array[j+1] = key  # Insert""",
            
            "Merge Sort": """1  # Merge Sort Algorithm
2  def merge_sort(array, left, right):
3      if left < right:
4          mid = (left + right) // 2
5          merge_sort(array, left, mid)
6          merge_sort(array, mid+1, right)
7          merge(array, left, mid, right)
8  
9  def merge(left_arr, right_arr):
10     while elements remain:
11         if left[i] <= right[j]:  # Compare
12             result[k] = left[i]
13         else:
14             result[k] = right[j]""",
            
            "Quick Sort": """1  # Quick Sort Algorithm
2  def quick_sort(array, low, high):
3      if low < high:
4          pivot_idx = partition(low, high)
5          quick_sort(array, low, pivot_idx-1)
6          quick_sort(array, pivot_idx+1, high)
7  
8  def partition(array, low, high):
9      pivot = array[high]
10     for j in range(low, high):
11         if array[j] <= pivot:  # Compare
12             swap(array[i], array[j])
13     swap(array[i+1], array[high])
14     return i + 1""",
            
            "Heap Sort": """1  # Heap Sort Algorithm
2  def heap_sort(array):
3      n = len(array)
4      for i in range(n//2-1, -1, -1):
5          heapify(array, n, i)  # Build heap
6      for i in range(n-1, 0, -1):
7          swap(array[0], array[i])  # Extract max
8          heapify(array, i, 0)
9  
10 def heapify(array, n, i):
11     largest = i
12     if left > array[largest]:  # Compare left
13         largest = left
14     if right > array[largest]:  # Compare right
15         largest = right
16     if largest != i:
17         swap and recurse""",
            
            "Counting Sort": """1  # Counting Sort Algorithm
2  def counting_sort(array):
3      max_val = max(array)
4      count = [0] * (max_val + 1)
5      for val in array:
6          count[val] += 1  # Count occurrences
7      idx = 0
8      for val in range(len(count)):
9          while count[val] > 0:
10             array[idx] = val  # Place element
11             count[val] -= 1
12             idx += 1""",
            
            "Radix Sort": """1  # Radix Sort Algorithm
2  def radix_sort(array):
3      max_val = max(array)
4      exp = 1
5      while max_val // exp > 0:
6          counting_sort_by_digit(exp)
7          exp *= 10
8  
9  def counting_sort_by_digit(exp):
10     for i in range(n):
11         digit = (array[i] // exp) % 10
12     for i in range(n):
13         output[count[digit]-1] = array[i]""",
            
            "Shell Sort": """1  # Shell Sort Algorithm
2  def shell_sort(array):
3      n = len(array)
4      gap = n // 2
5      while gap > 0:
6          for i in range(gap, n):
7              temp = array[i]
8              j = i
9              while j >= gap and array[j-gap] > temp:
10                 array[j] = array[j-gap]  # Shift
11                 j -= gap
12             array[j] = temp  # Insert
13         gap //= 2"""
        }
        
        return pseudocodes.get(self.current_algorithm, pseudocodes["Bubble Sort"])
        
    # ==================== SORTING ALGORITHMS ====================
    
    def bubble_sort(self):
        """Bubble Sort implementation"""
        n = len(self.array)
        for i in range(n):
            if not self.visualize_step({}, line_number=4):
                return
            swapped = False
            for j in range(0, n - i - 1):
                self.comparisons += 1
                
                color_map = {
                    j: self.colors['comparing'],
                    j + 1: self.colors['comparing']
                }
                # Mark sorted portion
                for k in range(n - i, n):
                    color_map[k] = self.colors['sorted']
                    
                if not self.visualize_step(color_map, line_number=7):
                    return
                    
                if self.array[j] > self.array[j + 1]:
                    self.array[j], self.array[j + 1] = self.array[j + 1], self.array[j]
                    self.swaps += 1
                    swapped = True
                    
                    color_map[j] = self.colors['swapping']
                    color_map[j + 1] = self.colors['swapping']
                    if not self.visualize_step(color_map, line_number=8):
                        return
                        
            if not swapped:
                if not self.visualize_step({}, line_number=11):
                    return
                break
                
    def selection_sort(self):
        """Selection Sort implementation"""
        n = len(self.array)
        for i in range(n):
            if not self.visualize_step({}, line_number=4):
                return
            min_idx = i
            
            for j in range(i + 1, n):
                self.comparisons += 1
                
                color_map = {
                    i: self.colors['swapping'],
                    min_idx: self.colors['minimum'],
                    j: self.colors['comparing']
                }
                for k in range(i):
                    color_map[k] = self.colors['sorted']
                    
                if not self.visualize_step(color_map, line_number=7):
                    return
                    
                if self.array[j] < self.array[min_idx]:
                    min_idx = j
                    if not self.visualize_step(color_map, line_number=8):
                        return
                    
            if min_idx != i:
                self.array[i], self.array[min_idx] = self.array[min_idx], self.array[i]
                self.swaps += 1
                color_map = {i: self.colors['swapping'], min_idx: self.colors['swapping']}
                for k in range(i):
                    color_map[k] = self.colors['sorted']
                if not self.visualize_step(color_map, line_number=9):
                    return
                
    def insertion_sort(self):
        """Insertion Sort implementation"""
        for i in range(1, len(self.array)):
            if not self.visualize_step({i: self.colors['comparing']}, line_number=3):
                return
            key = self.array[i]
            j = i - 1
            
            while j >= 0 and self.array[j] > key:
                self.comparisons += 1
                
                color_map = {
                    j: self.colors['comparing'],
                    j + 1: self.colors['swapping']
                }
                for k in range(j):
                    if k < i:
                        color_map[k] = self.colors['sorted']
                        
                if not self.visualize_step(color_map, line_number=6):
                    return
                    
                self.array[j + 1] = self.array[j]
                self.swaps += 1
                
                if not self.visualize_step(color_map, line_number=7):
                    return
                j -= 1
                
            self.array[j + 1] = key
            color_map = {j + 1: self.colors['sorted']}
            for k in range(j + 1):
                color_map[k] = self.colors['sorted']
            if not self.visualize_step(color_map, line_number=9):
                return
            
    def merge_sort(self, left: int, right: int):
        """Merge Sort implementation"""
        if left < right and self.is_running:
            mid = (left + right) // 2
            
            self.merge_sort(left, mid)
            self.merge_sort(mid + 1, right)
            self.merge(left, mid, right)
            
    def merge(self, left: int, mid: int, right: int):
        """Merge helper for merge sort"""
        left_arr = self.array[left:mid + 1]
        right_arr = self.array[mid + 1:right + 1]
        
        i = j = 0
        k = left
        
        while i < len(left_arr) and j < len(right_arr) and self.is_running:
            self.comparisons += 1
            
            color_map = {k: self.colors['swapping']}
            if not self.visualize_step(color_map, line_number=11):
                return
                
            if left_arr[i] <= right_arr[j]:
                self.array[k] = left_arr[i]
                i += 1
                if not self.visualize_step({k: self.colors['sorted']}, line_number=12):
                    return
            else:
                self.array[k] = right_arr[j]
                j += 1
                if not self.visualize_step({k: self.colors['sorted']}, line_number=14):
                    return
            self.swaps += 1
            k += 1
            
        while i < len(left_arr) and self.is_running:
            self.array[k] = left_arr[i]
            self.swaps += 1
            i += 1
            k += 1
            if not self.visualize_step({k - 1: self.colors['swapping']}, line_number=12):
                return
                
        while j < len(right_arr) and self.is_running:
            self.array[k] = right_arr[j]
            self.swaps += 1
            j += 1
            k += 1
            if not self.visualize_step({k - 1: self.colors['swapping']}, line_number=14):
                return
                
    def quick_sort(self, low: int, high: int):
        """Quick Sort implementation"""
        if low < high and self.is_running:
            pivot_idx = self.partition(low, high)
            if pivot_idx is not None:
                self.quick_sort(low, pivot_idx - 1)
                self.quick_sort(pivot_idx + 1, high)
                
    def partition(self, low: int, high: int) -> int:
        """Partition helper for quick sort"""
        pivot = self.array[high]
        i = low - 1
        
        if not self.visualize_step({high: self.colors['pivot']}, line_number=9):
            return None
        
        for j in range(low, high):
            self.comparisons += 1
            
            color_map = {
                high: self.colors['pivot'],
                j: self.colors['comparing']
            }
            if i >= low:
                color_map[i] = self.colors['swapping']
                
            if not self.visualize_step(color_map, line_number=11):
                return None
                
            if self.array[j] <= pivot:
                i += 1
                self.array[i], self.array[j] = self.array[j], self.array[i]
                self.swaps += 1
                if not self.visualize_step({i: self.colors['swapping'], j: self.colors['swapping']}, line_number=12):
                    return None
                
        self.array[i + 1], self.array[high] = self.array[high], self.array[i + 1]
        self.swaps += 1
        if not self.visualize_step({i + 1: self.colors['pivot']}, line_number=13):
            return None
        
        return i + 1
        
    def heap_sort(self):
        """Heap Sort implementation"""
        n = len(self.array)
        
        # Build max heap
        if not self.visualize_step({}, line_number=4):
            return
        for i in range(n // 2 - 1, -1, -1):
            self.heapify(n, i)
            
        # Extract elements
        for i in range(n - 1, 0, -1):
            if not self.is_running:
                return
                
            self.array[0], self.array[i] = self.array[i], self.array[0]
            self.swaps += 1
            
            color_map = {0: self.colors['swapping'], i: self.colors['sorted']}
            for j in range(i + 1, n):
                color_map[j] = self.colors['sorted']
            if not self.visualize_step(color_map, line_number=7):
                return
                
            self.heapify(i, 0)
            
    def heapify(self, n: int, i: int):
        """Heapify helper for heap sort"""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n:
            self.comparisons += 1
            color_map = {i: self.colors['comparing'], left: self.colors['comparing']}
            self.visualize_step(color_map, line_number=12)
            if self.array[left] > self.array[largest]:
                largest = left
                
        if right < n:
            self.comparisons += 1
            color_map = {i: self.colors['comparing'], right: self.colors['comparing']}
            self.visualize_step(color_map, line_number=14)
            if self.array[right] > self.array[largest]:
                largest = right
                
        if largest != i:
            self.array[i], self.array[largest] = self.array[largest], self.array[i]
            self.swaps += 1
            
            color_map = {i: self.colors['swapping'], largest: self.colors['swapping']}
            self.visualize_step(color_map, line_number=17)
            
            self.heapify(n, largest)
            
    def counting_sort(self):
        """Counting Sort implementation"""
        if not self.array:
            return
            
        max_val = max(self.array)
        count = [0] * (max_val + 1)
        
        # Count occurrences
        if not self.visualize_step({}, line_number=5):
            return
        for val in self.array:
            count[val] += 1
            self.comparisons += 1
            
        # Rebuild array
        idx = 0
        for val in range(len(count)):
            while count[val] > 0 and self.is_running:
                self.array[idx] = val
                self.swaps += 1
                count[val] -= 1
                
                color_map = {idx: self.colors['swapping']}
                for i in range(idx):
                    color_map[i] = self.colors['sorted']
                if not self.visualize_step(color_map, line_number=10):
                    return
                    
                idx += 1
                
    def radix_sort(self):
        """Radix Sort implementation"""
        if not self.array:
            return
            
        max_val = max(self.array)
        exp = 1
        
        while max_val // exp > 0 and self.is_running:
            self.counting_sort_by_digit(exp)
            exp *= 10
            
    def counting_sort_by_digit(self, exp: int):
        """Counting sort by digit helper for radix sort"""
        n = len(self.array)
        output = [0] * n
        count = [0] * 10
        
        for i in range(n):
            idx = (self.array[i] // exp) % 10
            count[idx] += 1
            self.comparisons += 1
            if not self.visualize_step({i: self.colors['comparing']}, line_number=11):
                return
            
        for i in range(1, 10):
            count[i] += count[i - 1]
            
        for i in range(n - 1, -1, -1):
            idx = (self.array[i] // exp) % 10
            output[count[idx] - 1] = self.array[i]
            count[idx] -= 1
            self.swaps += 1
            
        for i in range(n):
            if not self.is_running:
                return
            self.array[i] = output[i]
            
            color_map = {i: self.colors['swapping']}
            if not self.visualize_step(color_map, line_number=13):
                return
                
    def shell_sort(self):
        """Shell Sort implementation"""
        n = len(self.array)
        gap = n // 2
        
        while gap > 0 and self.is_running:
            if not self.visualize_step({}, line_number=5):
                return
            for i in range(gap, n):
                temp = self.array[i]
                j = i
                
                while j >= gap and self.array[j - gap] > temp and self.is_running:
                    self.comparisons += 1
                    
                    color_map = {
                        j: self.colors['swapping'],
                        j - gap: self.colors['comparing']
                    }
                    if not self.visualize_step(color_map, line_number=9):
                        return
                        
                    self.array[j] = self.array[j - gap]
                    self.swaps += 1
                    if not self.visualize_step(color_map, line_number=10):
                        return
                    j -= gap
                    
                self.array[j] = temp
                if not self.visualize_step({j: self.colors['sorted']}, line_number=12):
                    return
                
            gap //= 2


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Configure ttk styles
    style = ttk.Style()
    style.theme_use('clam')
    
    # Combobox style
    style.configure(
        "TCombobox",
        fieldbackground="#0f3460",
        background="#16213e",
        foreground="#eaeaea"
    )
    
    # Scale style
    style.configure(
        "TScale",
        background="#16213e",
        troughcolor="#0f3460"
    )
    
    app = AlgorithmVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
