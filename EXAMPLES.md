# 📚 Ejemplos de Uso - Sistema de Transferencia Segura ESICORP

Este documento contiene ejemplos prácticos de uso del sistema en diferentes escenarios reales.

---

## 🎯 Índice de Ejemplos

1. [Modo Interactivo](#1-modo-interactivo)
2. [Envío de Archivos Individuales](#2-envío-de-archivos-individuales)
3. [Envío de Carpetas Completas](#3-envío-de-carpetas-completas)
4. [Recepción Manual](#4-recepción-manual)
5. [Recepción Automática](#5-recepción-automática)
6. [Casos de Uso por Sede](#6-casos-de-uso-por-sede)
7. [Pruebas Locales](#7-pruebas-locales)
8. [Automatización con Scripts](#8-automatización-con-scripts)

---

## 1. Modo Interactivo

### Ejemplo 1.1: Iniciar con menú gráfico

```powershell
python main.py --interactivo
```

**Resultado:**

- Muestra menú principal con opciones
- Permite seleccionar archivos con diálogo visual
- Guía paso a paso para envío o recepción

### Ejemplo 1.2: Forma corta

```powershell
python main.py -i
```

---

## 2. Envío de Archivos Individuales

### Ejemplo 2.1: Enviar PDF de Compras a Santiago

```powershell
python main.py --emisor --archivo "C:\ESICORP\Datos\Compras-23-02-2023.santiago" --ip 192.168.1.10 --puerto 5000 --codigo 1234
```

**¿Qué hace?**

- Comprime el archivo PDF
- Calcula hash SHA-256
- Cifra con AES-256-GCM
- Envía a 192.168.1.10:5000
- Verifica con código 1234

### Ejemplo 2.2: Enviar archivo de Ventas a Lima (forma corta)

```powershell
python main.py -e -a "C:\ESICORP\Ventas\Ventas-10-11-2023.lima" -d 10.0.0.5 -c 9876
```

**Nota:** Puerto 5000 por defecto (no especificado)

### Ejemplo 2.3: Enviar archivo con espacios en el nombre

```powershell
python main.py -e -a "C:\Datos\Reporte Financiero 2023.xlsx" -d 192.168.1.20 -p 5001 -c 5555
```

**Importante:** Usar comillas cuando el nombre tiene espacios

### Ejemplo 2.4: Enviar archivo desde ruta larga

```powershell
python main.py -e -a "C:\Users\Usuario\Documents\ESICORP\Finanzas\Reportes\Q4\Finanzas-12-12-2023.buenosaires" -d 172.16.10.50 -c 7890
```

---

## 3. Envío de Carpetas Completas

### Ejemplo 3.1: Enviar carpeta de Compras completa

```powershell
python main.py -e -a "C:\ESICORP\Compras\2023" -d 192.168.1.10 -c 1234
```

**¿Qué incluye?**

- Todos los archivos dentro de la carpeta
- Todas las subcarpetas y su contenido
- Mantiene la estructura de directorios

### Ejemplo 3.2: Enviar carpeta de Ventas mensual

```powershell
python main.py -e -a "C:\ESICORP\Ventas\Noviembre" -d 192.168.5.25 -p 5002 -c 4567
```

### Ejemplo 3.3: Enviar proyecto completo

```powershell
python main.py -e -a "C:\Proyectos\Migracion_Sistema" -d 10.20.30.40 -c 1111
```

**El sistema automaticamente:**

1. ✅ Sanitiza nombres de archivos con caracteres especiales
2. ✅ Comprime toda la estructura en un solo ZIP
3. ✅ Cifra el paquete completo
4. ✅ Mantiene permisos y fechas originales

---

## 4. Recepción Manual

### Ejemplo 4.1: Recibir archivo (puerto automático)

```powershell
python main.py --receptor --codigo 1234
```

**Salida esperada:**

```
=== MODO RECEPTOR AUTOMÁTICO ===

Puerto: Asignación automática
Código: ****

🔊 Servidor activo en: 192.168.1.10:54321
   Código de Seguridad: 1234
   
Esperando conexión...
```

**Después de recibir:**

- Archivo queda cifrado en `transfers/[SESION]/receiver/`
- Requiere desencriptado manual posterior

### Ejemplo 4.2: Recibir en puerto específico

```powershell
python main.py -r -c 9876 -p 5000
```

**Uso:** Cuando necesitas usar un puerto fijo (firewall, NAT, etc.)

---

## 5. Recepción Automática

### Ejemplo 5.1: Recibir y desencriptar automáticamente

```powershell
python main.py --receptor --codigo 1234 --desencriptar
```

**Resultado:**

- Recibe el archivo
- Desencripta automáticamente
- Verifica integridad SHA-256
- Descomprime archivos
- Archivos listos en `transfers/[SESION]/receiver/decrypted_files/`

### Ejemplo 5.2: Forma corta con desencriptado

```powershell
python main.py -r -c 5555 --desencriptar
```

### Ejemplo 5.3: Puerto fijo con desencriptado automático

```powershell
python main.py -r -c 7890 -p 5001 --desencriptar
```

---

## 6. Casos de Uso por Sede

### Caso 6.1: Bogotá → Santiago (Datos de Compras)

**Máquina Receptora (Santiago):**

```powershell
python main.py -r -c 2023 --desencriptar
```

**Máquina Emisora (Bogotá):**

```powershell
python main.py -e -a "C:\ESICORP\Compras\Compras-23-02-2023.santiago" -d 192.168.100.10 -p 54321 -c 2023
```

### Caso 6.2: Bogotá → Buenos Aires (Reportes de Ventas)

**Máquina Receptora (Buenos Aires):**

```powershell
python main.py -r -c 8888 -p 5000 --desencriptar
```

**Máquina Emisora (Bogotá):**

```powershell
python main.py -e -a "C:\ESICORP\Ventas\Ventas-10-11-2023.buenosaires" -d 10.50.20.30 -p 5000 -c 8888
```

### Caso 6.3: Bogotá → Lima (Carpeta de Finanzas Mensual)

**Máquina Receptora (Lima):**

```powershell
python main.py -r -c 4040 --desencriptar
```

**Máquina Emisora (Bogotá):**

```powershell
python main.py -e -a "C:\ESICORP\Finanzas\Diciembre2023" -d 172.20.10.100 -p 51234 -c 4040
```

---

## 7. Pruebas Locales

### Ejemplo 7.1: Prueba en misma máquina (localhost)

**Terminal 1 (Receptor):**

```powershell
python main.py -r -c 9999 --desencriptar
```

**Terminal 2 (Emisor):**

```powershell
python main.py -e -a "C:\test\archivo_prueba.txt" -d 127.0.0.1 -p [PUERTO_MOSTRADO] -c 9999
```

### Ejemplo 7.2: Prueba con carpeta local

**Terminal 1:**

```powershell
python main.py -r -c 1111
```

**Terminal 2:**

```powershell
python main.py -e -a "C:\test\carpeta_prueba" -d 127.0.0.1 -p [PUERTO_MOSTRADO] -c 1111
```

---

## 🆘 Errores Comunes y Soluciones

### Error: "El archivo no existe"

```powershell
# ❌ Incorrecto (ruta mal escrita)
python main.py -e -a "C:\Datos\archivo.txt" -d 192.168.1.10 -c 1234

# ✅ Correcto (verificar ruta)
python main.py -e -a "C:\ESICORP\Datos\archivo.txt" -d 192.168.1.10 -c 1234
```

### Error: "Puerto inválido"

```powershell
# ❌ Incorrecto (puerto < 1024)
python main.py -e -a "archivo.txt" -d 192.168.1.10 -p 80 -c 1234

# ✅ Correcto (puerto válido)
python main.py -e -a "archivo.txt" -d 192.168.1.10 -p 5000 -c 1234
```

### Error: "No se pudo establecer conexión"

```powershell
# Solución: Verificar que el receptor esté escuchando primero
# Terminal 1: Iniciar receptor
python main.py -r -c 1234

# Terminal 2: Enviar después de ver "Esperando conexión..."
python main.py -e -a "archivo.txt" -d 192.168.1.10 -p [PUERTO] -c 1234
```
