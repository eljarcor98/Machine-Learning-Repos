# 🤖 Repositorios de Machine Learning & Data Science

Este repositorio contiene una colección de proyectos y estudios realizados sobre diversos algoritmos de Machine Learning y análisis de datos. Aquí encontrarás implementaciones desde modelos clásicos hasta análisis de riesgos sísmicos complejos.

---

## 📂 Contenido del Repositorio

| Proyecto | Descripción | Algoritmos / Herramientas |
| :--- | :--- | :--- |
| **[proyecto/](./proyecto/)** | **Análisis Sísmico USGS** (Proyecto Principal). Análisis de sismos en Colombia y alrededores con mapas interactivos. | K-Means, Plotly, Pandas, API USGS |
| **[Naive Bayes/](./Naive%20Bayes/)** | Clasificación de SPAM y análisis de probabilidad. | Naive Bayes, Scikit-learn, Seaborn |
| **[K-Means/](./K-Means/)** | Estudios de agrupamiento y segmentación de datos. | K-Means, Matplotlib |
| **[KNN/](./KNN/)** | Implementación de K-Nearest Neighbors para clasificación. | KNN, Iris Dataset |
| **[Random Forest/](./Random%20Forest/)** | Predicción de accidentes cerebrovasculares (Strokes) y comparativa de modelos base. | Random Forest, KNN, Naive Bayes, K-Means |
| **[Estudio IRIS/](./Estudio%20IRIS/)** | Análisis exploratorio y métricas del dataset Iris. | EDA, Matplotlib |

---

## 🛠️ Instrucciones para Reinstalación (Recuperación)

Si has perdido tus archivos o virus los afectaron, sigue estos pasos para recuperar el entorno de trabajo completo:

### 1. Clonar el repositorio
Si ya lo tienes en GitHub:
```bash
git clone https://github.com/TU_USUARIO/NOMBRE_DEL_REPO.git
cd NOMBRE_DEL_REPO
```

### 2. Crear un entorno virtual único (Recomendado)
Para no crear uno en cada carpeta, puedes crear uno global en la raíz:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Instalar todas las librerías
Instala todas las dependencias necesarias de una sola vez:
```powershell
pip install -r requirements.txt
```

---

## 📋 Librerías Principales Utilizadas

- **Análisis de Datos**: `pandas`, `numpy`, `scipy`
- **Machine Learning**: `scikit-learn`
- **Visualización**: `matplotlib`, `seaborn`, `plotly`
- **Utilidades**: `requests` (para APIs), `nbformat`, `kaleido`, `jinja2`

---

## 🔄 Cómo subir cambios a GitHub

Para mantener tus archivos protegidos en la nube, ejecuta estos comandos regularmente:

1. **Inicializar (solo la primera vez)**:
   ```bash
   git init
   git add .
   git commit -m "Backup inicial de todos los proyectos"
   ```

2. **Vincular a GitHub**:
   *(Debes crear un repositorio vacío en github.com primero)*
   ```bash
   git remote add origin https://github.com/TU_USUARIO/NOMBRE_DEL_REPO.git
   git branch -M main
   git push -u origin main
   ```

3. **Para guardar nuevos cambios**:
   ```bash
   git add .
   git commit -m "Actualización de archivos"
   git push
   ```

---
*Mantenimiento realizado por el Asistente AI (Antigravity).*
