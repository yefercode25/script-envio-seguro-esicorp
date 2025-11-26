import os


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    clear_screen()
    print("""
    ███████╗███████╗██╗ ██████╗ ██████╗ ██████╗ ██████╗ 
    ██╔════╝██╔════╝██║██╔════╝██╔═══██╗██╔══██╗██╔══██╗
    █████╗  ███████╗██║██║     ██║   ██║██████╔╝██████╔╝
    ██╔══╝  ╚════██║██║██║     ██║   ██║██╔══██╗██╔═══╝ 
    ███████╗███████║██║╚██████╗╚██████╔╝██║  ██║██║     
    ╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     
        SISTEMA DE TRANSFERENCIA SEGURA DE ARCHIVOS
    """)


def print_section(title):
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_phase(phase_name):
    print(f"\n🔷 FASE: {phase_name}")
    print("-" * 40)


def print_action(message):
    print(f"   🔸 {message}")


def print_crypto(message):
    print(f"      🔐 {message}")


def print_network(message):
    print(f"      📡 {message}")


def print_file(message):
    print(f"      📂 {message}")


def print_success(message):
    print(f"   ✅ {message}")


def print_error(message):
    print(f"   ❌ {message}")


def print_info(message):
    print(f"   ℹ️  {message}")


# Mantenemos print_detail por compatibilidad pero lo redirigimos a un formato más limpio
def print_detail(message):
    print(f"      ⚙️  {message}")
