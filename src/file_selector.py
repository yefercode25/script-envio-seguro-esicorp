"""
Utilidad para selección de archivos y carpetas

Proporciona funciones para seleccionar archivos mediante:
- Entrada manual de ruta
- Diálogo gráfico de selección
"""

import tkinter as tk
from tkinter import filedialog
from pathlib import Path


def seleccionar_archivo_dialogo():
    """
    Abre un diálogo gráfico para seleccionar un archivo.

    Returns:
        Path: Ruta del archivo seleccionado, o None si se cancela
    """
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        file_path = filedialog.askopenfilename(
            title="Seleccione el archivo a enviar",
            filetypes=[
                ("Archivos ESICORP", "*.lima *.santiago *.buenosaires"),
                ("Todos los archivos", "*.*"),
            ],
        )

        root.destroy()

        if file_path:
            return Path(file_path)
        return None
    except Exception as e:
        print(f"Error al abrir selector de archivos: {e}")
        return None


def seleccionar_carpeta_dialogo():
    """
    Abre un diálogo gráfico para seleccionar una carpeta.

    Returns:
        Path: Ruta de la carpeta seleccionada, o None si se cancela
    """
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        folder_path = filedialog.askdirectory(
            title="Seleccione la carpeta con archivos a enviar"
        )

        root.destroy()

        if folder_path:
            return Path(folder_path)
        return None
    except Exception as e:
        print(f"Error al abrir selector de carpeta: {e}")
        return None


def solicitar_archivo_o_carpeta():
    """
    Solicita al usuario un archivo o carpeta mediante ruta o selector.

    Returns:
        tuple: (Path, es_carpeta) donde es_carpeta es True si es carpeta
    """
    print("\n" + "=" * 60)
    print("SELECCIÓN DE ARCHIVO(S) A ENVIAR")
    print("=" * 60)
    print("\n1. 📝 Ingresar ruta manualmente")
    print("2. 📄 Seleccionar ARCHIVO con diálogo")
    print("3. 📁 Seleccionar CARPETA con diálogo")
    print("4. 🔙 Cancelar")

    opcion = input("\nOpción [1-4]: ").strip()

    if opcion == "1":
        # Entrada manual
        ruta = input("\nIngrese la ruta completa del archivo o carpeta: ").strip()
        ruta = ruta.strip('"').strip("'")  # Quitar comillas si las puso

        if not ruta:
            print("⚠️  Ruta vacía")
            return None, False

        path = Path(ruta)

        if not path.exists():
            print(f"❌ La ruta no existe: {path}")
            return None, False

        es_carpeta = path.is_dir()
        return path, es_carpeta

    elif opcion == "2":
        # Selector de archivo
        print("\n📂 Abriendo selector de archivos...")
        path = seleccionar_archivo_dialogo()

        if path:
            print(f"✅ Archivo seleccionado: {path}")
            return path, False
        else:
            print("⚠️  No se seleccionó ningún archivo")
            return None, False

    elif opcion == "3":
        # Selector de carpeta
        print("\n📂 Abriendo selector de carpetas...")
        path = seleccionar_carpeta_dialogo()

        if path:
            print(f"✅ Carpeta seleccionada: {path}")
            return path, True
        else:
            print("⚠️  No se seleccionó ninguna carpeta")
            return None, False

    elif opcion == "4":
        return None, False
    else:
        print("❌ Opción inválida")
        return None, False
