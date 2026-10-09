"""Regenerate every EDA figure and table without running the notebook.

    .venv/bin/python src/make_figures.py

Writes PNGs to outputs/figures/, tables to outputs/tables/, and 1800 px JPEG copies of the figures the report uses to
report/figures/. The notebook (notebooks/01_eda.ipynb) calls the same functions; this script just runs them in one go.
"""
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402

import viz  # noqa: E402
import viz_eda  # noqa: E402

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
C, F, T, R = ROOT / "data" / "clean", ROOT / "outputs" / "figures", ROOT / "outputs" / "tables", ROOT / "report" / "figures"
for p in (F, T, R):
    p.mkdir(parents=True, exist_ok=True)
viz.set_style()
slug = lambda m: m.lower().replace(" ", "_")


def save(fig, name):
    fig.savefig(F / f"{name}.png")
    plt.close(fig)


gd = viz.gradient_data(C)
acs = pd.read_csv(C / "zip_acs.csv", dtype={"zip": str})
flags = pd.read_csv(C / "zip_flags.csv", dtype={"zip": str})
zorig = pd.read_csv(C / "zori_growth.csv", dtype={"zip": str})
zc = gpd.read_file(C / "zcta_boundaries.gpkg")[["zip", "geometry"]]
ref = pd.read_csv(ROOT / "data" / "reference" / "city_centers.csv")

# 2.1
save(viz_eda.distributions(gd), "2_1a_distributions")
save(viz_eda.log_check(gd), "2_1b_log_check")
save(viz_eda.flags_by_distance(flags), "2_1c_flags_by_distance")
# 2.2
for m in viz.METRO_ORDER:
    save(viz.gradient_metro(gd, m), f"2_2_gradient_{slug(m)}")
fits = []
for m in viz.TWO_CENTER:
    for meas in ("level", "growth"):
        fig, st = viz.two_center(gd, m, measure=meas)
        save(fig, f"2_2_two_center_{meas}_{m.lower()}")
        fits.append(st.assign(metro=m, measure=meas))
pd.concat(fits).to_csv(T / "two_center_fits.csv", index=False)
tab = viz.slope_table(gd)
tab.to_csv(T / "gradient_slopes.csv", index=False)
save(viz.slope_summary(tab), "2_2_slope_summary")
# 2.3
rel = viz_eda.relative_growth(gd)
lim = viz_eda.growth_limit(rel)
for m in viz.METRO_ORDER:
    save(viz_eda.growth_maps(zc, rel, ref, m, lim), f"2_3a_growth_map_{slug(m)}")
save(viz_eda.level_quintile_maps(zc, gd, ref), "2_3b_level_quintile_maps")
# 2.4
xd = viz_eda.exposure_data(gd, acs)
fig, slopes = viz_eda.exposure_scatter(xd)
save(fig, "2_4a_exposure_scatter")
slopes.to_csv(T / "exposure_slopes.csv", index=False)
save(viz_eda.exposure_confounds(xd), "2_4c_exposure_confounds")
fig, cm = viz_eda.exposure_corr(xd)
save(fig, "2_4b_exposure_corr")
cm.to_csv(T / "exposure_corr.csv")
# 2.5
panel = pd.read_parquet(C / "zhvi_analysis_panel.parquet", columns=["zip", "date", "index_dec2019"])
P = viz_eda.path_matrix(panel, gd)
save(viz_eda.trajectory_panels(P, gd), "2_5a_trajectories")
save(viz_eda.relative_paths(P, gd), "2_5b_relative_paths")
sil, labels, k = viz_eda.cluster_paths(P)
fig, comp = viz_eda.cluster_figure(P, gd, sil, labels, k)
save(fig, "2_5c_clusters")
viz_eda.cluster_profile(gd, acs, labels).round(2).to_csv(T / "cluster_profile.csv")
sil.round(3).to_csv(T / "cluster_silhouette.csv")
comp.round(1).to_csv(T / "cluster_metro_composition.csv")
# 2.6
rt = viz_eda.robustness_table(gd, flags)
rt.to_csv(T / "robustness_flag_free.csv", index=False)
save(viz_eda.robustness_figure(rt), "2_6a_flag_free")
fig, rent = viz_eda.rent_vs_price(gd, zorig)
save(fig, "2_6c_rent_vs_price")
rent.to_csv(T / "rent_vs_price_slopes.csv", index=False)

# JPEG copies for the report
used = [p.stem for p in F.glob("2_*.png")]
for stem in used:
    im = Image.open(F / f"{stem}.png").convert("RGB")
    if im.width > 1800:
        im = im.resize((1800, round(im.height * 1800 / im.width)), Image.LANCZOS)
    im.save(R / f"{stem}.jpg", quality=90, optimize=True, subsampling=0)
print(f"{len(used)} figures written; report copies in {R}")
