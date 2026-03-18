import os
import sys
import subprocess
import platform
import time

# --- COLORES PARA LA TERMINAL ---
class Style:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def setup_windows_auto():
    """Instalación totalmente automática para Windows."""
    if platform.system() != "Windows":
        print(f"{Style.RED}❌ Este script es específico para Windows.{Style.RESET}")
        return

    # 1. Verificar/Instalar Tesseract vía Winget (Gestor oficial de Windows)
    print(f"{Style.CYAN}🔍 Verificando motor OCR (Tesseract)...{Style.RESET}")
    
    # Intentar buscar el ejecutable en la ruta por defecto
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    if not os.path.exists(tesseract_path):
        print(f"{Style.YELLOW}📦 Tesseract no encontrado. Instalando automáticamente vía Winget...{Style.RESET}")
        print(f"{Style.CYAN}⚠️ Por favor, si aparece una ventana de confirmación, acepta los permisos.{Style.RESET}")
        
        try:
            # Comando de instalación silenciosa de Winget
            subprocess.run(["winget", "install", "-e", "--id", "UB-Mannheim.TesseractOCR"], check=True)
            print(f"{Style.GREEN}✅ Tesseract instalado correctamente.{Style.RESET}")
            # Añadir al PATH de la sesión actual
            os.environ["PATH"] += os.pathsep + r'C:\Program Files\Tesseract-OCR'
        except Exception as e:
            print(f"{Style.RED}❌ Error al instalar con Winget: {e}{Style.RESET}")
            print("Por favor, instálalo manualmente desde: https://github.com/UB-Mannheim/tesseract/wiki")
            sys.exit(1)
    else:
        # Si ya existe, nos aseguramos de que esté en el PATH de Python
        os.environ["PATH"] += os.pathsep + os.path.dirname(tesseract_path)

def setup_venv():
    """Crea y reinicia en entorno virtual."""
    venv_dir = os.path.join(os.path.dirname(__file__), "venv_win")
    if not hasattr(sys, 'real_prefix') and not (sys.base_prefix != sys.prefix):
        if not os.path.exists(venv_dir):
            print(f"{Style.CYAN}📦 Creando entorno de Python...{Style.RESET}")
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        
        python_venv = os.path.join(venv_dir, "Scripts", "python.exe")
        os.execl(python_venv, python_venv, *sys.argv)

def install_python_libs():
    """Instala las librerías necesarias."""
    libs = ['ocrmypdf', 'pikepdf']
    for lib in libs:
        try:
            __import__(lib)
        except ImportError:
            print(f"{Style.YELLOW}📥 Instalando {lib}...{Style.RESET}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "--quiet"])

def main():
    import ocrmypdf
    print(f"\n{Style.BOLD}{Style.GREEN}✨ WINDOWS PDF SEARCHABLE TOOL READY ✨{Style.RESET}")
    
    pdfs = [f for f in os.listdir('.') if f.lower().endswith('.pdf') and not f.startswith('BUSCABLE_')]
    
    if not pdfs:
        print(f"{Style.RED}❌ No hay archivos .pdf en esta carpeta.{Style.RESET}")
        input("Presiona Enter para salir...")
        return

    for i, f in enumerate(pdfs, 1):
        print(f"  [{i}] {f}")

    choice = input(f"\n{Style.BOLD}👉 Elige el número del archivo: {Style.RESET}")
    
    try:
        idx = int(choice) - 1
        file_in = pdfs[idx]
        file_out = f"BUSCABLE_{file_in}"
        
        print(f"{Style.CYAN}⏳ Procesando OCR... Por favor, espera.{Style.RESET}")
        
        try:
            # Intento 1: Español + Inglés
            ocrmypdf.ocr(file_in, file_out, language="spa+eng", deskew=True, force_ocr=True, progress_bar=True)
        except Exception as e:
            if "spa" in str(e):
                print(f"{Style.YELLOW}⚠️  Idioma español no instalado en Tesseract.{Style.RESET}")
                print(f"{Style.CYAN}🔄 Reintentando solo con inglés...{Style.RESET}")
                # Intento 2: Solo Inglés (evita el error que viste en la imagen)
                ocrmypdf.ocr(file_in, file_out, language="eng", deskew=True, force_ocr=True, progress_bar=True)
                ocrmypdf.ocr(
                    file_in, 
                    file_out, 
                    language="spa+eng", 
                    deskew=True,         # Endereza el texto si está algo torcido [cite: 1]
                    clean=True,          # Elimina "ruido" y manchas del fondo
                    rotate_pages=True,   # Corrige la orientación automáticamente
                    force_ocr=True,      # Obliga a procesar todas las capas de imagen [cite: 1]
                    optimize=1,          # Comprime el archivo resultante sin perder calidad
                    sidecar="output.txt" # Opcional: genera un txt con todo el texto extraído
                   )
            else:
                raise e

        print(f"\n{Style.GREEN}✅ ¡LISTO! Archivo creado: {file_out}{Style.RESET}")
        
    except Exception as e:
        print(f"\n{Style.RED}⚠ Error crítico: {e}{Style.RESET}")
    
    input(f"\n{Style.YELLOW}Presiona Enter para cerrar...{Style.RESET}")
    
if __name__ == "__main__":
    # Importante: Primero el venv, luego el setup de Windows
    setup_venv()
    setup_windows_auto()
    install_python_libs()
    main()
