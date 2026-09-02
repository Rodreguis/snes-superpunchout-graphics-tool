"""
Super Punch-Out!! Graphics Tool GUI
Simple interface for decompressing and compressing SNES graphics
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
from graphics_codec import GraphicsCodec


class GraphicsToolGUI:
    """GUI application for Super Punch-Out!! graphics decompression/compression"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Super Punch-Out!! Graphics Tool")
        self.root.geometry("1000x700")
        self.codec = GraphicsCodec()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Super Punch-Out!! Graphics Codec",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, pady=10)
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Operações", padding="10")
        control_frame.grid(row=1, column=0, sticky="ew", pady=10)
        control_frame.columnconfigure(0, weight=1)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, sticky="ew")
        
        ttk.Button(
            button_frame,
            text="📂 Carregar Arquivo",
            command=self.load_file
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="🔍 Descompactar",
            command=self.decompress
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="📦 Compactar",
            command=self.compress
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="💾 Salvar Resultado",
            command=self.save_result
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame,
            text="🗑️ Limpar",
            command=self.clear_all
        ).pack(side="left", padx=5)
        
        # Content frame
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=2, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Input section
        input_label = ttk.Label(content_frame, text="Entrada (Hex)", font=("Arial", 10, "bold"))
        input_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.input_text = scrolledtext.ScrolledText(
            content_frame,
            height=20,
            width=40,
            font=("Courier", 9),
            wrap=tk.WORD
        )
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Output section
        output_label = ttk.Label(content_frame, text="Saída (Hex)", font=("Arial", 10, "bold"))
        output_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        self.output_text = scrolledtext.ScrolledText(
            content_frame,
            height=20,
            width=40,
            font=("Courier", 9),
            wrap=tk.WORD
        )
        self.output_text.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        ttk.Label(status_frame, text="Status:").pack(side="left", padx=5)
        self.status_label = ttk.Label(status_frame, text="Pronto", foreground="green")
        self.status_label.pack(side="left", padx=5)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Informações", padding="10")
        info_frame.grid(row=4, column=0, sticky="ew", pady=10)
        
        self.info_text = scrolledtext.ScrolledText(
            info_frame,
            height=4,
            width=100,
            font=("Courier", 8),
            wrap=tk.WORD
        )
        self.info_text.pack(fill="both", expand=True)
        
        # Welcome message
        welcome = """Bem-vindo ao Super Punch-Out!! Graphics Tool!

1. Carregue um arquivo ou cole dados HEX na entrada
2. Escolha entre Descompactar ou Compactar
3. O resultado aparecerá na saída
4. Salve o resultado como arquivo se desejar

Formato: Dados HEX separados por espaço ou quebra de linha"""
        
        self.info_text.insert("1.0", welcome)
        self.info_text.config(state="disabled")
    
    def load_file(self):
        """Load a file with hex data"""
        file_path = filedialog.askopenfilename(
            title="Selecione arquivo de dados",
            filetypes=[("Hex files", "*.hex"), ("Binary files", "*.bin"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            hex_str = self.codec.bytes_to_hex(data)
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", hex_str)
            
            self.update_status(f"Arquivo carregado: {os.path.basename(file_path)} ({len(data)} bytes)")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")
            self.update_status("Erro ao carregar arquivo", "red")
    
    def decompress(self):
        """Decompress the input data"""
        try:
            hex_input = self.input_text.get("1.0", "end").strip()
            
            if not hex_input:
                messagebox.showwarning("Aviso", "Por favor, insira dados HEX")
                return
            
            # Convert hex to bytes
            data = self.codec.hex_to_bytes(hex_input)
            self.update_status(f"Descompactando {len(data)} bytes...")
            self.root.update()
            
            # Decompress
            decompressed = self.codec.decompress(data)
            
            # Show result
            hex_output = self.codec.bytes_to_hex(decompressed)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", hex_output)
            
            self.update_status(
                f"✓ Descompactado: {len(data)} → {len(decompressed)} bytes",
                "green"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na descompactação:\n{str(e)}")
            self.update_status("Erro na descompactação", "red")
    
    def compress(self):
        """Compress the input data"""
        try:
            hex_input = self.input_text.get("1.0", "end").strip()
            
            if not hex_input:
                messagebox.showwarning("Aviso", "Por favor, insira dados HEX")
                return
            
            # Convert hex to bytes
            data = self.codec.hex_to_bytes(hex_input)
            self.update_status(f"Compactando {len(data)} bytes...")
            self.root.update()
            
            # Compress
            compressed = self.codec.compress(data)
            
            # Show result
            hex_output = self.codec.bytes_to_hex(compressed)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", hex_output)
            
            ratio = (1 - len(compressed) / len(data)) * 100
            self.update_status(
                f"✓ Compactado: {len(data)} → {len(compressed)} bytes ({ratio:.1f}% economia)",
                "green"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na compactação:\n{str(e)}")
            self.update_status("Erro na compactação", "red")
    
    def save_result(self):
        """Save the output result to a file"""
        hex_output = self.output_text.get("1.0", "end").strip()
        
        if not hex_output:
            messagebox.showwarning("Aviso", "Não há resultado para salvar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar resultado",
            defaultextension=".bin",
            filetypes=[("Binary files", "*.bin"), ("Hex files", "*.hex"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            data = self.codec.hex_to_bytes(hex_output)
            
            with open(file_path, 'wb') as f:
                f.write(data)
            
            messagebox.showinfo("Sucesso", f"Arquivo salvo:\n{file_path}\n{len(data)} bytes")
            self.update_status(f"Arquivo salvo: {os.path.basename(file_path)}", "green")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{str(e)}")
            self.update_status("Erro ao salvar", "red")
    
    def clear_all(self):
        """Clear all text areas"""
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.update_status("Limpado", "blue")
    
    def update_status(self, message: str, color: str = "black"):
        """Update status bar"""
        self.status_label.config(text=message, foreground=color)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = GraphicsToolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
