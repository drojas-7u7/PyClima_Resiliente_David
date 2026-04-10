import json
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

ARCHIVO_BASE = "datos_clima.json" 

def generar_reporte_visual_pro():
    if not os.path.exists(ARCHIVO_BASE):
        return 

    try:
        with open(ARCHIVO_BASE, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        distritos = [d['distrito'] for d in datos]
        temps = [d['temp'] for d in datos]
        
        if not temps: return
        
    except (json.JSONDecodeError, KeyError):
        return

    sns.set_theme(style="white")
    plt.figure(figsize=(10, 6))

    sns.barplot(x=distritos, y=temps, palette="magma", hue=distritos, 
                legend=False, linewidth=0, errorbar=None)

    media = np.mean(temps)
    plt.axhline(y=media, color='#e74c3c', linestyle='--', label=f'Media: {media:.2f}°C')
    
    plt.title("ESTADO TÉRMICO HISTÓRICO POR DISTRITO", fontweight='bold')
    plt.ylabel("Temperatura (°C)")
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    generar_reporte_visual_pro()