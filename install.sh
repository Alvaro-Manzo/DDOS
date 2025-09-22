#!/bin/bash

echo "🚀 INSTALACIÓN AUTOMÁTICA - ADVANCED DDOS TESTING FRAMEWORK"
echo "============================================================="
echo ""

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "📥 Instala Python 3 desde: https://python.org"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado"
    echo "📥 Instala pip3 para continuar"
    exit 1
fi

echo "✅ pip3 encontrado"

# Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencias instaladas correctamente"
else
    echo "❌ Error instalando dependencias"
    exit 1
fi

# Hacer archivos ejecutables
echo ""
echo "🔧 Configurando permisos..."
chmod +x ddos.py
chmod +x visual_honeypot.py
chmod +x honeypot_server.py
chmod +x setup_honeypot.sh
chmod +x demo_visual.sh

echo "✅ Permisos configurados"

# Verificar instalación
echo ""
echo "🧪 Verificando instalación..."
python3 -c "import requests, json, threading, socket, time, logging" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Todas las dependencias verificadas"
else
    echo "❌ Error en verificación de dependencias"
    exit 1
fi

echo ""
echo "🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE"
echo "======================================"
echo ""
echo "📋 ARCHIVOS DISPONIBLES:"
echo "   🎯 ddos.py              - Framework principal de DDoS"
echo "   🍯 visual_honeypot.py   - Honeypot con dashboard visual"
echo "   📟 honeypot_server.py   - Honeypot clásico"
echo "   🚀 demo_visual.sh       - Demo del honeypot visual"
echo ""
echo "⚡ INICIO RÁPIDO:"
echo "   1. Honeypot visual:  ./demo_visual.sh"
echo "   2. Honeypot clásico: python3 honeypot_server.py"
echo "   3. Framework DDoS:   python3 ddos.py"
echo ""
echo "🌐 HONEYPOT VISUAL:"
echo "   URL: http://localhost:8080"
echo "   Usuario: Alvaro"
echo "   Contraseña: falcon40"
echo ""
echo "📚 DOCUMENTACIÓN:"
echo "   📖 README.md       - Documentación completa"
echo "   ⚡ QUICKSTART.md   - Guía rápida"
echo "   🤝 CONTRIBUTING.md - Guía para contribuir"
echo "   🔐 SECURITY.md     - Políticas de seguridad"
echo ""
echo "⚠️  RECORDATORIO:"
echo "   ✅ Solo para uso educativo y testing autorizado"
echo "   ❌ NO usar para ataques no autorizados"
echo "   📋 Cumplir con las leyes locales"
echo ""
echo "🎯 ¡Listo para testing profesional de DDoS!"
