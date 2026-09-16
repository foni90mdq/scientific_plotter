import io
import re
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="KodaPlot", page_icon="📈", layout="wide")

lang = "en" if st.sidebar.toggle("English", value=False) else "es"

TXT = {
"es":{
"title":"KodaPlot",
"caption":"Graficador científico simple para visualizar datos, ajustar regresiones lineales, extrapolar y exportar figuras.",
"data":"1. Datos","example":"Ejemplo","clear":"Vaciar","method":"¿Cómo querés cargar los datos?","paste":"Pegar datos","upload":"Subir archivo CSV",
"pastebox":"Pegá una tabla con encabezados","uploadbox":"Seleccioná un archivo CSV","needdata":"Pegá una tabla con al menos dos columnas, cargá un CSV o hacé clic en Ejemplo.",
"neednum":"Se necesitan al menos dos columnas numéricas.","datahead":"Datos","vars":"2. Variables","xvar":"Variable del eje X","yvar":"Variable del eje Y",
"appearance":"3. Apariencia","point":"Tamaño de los puntos","axisfont":"Tamaño de fuente de los ejes","tickfont":"Tamaño de los números de los ejes",
"xlabel":"Etiqueta del eje X","ylabel":"Etiqueta del eje Y",
"reg":"4. Regresión lineal","showreg":"Mostrar regresión lineal","fithelp":"El rango de ajuste define qué datos se usan para calcular la regresión.",
"fitmin":"Inicio del rango de ajuste","fitmax":"Fin del rango de ajuste","linehelp":"El rango de la línea define hasta dónde se muestra o extrapola la recta.",
"linemin":"Inicio de la línea","linemax":"Fin de la línea",
"pred":"5. Predicción sobre la recta","showpred":"Mostrar predicción","predmode":"¿Qué querés predecir?",
"predy":"Predecir Y a partir de X","predx":"Predecir X a partir de Y","knownx":"Valor de X conocido","knowny":"Valor de Y conocido",
"sigsection":"6. Cifras significativas","sig":"Cifras significativas","sighelp":"El valor inicial se estima a partir de la precisión de los datos cargados.",
"limits":"7. Límites de los ejes","autolimits":"Ajustar ejes automáticamente","margin":"Margen automático (%)",
"xmin":"X mínimo","xmax":"X máximo","ymin":"Y mínimo","ymax":"Y máximo","badlim":"Los límites mínimos deben ser menores que los máximos.",
"export":"8. Exportación","width":"Ancho de la figura (pulgadas)","height":"Alto de la figura (pulgadas)","dpi":"Resolución (DPI)",
"plot":"Gráfico","results":"Resultados","slope":"Pendiente","intercept":"Ordenada al origen","r2":"R²","equation":"Ecuación",
"range":"Rango de datos usado","complete":"Completo","partial":"Parcial","fromto":"de {a} a {b}",
"predyr":"Y predicho para X = {v}","predxr":"X predicho para Y = {v}",
"notenough":"El rango seleccionado no contiene suficientes puntos distintos para hacer una regresión.",
"zeroslope":"No se puede predecir X porque la pendiente es cero.",
"activate":"Activá la regresión lineal para ver los resultados.","exportfig":"Exportar figura","download":"Descargar {fmt}",
"save_analysis":"Guardar análisis","load_analysis":"Cargar análisis","analysis_file":"Archivo de análisis de KodaPlot (.txt)",
"apply_analysis":"Cargar archivo","bad_analysis":"No se pudo cargar el análisis. Verificá que sea un archivo creado por KodaPlot.",
"analysis_loaded":"Análisis cargado correctamente."
},
"en":{
"title":"KodaPlot",
"caption":"A simple scientific plotter for visualizing data, fitting linear regressions, extrapolating, and exporting figures.",
"data":"1. Data","example":"Example","clear":"Clear","method":"How do you want to load the data?","paste":"Paste data","upload":"Upload CSV file",
"pastebox":"Paste a table with headers","uploadbox":"Select a CSV file","needdata":"Paste a table with at least two columns, upload a CSV, or click Example.",
"neednum":"At least two numeric columns are required.","datahead":"Data","vars":"2. Variables","xvar":"X-axis variable","yvar":"Y-axis variable",
"appearance":"3. Appearance","point":"Point size","axisfont":"Axis-label font size","tickfont":"Axis-number font size",
"xlabel":"X-axis label","ylabel":"Y-axis label",
"reg":"4. Linear regression","showreg":"Show linear regression","fithelp":"The fit range defines which data are used to calculate the regression.",
"fitmin":"Fit range start","fitmax":"Fit range end","linehelp":"The line range defines how far the fitted line is displayed or extrapolated.",
"linemin":"Line start","linemax":"Line end",
"pred":"5. Prediction from the fitted line","showpred":"Show prediction","predmode":"What do you want to predict?",
"predy":"Predict Y from X","predx":"Predict X from Y","knownx":"Known X value","knowny":"Known Y value",
"sigsection":"6. Significant figures","sig":"Significant figures","sighelp":"The initial value is estimated from the precision of the loaded data.",
"limits":"7. Axis limits","autolimits":"Adjust axes automatically","margin":"Automatic margin (%)",
"xmin":"X minimum","xmax":"X maximum","ymin":"Y minimum","ymax":"Y maximum","badlim":"Minimum limits must be smaller than maximum limits.",
"export":"8. Export","width":"Figure width (inches)","height":"Figure height (inches)","dpi":"Resolution (DPI)",
"plot":"Plot","results":"Results","slope":"Slope","intercept":"Y-intercept","r2":"R²","equation":"Equation",
"range":"Data range used","complete":"Complete","partial":"Partial","fromto":"from {a} to {b}",
"predyr":"Predicted Y at X = {v}","predxr":"Predicted X at Y = {v}",
"notenough":"The selected range does not contain enough distinct points for a regression.",
"zeroslope":"X cannot be predicted because the slope is zero.",
"activate":"Turn on linear regression to see results.","exportfig":"Export figure","download":"Download {fmt}",
"save_analysis":"Save analysis","load_analysis":"Load analysis","analysis_file":"KodaPlot analysis file (.txt)",
"apply_analysis":"Load file","bad_analysis":"The analysis could not be loaded. Make sure it is a file created by KodaPlot.",
"analysis_loaded":"Analysis loaded successfully."
}}[lang]

st.title(TXT["title"])
st.caption(TXT["caption"])

EXAMPLE_DATA = """Time\tTemperature
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


def read_data(text):
    """Read pasted data while preserving the original cell strings."""
    if not text.strip():
        return None
    for sep in ["\t", ",", ";"]:
        try:
            df = pd.read_csv(io.StringIO(text.strip()), sep=sep, dtype=str)
            if df.shape[1] >= 2:
                return df
        except Exception:
            pass
    try:
        df = pd.read_csv(io.StringIO(text.strip()), sep=r"\s+", engine="python", dtype=str)
        return df if df.shape[1] >= 2 else None
    except Exception:
        return None


def num(s):
    return pd.to_numeric(s, errors="coerce")


def fs(v, n):
    if v is None or not np.isfinite(v):
        return "—"
    return f"{v:.{n}g}"


def count_sig_figs(value):
    """Estimate significant figures from the user's original text representation."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None

    s = str(value).strip()
    if not s:
        return None

    s = s.replace(",", ".")
    s = s.lstrip("+-")

    # Remove exponent but retain the mantissa precision.
    mantissa = re.split(r"[eE]", s)[0]

    if not re.search(r"\d", mantissa):
        return None

    if "." in mantissa:
        before, after = mantissa.split(".", 1)
        digits = before + after
        significant = digits.lstrip("0")

        # For zero values, decimal places convey precision: 0.0 -> 1, 0.00 -> 2.
        if significant == "":
            return max(1, len(after))
        return len(significant)

    digits = re.sub(r"\D", "", mantissa).lstrip("0")
    return max(1, len(digits)) if digits else 1


def infer_sig_figs(df, xcol, ycol):
    """Use the higher typical precision of X and Y as a practical default."""
    medians = []
    for col in [xcol, ycol]:
        counts = [count_sig_figs(v) for v in df[col].dropna()]
        counts = [c for c in counts if c is not None]
        if counts:
            medians.append(float(np.median(counts)))

    if not medians:
        return 3

    return int(np.clip(round(max(medians)), 1, 8))


def apply_analysis_payload(payload):
    """Restore a KodaPlot analysis saved as a human-readable JSON text file."""
    if not isinstance(payload, dict) or payload.get("format") != "KodaPlot analysis":
        raise ValueError("Not a KodaPlot analysis file")

    data_text = payload.get("data", {}).get("text", "")
    if not isinstance(data_text, str) or not data_text.strip():
        raise ValueError("Analysis file contains no data")

    st.session_state["load_mode"] = "paste"
    st.session_state["data_text"] = data_text

    allowed = {
        "x_col", "y_col", "point_size", "axis_font", "tick_font",
        "x_label", "y_label", "show_regression", "fitmin", "fitmax",
        "linemin", "linemax", "show_prediction", "prediction_mode",
        "known_x", "known_y", "sigfigs", "auto_limits", "auto_margin_pct",
        "manual_xmin", "manual_xmax", "manual_ymin", "manual_ymax",
        "figure_width", "figure_height", "export_dpi"
    }

    for key, value in payload.get("settings", {}).items():
        if key in allowed:
            st.session_state[key] = value

    # Prevent the normal data-change defaults from overwriting restored settings.
    st.session_state["_analysis_loaded_pending"] = True
    st.session_state["data_signature"] = None


# ---------------------------------------------------------
# Save / load analysis controls (shown near the top)
# ---------------------------------------------------------
action_save, action_load, _action_spacer = st.columns([1.0, 1.0, 2.4])
with action_save:
    save_analysis_placeholder = st.empty()
    save_analysis_placeholder.button(
        TXT["save_analysis"],
        disabled=True,
        use_container_width=True,
        key="save_analysis_disabled"
    )

with action_load:
    with st.popover(TXT["load_analysis"], use_container_width=True):
        analysis_upload = st.file_uploader(
            TXT["analysis_file"],
            type=["txt"],
            key="analysis_upload"
        )
        if st.button(TXT["apply_analysis"], use_container_width=True, key="apply_analysis_button"):
            try:
                if analysis_upload is None:
                    raise ValueError("No file selected")
                payload = json.loads(analysis_upload.getvalue().decode("utf-8"))
                apply_analysis_payload(payload)
                st.rerun()
            except Exception:
                st.error(TXT["bad_analysis"])


# ---------------------------------------------------------
# Data
# ---------------------------------------------------------
st.sidebar.header(TXT["data"])
example_col, clear_col = st.sidebar.columns(2)
with example_col:
    if st.button(TXT["example"], use_container_width=True, key="example_button"):
        st.session_state["load_mode"] = "paste"
        st.session_state["data_text"] = EXAMPLE_DATA
        st.session_state["data_signature"] = None
with clear_col:
    if st.button(TXT["clear"], use_container_width=True, key="clear_button"):
        st.session_state["load_mode"] = "paste"
        st.session_state["data_text"] = ""
        st.session_state["data_signature"] = None

mode = st.sidebar.radio(
    TXT["method"],
    ["paste", "upload"],
    format_func=lambda x: TXT["paste"] if x == "paste" else TXT["upload"],
    index=0,
    key="load_mode"
)

df = None

if mode == "paste":
    if "data_text" not in st.session_state:
        st.session_state["data_text"] = ""

    pasted_text = st.sidebar.text_area(
        TXT["pastebox"],
        height=250,
        key="data_text"
    )
    df = read_data(pasted_text)
    is_example = pasted_text.strip() == EXAMPLE_DATA.strip()
else:
    is_example = False
    f = st.sidebar.file_uploader(TXT["uploadbox"], type=["csv"])
    if f is not None:
        try:
            df = pd.read_csv(f, dtype=str)
        except Exception:
            f.seek(0)
            df = pd.read_csv(f, sep=";", dtype=str)

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

if st.session_state.get("x_col") not in numeric_cols:
    st.session_state["x_col"] = numeric_cols[0]
if st.session_state.get("y_col") not in numeric_cols:
    st.session_state["y_col"] = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]

xcol = st.sidebar.selectbox(TXT["xvar"], numeric_cols, key="x_col")
ycol = st.sidebar.selectbox(TXT["yvar"], numeric_cols, key="y_col")

xv = num(df[xcol])
yv = num(df[ycol])
base = pd.DataFrame({"x": xv, "y": yv}).dropna()

xd0 = float(base["x"].min())
xd1 = float(base["x"].max())
yd0 = float(base["y"].min())
yd1 = float(base["y"].max())

xs = xd1 - xd0 or 1.0
ys = yd1 - yd0 or 1.0

# Reset sensible defaults only when the data/selected variables change.
data_signature = (
    xcol,
    ycol,
    len(base),
    float(base["x"].sum()),
    float(base["y"].sum()),
    xd0,
    xd1,
    yd0,
    yd1,
)

if st.session_state.get("data_signature") != data_signature:
    st.session_state["data_signature"] = data_signature
    loaded_pending = st.session_state.pop("_analysis_loaded_pending", False)

    if not loaded_pending:
        if is_example:
            # Demonstration defaults for the built-in cooling example only.
            st.session_state["fitmin"] = 3.0
            st.session_state["fitmax"] = 6.0
            st.session_state["linemin"] = 1.0
            st.session_state["linemax"] = 6.0
            st.session_state["known_x"] = 2.0
            st.session_state["known_y"] = float(yd0 + ys / 2)
            st.session_state["show_prediction"] = True
            st.session_state["prediction_mode"] = "y_from_x"
        else:
            # Generic datasets start with the complete X range, no extrapolation,
            # and prediction hidden by default.
            st.session_state["fitmin"] = xd0
            st.session_state["fitmax"] = xd1
            st.session_state["linemin"] = xd0
            st.session_state["linemax"] = xd1
            st.session_state["known_x"] = float(xd0 + xs / 3)
            st.session_state["known_y"] = float(yd0 + ys / 2)
            st.session_state["show_prediction"] = False
            st.session_state["prediction_mode"] = "y_from_x"

        st.session_state["sigfigs"] = infer_sig_figs(df, xcol, ycol)
        st.session_state["x_label"] = str(xcol)
        st.session_state["y_label"] = str(ycol)
        st.session_state["manual_xmin"] = float(xd0 - 0.05 * xs)
        st.session_state["manual_xmax"] = float(xd1 + 0.05 * xs)
        st.session_state["manual_ymin"] = float(yd0 - 0.08 * ys)
        st.session_state["manual_ymax"] = float(yd1 + 0.15 * ys)

# Defaults for controls that are independent of the loaded dataset.
st.session_state.setdefault("point_size", 60)
st.session_state.setdefault("axis_font", 16)
st.session_state.setdefault("tick_font", 14)
st.session_state.setdefault("show_regression", True)
st.session_state.setdefault("show_prediction", False)
st.session_state.setdefault("prediction_mode", "y_from_x")
st.session_state.setdefault("auto_limits", True)
st.session_state.setdefault("auto_margin_pct", 7)
st.session_state.setdefault("figure_width", 7.0)
st.session_state.setdefault("figure_height", 5.0)
st.session_state.setdefault("export_dpi", 300)

# ---------------------------------------------------------
# Appearance
# ---------------------------------------------------------
st.sidebar.header(TXT["appearance"])

ps = st.sidebar.slider(TXT["point"], min_value=10, max_value=200, step=5, key="point_size")
af = st.sidebar.slider(TXT["axisfont"], 8, 30, key="axis_font")
tf = st.sidebar.slider(TXT["tickfont"], 8, 26, key="tick_font")

xl = st.sidebar.text_input(TXT["xlabel"], key="x_label")
yl = st.sidebar.text_input(TXT["ylabel"], key="y_label")

# ---------------------------------------------------------
# Regression
# ---------------------------------------------------------
st.sidebar.header(TXT["reg"])

showreg = st.sidebar.checkbox(TXT["showreg"], key="show_regression")

fitmin, fitmax = xd0, xd1
linemin, linemax = xd0, xd1

if showreg:
    st.sidebar.caption(TXT["fithelp"])

    fitmin = st.sidebar.number_input(
        TXT["fitmin"],
        key="fitmin"
    )
    fitmax = st.sidebar.number_input(
        TXT["fitmax"],
        key="fitmax"
    )

    st.sidebar.caption(TXT["linehelp"])

    linemin = st.sidebar.number_input(
        TXT["linemin"],
        key="linemin"
    )
    linemax = st.sidebar.number_input(
        TXT["linemax"],
        key="linemax"
    )

# ---------------------------------------------------------
# Calculate regression early so prediction and auto-limits can use it
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
    showpred = st.sidebar.checkbox(TXT["showpred"], key="show_prediction")

    if showpred:
        choice = st.sidebar.radio(
            TXT["predmode"],
            ["y_from_x", "x_from_y"],
            format_func=lambda v: TXT["predy"] if v == "y_from_x" else TXT["predx"],
            key="prediction_mode"
        )

        if choice == "y_from_x":
            predmode = "y_from_x"
            known = st.sidebar.number_input(
                TXT["knownx"],
                key="known_x"
            )

            if reg_ok:
                px = known
                py = m * known + b

        else:
            predmode = "x_from_y"
            known = st.sidebar.number_input(
                TXT["knowny"],
                key="known_y"
            )

            if reg_ok:
                py = known

                if abs(m) < 1e-15:
                    pred_err = "zero"
                else:
                    px = (known - b) / m

# ---------------------------------------------------------
# Significant figures
# ---------------------------------------------------------
st.sidebar.header(TXT["sigsection"])
st.sidebar.caption(TXT["sighelp"])

sig = st.sidebar.slider(
    TXT["sig"],
    min_value=1,
    max_value=8,
    key="sigfigs"
)

# ---------------------------------------------------------
# Axis limits
# ---------------------------------------------------------
st.sidebar.header(TXT["limits"])

auto_limits = st.sidebar.checkbox(TXT["autolimits"], key="auto_limits")

auto_margin = st.sidebar.slider(
    TXT["margin"],
    min_value=0,
    max_value=25,
    step=1,
    key="auto_margin_pct"
) / 100.0

# Start with measured data.
all_x = list(base["x"].to_numpy())
all_y = list(base["y"].to_numpy())

# Add the complete displayed regression line.
if reg_ok and linemin < linemax:
    xx_for_limits = np.linspace(linemin, linemax, 300)
    yy_for_limits = m * xx_for_limits + b
    all_x.extend(xx_for_limits.tolist())
    all_y.extend(yy_for_limits.tolist())

# Add predicted point.
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
    xmin = st.sidebar.number_input(TXT["xmin"], key="manual_xmin")
    xmax = st.sidebar.number_input(TXT["xmax"], key="manual_xmax")
    ymin = st.sidebar.number_input(TXT["ymin"], key="manual_ymin")
    ymax = st.sidebar.number_input(TXT["ymax"], key="manual_ymax")

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
    step=0.5,
    key="figure_width"
)

fh = st.sidebar.number_input(
    TXT["height"],
    min_value=2.0,
    max_value=20.0,
    step=0.5,
    key="figure_height"
)

dpi = st.sidebar.selectbox(
    TXT["dpi"],
    [100, 150, 300, 600],
    key="export_dpi"
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
                    f"({TXT['fromto'].format(a=fs(fitmin, sig), b=fs(fitmax, sig))})"
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
# Save complete analysis state as a portable text file
# ---------------------------------------------------------
analysis_settings = {
    "x_col": xcol,
    "y_col": ycol,
    "point_size": ps,
    "axis_font": af,
    "tick_font": tf,
    "x_label": xl,
    "y_label": yl,
    "show_regression": showreg,
    "fitmin": fitmin,
    "fitmax": fitmax,
    "linemin": linemin,
    "linemax": linemax,
    "show_prediction": showpred,
    "prediction_mode": predmode,
    "known_x": st.session_state.get("known_x"),
    "known_y": st.session_state.get("known_y"),
    "sigfigs": sig,
    "auto_limits": auto_limits,
    "auto_margin_pct": st.session_state.get("auto_margin_pct", 7),
    "manual_xmin": st.session_state.get("manual_xmin"),
    "manual_xmax": st.session_state.get("manual_xmax"),
    "manual_ymin": st.session_state.get("manual_ymin"),
    "manual_ymax": st.session_state.get("manual_ymax"),
    "figure_width": fw,
    "figure_height": fh,
    "export_dpi": dpi,
}

analysis_results = None
if res is not None:
    analysis_results = {
        "slope": float(res["m"]),
        "intercept": float(res["b"]),
        "r_squared": None if not np.isfinite(res["r2"]) else float(res["r2"]),
        "predicted_x": None if res["px"] is None else float(res["px"]),
        "predicted_y": None if res["py"] is None else float(res["py"]),
    }

analysis_payload = {
    "format": "KodaPlot analysis",
    "version": 1,
    "data": {
        "text": df.to_csv(sep="\t", index=False, lineterminator="\n")
    },
    "settings": analysis_settings,
    "results": analysis_results,
}

analysis_text = json.dumps(analysis_payload, ensure_ascii=False, indent=2)
save_analysis_placeholder.download_button(
    TXT["save_analysis"],
    data=analysis_text.encode("utf-8"),
    file_name="kodaplot_analysis.txt",
    mime="text/plain",
    use_container_width=True
)

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
            file_name=f"kodaplot.{fmt.lower()}",
            mime=mime,
            use_container_width=True
        )

plt.close(fig)
