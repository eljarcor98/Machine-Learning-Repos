# Taller 1: Clustering de Actividad Sísmica en Colombia
**Autor:** Torres Anzola Arnold Santiago

## 📦 Estructura del Entregable (100% Autónomo)
Este directorio ha sido diseñado para ser **completamente portátil**. Puede abrirse y ejecutarse en cualquier ordenador sin depender de rutas locales externas:

- `dashboard.html`: Explorador dinámico e interactivo (Datos embebidos, funciona offline/online).
- `reporte.md`: Reporte ejecutivo con rutas relativas a `./assets/`.
- `taller1.ipynb`: **Notebook Maestro**. Incluye el ciclo completo: Carga de CSV Crudo -> Limpieza -> Enriquecimiento -> Modelado.
- `data/`: Contiene `earthquakes_raw.csv` (Datos vírgenes) y `earthquakes.csv` (Datos procesados).
- `assets/`: Galería de imágenes local para el reporte y el notebook.
- `scripts/`: Código fuente modular para entusiastas y desarrolladores.

## 🚀 Instrucciones de Ejecución
1. **Dashboard**: Abrir `dashboard.html` directamente. Permite filtrar por año, profundidad y número de zonas (K).
2. **Análisis**: El archivo `taller1.ipynb` puede ejecutarse en Jupyter Lab, VS Code o Google Colab.
3. **Reproducibilidad**: El modelo utiliza `random_state=42` para garantizar que los clusters sean idénticos en cada ejecución.

---
*Machine Learning para la Gestión del Riesgo Sísmico.*
