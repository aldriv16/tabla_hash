import tkinter as tk
from tkinter import ttk, messagebox
import re

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None

class HashTable:
    def __init__(self, capacity=30):
        self.capacity = capacity
        self.size = 0
        self.table = [None] * capacity
        
    def _hash(self, key):
        hash_val = 0
        for char in key:
            hash_val = (hash_val * 31 + ord(char)) % self.capacity
        return hash_val
        
    def insert(self, key, value):
        index = self._hash(key)
        if self.table[index] is None:
            self.table[index] = Node(key, value)
            self.size += 1
        else:
            current = self.table[index]
            while current:
                if current.key == key:
                    current.value = value 
                if current.next is None:
                    break
                current = current.next
            current.next = Node(key, value)
            self.size += 1
            
    def get(self, key):
        index = self._hash(key)
        current = self.table[index]
        steps = 0
        while current:
            steps += 1
            if current.key == key:
                return current.value, steps
            current = current.next
        return None, steps

    def get_all(self):
        items = []
        for i in range(self.capacity):
            current = self.table[i]
            while current:
                items.append((current.key, current.value))
                current = current.next
        return items

class LexerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Léxico con Tabla Hash")
        self.root.geometry("800x500")
        self.hash_table = HashTable()
        
        self.setup_ui()
        
    def setup_ui(self):
        left_frame = tk.Frame(self.root, padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = tk.Frame(self.root, padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="Ingrese el código fuente (C++ like):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.text_input = tk.Text(left_frame, height=15, width=40, font=("Courier New", 12))
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=5)
 
        example_code = "int suma = 0;\nsuma = 54 + 20;"
        self.text_input.insert(tk.END, example_code)
        
        tk.Button(left_frame, text="Analizar Código", command=self.analyze_code, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=10)

        tk.Label(right_frame, text="Tabla Hash Resultante:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
 
        columns = ("Clave Hash", "Token")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        self.tree.heading("Clave Hash", text="Clave Hash (fila,columna)")
        self.tree.heading("Token", text="Token")
        self.tree.column("Clave Hash", width=160, anchor=tk.CENTER)
        self.tree.column("Token", width=200, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        search_frame = tk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(search_frame, text="Buscar token (Ej: 0,0):", font=("Arial", 9)).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=10, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Buscar", command=self.search_token, bg="#2196F3", fg="white").pack(side=tk.LEFT)
        
        self.search_result = tk.Label(right_frame, text="", fg="blue", font=("Arial", 10))
        self.search_result.pack(anchor=tk.W, pady=5)

    def analyze_code(self):
        code = self.text_input.get("1.0", tk.END).strip("\n")
        
        self.hash_table = HashTable(capacity=30)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not code.strip():
            return
            
        token_pattern = re.compile(
            r'(?P<NUMBER>\d+\.\d+|\d+)|'
            r'(?P<WORD>[a-zA-Z_][a-zA-Z0-9_]*)|'
            r'(?P<SYMBOL>[=+\-*/;,\(\)])|'
            r'(?P<OTHER>[^\s])' 
        )
        
        lines = code.split('\n')
        
        for row, line in enumerate(lines):
            for match in token_pattern.finditer(line):
                token = match.group()
                col = match.start()
                key = f"{row},{col}"
                
                self.hash_table.insert(key, token)
 
        for key, value in self.hash_table.get_all():
            self.tree.insert("", tk.END, values=(key, value))
            
        self.sort_treeview()
        self.search_result.config(text=f"Análisis completado. {self.hash_table.size} tokens insertados.", fg="green")

    def sort_treeview(self):
        items = [(self.tree.set(k, "Clave Hash"), k) for k in self.tree.get_children("")]
        
        def sort_key(item):
            key_str = item[0]
            try:
                r, c = map(int, key_str.split(','))
                return r, c
            except:
                return 0, 0
                
        items.sort(key=sort_key)
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)

    def search_token(self):
        key = self.search_entry.get().strip()
        if not key:
            messagebox.showwarning("Aviso", "Por favor ingrese una clave para buscar (Ej: 1,5).")
            return 
       
        token, steps = self.hash_table.get(key)
        if token:
            self.search_result.config(text=f"✅ Encontrado: '{token}' (Nodos revisados: {steps})", fg="green")
        else:
            self.search_result.config(text=f"❌ Clave '{key}' no encontrada en la tabla hash.", fg="red")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = LexerApp(root)
    root.mainloop()
