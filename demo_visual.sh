#!/bin/bash

echo "🍯 DEMOSTRACIÓN DEL VISUAL HONEYPOT DASHBOARD"
echo "=============================================="
echo ""
echo "🚀 Este script te guiará para probar el honeypot visual"
echo ""

# Verificar que existe el archivo
if [ ! -f "visual_honeypot.py" ]; then
    echo "❌ Error: visual_honeypot.py no encontrado"
    exit 1
fi

echo "📋 PASOS A SEGUIR:"
echo ""
echo "1️⃣  En esta terminal, ejecutaremos el honeypot visual"
echo "2️⃣  Abre http://localhost:8080 en tu navegador"
echo "3️⃣  Login con: Usuario=Alvaro, Contraseña=falcon40"
echo "4️⃣  En otra terminal, ejecuta: python3 ddos.py"
echo "5️⃣  Ataca la URL: http://localhost:8080/target"
echo ""

read -p "👉 ¿Estás listo para iniciar el honeypot visual? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "❌ Demostración cancelada"
    exit 0
fi

echo ""
echo "🎯 CREDENCIALES DEL DASHBOARD:"
echo "   🌐 URL: http://localhost:8080"
echo "   👤 Usuario: Alvaro"
echo "   🔑 Contraseña: falcon40"
echo ""
echo "🚀 Iniciando Visual Honeypot Dashboard..."
echo "   (Presiona Ctrl+C para detener)"
echo ""

# Ejecutar el honeypot visual
python3 visual_honeypot.py
