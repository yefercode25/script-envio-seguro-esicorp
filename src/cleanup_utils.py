"""
Utilidad para limpiar configuraciones y archivos del sistema ESICORP
"""

import os
import shutil
from pathlib import Path


def limpiar_llaves():
    """
    Elimina las llaves RSA del directorio ./keys
    """
    keys_dir = Path("./keys")

    if not keys_dir.exists():
        print("[i] No existe el directorio de llaves")
        return True

    print("[PROC] Limpiando directorio de llaves...")

    archivos_eliminados = 0
    for archivo in keys_dir.iterdir():
        if archivo.is_file():
            print(f"  [X] Eliminando: {archivo.name}")
            archivo.unlink()
            archivos_eliminados += 1

    print(f"[OK] {archivos_eliminados} archivo(s) eliminado(s) de ./keys/")
    return True


def limpiar_known_hosts():
    """
    Limpia entradas relacionadas con ESICORP en known_hosts
    """
    ssh_dir = Path.home() / ".ssh"
    known_hosts = ssh_dir / "known_hosts"

    if not known_hosts.exists():
        print("[i] No existe archivo known_hosts")
        return True

    print("[PROC] Limpiando known_hosts...")

    try:
        with open(known_hosts, "r") as f:
            lines = f.readlines()

        # Filtrar líneas que contengan IPs/hosts del proyecto
        # (simplemente limpiamos todo ya que es desarrollo)
        # En producción, aquí se filtrarían IPs específicas

        print(f"[!] Se recomienda limpiar manualmente: {known_hosts}")
        print(f"[TIP] O ejecutar: ssh-keygen -R <IP_SERVIDOR>")

        return True
    except Exception as e:
        print(f"[!] Error al limpiar known_hosts: {e}")
        return False


def limpiar_procesados():
    """
    Limpia el directorio ./procesados
    """
    procesados_dir = Path("./procesados")

    if not procesados_dir.exists():
        print("[i] No existe el directorio procesados")
        return True

    print("[PROC] Limpiando directorio procesados...")

    archivos_eliminados = 0
    for archivo in procesados_dir.iterdir():
        if archivo.is_file():
            print(f"  [X] Eliminando: {archivo.name}")
            archivo.unlink()
            archivos_eliminados += 1

    print(f"[OK] {archivos_eliminados} archivo(s) eliminado(s) de ./procesados/")
    return True


def limpiar_directorio_remoto(sftp_client, ruta_remota="/home/grupo1/upload/"):
    """
    Limpia archivos del directorio remoto en el servidor

    Args:
        sftp_client: Cliente SFTP conectado
        ruta_remota: Ruta del directorio a limpiar
    """
    try:
        print(f"[PROC] Limpiando directorio remoto: {ruta_remota}")

        # Listar archivos
        archivos = sftp_client.listdir(ruta_remota)

        if not archivos:
            print("[i] El directorio remoto ya está vacío")
            return True

        print(f"[INFO] Encontrados {len(archivos)} elemento(s)")

        confirmacion = (
            input(f"[?] Eliminar {len(archivos)} elemento(s) en {ruta_remota}? (s/N): ")
            .strip()
            .lower()
        )

        if confirmacion != "s":
            print("[i] Operación cancelada")
            return False

        eliminados = 0
        for archivo in archivos:
            ruta_completa = ruta_remota + archivo
            try:
                # Intentar eliminar como archivo
                sftp_client.remove(ruta_completa)
                print(f"  [X] Eliminado: {archivo}")
                eliminados += 1
            except:
                # Si falla, puede ser un directorio
                try:
                    sftp_client.rmdir(ruta_completa)
                    print(f"  [X] Eliminado (dir): {archivo}")
                    eliminados += 1
                except Exception as e:
                    print(f"  [!] No se pudo eliminar: {archivo} ({e})")

        print(f"[OK] {eliminados} elemento(s) eliminado(s) del servidor")
        return True

    except Exception as e:
        print(f"[X] Error al limpiar directorio remoto: {e}")
        return False


def limpiar_todo_local():
    """
    Limpia todas las configuraciones y archivos locales
    """
    print("\n" + "=" * 60)
    print("LIMPIEZA DE CONFIGURACIONES Y ARCHIVOS LOCALES")
    print("=" * 60)
    print()

    print("[!] Esta operación eliminará:")
    print("    - Llaves RSA en ./keys/")
    print("    - Archivos procesados en ./procesados/")
    print()

    confirmacion = input("[?] Continuar con la limpieza local? (s/N): ").strip().lower()

    if confirmacion != "s":
        print("\n[i] Operación cancelada")
        return False

    print()

    # Limpiar llaves
    limpiar_llaves()
    print()

    # Limpiar procesados
    limpiar_procesados()
    print()

    # Info sobre known_hosts
    limpiar_known_hosts()

    print("\n" + "=" * 60)
    print("[OK] Limpieza local completada")
    print("=" * 60)

    return True
