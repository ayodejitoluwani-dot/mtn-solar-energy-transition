import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

BLUE  = "#1F4E79"; LIGHT = "#2E75B6"; ACCENT = "#F4A21E"
GREEN = "#27AE60"; RED   = "#C0392B"; GRAY   = "#555555"
ORANGE= "#E67E22"; BG    = "#F7F9FC"

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'figure.facecolor': BG,
    'axes.facecolor': BG, 'axes.spines.top': False, 'axes.spines.right': False
})

df = pd.read_csv('/Users/chugga/Desktop/MTN energy/mtn_energy.csv')

def billions(x, _): return f'₦{x/1e9:.1f}B'
def millions(x, _):  return f'₦{x/1e6:.0f}M'

# ── CHART 1: Energy Cost Overview ────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(17, 5))
fig.suptitle('MTN Nigeria — Current Diesel Energy Cost Overview', fontsize=15, fontweight='bold', color=BLUE)

# Cost by asset type
cost_by_type = df.groupby('asset_type')['annual_diesel_cost_ngn'].sum()
wedges, texts, autotexts = axes[0].pie(
    cost_by_type.values, labels=['Cell Towers', 'Offices & Facilities'],
    autopct='%1.1f%%', colors=[BLUE, ACCENT], wedgeprops=dict(width=0.55),
    startangle=90, textprops={'fontsize': 11})
for at in autotexts: at.set_color('white'); at.set_fontweight('bold')
axes[0].set_title('Annual Diesel Cost Split', fontweight='bold', color=BLUE)

# Cost by state (top 10)
state_cost = df.groupby('state')['annual_diesel_cost_ngn'].sum().sort_values(ascending=True).tail(10)
bar_colors = [RED if v == state_cost.max() else LIGHT for v in state_cost.values]
axes[1].barh(state_cost.index, state_cost.values, color=bar_colors, edgecolor='white')
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(billions))
axes[1].set_title('Top 10 States by Diesel Cost', fontweight='bold', color=BLUE)
axes[1].set_xlabel('Annual Diesel Cost')

# Tower type cost breakdown
tower_cost = df[df['asset_type']=='Cell Tower'].groupby('tower_type')['annual_diesel_cost_ngn'].mean()
bars = axes[2].bar(tower_cost.index, tower_cost.values, color=[BLUE, LIGHT, ACCENT], edgecolor='white', linewidth=1.5)
for bar, val in zip(bars, tower_cost.values):
    axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100000,
                 f'₦{val/1e6:.1f}M', ha='center', fontsize=10, fontweight='bold', color=BLUE)
axes[2].yaxis.set_major_formatter(mticker.FuncFormatter(millions))
axes[2].set_title('Avg Annual Diesel Cost\nby Tower Type', fontweight='bold', color=BLUE)
axes[2].set_ylabel('Annual Cost (NGN)')

plt.tight_layout()
plt.savefig('/Users/chugga/Desktop/MTN energy/mtn_chart1_overview.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 1 saved")

# ── CHART 2: Solar Opportunity ───────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(17, 5))
fig.suptitle('Solar Transition Opportunity', fontsize=15, fontweight='bold', color=BLUE)

# Diesel cost vs solar saving
categories = ['Current\nDiesel Cost', 'Potential\nSolar Saving', 'Residual\nCost']
total_diesel  = df['annual_diesel_cost_ngn'].sum()
total_saving  = df['annual_solar_saving_ngn'].sum()
residual      = total_diesel - total_saving
values = [total_diesel, total_saving, residual]
colors = [RED, GREEN, ORANGE]
bars = axes[0].bar(categories, values, color=colors, edgecolor='white', linewidth=1.5, width=0.5)
for bar, val in zip(bars, values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50_000_000,
                 f'₦{val/1e9:.2f}B', ha='center', fontsize=11, fontweight='bold')
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(billions))
axes[0].set_title('Annual Cost vs Saving\n(Full Portfolio)', fontweight='bold', color=BLUE)
axes[0].set_ylabel('NGN per Year')

# Solar irradiance by state
irr_state = df.groupby('state')['solar_irradiance'].mean().sort_values(ascending=True)
bar_colors2 = [GREEN if v >= 6.0 else LIGHT if v >= 5.5 else ACCENT for v in irr_state.values]
axes[1].barh(irr_state.index, irr_state.values, color=bar_colors2, edgecolor='white')
axes[1].axvline(5.5, color=RED, lw=1.5, linestyle='--', label='High solar threshold (5.5)')
axes[1].set_title('Solar Irradiance by State\n(kWh/m²/day)', fontweight='bold', color=BLUE)
axes[1].set_xlabel('Avg Solar Irradiance')
axes[1].legend(fontsize=9)

# Payback period distribution
payback_clip = df['payback_years'].clip(0, 6)
axes[2].hist(payback_clip, bins=25, color=LIGHT, edgecolor='white', linewidth=0.8)
axes[2].axvline(payback_clip.mean(), color=RED, lw=2, linestyle='--',
                label=f'Avg payback: {payback_clip.mean():.1f} yrs')
axes[2].axvline(3, color=GREEN, lw=2, linestyle='--', label='3-year target')
axes[2].set_title('Solar Investment Payback\nPeriod Distribution', fontweight='bold', color=BLUE)
axes[2].set_xlabel('Payback Period (Years)')
axes[2].set_ylabel('Number of Assets')
axes[2].legend(fontsize=9)

plt.tight_layout()
plt.savefig('/Users/chugga/Desktop/MTN energy/mtn_chart2_solar.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 2 saved")

# ── CHART 3: ROI & 10-Year Savings ───────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Financial Case for Solar Transition', fontsize=15, fontweight='bold', color=BLUE)

# 10-year cumulative savings vs capex
years = np.arange(0, 11)
total_capex   = df['solar_capex_ngn'].sum()
annual_saving = df['annual_solar_saving_ngn'].sum()
cumulative_saving  = np.array([max(0, annual_saving * y - total_capex) for y in years])
cumulative_cost    = np.array([total_capex + (total_diesel - annual_saving) * y for y in years])
cumulative_diesel  = np.array([total_diesel * y for y in years])

axes[0].plot(years, cumulative_diesel/1e9,  color=RED,   lw=2.5, marker='o', markersize=5, label='Do nothing (diesel only)')
axes[0].plot(years, cumulative_cost/1e9,    color=ORANGE, lw=2.5, marker='s', markersize=5, label='Solar transition (capex + residual)')
axes[0].fill_between(years, cumulative_cost/1e9, cumulative_diesel/1e9, alpha=0.15, color=GREEN, label='Cumulative savings')
axes[0].set_title('10-Year Cost: Diesel vs Solar Transition', fontweight='bold', color=BLUE)
axes[0].set_xlabel('Years'); axes[0].set_ylabel('Cumulative Cost (₦B)')
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'₦{x:.0f}B'))
axes[0].legend(fontsize=9)

# Priority matrix: saving vs payback (bubble = co2)
sample = df.sample(80, random_state=42)
scatter = axes[1].scatter(
    sample['payback_years'].clip(0,5),
    sample['annual_solar_saving_ngn']/1e6,
    c=sample['co2_annual_kg']/1000,
    s=60, cmap='RdYlGn_r', alpha=0.7, edgecolors='white', linewidth=0.5
)
axes[1].axvline(2, color=RED, lw=1.5, linestyle='--', alpha=0.7, label='2-yr payback line')
axes[1].set_title('Asset Priority Matrix\nPayback vs Annual Saving', fontweight='bold', color=BLUE)
axes[1].set_xlabel('Payback Period (Years)')
axes[1].set_ylabel('Annual Solar Saving (₦M)')
axes[1].legend(fontsize=9)
cbar = plt.colorbar(scatter, ax=axes[1])
cbar.set_label('CO₂ (tonnes/yr)', fontsize=9)

plt.tight_layout()
plt.savefig('/Users/chugga/Desktop/MTN energy/mtn_chart3_roi.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 3 saved")

# ── CHART 4: Top Priority Assets ─────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Priority Assets for Immediate Solar Conversion', fontsize=15, fontweight='bold', color=BLUE)

# Top 10 assets by annual saving
top10 = df.nlargest(10, 'annual_solar_saving_ngn')[['asset_id','state','annual_solar_saving_ngn','payback_years']]
bar_colors3 = [GREEN if p <= 1 else LIGHT if p <= 2 else ACCENT for p in top10['payback_years']]
axes[0].barh(top10['asset_id'] + ' (' + top10['state'] + ')',
             top10['annual_solar_saving_ngn']/1e6,
             color=bar_colors3, edgecolor='white')
axes[0].set_title('Top 10 Assets by Annual Solar Saving', fontweight='bold', color=BLUE)
axes[0].set_xlabel('Annual Saving (₦M)')

# Saving by state
state_saving = df.groupby('state')['annual_solar_saving_ngn'].sum().sort_values(ascending=True)
state_colors = [GREEN if v == state_saving.max() else LIGHT for v in state_saving.values]
axes[1].barh(state_saving.index, state_saving.values/1e6, color=state_colors, edgecolor='white')
axes[1].set_title('Total Solar Saving Potential by State', fontweight='bold', color=BLUE)
axes[1].set_xlabel('Annual Saving (₦M)')

plt.tight_layout()
plt.savefig('/Users/chugga/Desktop/MTN energy/mtn_chart4_priority.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 4 saved")

# ── SAVE METRICS ─────────────────────────────────────────────────────────────
import json
ten_yr_diesel  = total_diesel * 10
ten_yr_solar   = total_capex + (total_diesel - annual_saving) * 10
ten_yr_net_save= ten_yr_diesel - ten_yr_solar

metrics = {
    "total_assets": int(len(df)),
    "total_towers": int((df['asset_type']=='Cell Tower').sum()),
    "total_offices": int((df['asset_type']=='Office/Facility').sum()),
    "annual_diesel_cost_ngn": round(total_diesel/1e9, 2),
    "annual_solar_saving_ngn": round(annual_saving/1e9, 2),
    "solar_capex_ngn": round(total_capex/1e9, 2),
    "avg_payback_years": round(float(df['payback_years'].clip(0,6).mean()), 1),
    "annual_co2_tonnes": round(float(df['co2_annual_kg'].sum()/1000), 0),
    "ten_year_net_saving_ngn": round(ten_yr_net_save/1e9, 2),
    "saving_pct": round(annual_saving/total_diesel*100, 1),
}
with open('/Users/chugga/Desktop/MTN energy/mtn_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("\n=== KEY METRICS ===")
for k, v in metrics.items():
    print(f"{k}: {v}")
