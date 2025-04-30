import streamlit as st
import pandas as pd
import plotly.express as px
import io
import matplotlib.pyplot as plt

st.title("Evolution of Carbonate Chemistry since Pre-Industrial Times")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('datasheet.csv', skiprows=1)
    # strip whitespace from column names
    df.columns = df.columns.str.strip()
    # add a time index if no Year column
    if 'Year' not in df.columns:
        df['Year'] = df.index
    return df

df = load_data()

# plot settings
st.header("Input Conditions and Results Overview")
st.write("Data loaded with {} rows".format(len(df)))

# Compute and plot Omega CaCO3 (saturation state)
# approximate calcium concentration (mol/kgSW) and Ksp (calcite)
Ca_mol = 0.01028  # mol/kgSW
Ksp_calcite = 3.3e-7
# convert CO3 from mmol to mol
df['CO3_mol'] = df['CO3 out (mmol/kgSW)'] * 1e-3
# compute Omega
df['Omega_CaCO3'] = (Ca_mol * df['CO3_mol']) / Ksp_calcite

# add grouping by Year to compute mean values
df_group = df.groupby('Year').agg({
    'pCO2 out (matm)': 'mean',
    'pH out': 'mean',
    'CO3 out (mmol/kgSW)': 'mean',
    'Omega_CaCO3': 'mean',
    't(oC) out': 'mean',
    'P (dbars) out': 'mean'
}).reset_index()

# display Input Conditions
st.subheader("Input Conditions")
st.write(df[['t(oC) out','P (dbars) out']].head())

# display Results for Input Conditions (mean values)
st.subheader("Mean Results for Input Conditions")
st.write(df_group.head())

# update plots to use mean series
# Plot mean pCO2 evolution
st.subheader("Mean pCO2 (µatm) over Time")
fig1 = px.line(df_group, x='Year', y='pCO2 out (matm)', title='Mean pCO2 evolution')
st.plotly_chart(fig1, use_container_width=True)

# Plot mean pH evolution
st.subheader("Mean pH over Time")
fig2 = px.line(df_group, x='Year', y='pH out', title='Mean pH evolution')
st.plotly_chart(fig2, use_container_width=True)

# Plot mean carbonate concentration evolution
st.subheader("Mean [CO3^2-] (mmol/kgSW) over Time")
fig3 = px.line(df_group, x='Year', y='CO3 out (mmol/kgSW)', title='Mean Carbonate ion concentration evolution')
st.plotly_chart(fig3, use_container_width=True)

# Plot mean Omega CaCO3 evolution
st.subheader("Mean ΩCaCO3 (Calcite saturation) over Time")
fig4 = px.line(df_group, x='Year', y='Omega_CaCO3', title='Mean Omega CaCO3 evolution')
st.plotly_chart(fig4, use_container_width=True)

# Estimate change in mean saturation state
delta_mean = df_group['Omega_CaCO3'].iloc[-1] - df_group['Omega_CaCO3'].iloc[0]
st.write(f"Estimated change in mean ΩCaCO3 between start and end: {delta_mean:.2f}")

# Additional helpful graphs
st.subheader("Mean Temperature over Time")
fig_temp = px.line(df_group, x='Year', y='t(oC) out', title='Mean Temperature Evolution')
st.plotly_chart(fig_temp, use_container_width=True)

st.subheader("Mean Pressure over Time")
fig_press = px.line(df_group, x='Year', y='P (dbars) out', title='Mean Pressure Evolution')
st.plotly_chart(fig_press, use_container_width=True)

st.subheader("Scatter: Mean pCO2 vs pH")
fig_scatter = px.scatter(df_group, x='pCO2 out (matm)', y='pH out', title='Mean pCO2 vs pH', trendline='ols')
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Correlation Heatmap")
corr_cols = ['pCO2 out (matm)', 'pH out', 'CO3 out (mmol/kgSW)', 'Omega_CaCO3', 't(oC) out', 'P (dbars) out']
corr = df_group[corr_cols].corr()
fig_heatmap = px.imshow(corr, text_auto=True, title='Correlation Matrix')
st.plotly_chart(fig_heatmap, use_container_width=True)

st.subheader("Histogram of ΩCaCO3")
fig_hist = px.histogram(df_group, x='Omega_CaCO3', nbins=30, title='ΩCaCO3 Distribution')
st.plotly_chart(fig_hist, use_container_width=True)

st.header("Downloadable Matplotlib Plots")

def create_and_download_fig(df, x, y, title, filename):
    fig, ax = plt.subplots()
    ax.plot(df[x], df[y])
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    st.pyplot(fig)
    st.download_button(
        label=f"Download {title} as PNG",
        data=buf,
        file_name=filename,
        mime="image/png"
    )
    plt.close(fig)

create_and_download_fig(df_group, 'Year', 'pCO2 out (matm)', 'Mean pCO2 evolution', 'pco2_evolution.png')
create_and_download_fig(df_group, 'Year', 'pH out', 'Mean pH evolution', 'ph_evolution.png')
create_and_download_fig(df_group, 'Year', 'CO3 out (mmol/kgSW)', 'Mean [CO3^2-] evolution', 'co3_evolution.png')
create_and_download_fig(df_group, 'Year', 'Omega_CaCO3', 'Mean Omega CaCO3 evolution', 'omega_caco3_evolution.png')

#create combined plot for all metrics
fig, ax = plt.subplots()
metrics = [
    ('pCO2 out (matm)', 'Mean pCO2'),
    ('pH out', 'Mean pH'),
    ('CO3 out (mmol/kgSW)', 'Mean CO3'),
    ('Omega_CaCO3', 'Mean Omega CaCO3'),
    ('t(oC) out', 'Mean Temp'),
    ('P (dbars) out', 'Mean Pressure')
]
for col, label in metrics:
    ax.plot(df_group['Year'], df_group[col], label=label)
ax.set_xlabel('Year')
ax.set_title('All Mean Metrics Over Time')
ax.legend()
buf_all = io.BytesIO()
fig.savefig(buf_all, format='png')
buf_all.seek(0)
st.pyplot(fig)
st.download_button(
    label="Download combined metrics plot as PNG",
    data=buf_all,
    file_name="combined_metrics.png",
    mime="image/png"
)
plt.close(fig)