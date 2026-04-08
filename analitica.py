import json
import os
import numpy as np
import matplotlib.pyplot as plt

ARCHIVO_BASE = "datos_clima.json" 

def generar_reporte_visual():
    if not os.path.exists(ARCHIVO_BASE):
        print(f"Error: No se encuentra '{ARCHIVO_BASE}'.")
        return

    with open(ARCHIVO_BASE, 'r', encoding='utf-8') as f:
        try:
            datos = json.load(f)
        except json.JSONDecodeError:
            print("Error: JSON mal formado.")
            return

    if not datos:
        return

    distritos_lista = [d['distrito'] for d in datos]
    temperaturas = np.array([d['temp'] for d in datos])
    
    nombres_distritos = list(set(distritos_lista))
    promedios = []

    for dist in nombres_distritos:
        indices = [i for i, nombre in enumerate(distritos_lista) if nombre == dist]
        promedios.append(np.mean(temperaturas[indices]))

    plt.style.use('seaborn-v0_8-darkgrid')
    ax = plt.subplots(figsize=(12, 7))
    norm = plt.Normalize(min(promedios), max(promedios))
    colores = plt.cm.plasma(norm(promedios))
    
    bars = ax.bar(nombres_distritos, promedios, color=colores, edgecolor='white', linewidth=0.7, alpha=0.9)
    
    media_global = np.mean(temperaturas)
    ax.axhline(y=media_global, color='#e74c3c', linestyle='--', linewidth=2, 
               label=f'Media Ciudad: {media_global:.1f}°C')

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval:.1f}°', 
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='#2c3e50')

    ax.set_title("REPORTE ESTRATÉGICO: TEMPERATURA MEDIA POR DISTRITO", 
                 fontsize=16, fontweight='bold', pad=20, color='#2c3e50')
    ax.set_ylabel("Grados Celsius (°C)", fontsize=12, fontweight='semibold')
    ax.set_xlabel("Distritos de Madrid", fontsize=12, fontweight='semibold')

    plt.xticks(rotation=35, ha='right', fontsize=10)
    
    ax.legend(frameon=True, facecolor='white', framealpha=1, loc='upper right')

    plt.tight_layout()
    
    plt.show()