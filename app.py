
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Scientific Plotter", page_icon="📈", layout="wide")

lang = "en" if st.sidebar.toggle("English", value=False) else "es"

TXT = {
"es":{
"title":"Graficador científico simple",
"caption":"Carga o pega datos, crea un gráfico, ajusta una regresión lineal, extrapola y exporta la figura.",
"data":"1. Datos","method":"¿Cómo querés cargar los datos?","paste":"Pegar datos","upload":"Subir archivo CSV",
"pastebox":"Pegá una tabla con encabezados","uploadbox":"Seleccioná un archivo CSV","needdata":"Pegá una tabla con al menos dos columnas o cargá un CSV.",
"neednum":"Se necesitan al menos dos columnas numéricas.","datahead":"Datos","vars":"2. Variables","xvar":"Variable del eje X","yvar":"Variable del eje Y",
"appearance":"3. Apariencia","point":"Tamaño de los puntos","axisfont":"Tamaño de fuente de los ejes","tickfont":"Tamaño de los números de los ejes",
"xlabel":"Etiqueta del eje X","ylabel":"Etiqueta del eje Y","sig":"Cifras significativas",
"reg":"4. Regresión lineal","showreg":"Mostrar regresión lineal","fithelp":"El rango de ajuste define qué datos se usan para calcular la regresión.",
"fitmin":"Inicio del rango de ajuste","fitmax":"Fin del rango de ajuste","linehelp":"El rango de la línea define hasta dónde se muestra o extrapola la recta.",
"linemin":"Inicio de la línea","linemax":"Fin de la línea",
"pred":"5. Predicción sobre la recta","showpred":"Mostrar predicción","predmode":"¿Qué querés predecir?",
"predy":"Predecir Y a partir de X","predx":"Predecir X a partir de Y","knownx":"Valor de X conocido","knowny":"Valor de Y conocido",
"limits":"6. Límites de los ejes","autolimits":"Ajustar ejes automáticamente","margin":"Margen automático (%)",
"xmin":"X mínimo","xmax":"X máximo","ymin":"Y mínimo","ymax":"Y máximo","badlim":"Los límites mínimos deben ser menores que los máximos.",
"export":"7. Exportación","width":"Ancho de la figura (pulgadas)","height":"Alto de la figura (pulgadas)","dpi":"Resolución (DPI)",
"plot":"Gráfico","results":"Resultados","slope":"Pendiente","intercept":"Ordenada al origen","r2":"R²","equation":"Ecuación",
"range":"Rango de datos usado","complete":"Completo","partial":"Parcial","fromto":"de {a} a {b}",
"predyr":"Y predicho para X = {v}","predxr":"X predicho para Y = {v}",
"notenough":"El rango seleccionado no contiene suficientes puntos distintos para hacer una regresión.",
"zeroslope":"No se puede predecir X porque la pendiente es cero.",
"activate":"Activá la regresión lineal para ver los resultados.","exportfig":"Exportar figura","download":"Descargar {fmt}"
},
"en":{
"title":"Simple scientific plotter",
"caption":"Load or paste data, create a plot, fit a linear regression, extrapolate, and export the figure.",
"data":"1. Data","method":"How do you want to load the data?","paste":"Paste data","upload":"Upload CSV file",
"pastebox":"Paste a table with headers","uploadbox":"Select a CSV file","needdata":"Paste a table with at least two columns or upload a CSV file.",
"neednum":"At least two numeric columns are required.","datahead":"Data","vars":"2. Variables","xvar":"X-axis variable","yvar":"Y-axis variable",
"appearance":"3. Appearance","point":"Point size","axisfont":"Axis-label font size","tickfont":"Axis-number font size",
"xlabel":"X-axis label","ylabel":"Y-axis label","sig":"Significant figures",
"reg":"4. Linear regression","showreg":"Show linear regression","fithelp":"The fit range defines which data are used to calculate the regression.",
"fitmin":"Fit range start","fitmax":"Fit range end","linehelp":"The line range defines how far the fitted line is displayed or extrapolated.",
"linemin":"Line start","linemax":"Line end",
"pred":"5. Prediction from the fitted line","showpred":"Show prediction","predmode":"What do you want to predict?",
"predy":"Predict Y from X","predx":"Predict X from Y","knownx":"Known X value","knowny":"Known Y value",
"limits":"6. Axis limits","autolimits":"Adjust axes automatically","margin":"Automatic margin (%)",
"xmin":"X minimum","xmax":"X maximum","ymin":"Y minimum","ymax":"Y maximum","badlim":"Minimum limits must be smaller than maximum limits.",
"export":"7. Export","width":"Figure width (inches)","height":"Figure height (inches)","dpi":"Resolution (DPI)",
"plot":"Plot","results":"Results","slope":"Slope","intercept":"Y-intercept","r2":"R²","equation":"Equation",
"range":"Data range used","complete":"Complete","partial":"Partial","fromto":"from {a} to {b}",
"predyr":"Predicted Y at X = {v}","predxr":"Predicted X at Y = {v}",
"notenough":"The selected range does not contain enough distinct points for a regression.",
"zeroslope":"X cannot be predicted because the slope is zero.",
"activate":"Turn on linear regression to see results.","exportfig":"Export figure","download":"Download {fmt}"
}}[lang]

st.title(TXT["title"])
st.caption(TXT["caption"])

def read_data(text):
    if not text.strip():
        return None
    for sep in ["\t", ",", ";"]:
        try:
            df = pd.read_csv(io.StringIO(text.strip()), sep=sep)
            if df.shape[1] >= 2:
                return df
        except Exception:
            pass
    try:
        df = pd.read_csv(io.StringIO(text.strip()), sep=r"\s+", engine="python")
        return df if df.shape[1] >= 2 else None
    except Exception:
        return None

def num(s):
    return pd.to_numeric(s, errors="coerce")

def fs(v, n):
    if v is None or not np.isfinite(v):
        return "—"
    return f"{v:.{n}g}"

# ---------------------------------------------------------
# Data
# ---------------------------------------------------------
st.sidebar.header(TXT["data"])

mode = st.sidebar.radio(TXT["method"], [TXT["paste"], TXT["upload"]], index=0)

df = None
example = """Time\tTemperature
0.0\t24.8
0.5\t25.3
1.0\t24.9
1.5\t25.4
2.0\t25.1
2.5\t34.6
3.0\t69.4
3.5\t66.7
4.0\t62.9
4.5\t59.0
5.0\t56.1
5.5\t52.7
6.0\t50.3"""

if mode == TXT["paste"]:
    df = read_data(st.sidebar.text_area(TXT["pastebox"], value=example, height=250))
else:
    f = st.sidebar.file_uploader(TXT["uploadbox"], type=["csv"])
    if f is not None:
        try:
            df = pd.read_csv(f)
        except Exception:
            f.seek(0)
            df = pd.read_csv(f, sep=";")

if df is None or df.shape[1] < 2:
    st.info(TXT["needdata"])
    st.stop()

st.subheader(TXT["datahead"])
st.dataframe(df, use_container_width=True, height=240)

numeric_cols = [c for c in df.columns if num(df[c]).notna().sum() >= 2]
if len(numeric_cols) < 2:
    st.error(TXT["neednum"])
    st.stop()

# ---------------------------------------------------------
# Variables
# ---------------------------------------------------------
st.sidebar.header(TXT["vars"])

xcol = st.sidebar.selectbox(TXT["xvar"], numeric_cols, index=0)
ycol = st.sidebar.selectbox(TXT["yvar"], numeric_cols, index=1 if len(numeric_cols) > 1 else 0)

xv = num(df[xcol])
yv = num(df[ycol])

base = pd.DataFrame({"x": xv, "y": yv}).dropna()

xd0 = float(base["x"].min())
xd1 = float(base["x"].max())
yd0 = float(base["y"].min())
yd1 = float(base["y"].max())

xs = xd1 - xd0 or 1.0
ys = yd1 - yd0 or 1.0

# ---------------------------------------------------------
# Appearance
# ---------------------------------------------------------
st.sidebar.header(TXT["appearance"])

ps = st.sidebar.slider(TXT["point"], 10, 200, 60, 5)
af = st.sidebar.slider(TXT["axisfont"], 8, 30, 16)
tf = st.sidebar.slider(TXT["tickfont"], 8, 26, 14)

xl = st.sidebar.text_input(TXT["xlabel"], value=str(xcol))
yl = st.sidebar.text_input(TXT["ylabel"], value=str(ycol))

sig = st.sidebar.slider(TXT["sig"], 1, 8, 4)

# ---------------------------------------------------------
# Regression
# ---------------------------------------------------------
st.sidebar.header(TXT["reg"])

showreg = st.sidebar.checkbox(TXT["showreg"], value=True)

fitmin, fitmax = xd0, xd1
linemin, linemax = xd0, xd1

if showreg:
    st.sidebar.caption(TXT["fithelp"])

    fitmin = st.sidebar.number_input(
        TXT["fitmin"],
        value=float(max(xd0, xd1 - 3))
    )
    fitmax = st.sidebar.number_input(
        TXT["fitmax"],
        value=float(xd1)
    )

    st.sidebar.caption(TXT["linehelp"])

    # Default extrapolation starts at 1 when the data range allows it.
    default_line_min = 1.0 if xd0 <= 1.0 <= xd1 else float(xd0)

    linemin = st.sidebar.number_input(
        TXT["linemin"],
        value=float(default_line_min)
    )
    linemax = st.sidebar.number_input(
        TXT["linemax"],
        value=float(xd1)
    )

# ---------------------------------------------------------
# Calculate regression early so auto-limits can use it
# ---------------------------------------------------------
reg_ok = False
m = b = r2 = None
sub = None

if showreg:
    sub = base[(base["x"] >= fitmin) & (base["x"] <= fitmax)]

    if len(sub) >= 2 and sub["x"].nunique() >= 2:
        m, b = np.polyfit(sub["x"], sub["y"], 1)

        pred_fit = m * sub["x"] + b
        ssr = np.sum((sub["y"] - pred_fit) ** 2)
        sst = np.sum((sub["y"] - sub["y"].mean()) ** 2)
        r2 = np.nan if sst == 0 else 1 - ssr / sst

        reg_ok = True

# ---------------------------------------------------------
# Prediction
# ---------------------------------------------------------
st.sidebar.header(TXT["pred"])

showpred = False
predmode = "y_from_x"
known = None
px = py = None
pred_err = None

if showreg:
    showpred = st.sidebar.checkbox(TXT["showpred"], value=True)

    if showpred:
        choice = st.sidebar.radio(
            TXT["predmode"],
            [TXT["predy"], TXT["predx"]],
            index=0
        )

        if choice == TXT["predy"]:
            predmode = "y_from_x"
            known = st.sidebar.number_input(
                TXT["knownx"],
                value=float(xd0 + xs / 3)
            )

            if reg_ok:
                px = known
                py = m * known + b

        else:
            predmode = "x_from_y"
            known = st.sidebar.number_input(
                TXT["knowny"],
                value=float(yd0 + ys / 2)
            )

            if reg_ok:
                py = known

                if abs(m) < 1e-15:
                    pred_err = "zero"
                else:
                    px = (known - b) / m

# ---------------------------------------------------------
# Axis limits
# ---------------------------------------------------------
st.sidebar.header(TXT["limits"])

auto_limits = st.sidebar.checkbox(TXT["autolimits"], value=True)

auto_margin = st.sidebar.slider(
    TXT["margin"],
    min_value=0,
    max_value=25,
    value=7,
    step=1
) / 100.0

# Start with measured data
all_x = list(base["x"].to_numpy())
all_y = list(base["y"].to_numpy())

# Add the complete displayed regression line
if reg_ok and linemin < linemax:
    xx_for_limits = np.linspace(linemin, linemax, 300)
    yy_for_limits = m * xx_for_limits + b
    all_x.extend(xx_for_limits.tolist())
    all_y.extend(yy_for_limits.tolist())

# Add predicted point
if showpred and pred_err is None and px is not None and py is not None:
    all_x.append(float(px))
    all_y.append(float(py))

auto_xmin = float(np.min(all_x))
auto_xmax = float(np.max(all_x))
auto_ymin = float(np.min(all_y))
auto_ymax = float(np.max(all_y))

auto_xspan = auto_xmax - auto_xmin
auto_yspan = auto_ymax - auto_ymin

if auto_xspan == 0:
    auto_xspan = 1.0
if auto_yspan == 0:
    auto_yspan = 1.0

auto_xmin -= auto_margin * auto_xspan
auto_xmax += auto_margin * auto_xspan
auto_ymin -= auto_margin * auto_yspan
auto_ymax += auto_margin * auto_yspan

if auto_limits:
    xmin, xmax = auto_xmin, auto_xmax
    ymin, ymax = auto_ymin, auto_ymax

    st.sidebar.caption(
        f"X: {fs(xmin, sig)} → {fs(xmax, sig)} | "
        f"Y: {fs(ymin, sig)} → {fs(ymax, sig)}"
    )
else:
    xmin = st.sidebar.number_input(
        TXT["xmin"],
        value=float(xd0 - 0.05 * xs)
    )
    xmax = st.sidebar.number_input(
        TXT["xmax"],
        value=float(xd1 + 0.05 * xs)
    )
    ymin = st.sidebar.number_input(
        TXT["ymin"],
        value=float(yd0 - 0.08 * ys)
    )
    ymax = st.sidebar.number_input(
        TXT["ymax"],
        value=float(yd1 + 0.15 * ys)
    )

    if xmin >= xmax or ymin >= ymax:
        st.error(TXT["badlim"])
        st.stop()

# ---------------------------------------------------------
# Export
# ---------------------------------------------------------
st.sidebar.header(TXT["export"])

fw = st.sidebar.number_input(
    TXT["width"],
    min_value=2.0,
    max_value=20.0,
    value=7.0,
    step=0.5
)

fh = st.sidebar.number_input(
    TXT["height"],
    min_value=2.0,
    max_value=20.0,
    value=5.0,
    step=0.5
)

dpi = st.sidebar.selectbox(
    TXT["dpi"],
    [100, 150, 300, 600],
    index=2
)

# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(fw, fh))

ax.scatter(
    base["x"],
    base["y"],
    s=ps,
    color="black",
    zorder=3
)

res = None

if showreg and reg_ok:
    xx = np.linspace(linemin, linemax, 300)
    yy = m * xx + b

    ax.plot(
        xx,
        yy,
        color="black",
        linewidth=2,
        zorder=2
    )

    if showpred and pred_err is None and px is not None and py is not None:
        if predmode == "y_from_x":
            ax.axvline(
                px,
                color="gray",
                linestyle="--",
                linewidth=1.4,
                zorder=1
            )
        else:
            ax.axhline(
                py,
                color="gray",
                linestyle="--",
                linewidth=1.4,
                zorder=1
            )

        ax.scatter(
            [px],
            [py],
            marker="x",
            color="red",
            s=max(ps * 1.8, 80),
            linewidths=2,
            zorder=5
        )

        dx = 0.035 * (xmax - xmin)
        dy = 0.035 * (ymax - ymin)

        label = (
            f"Y = {fs(py, sig)}"
            if predmode == "y_from_x"
            else f"X = {fs(px, sig)}"
        )

        ax.text(
            px + dx,
            py + dy,
            label,
            fontsize=tf,
            color="red",
            ha="left",
            va="bottom"
        )

    complete = (
        fitmin <= float(base["x"].min())
        and fitmax >= float(base["x"].max())
    )

    res = {
        "m": m,
        "b": b,
        "r2": r2,
        "px": px,
        "py": py,
        "err": pred_err,
        "complete": complete
    }

ax.set_xlabel(xl, fontsize=af)
ax.set_ylabel(yl, fontsize=af)

ax.tick_params(axis="both", labelsize=tf)

ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)

ax.grid(False)

fig.tight_layout()

# ---------------------------------------------------------
# Results
# ---------------------------------------------------------
c1, c2 = st.columns([3, 1])

with c1:
    st.subheader(TXT["plot"])
    st.pyplot(fig, use_container_width=True)

with c2:
    st.subheader(TXT["results"])

    if showreg:
        if res is None:
            st.warning(TXT["notenough"])
        else:
            st.metric(TXT["slope"], fs(res["m"], sig))
            st.metric(TXT["intercept"], fs(res["b"], sig))
            st.metric(TXT["r2"], fs(res["r2"], sig))

            st.markdown(f"**{TXT['equation']}:**")

            sign = "+" if res["b"] >= 0 else "-"
            st.latex(
                rf"y = {fs(res['m'], sig)}x {sign} {fs(abs(res['b']), sig)}"
            )

            st.markdown(f"**{TXT['range']}:**")

            if res["complete"]:
                st.write(TXT["complete"])
            else:
                st.write(
                    f"{TXT['partial']} "
                    f"({TXT['fromto'].format(a=fs(fitmin,sig), b=fs(fitmax,sig))})"
                )

            if showpred:
                if res["err"] == "zero":
                    st.warning(TXT["zeroslope"])

                elif predmode == "y_from_x":
                    st.metric(
                        TXT["predyr"].format(v=fs(known, sig)),
                        fs(res["py"], sig)
                    )

                else:
                    st.metric(
                        TXT["predxr"].format(v=fs(known, sig)),
                        fs(res["px"], sig)
                    )

    else:
        st.caption(TXT["activate"])

# ---------------------------------------------------------
# Export buttons
# ---------------------------------------------------------
st.subheader(TXT["exportfig"])

d1, d2, d3 = st.columns(3)

for fmt, col, mime in [
    ("PNG", d1, "image/png"),
    ("PDF", d2, "application/pdf"),
    ("SVG", d3, "image/svg+xml"),
]:
    buf = io.BytesIO()

    if fmt == "PNG":
        fig.savefig(
            buf,
            format="png",
            dpi=dpi,
            bbox_inches="tight"
        )
    else:
        fig.savefig(
            buf,
            format=fmt.lower(),
            bbox_inches="tight"
        )

    buf.seek(0)

    with col:
        st.download_button(
            TXT["download"].format(fmt=fmt),
            buf.getvalue(),
            file_name=f"scientific_plot.{fmt.lower()}",
            mime=mime,
            use_container_width=True
        )

plt.close(fig)
