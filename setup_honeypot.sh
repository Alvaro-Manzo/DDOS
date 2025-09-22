#!/bin/bash
"""
QUICK SETUP SCRIPT PARA HONEYPOT
=====================================
"""

echo "🍯 CONFIGURANDO HONEYPOT PARA DDOS TESTING..."
echo "=============================================="

# Crear directorio de logs si no existe
mkdir -p logs

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 encontrado"

# Verificar dependencias
echo "📦 Verificando dependencias..."

python3 -c "import socket, threading, json, logging, http.server" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Todas las dependencias están disponibles"
else
    echo "❌ Faltan dependencias de Python"
    exit 1
fi

# Hacer script ejecutable
chmod +x honeypot_server.py
chmod +x ddos.py

echo ""
echo "🚀 HONEYPOT LISTO PARA USAR"
echo "==========================="
echo ""
echo "📋 INSTRUCCIONES:"
echo "1. Terminal 1 - Iniciar honeypot:"
echo "   python3 honeypot_server.py"
echo ""
echo "2. Terminal 2 - Ejecutar ataques:"
echo "   python3 ddos.py"
echo "   URL objetivo: http://localhost:8080"
echo ""
echo "3. Puertos utilizados:"
echo "   🌐 HTTP: localhost:8080"
echo "   🔌 TCP:  localhost:8081"
echo ""
echo "4. Logs generados:"
echo "   📄 honeypot.log (tiempo real)"
echo "   📊 honeypot_analysis.json (análisis completo)"
echo ""
echo "⚡ ¡Todo listo para testing seguro!"
