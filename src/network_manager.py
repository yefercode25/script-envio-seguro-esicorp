import socket
import os
import tqdm
from . import config
from .utils import print_network, print_success, print_error, print_info


class NetworkManager:
    def __init__(self):
        pass

    def send_file(
        self, ip, port, file_path, security_code, session_id, original_filename
    ):
        filesize = os.path.getsize(file_path)
        filename = original_filename

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print_network(f"Iniciando conexión TCP/IP...")
            print_network(f"  - Destino: {ip}:{port}")

            try:
                s.connect((ip, int(port)))
            except Exception as e:
                raise ConnectionError(
                    f"No se pudo establecer conexión con {ip}:{port}. Verifique IP/Puerto."
                )

            print_network("  ✅ Conexión establecida (3-way handshake OK).")

            # 1. Handshake (Código)
            print_network(f"Autenticando sesión...")
            print_network(f"  - Enviando código: {security_code}")
            s.send(f"CODE:{security_code}".encode())

            response = s.recv(1024).decode()
            if response != "OK":
                print_error("Código rechazado por el receptor.")
                print_network(f"  - Respuesta del servidor: {response}")
                raise PermissionError("Código de seguridad incorrecto.")

            print_success("Autenticación exitosa. Canal seguro establecido.")

            # 2. Metadatos
            metadata = (
                f"{filename}{config.SEPARATOR}{filesize}{config.SEPARATOR}{session_id}"
            )
            print_network(f"Negociando transferencia...")
            print_network(f"  - Enviando metadatos: {metadata}")
            s.send(metadata.encode())

            response = s.recv(1024).decode()
            if response != "READY":
                print_error("Servidor no listo para recibir datos.")
                raise RuntimeError("El servidor no respondió READY.")

            print_network("  - Servidor listo (ACK recibido).")

            # 3. Transferencia
            print_network("Iniciando flujo de datos...")
            progress = tqdm.tqdm(
                range(filesize),
                f"      📡 Enviando",
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                ncols=80,
            )
            with open(file_path, "rb") as f:
                while True:
                    bytes_read = f.read(config.BUFFER_SIZE)
                    if not bytes_read:
                        break
                    s.sendall(bytes_read)
                    progress.update(len(bytes_read))

            print_network("Transmisión finalizada. Cerrando socket.")
            s.close()
            return True

        except ConnectionError as e:
            raise e
        except PermissionError as e:
            raise e
        except Exception as e:
            print_error(f"Error de red: {e}")
            raise e
        finally:
            s.close()

    def start_server(self, port, security_code):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", int(port)))
        actual_port = s.getsockname()[1]
        s.listen(1)
        s.settimeout(1.0)

        # Obtener IP local preferida
        try:
            temp_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_s.connect(("8.8.8.8", 80))
            local_ip = temp_s.getsockname()[0]
            temp_s.close()
        except Exception:
            local_ip = "127.0.0.1"

        print("\n" + "=" * 40)
        print(f"📡 SERVIDOR EN ESCUCHA")
        print(f"🌐 IP LOCAL: {local_ip}")
        print(f"👉 PUERTO:   {actual_port}")
        print(f"🔑 CÓDIGO:   {security_code}")
        print("=" * 40 + "\n")
        print_info(f"Comparte estos datos con el Emisor.")
        print_info(f"Presione Ctrl+C para cancelar.")

        print_network(f"Socket vinculado a 0.0.0.0:{actual_port}. Esperando SYN...")

        while True:
            client_socket = None
            try:
                while True:
                    try:
                        client_socket, address = s.accept()
                        break
                    except socket.timeout:
                        continue
                    except KeyboardInterrupt:
                        raise KeyboardInterrupt

                client_socket.settimeout(None)
                print_success(f"Conexión entrante desde {address}")
                print_network(f"Iniciando handshake de aplicación...")

                try:
                    # 1. Verificar Código
                    msg = client_socket.recv(1024).decode()
                    print_network(f"  - Mensaje recibido: {msg}")
                    if (
                        not msg.startswith("CODE:")
                        or msg.split(":")[1] != security_code
                    ):
                        print_error("Código incorrecto. Enviando RST (FAIL).")
                        client_socket.send("FAIL".encode())
                        client_socket.close()
                        print_info("Esperando nuevo intento...")
                        continue

                    client_socket.send("OK".encode())
                    print_success("Código correcto. Enviando ACK.")

                    # 2. Recibir Metadatos
                    received = client_socket.recv(1024).decode()
                    print_network(f"  - Metadatos recibidos: {received}")
                    filename, filesize, session_id = received.split(config.SEPARATOR)
                    original_filename = os.path.basename(filename)
                    filesize = int(filesize)

                    session_dir = os.path.join(config.BASE_DIR, session_id, "receiver")
                    if not os.path.exists(session_dir):
                        os.makedirs(session_dir)

                    save_path = os.path.join(session_dir, "received.enc")

                    client_socket.send("READY".encode())
                    print_network("Enviando READY. Recibiendo stream de datos...")

                    # 3. Recibir Archivo
                    progress = tqdm.tqdm(
                        range(filesize),
                        f"      📥 Recibiendo",
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        ncols=80,
                    )

                    with open(save_path, "wb") as f:
                        bytes_received = 0
                        while bytes_received < filesize:
                            bytes_read = client_socket.recv(config.BUFFER_SIZE)
                            if not bytes_read:
                                break
                            f.write(bytes_read)
                            progress.update(len(bytes_read))
                            bytes_received += len(bytes_read)

                    print_success(f"Transferencia completada.")
                    print_network(f"  - Archivo guardado en: {save_path}")

                    client_socket.close()
                    s.close()
                    return save_path, session_id, original_filename

                except Exception as e:
                    print_error(f"Error durante la recepción: {e}")
                    if client_socket:
                        client_socket.close()
                    print_info("Esperando nuevo intento...")
                    continue

            except KeyboardInterrupt:
                print("\n[!] Cancelado por usuario.")
                if client_socket:
                    client_socket.close()
                s.close()
                return None, None, None
            except Exception as e:
                print_error(f"Error crítico: {e}")
                s.close()
                return None, None, None
