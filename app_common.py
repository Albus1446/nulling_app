"""讲义共用的工具：页面设置、章节状态、带缓存的计算、显示图片。"""
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

import core as nl
import schematics as S
import optics as O

MAS = S.MAS


def page(title, subtitle=None):
    st.set_page_config(page_title=title, layout="wide")
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def show(fig):
    import os
    S.prepare_figure(fig)
    image = BytesIO()
    fig.savefig(image, format="png", bbox_inches="tight", pad_inches=0.2, dpi=160)
    out = os.environ.get("NULLING_APP_SAVE_FIGS")      # 仅用于离线检查图件，正常使用时不设置
    if out:
        os.makedirs(out, exist_ok=True)
        n = len(os.listdir(out))
        with open(os.path.join(out, f"fig{n:02d}.png"), "wb") as output:
            output.write(image.getvalue())
    st.image(image.getvalue(), width="stretch")
    plt.close(fig)


def goal(text):
    st.info("**这一节的实验：** " + text.strip())


def think(question, answer):
    with st.expander("想一想：" + question):
        st.markdown(answer)


def control_value(key, default):
    """以保存的值初始化重新出现的控件，避免同时赋默认值和控件状态。"""
    saved = st.session_state.get("_lesson_values", {})
    return st.session_state.get(key, saved.get(key, default))


def save_controls(section):
    """用不绑定控件的状态保存参数；按钮是一次动作，不保存。"""
    values = dict(st.session_state.get("_lesson_values", {}))
    prefix = f"lesson_{section}_"
    values.update({key: value for key, value in st.session_state.items() if key.startswith(prefix)})
    st.session_state["_lesson_values"] = values


@st.cache_data(show_spinner="正在计算各光源的光谱与旋转信号……", max_entries=4)
def observation(**parameters):
    return O.spectral_observation(**parameters)


@st.cache_data(show_spinner="正在准备候选位置的匹配模板……", max_entries=2)
def search_library(baseline, diameter, half_width, planet_counts):
    inst = nl.build_instrument(nl.default_config(instrument__D=diameter, array__baseline=baseline))
    samp = nl.rotation_sampling(nl.default_config(), inst)
    return O.search_templates(dict(inst=inst, samp=samp, planet_counts=np.array(planet_counts)), half_width)


STAR_TYPES = {
    "类太阳恒星（G 型，5800 K）": (5778.0, 1.0),
    "橙矮星（K 型，5000 K）": (5000.0, 0.8),
    "红矮星（M 型，3500 K）": (3500.0, 0.45),
}


@st.cache_resource(show_spinner="正在计算目标场景……")
def bundle(baseline=14.5, distance=10.0, exozodi=1.0, T_star=5778.0, R_star=1.0, sep=None, pa=40.0, hours=10.0, q=6.0):
    """仪器、目标、旋转采样与光子预算。sep=None 时把行星放在等效地球受照处。"""
    L_star = R_star**2 * (T_star / 5780.0) ** 4
    if sep is None:
        sep = np.sqrt(L_star) / distance
    cfg = nl.default_config(array__baseline=float(baseline), array__ratio=float(q), star__distance=float(distance),
                            exozodi=float(exozodi), star__temperature=float(T_star), star__radius=float(R_star),
                            planet__ang_sep=float(sep), planet__ang_pa=float(pa), array__integration_h=float(hours))
    cfg["npix"] = 128
    inst = nl.build_instrument(cfg)
    sc = nl.build_scene(cfg, inst)
    samp = nl.rotation_sampling(cfg, inst)
    bud = nl.photon_budget(inst, sc, samp)
    e3, e4, pchop = nl.expected_counts(inst, sc, samp, bud)
    return {"cfg": cfg, "inst": inst, "scene": sc, "samp": samp, "bud": bud, "e3": e3, "e4": e4, "pchop": pchop,
            "true": np.array(nl.planet_sky_position(sc)) / MAS}


@st.cache_resource(show_spinner="正在准备\"指纹库\"（相关图模板）……")
def templates(baseline=14.5, q=6.0, half_width=150.0):
    """相关图模板：只用 6 µm 以长的谱道、每 4 步取 1 步、81×81 网格，以保证网页响应快。"""
    b = bundle(baseline=baseline, q=q)
    wl = b["inst"]["wl"]
    return nl.correlation_templates(b["inst"], b["samp"], wl_idx=np.where(wl > 6e-6)[0], step=4,
                                    grid_mas=(-half_width, half_width), n_grid=81)
