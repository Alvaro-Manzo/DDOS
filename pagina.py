#!/usr/bin/env python3
"""
==============================================
VISUAL HONEYPOT SERVER FOR DDOS TESTING
==============================================
BY: ALVARO MANZO
VERSION: 2.0 VISUAL DASHBOARD EDITION
SERVIDOR HONEYPOT CON INTERFAZ WEB PROFESIONAL
==============================================
"""

import socket
import threading
import time
import json
import logging
import base64
import hashlib
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs, urlparse
import os
import signal
import sys
import secrets

class VisualDDoSHoneypot:
    def __init__(self):
        self.start_time = datetime.now()
        self.total_requests = 0
        self.get_requests = 0
        self.post_requests = 0
        self.tcp_connections = 0
        self.error_requests = 0
        self.client_ips = set()
        self.attack_patterns = []
        self.is_running = False
        self.max_requests_per_ip = 1000
        self.ip_request_count = {}
        
        # Nuevas métricas para visualización
        self.requests_timeline = []  # Para gráficas temporales
        self.attack_types_count = {'GET': 0, 'POST': 0, 'TCP': 0, 'ERROR': 0}
        self.user_agents_count = {}
        self.country_stats = {}
        self.hourly_stats = [0] * 24
        self.response_times = []
        self.attack_intensity = []  # RPS en intervalos de 5 segundos
        self.geographic_data = []
        self.security_alerts = []
        
        # Sistema de autenticación
        self.sessions = {}
        self.valid_credentials = {
            'Alvaro': 'falcon40'
        }
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('honeypot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def print_banner(self):
        banner = """
    ╔══════════════════════════════════════════════╗
    ║       VISUAL HONEYPOT DASHBOARD v2.0         ║
    ║         SERVIDOR CON INTERFAZ WEB            ║
    ╠══════════════════════════════════════════════╣
    ║  [+] Dashboard web en puerto 8080           ║
    ║  [+] API de datos en tiempo real            ║
    ║  [+] Gráficas interactivas                  ║
    ║  [+] Sistema de autenticación               ║
    ║  [+] Métricas avanzadas                     ║
    ╚══════════════════════════════════════════════╝
        """
        print("\033[92m" + banner + "\033[0m")
    
    def generate_session_id(self):
        """Generar ID de sesión único"""
        return secrets.token_hex(32)
    
    def authenticate_user(self, username, password):
        """Autenticar usuario"""
        return self.valid_credentials.get(username) == password
    
    def is_authenticated(self, session_id):
        """Verificar si la sesión está autenticada"""
        return session_id in self.sessions and \
               datetime.now() < self.sessions[session_id]['expires']
    
    def add_security_alert(self, alert_type, message, severity='medium'):
        """Añadir alerta de seguridad"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }
        self.security_alerts.append(alert)
        if len(self.security_alerts) > 100:
            self.security_alerts.pop(0)  # Mantener solo las últimas 100
    
    def update_metrics(self, request_type, client_ip, user_agent=None, response_time=0):
        """Actualizar métricas para visualización"""
        now = datetime.now()
        
        # Timeline de requests
        self.requests_timeline.append({
            'timestamp': now.isoformat(),
            'type': request_type,
            'ip': client_ip
        })
        
        # Mantener solo las últimas 1000 entradas
        if len(self.requests_timeline) > 1000:
            self.requests_timeline.pop(0)
        
        # Contadores por tipo de ataque
        self.attack_types_count[request_type] = self.attack_types_count.get(request_type, 0) + 1
        
        # User agents
        if user_agent:
            self.user_agents_count[user_agent] = self.user_agents_count.get(user_agent, 0) + 1
        
        # Estadísticas por hora
        hour = now.hour
        self.hourly_stats[hour] += 1
        
        # Tiempos de respuesta
        self.response_times.append(response_time)
        if len(self.response_times) > 1000:
            self.response_times.pop(0)
        
        # Intensidad de ataque (RPS)
        current_minute = now.replace(second=0, microsecond=0)
        if not self.attack_intensity or self.attack_intensity[-1]['time'] != current_minute:
            self.attack_intensity.append({'time': current_minute, 'count': 1})
        else:
            self.attack_intensity[-1]['count'] += 1
        
        # Mantener solo los últimos 60 minutos
        if len(self.attack_intensity) > 60:
            self.attack_intensity.pop(0)
        
        # Detectar patrones de ataque sospechosos
        if self.ip_request_count.get(client_ip, 0) > 100:
            self.add_security_alert(
                'high_volume_attack',
                f'IP {client_ip} ha enviado {self.ip_request_count[client_ip]} requests',
                'high'
            )
    
    def get_dashboard_data(self):
        """Obtener datos para el dashboard"""
        now = datetime.now()
        elapsed = (now - self.start_time).total_seconds()
        
        # Top IPs atacantes
        top_ips = sorted(self.ip_request_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Top User Agents
        top_user_agents = sorted(self.user_agents_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Calcular RPS actual (último minuto)
        recent_requests = [r for r in self.requests_timeline 
                          if datetime.fromisoformat(r['timestamp']) > now - timedelta(minutes=1)]
        current_rps = len(recent_requests) / 60 if recent_requests else 0
        
        return {
            'summary': {
                'total_requests': self.total_requests,
                'unique_ips': len(self.client_ips),
                'uptime_seconds': elapsed,
                'current_rps': round(current_rps, 2),
                'avg_response_time': round(sum(self.response_times)/len(self.response_times), 3) if self.response_times else 0
            },
            'attack_types': self.attack_types_count,
            'top_ips': [{'ip': ip, 'count': count} for ip, count in top_ips],
            'top_user_agents': [{'agent': agent, 'count': count} for agent, count in top_user_agents],
            'hourly_stats': self.hourly_stats,
            'requests_timeline': self.requests_timeline[-100:],  # Últimos 100
            'attack_intensity': [{'time': item['time'].isoformat(), 'count': item['count']} 
                               for item in self.attack_intensity],
            'security_alerts': self.security_alerts[-20:],  # Últimas 20 alertas
            'response_times': self.response_times[-100:],  # Últimos 100
            'status': 'active' if self.is_running else 'stopped'
        }

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP Server que maneja múltiples conexiones simultáneas"""
    allow_reuse_address = True
    daemon_threads = True

class VisualHoneypotHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, honeypot_instance=None, **kwargs):
        self.honeypot = honeypot_instance
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Suprimir logs HTTP por defecto para usar nuestro sistema"""
        pass
    
    def get_session_id(self):
        """Obtener session ID de las cookies"""
        cookies = self.headers.get('Cookie', '')
        for cookie in cookies.split(';'):
            if 'session_id=' in cookie:
                return cookie.split('session_id=')[1].strip()
        return None
    
    def send_login_page(self):
        """Enviar página de login"""
        html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🍯 Honeypot Login - Visual Dashboard</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .login-container {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                    border: 1px solid rgba(255, 255, 255, 0.18);
                    text-align: center;
                    min-width: 400px;
                }
                .logo {
                    font-size: 4em;
                    margin-bottom: 10px;
                }
                h1 {
                    color: white;
                    margin-bottom: 30px;
                    font-weight: 300;
                }
                .form-group {
                    margin-bottom: 20px;
                    text-align: left;
                }
                label {
                    color: rgba(255, 255, 255, 0.8);
                    display: block;
                    margin-bottom: 5px;
                    font-weight: 500;
                }
                input {
                    width: 100%;
                    padding: 15px;
                    border: none;
                    border-radius: 10px;
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    font-size: 16px;
                }
                input::placeholder {
                    color: rgba(255, 255, 255, 0.6);
                }
                input:focus {
                    outline: none;
                    background: rgba(255, 255, 255, 0.3);
                }
                .login-btn {
                    width: 100%;
                    padding: 15px;
                    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                    border: none;
                    border-radius: 10px;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: all 0.3s;
                }
                .login-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }
                .info {
                    color: rgba(255, 255, 255, 0.7);
                    margin-top: 20px;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <div class="logo">🍯</div>
                <h1>Visual Honeypot Dashboard</h1>
                <form method="POST" action="/login">
                    <div class="form-group">
                        <label for="username">Usuario:</label>
                        <input type="text" id="username" name="username" placeholder="Ingresa tu usuario" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Contraseña:</label>
                        <input type="password" id="password" name="password" placeholder="Ingresa tu contraseña" required>
                    </div>
                    <button type="submit" class="login-btn">🔐 Acceder al Dashboard</button>
                </form>
                <div class="info">
                    <strong>Sistema de Monitoreo DDoS</strong><br>
                    dessarrollado con ❤️ por Alvaro Manzo
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_dashboard(self):
        """Enviar dashboard principal con todas las gráficas y datos"""
        html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🍯 Visual Honeypot Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: #0f0f23;
                    color: #ffffff;
                    overflow-x: auto;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                    text-align: center;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                }
                .header h1 {
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }
                .status-bar {
                    display: flex;
                    justify-content: space-around;
                    padding: 15px;
                    background: rgba(255,255,255,0.1);
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }
                .status-item {
                    text-align: center;
                    min-width: 120px;
                }
                .status-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #00ff88;
                }
                .dashboard {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
                    gap: 20px;
                    padding: 20px;
                    max-width: 1800px;
                    margin: 0 auto;
                }
                .card {
                    background: rgba(255,255,255,0.05);
                    border-radius: 15px;
                    padding: 20px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.1);
                    min-height: 350px;
                }
                .card h3 {
                    margin-bottom: 15px;
                    color: #00ff88;
                    font-size: 1.3em;
                    border-bottom: 2px solid #00ff88;
                    padding-bottom: 5px;
                }
                .chart-container {
                    position: relative;
                    height: 280px;
                }
                .data-table {
                    max-height: 250px;
                    overflow-y: auto;
                }
                .data-table table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .data-table th, .data-table td {
                    padding: 8px 12px;
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                    text-align: left;
                }
                .data-table th {
                    background: rgba(0,255,136,0.2);
                    font-weight: bold;
                    position: sticky;
                    top: 0;
                }
                .alert {
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 5px;
                    font-size: 0.9em;
                }
                .alert-high { background: rgba(255,71,87,0.3); border-left: 4px solid #ff4757; }
                .alert-medium { background: rgba(255,165,0,0.3); border-left: 4px solid #ffa500; }
                .alert-low { background: rgba(0,255,136,0.3); border-left: 4px solid #00ff88; }
                .metric {
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                }
                .metric-value {
                    color: #00ff88;
                    font-weight: bold;
                }
                .controls {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    display: flex;
                    gap: 10px;
                }
                .btn {
                    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                    border: none;
                    border-radius: 25px;
                    color: white;
                    padding: 12px 20px;
                    font-size: 14px;
                    cursor: pointer;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    transition: all 0.3s;
                    text-decoration: none;
                    display: inline-block;
                }
                .btn:hover {
                    transform: translateY(-2px);
                }
                .timeline-entry {
                    padding: 4px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.05);
                    font-family: monospace;
                    font-size: 12px;
                }
                .timeline-get { color: #00ff88; }
                .timeline-post { color: #ff6b6b; }
                .timeline-tcp { color: #ffa500; }
                .timeline-error { color: #ff4757; }
                .auto-refresh {
                    color: #00ff88;
                    font-size: 0.9em;
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🍯 Visual Honeypot Dashboard</h1>
                <p>Sistema de Monitoreo DDoS en Tiempo Real - Alvaro Manzo</p>
                <div class="auto-refresh">⚡ Auto-actualización cada 3 segundos</div>
            </div>
            
            <div class="status-bar">
                <div class="status-item">
                    <div class="status-value" id="total-requests">0</div>
                    <div>Total Requests</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="unique-ips">0</div>
                    <div>IPs Únicas</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="current-rps">0.0</div>
                    <div>RPS Actual</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="uptime">0</div>
                    <div>Uptime (min)</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="avg-response-time">0</div>
                    <div>Resp. Time (ms)</div>
                </div>
            </div>
            
            <div class="dashboard">
                <!-- Gráfica de Tipos de Ataque -->
                <div class="card">
                    <h3>📊 Distribución de Tipos de Ataque</h3>
                    <div class="chart-container">
                        <canvas id="attackTypesChart"></canvas>
                    </div>
                </div>
                
                <!-- Gráfica de Intensidad en Tiempo Real -->
                <div class="card">
                    <h3>⚡ Intensidad de Ataques (Tiempo Real)</h3>
                    <div class="chart-container">
                        <canvas id="intensityChart"></canvas>
                    </div>
                </div>
                
                <!-- Top IPs Atacantes -->
                <div class="card">
                    <h3>🎯 Top IPs Atacantes</h3>
                    <div class="data-table">
                        <table>
                            <thead>
                                <tr><th>IP Address</th><th>Requests</th><th>Porcentaje</th></tr>
                            </thead>
                            <tbody id="top-ips-table">
                                <tr><td colspan="3">No hay datos disponibles</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Estadísticas por Hora -->
                <div class="card">
                    <h3>🕐 Distribución Horaria de Ataques</h3>
                    <div class="chart-container">
                        <canvas id="hourlyChart"></canvas>
                    </div>
                </div>
                
                <!-- Timeline de Ataques en Vivo -->
                <div class="card">
                    <h3>📈 Timeline en Vivo</h3>
                    <div id="attack-timeline" style="max-height: 280px; overflow-y: auto;">
                        <div class="timeline-entry">Esperando ataques...</div>
                    </div>
                </div>
                
                <!-- Alertas de Seguridad -->
                <div class="card">
                    <h3>🚨 Alertas de Seguridad</h3>
                    <div id="security-alerts" style="max-height: 280px; overflow-y: auto;">
                        <div class="alert alert-low">Sistema iniciado correctamente</div>
                    </div>
                </div>
                
                <!-- Top User Agents -->
                <div class="card">
                    <h3>🌐 Top User Agents</h3>
                    <div class="data-table">
                        <table>
                            <thead>
                                <tr><th>User Agent</th><th>Count</th></tr>
                            </thead>
                            <tbody id="user-agents-table">
                                <tr><td colspan="2">No hay datos disponibles</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Métricas del Sistema -->
                <div class="card">
                    <h3>⚙️ Métricas del Sistema</h3>
                    <div id="system-metrics">
                        <div class="metric">
                            <span>Estado:</span>
                            <span class="metric-value">Inicializando...</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="controls">
                <button class="btn" onclick="loadDashboardData()">🔄 Actualizar</button>
                <a href="/logout" class="btn">🚪 Logout</a>
            </div>
            
            <script>
                let charts = {};
                
                // Configuración global de Chart.js
                Chart.defaults.color = '#ffffff';
                Chart.defaults.borderColor = 'rgba(255,255,255,0.1)';
                
                function initCharts() {
                    // Gráfica de Tipos de Ataque (Doughnut)
                    const attackTypesCtx = document.getElementById('attackTypesChart').getContext('2d');
                    charts.attackTypes = new Chart(attackTypesCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['GET Requests', 'POST Requests', 'TCP Connections', 'Errors'],
                            datasets: [{
                                data: [0, 0, 0, 0],
                                backgroundColor: ['#00ff88', '#ff6b6b', '#ffa500', '#ff4757'],
                                borderWidth: 3,
                                borderColor: '#0f0f23'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { 
                                    position: 'bottom',
                                    labels: { color: '#ffffff', padding: 20 }
                                }
                            }
                        }
                    });
                    
                    // Gráfica de Intensidad (Line)
                    const intensityCtx = document.getElementById('intensityChart').getContext('2d');
                    charts.intensity = new Chart(intensityCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Requests por minuto',
                                data: [],
                                borderColor: '#00ff88',
                                backgroundColor: 'rgba(0,255,136,0.1)',
                                tension: 0.4,
                                fill: true,
                                pointBackgroundColor: '#00ff88',
                                pointBorderColor: '#ffffff',
                                pointBorderWidth: 2
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: { 
                                    beginAtZero: true,
                                    grid: { color: 'rgba(255,255,255,0.1)' }
                                },
                                x: {
                                    grid: { color: 'rgba(255,255,255,0.1)' }
                                }
                            },
                            plugins: {
                                legend: { 
                                    labels: { color: '#ffffff' }
                                }
                            }
                        }
                    });
                    
                    // Gráfica Horaria (Bar)
                    const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
                    charts.hourly = new Chart(hourlyCtx, {
                        type: 'bar',
                        data: {
                            labels: Array.from({length: 24}, (_, i) => i + ':00'),
                            datasets: [{
                                label: 'Requests por hora',
                                data: new Array(24).fill(0),
                                backgroundColor: 'rgba(0,255,136,0.6)',
                                borderColor: '#00ff88',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: { 
                                    beginAtZero: true,
                                    grid: { color: 'rgba(255,255,255,0.1)' }
                                },
                                x: {
                                    grid: { color: 'rgba(255,255,255,0.1)' }
                                }
                            },
                            plugins: {
                                legend: { 
                                    labels: { color: '#ffffff' }
                                }
                            }
                        }
                    });
                }
                
                function updateCharts(data) {
                    // Actualizar gráfica de tipos de ataque
                    const attackTypes = data.attack_types || {};
                    charts.attackTypes.data.datasets[0].data = [
                        attackTypes.GET || 0,
                        attackTypes.POST || 0,
                        attackTypes.TCP || 0,
                        attackTypes.ERROR || 0
                    ];
                    charts.attackTypes.update();
                    
                    // Actualizar gráfica de intensidad
                    const intensity = data.attack_intensity || [];
                    charts.intensity.data.labels = intensity.slice(-20).map(item => {
                        const time = new Date(item.time);
                        return time.getHours() + ':' + String(time.getMinutes()).padStart(2, '0');
                    });
                    charts.intensity.data.datasets[0].data = intensity.slice(-20).map(item => item.count);
                    charts.intensity.update();
                    
                    // Actualizar gráfica horaria
                    charts.hourly.data.datasets[0].data = data.hourly_stats || new Array(24).fill(0);
                    charts.hourly.update();
                }
                
                function loadDashboardData() {
                    fetch('/api/data')
                        .then(response => response.json())
                        .then(data => {
                            console.log('Data received:', data);
                            
                            // Actualizar estadísticas principales
                            document.getElementById('total-requests').textContent = data.summary.total_requests || 0;
                            document.getElementById('unique-ips').textContent = data.summary.unique_ips || 0;
                            document.getElementById('current-rps').textContent = data.summary.current_rps || '0.0';
                            document.getElementById('uptime').textContent = Math.round((data.summary.uptime_seconds || 0) / 60);
                            document.getElementById('avg-response-time').textContent = (data.summary.avg_response_time || 0).toFixed(1);
                            
                            // Actualizar gráficas
                            updateCharts(data);
                            
                            // Actualizar tablas y otros elementos
                            updateTopIpsTable(data.top_ips || []);
                            updateUserAgentsTable(data.top_user_agents || []);
                            updateTimeline(data.requests_timeline || []);
                            updateSecurityAlerts(data.security_alerts || []);
                            updateSystemMetrics(data.summary || {});
                        })
                        .catch(error => {
                            console.error('Error loading data:', error);
                        });
                }
                
                function updateTopIpsTable(topIps) {
                    const tableBody = document.getElementById('top-ips-table');
                    const total = topIps.reduce((sum, item) => sum + item.count, 0);
                    
                    if (topIps.length === 0) {
                        tableBody.innerHTML = '<tr><td colspan="3">No hay datos disponibles</td></tr>';
                        return;
                    }
                    
                    tableBody.innerHTML = topIps.slice(0, 10).map(item => `
                        <tr>
                            <td>${item.ip}</td>
                            <td>${item.count}</td>
                            <td>${total > 0 ? ((item.count / total) * 100).toFixed(1) : 0}%</td>
                        </tr>
                    `).join('');
                }
                
                function updateUserAgentsTable(userAgents) {
                    const tableBody = document.getElementById('user-agents-table');
                    
                    if (userAgents.length === 0) {
                        tableBody.innerHTML = '<tr><td colspan="2">No hay datos disponibles</td></tr>';
                        return;
                    }
                    
                    tableBody.innerHTML = userAgents.slice(0, 8).map(item => `
                        <tr>
                            <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">${item.agent}</td>
                            <td>${item.count}</td>
                        </tr>
                    `).join('');
                }
                
                function updateTimeline(timeline) {
                    const container = document.getElementById('attack-timeline');
                    
                    if (timeline.length === 0) {
                        container.innerHTML = '<div class="timeline-entry">Esperando ataques...</div>';
                        return;
                    }
                    
                    container.innerHTML = timeline.slice(-30).reverse().map(entry => {
                        const time = new Date(entry.timestamp).toLocaleTimeString();
                        const cssClass = `timeline-${entry.type.toLowerCase()}`;
                        return `<div class="timeline-entry ${cssClass}">[${time}] ${entry.type} request from ${entry.ip}</div>`;
                    }).join('');
                }
                
                function updateSecurityAlerts(alerts) {
                    const container = document.getElementById('security-alerts');
                    
                    if (alerts.length === 0) {
                        container.innerHTML = '<div class="alert alert-low">No hay alertas recientes</div>';
                        return;
                    }
                    
                    container.innerHTML = alerts.slice(-15).reverse().map(alert => {
                        const time = new Date(alert.timestamp).toLocaleTimeString();
                        return `<div class="alert alert-${alert.severity}">[${time}] ${alert.message}</div>`;
                    }).join('');
                }
                
                function updateSystemMetrics(summary) {
                    const container = document.getElementById('system-metrics');
                    container.innerHTML = `
                        <div class="metric">
                            <span>Estado del Sistema:</span>
                            <span class="metric-value">${summary.status || 'Activo'}</span>
                        </div>
                        <div class="metric">
                            <span>Tiempo Promedio de Respuesta:</span>
                            <span class="metric-value">${(summary.avg_response_time || 0).toFixed(1)}ms</span>
                        </div>
                        <div class="metric">
                            <span>Uptime Total:</span>
                            <span class="metric-value">${Math.floor((summary.uptime_seconds || 0) / 60)}min</span>
                        </div>
                        <div class="metric">
                            <span>RPS Máximo:</span>
                            <span class="metric-value">${summary.current_rps || 0}</span>
                        </div>
                    `;
                }
                
                // Inicializar dashboard
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('Initializing dashboard...');
                    initCharts();
                    loadDashboardData();
                    
                    // Auto-actualizar cada 3 segundos
                    setInterval(loadDashboardData, 3000);
                });
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def do_GET(self):
        """Manejar requests GET"""
        start_time = time.time()
        client_ip = self.client_address[0]
        
        # Rutas del dashboard
        if self.path == '/':
            session_id = self.get_session_id()
            if session_id and self.honeypot.is_authenticated(session_id):
                self.send_dashboard()
                return
            else:
                self.send_login_page()
                return
        
        elif self.path == '/api/data':
            session_id = self.get_session_id()
            if session_id and self.honeypot.is_authenticated(session_id):
                data = self.honeypot.get_dashboard_data()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
                return
            else:
                self.send_response(401)
                self.end_headers()
                return
        
        elif self.path == '/logout':
            session_id = self.get_session_id()
            if session_id and session_id in self.honeypot.sessions:
                del self.honeypot.sessions[session_id]
            self.send_response(302)
            self.send_header('Location', '/')
            self.send_header('Set-Cookie', 'session_id=; expires=Thu, 01 Jan 1970 00:00:00 GMT')
            self.end_headers()
            return
        
        # Simular ataque real para testing
        else:
            user_agent = self.headers.get('User-Agent', 'Unknown')
            response_time = time.time() - start_time
            
            self.honeypot.total_requests += 1
            self.honeypot.get_requests += 1
            self.honeypot.client_ips.add(client_ip)
            
            if client_ip not in self.honeypot.ip_request_count:
                self.honeypot.ip_request_count[client_ip] = 0
            self.honeypot.ip_request_count[client_ip] += 1
            
            self.honeypot.update_metrics('GET', client_ip, user_agent, response_time * 1000)
            
            # Detectar ataques de alta frecuencia
            if self.honeypot.ip_request_count[client_ip] % 50 == 0:
                self.honeypot.add_security_alert(
                    'high_frequency_attack',
                    f'IP {client_ip} ha realizado {self.honeypot.ip_request_count[client_ip]} requests',
                    'high' if self.honeypot.ip_request_count[client_ip] > 200 else 'medium'
                )
            
            try:
                if self.honeypot.ip_request_count[client_ip] > self.honeypot.max_requests_per_ip:
                    self.send_response(429)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>429 - Too Many Requests</h1>')
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Server', 'HoneypotServer/2.0')
                    self.end_headers()
                    
                    response = f"""
                    <html>
                    <head><title>DDoS Testing Target</title></head>
                    <body>
                        <h1>🎯 Honeypot Target Response</h1>
                        <p>Request #{self.honeypot.total_requests} processed successfully</p>
                        <p>Client IP: {client_ip}</p>
                        <p>Path: {self.path}</p>
                        <p>Timestamp: {datetime.now()}</p>
                        <p>Response Time: {response_time*1000:.2f}ms</p>
                        <hr>
                        <p><em>This is a honeypot target for authorized DDoS testing</em></p>
                    </body>
                    </html>
                    """
                    self.wfile.write(response.encode())
                    
            except Exception as e:
                self.honeypot.error_requests += 1
                self.honeypot.update_metrics('ERROR', client_ip, user_agent, response_time * 1000)
                self.honeypot.logger.error(f"Error handling GET from {client_ip}: {e}")
    
    def do_POST(self):
        """Manejar requests POST"""
        start_time = time.time()
        client_ip = self.client_address[0]
        
        # Login
        if self.path == '/login':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parsear datos del formulario
            form_data = parse_qs(post_data)
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            
            if self.honeypot.authenticate_user(username, password):
                # Crear sesión
                session_id = self.honeypot.generate_session_id()
                self.honeypot.sessions[session_id] = {
                    'username': username,
                    'created': datetime.now(),
                    'expires': datetime.now() + timedelta(hours=8),
                    'ip': client_ip
                }
                
                # Redireccionar al dashboard
                self.send_response(302)
                self.send_header('Location', '/')
                self.send_header('Set-Cookie', f'session_id={session_id}; HttpOnly; Path=/')
                self.end_headers()
                
                self.honeypot.add_security_alert(
                    'successful_login',
                    f'Usuario {username} autenticado exitosamente desde {client_ip}',
                    'low'
                )
            else:
                # Login fallido
                self.send_login_page()
                self.honeypot.add_security_alert(
                    'failed_login',
                    f'Intento de login fallido desde {client_ip} (usuario: {username})',
                    'medium'
                )
            return
        
        # Ataques POST normales
        else:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''
            user_agent = self.headers.get('User-Agent', 'Unknown')
            response_time = time.time() - start_time
            
            self.honeypot.total_requests += 1
            self.honeypot.post_requests += 1
            self.honeypot.client_ips.add(client_ip)
            
            if client_ip not in self.honeypot.ip_request_count:
                self.honeypot.ip_request_count[client_ip] = 0
            self.honeypot.ip_request_count[client_ip] += 1
            
            self.honeypot.update_metrics('POST', client_ip, user_agent, response_time * 1000)
            
            # Detectar POST payloads grandes
            if content_length > 50000:
                self.honeypot.add_security_alert(
                    'large_payload_attack',
                    f'POST payload de {content_length} bytes desde {client_ip}',
                    'high'
                )
            
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Server', 'HoneypotServer/2.0')
                self.end_headers()
                
                response = {
                    'status': 'success',
                    'message': 'POST data received and processed',
                    'request_id': self.honeypot.total_requests,
                    'client_ip': client_ip,
                    'data_size': content_length,
                    'response_time_ms': round(response_time * 1000, 2),
                    'timestamp': datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.honeypot.error_requests += 1
                self.honeypot.update_metrics('ERROR', client_ip, user_agent, response_time * 1000)
                self.honeypot.logger.error(f"Error handling POST from {client_ip}: {e}")

class HoneypotManager:
    def __init__(self):
        self.honeypot = VisualDDoSHoneypot()
        self.http_server = None
        self.running = False
    
    def start(self):
        """Iniciar honeypot completo"""
        self.honeypot.print_banner()
        
        try:
            # Configurar manejador de señales para shutdown limpio
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Iniciar HTTP server
            def make_handler(*args, **kwargs):
                return VisualHoneypotHTTPHandler(*args, honeypot_instance=self.honeypot, **kwargs)
            
            self.http_server = ThreadedHTTPServer(('0.0.0.0', 8080), make_handler)
            
            self.running = True
            self.honeypot.is_running = True
            
            print("\n\033[92m[INICIADO]\033[0m Visual Honeypot Dashboard:")
            print(f"  🌐 Dashboard: http://localhost:8080")
            print(f"  👤 Usuario: Alvaro")
            print(f"  🔑 Contraseña: falcon40")
            print(f"  📊 Gráficas en tiempo real habilitadas")
            print(f"  🔄 Auto-actualización cada 3 segundos")
            print("\n\033[93m[TESTING]\033[0m Para atacar el honeypot:")
            print(f"  python3 ddos.py")
            print(f"  URL objetivo: http://localhost:8080/target")
            print("\n\033[91m[CONTROL]\033[0m Presiona Ctrl+C para detener")
            print("="*60)
            
            # Agregar alerta de inicio
            self.honeypot.add_security_alert(
                'system_start',
                'Visual Honeypot Dashboard iniciado correctamente',
                'low'
            )
            
            # Mantener servidor vivo
            self.http_server.serve_forever()
                
        except Exception as e:
            self.honeypot.logger.error(f"Error starting honeypot: {e}")
        finally:
            self.stop()
    
    def signal_handler(self, signum, frame):
        """Manejar señales de shutdown"""
        print(f"\n\033[93m[SHUTDOWN]\033[0m Señal recibida ({signum}), deteniendo honeypot...")
        self.stop()
    
    def stop(self):
        """Detener honeypot y mostrar estadísticas finales"""
        self.running = False
        self.honeypot.is_running = False
        
        if self.http_server:
            self.http_server.shutdown()
        
        self.show_final_stats()
        sys.exit(0)
    
    def show_final_stats(self):
        """Mostrar estadísticas finales detalladas"""
        elapsed = (datetime.now() - self.honeypot.start_time).total_seconds()
        
        print(f"\n\n\033[96m{'='*70}")
        print("              ESTADÍSTICAS FINALES DEL HONEYPOT")
        print(f"{'='*70}\033[0m")
        print(f"⏱️  Tiempo activo: {elapsed:.2f} segundos ({elapsed/60:.1f} minutos)")
        print(f"📤 Total requests: {self.honeypot.total_requests}")
        print(f"🌊 GET requests: {self.honeypot.get_requests}")
        print(f"💥 POST requests: {self.honeypot.post_requests}")
        print(f"❌ Errores: {self.honeypot.error_requests}")
        print(f"📍 IPs únicas atacantes: {len(self.honeypot.client_ips)}")
        print(f"⚡ Promedio RPS: {self.honeypot.total_requests / elapsed:.2f}")
        print(f"🚨 Alertas de seguridad: {len(self.honeypot.security_alerts)}")
        
        # Top IPs atacantes
        if self.honeypot.ip_request_count:
            print("\n🎯 Top 5 IPs atacantes:")
            sorted_ips = sorted(self.honeypot.ip_request_count.items(), 
                              key=lambda x: x[1], reverse=True)[:5]
            for i, (ip, count) in enumerate(sorted_ips, 1):
                percentage = (count / self.honeypot.total_requests) * 100 if self.honeypot.total_requests > 0 else 0
                print(f"  {i}. {ip}: {count} requests ({percentage:.1f}%)")
        
        # Top User Agents
        if self.honeypot.user_agents_count:
            print("\n🌐 Top 3 User Agents:")
            sorted_agents = sorted(self.honeypot.user_agents_count.items(), 
                                 key=lambda x: x[1], reverse=True)[:3]
            for i, (agent, count) in enumerate(sorted_agents, 1):
                short_agent = agent[:50] + "..." if len(agent) > 50 else agent
                print(f"  {i}. {short_agent}: {count} requests")
        
        # Guardar log detallado
        self.save_final_report()
        print(f"\n📋 Informe completo guardado en: honeypot_final_report.json")
        print(f"📊 Dashboard data guardado en: dashboard_session_data.json")
    
    def save_final_report(self):
        """Guardar informe final completo"""
        final_report = {
            'session_info': {
                'start_time': self.honeypot.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.honeypot.start_time).total_seconds(),
                'honeypot_version': '2.0_visual'
            },
            'attack_summary': {
                'total_requests': self.honeypot.total_requests,
                'get_requests': self.honeypot.get_requests,
                'post_requests': self.honeypot.post_requests,
                'tcp_connections': self.honeypot.tcp_connections,
                'error_requests': self.honeypot.error_requests,
                'unique_ips': len(self.honeypot.client_ips),
                'unique_user_agents': len(self.honeypot.user_agents_count)
            },
            'detailed_metrics': {
                'attack_types_breakdown': self.honeypot.attack_types_count,
                'hourly_distribution': self.honeypot.hourly_stats,
                'top_attacking_ips': dict(sorted(self.honeypot.ip_request_count.items(), 
                                                key=lambda x: x[1], reverse=True)[:10]),
                'top_user_agents': dict(sorted(self.honeypot.user_agents_count.items(), 
                                             key=lambda x: x[1], reverse=True)[:10]),
                'response_time_stats': {
                    'avg': sum(self.honeypot.response_times)/len(self.honeypot.response_times) if self.honeypot.response_times else 0,
                    'min': min(self.honeypot.response_times) if self.honeypot.response_times else 0,
                    'max': max(self.honeypot.response_times) if self.honeypot.response_times else 0
                }
            },
            'security_events': self.honeypot.security_alerts,
            'attack_timeline': self.honeypot.requests_timeline[-100:],  # Últimos 100
            'dashboard_data': self.honeypot.get_dashboard_data()
        }
        
        try:
            with open('honeypot_final_report.json', 'w') as f:
                json.dump(final_report, f, indent=2)
            
            # Guardar también datos de dashboard para análisis posterior
            with open('dashboard_session_data.json', 'w') as f:
                json.dump(self.honeypot.get_dashboard_data(), f, indent=2)
                
        except Exception as e:
            self.honeypot.logger.error(f"Error saving final report: {e}")

def main():
    print("\033[91m" + "="*70 + "\033[0m")
    print("\033[91m🍯 VISUAL HONEYPOT DASHBOARD PARA TESTING DE DDOS 🍯\033[0m")
    print("\033[91m" + "="*70 + "\033[0m")
    print("Honeypot visual profesional con dashboard web en tiempo real.")
    print("Incluye gráficas interactivas, métricas avanzadas y sistema de login.")
    print("")
    print("🔐 Credenciales de acceso:")
    print("   Usuario: Alvaro")
    print("   Contraseña: falcon40")
    print("")
    print("📊 Características:")
    print("   • Dashboard web interactivo en tiempo real")
    print("   • Gráficas con Chart.js (tipos de ataque, intensidad, horarios)")
    print("   • Sistema de alertas de seguridad")
    print("   • Métricas avanzadas y timeline en vivo")
    print("   • Auto-actualización cada 3 segundos")
    print("\033[91m" + "="*70 + "\033[0m")
    
    manager = HoneypotManager()
    manager.start()

if __name__ == "__main__":
    main()
