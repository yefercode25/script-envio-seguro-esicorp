#!/usr/bin/env python3
"""
Script de diagnóstico para verificar rutas SSH
"""

import os
import platform
from pathlib import Path

print("=" * 60)
print("DIAGNÓSTICO DE RUTAS SSH")
print("=" * 60)

# Información del sistema
print(f"\n[SISTEMA]")
print(f"  OS: {platform.system()}")
print(f"  Versión: {platform.version()}")
print(f"  Usuario de OS: {os.getenv('USER', os.getenv('USERNAME', 'DESCONOCIDO'))}")

# Rutas importantes
print(f"\n[RUTAS]")
print(f"  Path.home(): {Path.home()}")
print(f"  HOME env: {os.getenv('HOME', 'NO DEFINIDO')}")
print(f"  User env: {os.getenv('USER', 'NO DEFINIDO')}")
print(f"  PWD actual: {Path.cwd()}")

# Ruta SSH calculada
ssh_dir = Path.home() / ".ssh"
print(f"\n[RUTA SSH CALCULADA]")
print(f"  {ssh_dir}")
print(f"  Existe: {ssh_dir.exists()}")

if ssh_dir.exists():
    print(f"  Permisos: {oct(ssh_dir.stat().st_mode)[-3:]}")
    print(f"  Owner UID: {ssh_dir.stat().st_uid}")
    print(f"  UID actual: {os.getuid() if hasattr(os, 'getuid') else 'N/A (Windows)'}")

# Probar creación
print(f"\n[PRUEBA DE PERMISOS]")
test_dir = Path.home() / ".ssh_test"
try:
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "test.txt"
    test_file.write_text("test")
    test_file.unlink()
    test_dir.rmdir()
    print(f"  ✅ SÍ tienes permisos para crear en: {Path.home()}")
except Exception as e:
    print(f"  ❌ NO tienes permisos: {e}")

# Verificar si existe ./ssh (ruta incorrecta)
local_ssh = Path(".ssh")
print(f"\n[VERIFICACIÓN DE RUTA LOCAL INCORRECTA]")
print(f"  ./.ssh = {local_ssh.absolute()}")
print(f"  Existe: {local_ssh.exists()}")

if local_ssh.exists():
    print(f"  ⚠️  ADVERTENCIA: Existe ./.ssh en directorio actual!")
    print(f"  Esta NO es la ubicación correcta para SSH")

print("\n" + "=" * 60)
print("FIN DEL DIAGNÓSTICO")
print("=" * 60)
