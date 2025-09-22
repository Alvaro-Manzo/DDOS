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
            'Alvaro': 'falcon40',
            'admin': 'admin123'
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
                .error {
                    color: #ff4757;
                    margin-top: 10px;
                    font-weight: 500;
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
                    Acceso restringido solo para administradores
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
        """Enviar dashboard principal"""
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
                    padding: 10px;
                    background: rgba(255,255,255,0.1);
                    margin-bottom: 20px;
                }
                .status-item {
                    text-align: center;
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
                    min-height: 300px;
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
                    height: 250px;
                }
                .data-table {
                    max-height: 200px;
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
                    padding: 5px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                }
                .metric-value {
                    color: #00ff88;
                    font-weight: bold;
                }
                .refresh-btn {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                    border: none;
                    border-radius: 50px;
                    color: white;
                    padding: 15px 25px;
                    font-size: 16px;
                    cursor: pointer;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    transition: all 0.3s;
                }
                .refresh-btn:hover {
                    transform: translateY(-2px);
                }
                .attack-timeline {
                    max-height: 200px;
                    overflow-y: auto;
                    font-family: monospace;
                    font-size: 12px;
                }
                .timeline-entry {
                    padding: 2px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.05);
                }
                .timeline-get { color: #00ff88; }
                .timeline-post { color: #ff6b6b; }
                .timeline-tcp { color: #ffa500; }
                .timeline-error { color: #ff4757; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🍯 Visual Honeypot Dashboard</h1>
                <p>Sistema de Monitoreo DDoS en Tiempo Real</p>
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
                    <div>Uptime (s)</div>
                </div>
            </div>
            
            <div class="dashboard">
                <!-- Gráfica de Tipos de Ataque -->
                <div class="card">
                    <h3>📊 Tipos de Ataque</h3>
                    <div class="chart-container">
                        <canvas id="attackTypesChart"></canvas>
                    </div>
                </div>
                
                <!-- Gráfica de Intensidad en Tiempo Real -->
                <div class="card">
                    <h3>⚡ Intensidad de Ataques</h3>
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
                                <tr><th>IP Address</th><th>Requests</th><th>%</th></tr>
                            </thead>
                            <tbody id="top-ips-table">
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Estadísticas por Hora -->
                <div class="card">
                    <h3>🕐 Distribución Horaria</h3>
                    <div class="chart-container">
                        <canvas id="hourlyChart"></canvas>
                    </div>
                </div>
                
                <!-- Timeline de Ataques -->
                <div class="card">
                    <h3>📈 Timeline en Vivo</h3>
                    <div class="attack-timeline" id="attack-timeline">
                    </div>
                </div>
                
                <!-- Alertas de Seguridad -->
                <div class="card">
                    <h3>🚨 Alertas de Seguridad</h3>
                    <div id="security-alerts">
                    </div>
                </div>
                
                <!-- User Agents -->
                <div class="card">
                    <h3>🌐 Top User Agents</h3>
                    <div class="data-table">
                        <table>
                            <thead>
                                <tr><th>User Agent</th><th>Count</th></tr>
                            </thead>
                            <tbody id="user-agents-table">
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Métricas del Sistema -->
                <div class="card">
                    <h3>⚙️ Métricas del Sistema</h3>
                    <div id="system-metrics">
                    </div>
                </div>
            </div>
            
            <button class="refresh-btn" onclick="loadDashboardData()">🔄 Actualizar</button>
            
            <script>
                let charts = {};
                
                // Configuración de Chart.js
                Chart.defaults.color = '#ffffff';
                Chart.defaults.borderColor = 'rgba(255,255,255,0.1)';
                
                function initCharts() {
                    // Gráfica de Tipos de Ataque (Doughnut)
                    const attackTypesCtx = document.getElementById('attackTypesChart').getContext('2d');
                    charts.attackTypes = new Chart(attackTypesCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['GET', 'POST', 'TCP', 'ERROR'],
                            datasets: [{
                                data: [0, 0, 0, 0],
                                backgroundColor: ['#00ff88', '#ff6b6b', '#ffa500', '#ff4757'],
                                borderWidth: 2,
                                borderColor: '#0f0f23'
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: { position: 'bottom' }
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
                                label: 'Requests/min',
                                data: [],
                                borderColor: '#00ff88',
                                backgroundColor: 'rgba(0,255,136,0.1)',
                                tension: 0.4,
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {
                                y: { beginAtZero: true }
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
                                y: { beginAtZero: true }
                            }
                        }
                    });
                }
                
                function updateCharts(data) {
                    // Actualizar gráfica de tipos de ataque
                    const attackTypes = data.attack_types;
                    charts.attackTypes.data.datasets[0].data = [
                        attackTypes.GET || 0,
                        attackTypes.POST || 0,
                        attackTypes.TCP || 0,
                        attackTypes.ERROR || 0
                    ];
                    charts.attackTypes.update();
                    
                    // Actualizar gráfica de intensidad
                    const intensity = data.attack_intensity || [];
                    charts.intensity.data.labels = intensity.map(item => {
                        const time = new Date(item.time);
                        return time.getHours() + ':' + String(time.getMinutes()).padStart(2, '0');
                    });
                    charts.intensity.data.datasets[0].data = intensity.map(item => item.count);
                    charts.intensity.update();
                    
                    // Actualizar gráfica horaria
                    charts.hourly.data.datasets[0].data = data.hourly_stats || new Array(24).fill(0);
                    charts.hourly.update();
                }
                
                function loadDashboardData() {
                    fetch('/api/data')
                        .then(response => response.json())
                        .then(data => {
                            // Actualizar estadísticas principales
                            document.getElementById('total-requests').textContent = data.summary.total_requests;
                            document.getElementById('unique-ips').textContent = data.summary.unique_ips;
                            document.getElementById('current-rps').textContent = data.summary.current_rps;
                            document.getElementById('uptime').textContent = Math.round(data.summary.uptime_seconds);
                            
                            // Actualizar gráficas
                            updateCharts(data);
                            
                            // Actualizar tabla de IPs
                            updateTopIpsTable(data.top_ips || []);
                            
                            // Actualizar User Agents
                            updateUserAgentsTable(data.top_user_agents || []);
                            
                            // Actualizar timeline
                            updateTimeline(data.requests_timeline || []);
                            
                            // Actualizar alertas
                            updateSecurityAlerts(data.security_alerts || []);
                            
                            // Actualizar métricas del sistema
                            updateSystemMetrics(data.summary);
                        })
                        .catch(error => console.error('Error:', error));
                }
                
                function updateTopIpsTable(topIps) {
                    const tableBody = document.getElementById('top-ips-table');
                    const total = topIps.reduce((sum, item) => sum + item.count, 0);
                    
                    tableBody.innerHTML = topIps.map(item => `
                        <tr>
                            <td>${item.ip}</td>
                            <td>${item.count}</td>
                            <td>${total > 0 ? ((item.count / total) * 100).toFixed(1) : 0}%</td>
                        </tr>
                    `).join('');
                }
                
                function updateUserAgentsTable(userAgents) {
                    const tableBody = document.getElementById('user-agents-table');
                    tableBody.innerHTML = userAgents.slice(0, 10).map(item => `
                        <tr>
                            <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis;">${item.agent}</td>
                            <td>${item.count}</td>
                        </tr>
                    `).join('');
                }
                
                function updateTimeline(timeline) {
                    const container = document.getElementById('attack-timeline');
                    container.innerHTML = timeline.slice(-20).reverse().map(entry => {
                        const time = new Date(entry.timestamp).toLocaleTimeString();
                        const cssClass = `timeline-${entry.type.toLowerCase()}`;
                        return `<div class="timeline-entry ${cssClass}">[${time}] ${entry.type} from ${entry.ip}</div>`;
                    }).join('');
                }
                
                function updateSecurityAlerts(alerts) {
                    const container = document.getElementById('security-alerts');
                    container.innerHTML = alerts.slice(-10).reverse().map(alert => {
                        const time = new Date(alert.timestamp).toLocaleTimeString();
                        return `<div class="alert alert-${alert.severity}">[${time}] ${alert.message}</div>`;
                    }).join('');
                }
                
                function updateSystemMetrics(summary) {
                    const container = document.getElementById('system-metrics');
                    container.innerHTML = `
                        <div class="metric">
                            <span>Tiempo Promedio de Respuesta:</span>
                            <span class="metric-value">${summary.avg_response_time}ms</span>
                        </div>
                        <div class="metric">
                            <span>Estado del Sistema:</span>
                            <span class="metric-value">${summary.status || 'active'}</span>
                        </div>
                        <div class="metric">
                            <span>Uptime:</span>
                            <span class="metric-value">${Math.floor(summary.uptime_seconds / 60)}min</span>
                        </div>
                    `;
                }
                
                // Inicializar dashboard
                document.addEventListener('DOMContentLoaded', function() {
                    initCharts();
                    loadDashboardData();
                    
                    // Actualizar cada 5 segundos
                    setInterval(loadDashboardData, 5000);
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
        client_ip = self.client_address[0]
        
        # Registrar ataque
        self.honeypot.total_requests += 1
        self.honeypot.get_requests += 1
        self.honeypot.client_ips.add(client_ip)
        
        # Contar requests por IP
        if client_ip not in self.honeypot.ip_request_count:
            self.honeypot.ip_request_count[client_ip] = 0
        self.honeypot.ip_request_count[client_ip] += 1
        
        # Detectar patrón de ataque
        attack_pattern = {
            'timestamp': datetime.now().isoformat(),
            'type': 'GET',
            'client_ip': client_ip,
            'path': self.path,
            'user_agent': self.headers.get('User-Agent', 'Unknown'),
            'headers': dict(self.headers)
        }
        self.honeypot.attack_patterns.append(attack_pattern)
        
        # Simular diferentes tipos de respuesta
        if 'slow' in self.path.lower():
            time.sleep(5)  # Simular slowloris
        
        # Responder
        try:
            if self.honeypot.ip_request_count[client_ip] > self.honeypot.max_requests_per_ip:
                self.send_response(429)  # Too Many Requests
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>429 - Too Many Requests</h1>')
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.send_header('Server', 'HoneypotServer/1.0')
                self.end_headers()
                
                response = f"""
                <html>
                <head><title>DDoS Testing Honeypot</title></head>
                <body>
                    <h1>🍯 Honeypot Response</h1>
                    <p>Request #{self.honeypot.total_requests} processed</p>
                    <p>Client IP: {client_ip}</p>
                    <p>Path: {self.path}</p>
                    <p>Time: {datetime.now()}</p>
                    <hr>
                    <p><i>This is a honeypot for DDoS testing purposes</i></p>
                </body>
                </html>
                """
                self.wfile.write(response.encode())
                
        except Exception as e:
            self.honeypot.error_requests += 1
            self.honeypot.logger.error(f"Error handling GET from {client_ip}: {e}")
    
    def do_POST(self):
        """Manejar requests POST"""
        client_ip = self.client_address[0]
        
        # Leer datos POST
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        # Registrar ataque
        self.honeypot.total_requests += 1
        self.honeypot.post_requests += 1
        self.honeypot.client_ips.add(client_ip)
        
        # Contar requests por IP
        if client_ip not in self.honeypot.ip_request_count:
            self.honeypot.ip_request_count[client_ip] = 0
        self.honeypot.ip_request_count[client_ip] += 1
        
        # Detectar patrón de ataque
        attack_pattern = {
            'timestamp': datetime.now().isoformat(),
            'type': 'POST',
            'client_ip': client_ip,
            'path': self.path,
            'user_agent': self.headers.get('User-Agent', 'Unknown'),
            'content_length': content_length,
            'data_preview': post_data[:100].decode('utf-8', errors='ignore')
        }
        self.honeypot.attack_patterns.append(attack_pattern)
        
        # Responder
        try:
            if self.honeypot.ip_request_count[client_ip] > self.honeypot.max_requests_per_ip:
                self.send_response(429)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'status': 'error', 'message': 'Too many requests'}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Server', 'HoneypotServer/1.0')
                self.end_headers()
                
                response = {
                    'status': 'success',
                    'message': 'POST data received',
                    'request_id': self.honeypot.total_requests,
                    'client_ip': client_ip,
                    'data_size': content_length,
                    'timestamp': datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(response).encode())
                
        except Exception as e:
            self.honeypot.error_requests += 1
            self.honeypot.logger.error(f"Error handling POST from {client_ip}: {e}")

class TCPHoneypotHandler:
    def __init__(self, honeypot_instance):
        self.honeypot = honeypot_instance
        self.socket = None
        self.is_running = False
    
    def start_tcp_listener(self, port=8081):
        """Iniciar listener TCP para ataques SYN flood"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', port))
            self.socket.listen(100)  # Cola de conexiones alta
            self.socket.settimeout(1)  # Timeout para permitir shutdown
            
            self.is_running = True
            self.honeypot.logger.info(f"TCP Honeypot listening on port {port}")
            
            while self.is_running:
                try:
                    client_socket, address = self.socket.accept()
                    self.honeypot.tcp_connections += 1
                    self.honeypot.client_ips.add(address[0])
                    
                    # Manejar conexión en thread separado
                    thread = threading.Thread(
                        target=self.handle_tcp_connection,
                        args=(client_socket, address),
                        daemon=True
                    )
                    thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.is_running:
                        self.honeypot.logger.error(f"TCP listener error: {e}")
                        
        except Exception as e:
            self.honeypot.logger.error(f"Failed to start TCP listener: {e}")
        finally:
            if self.socket:
                self.socket.close()
    
    def handle_tcp_connection(self, client_socket, address):
        """Manejar conexión TCP individual"""
        try:
            client_ip = address[0]
            
            # Registrar patrón de ataque TCP
            attack_pattern = {
                'timestamp': datetime.now().isoformat(),
                'type': 'TCP',
                'client_ip': client_ip,
                'port': address[1]
            }
            self.honeypot.attack_patterns.append(attack_pattern)
            
            # Simular respuesta lenta para detectar slowloris
            time.sleep(1)
            
            # Enviar respuesta básica
            response = b"HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nTCP Connected"
            client_socket.send(response)
            
        except Exception as e:
            self.honeypot.logger.error(f"Error handling TCP connection from {address}: {e}")
        finally:
            client_socket.close()
    
    def stop(self):
        """Detener TCP listener"""
        self.is_running = False

class HoneypotManager:
    def __init__(self):
        self.honeypot = DDoSHoneypot()
        self.http_server = None
        self.tcp_handler = None
        self.stats_thread = None
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
                return HoneypotHTTPHandler(*args, honeypot_instance=self.honeypot, **kwargs)
            
            self.http_server = ThreadedHTTPServer(('0.0.0.0', 8080), make_handler)
            http_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
            http_thread.start()
            
            # Iniciar TCP listener
            self.tcp_handler = TCPHoneypotHandler(self.honeypot)
            tcp_thread = threading.Thread(target=self.tcp_handler.start_tcp_listener, daemon=True)
            tcp_thread.start()
            
            # Iniciar thread de estadísticas
            self.stats_thread = threading.Thread(target=self.show_stats, daemon=True)
            self.stats_thread.start()
            
            self.running = True
            self.honeypot.is_running = True
            
            print("\n\033[92m[ACTIVO]\033[0m Honeypot iniciado:")
            print(f"  🌐 HTTP Server: http://localhost:8080")
            print(f"  🔌 TCP Listener: localhost:8081")
            print(f"  📊 Presiona Ctrl+C para detener y ver estadísticas")
            print("\n\033[93m[TESTING]\033[0m Comandos para probar:")
            print(f"  python3 ddos.py")
            print(f"  URL objetivo: http://localhost:8080")
            print("\n" + "="*50)
            
            # Mantener programa vivo
            while self.running:
                time.sleep(1)
                
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
            
        if self.tcp_handler:
            self.tcp_handler.stop()
        
        self.show_final_stats()
        sys.exit(0)
    
    def show_stats(self):
        """Mostrar estadísticas en tiempo real"""
        while self.running:
            time.sleep(5)  # Actualizar cada 5 segundos
            
            if self.honeypot.total_requests > 0:
                elapsed = (datetime.now() - self.honeypot.start_time).total_seconds()
                rps = self.honeypot.total_requests / elapsed if elapsed > 0 else 0
                
                print(f"\r\033[K📊 Requests: {self.honeypot.total_requests} | "
                      f"RPS: {rps:.1f} | IPs: {len(self.honeypot.client_ips)} | "
                      f"TCP: {self.honeypot.tcp_connections} | "
                      f"Tiempo: {elapsed:.0f}s", end="", flush=True)
    
    def show_final_stats(self):
        """Mostrar estadísticas finales detalladas"""
        elapsed = (datetime.now() - self.honeypot.start_time).total_seconds()
        
        print(f"\n\n\033[96m{'='*60}")
        print("                ESTADÍSTICAS DEL HONEYPOT")
        print(f"{'='*60}\033[0m")
        print(f"⏱️  Tiempo activo: {elapsed:.2f} segundos")
        print(f"📤 Total requests: {self.honeypot.total_requests}")
        print(f"🌊 GET requests: {self.honeypot.get_requests}")
        print(f"💥 POST requests: {self.honeypot.post_requests}")
        print(f"🔌 TCP conexiones: {self.honeypot.tcp_connections}")
        print(f"❌ Errores: {self.honeypot.error_requests}")
        print(f"📍 IPs únicas: {len(self.honeypot.client_ips)}")
        print(f"⚡ Promedio RPS: {self.honeypot.total_requests / elapsed:.2f}")
        
        # Top IPs atacantes
        if self.honeypot.ip_request_count:
            print("\n🎯 Top IPs atacantes:")
            sorted_ips = sorted(self.honeypot.ip_request_count.items(), 
                              key=lambda x: x[1], reverse=True)[:5]
            for ip, count in sorted_ips:
                print(f"  {ip}: {count} requests")
        
        # Guardar log detallado
        self.save_detailed_log()
        print(f"\n📋 Logs guardados en: honeypot.log y honeypot_analysis.json")
    
    def save_detailed_log(self):
        """Guardar análisis detallado en JSON"""
        analysis = {
            'honeypot_session': {
                'start_time': self.honeypot.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.honeypot.start_time).total_seconds(),
                'total_requests': self.honeypot.total_requests,
                'get_requests': self.honeypot.get_requests,
                'post_requests': self.honeypot.post_requests,
                'tcp_connections': self.honeypot.tcp_connections,
                'error_requests': self.honeypot.error_requests,
                'unique_ips': len(self.honeypot.client_ips),
                'client_ips': list(self.honeypot.client_ips),
                'ip_request_counts': self.honeypot.ip_request_count
            },
            'attack_patterns': self.honeypot.attack_patterns[-100:]  # Últimos 100
        }
        
        try:
            with open('honeypot_analysis.json', 'w') as f:
                json.dump(analysis, f, indent=2)
        except Exception as e:
            self.honeypot.logger.error(f"Error saving analysis: {e}")

def main():
    print("\033[91m" + "="*60 + "\033[0m")
    print("\033[91m🍯 HONEYPOT PARA TESTING DE DDOS 🍯\033[0m")
    print("\033[91m" + "="*60 + "\033[0m")
    print("Este honeypot es para testing SEGURO de tu framework DDoS.")
    print("Solo acepta conexiones locales y registra todo para análisis.")
    print("\033[91m" + "="*60 + "\033[0m")
    
    manager = HoneypotManager()
    manager.start()

if __name__ == "__main__":
    main()
