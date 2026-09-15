# Scientific Plotter / Graficador científico

Streamlit app for simple scientific plotting and linear regression.

## Features
- Spanish / English interface toggle
- Paste tabular data or upload CSV
- Select X and Y variables
- Scatter plots
- Adjustable point size, font sizes and axis limits
- Select full or partial X range for linear regression
- Independent display/extrapolation range for the fitted line
- Slope, Y-intercept / ordenada al origen, R²
- Significant-figures selector
- Predict Y from X with a vertical dashed guide
- Predict X from Y with a horizontal dashed guide
- Red cross marking the predicted point
- PNG, PDF and SVG export
- Figure width, height and PNG DPI controls

## Run locally

```bash
conda create -n graficador python=3.11 -y
conda activate graficador
pip install -r requirements.txt
streamlit run app.py
```

## GitHub
Upload this folder as a repository. For Streamlit Community Cloud, choose `app.py` as the entry point.
