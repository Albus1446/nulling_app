import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import app_common as C
import schematics as S
import core as nl

C.page("7  找到行星", "拿\"指纹库\"去比对")
C.goal("怎样从带噪声的数据中找出行星的位置；什么是相关图；为什么数据越多越可靠。")

st.markdown("""
这一步很像手机上的**听歌识曲**：录下一段嘈杂的音乐，拿去和曲库里每一首歌比对，最像的那首就是答案。

1. **指纹库**：对天空中每一个可能的位置，算出"如果行星在这里，信号应该长什么样"（第 5 页的曲线，每个波长一条）。
2. **比对**：把实际测到的数据和每一个指纹逐点相乘再加起来，得到一个"相似度分数"。
3. **找最大值**：把所有位置的分数画成一张图（**相关图**），最亮的地方就是行星。

比对时，噪声大的波长（短波长）分量会降低权重，噪声小的分量权重高——就像嘈杂的片段在听歌识曲里不太算数。
""")

if "seed7" not in st.session_state:
    st.session_state.seed7 = 0
c1, c2 = st.columns([1, 2.6])
with c1:
    hours = st.slider("观测时间（小时）", 1.0, 40.0, 10.0, 1.0, key="h7")
    weighted = st.toggle("按噪声大小给各波长加权", value=True)
    if st.button("再观测一次（换一组随机噪声）"):
        st.session_state.seed7 += 1
bd = C.bundle()
tpl = C.templates()
f = hours / 10
e3, e4 = bd["e3"] * f, bd["e4"] * f
rng = np.random.default_rng(st.session_state.seed7)
data = nl.simulate_chop(e3, e4, rng)
w = 1.0 / (e3 + e4).mean(axis=1) if weighted else None
cm = nl.correlation_map(tpl, data, w)
_, found = nl.locate(tpl, cm)
true = bd["true"]
err = float(np.hypot(*(found - true)))
snr = bd["bud"]["snr_total"] * np.sqrt(f)
with c1:
    st.metric("SNR", f"{snr:.1f}")
    st.metric("找到的位置与真实位置相差", f"{err:.1f} mas", delta="找对了" if err < 10 else "找错了",
              delta_color="normal" if err < 10 else "inverse")
with c2:
    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    hw = 150
    im = ax.imshow(cm / np.abs(cm).max(), extent=[-hw, hw, -hw, hw], cmap="RdBu_r", vmin=-1, vmax=1)
    ax.plot(0, 0, "*", color=S.STAR, ms=14, mec="k", mew=0.5)
    ax.plot(*true, "o", ms=13, mfc="none", mec="k", mew=1.5, label="真实位置")
    ax.plot(*found, "x", ms=11, color="k", mew=2, label="找到的位置（最亮处）")
    ax.set_xlabel("mas"); ax.set_ylabel("mas"); ax.legend(loc="lower left", fontsize=8.5)
    ax.set_title("相关图：每一点的颜色 = 该位置的相似度")
    fig.colorbar(im, ax=ax, shrink=0.8)
    C.show(fig)

st.markdown("""
**观察**：相关图在行星处最亮（红）；在关于恒星对称的位置有一个"负的影子"（蓝），因为那里的指纹正好和行星反号。
行星周围还有一圈圈较亮的"回声"（旁瓣）——有噪声时，偶尔某个回声会比真正的行星更亮，就会**找错位置**。
""")

st.header("多观测几次，统计一下")
st.markdown("同样的条件重复观测 100 次，看看有多少次找对了。")
if st.button("开始 100 次模拟"):
    rng = np.random.default_rng(100)
    errs = np.array([np.hypot(*(nl.locate(tpl, nl.correlation_map(tpl, nl.simulate_chop(e3, e4, rng), w))[1] - true))
                     for _ in range(100)])
    ok = errs < 10
    c1, c2 = st.columns([1, 2.4])
    c1.metric("找对的次数（误差 < 10 mas）", f"{ok.sum()} / 100")
    if ok.any():
        c1.metric("找对时的典型误差", f"{np.median(errs[ok]):.1f} mas")
    with c2:
        fig, ax = plt.subplots(figsize=(6.4, 2.6))
        ax.hist(np.clip(errs, 0, 60), bins=30, color=S.GREY)
        ax.axvline(10, color=S.RED, ls="--", lw=1)
        ax.set_xlabel("误差（mas，超过 60 的计入最右一格）"); ax.set_ylabel("次数")
        C.show(fig)
    st.caption("试试：把观测时间调到 3 小时或 30 小时，或者关掉加权，再跑一次。")

st.success("**小结**：相关图 = 拿每个位置的指纹去和数据比对。SNR 越高，真正的行星越突出，越不容易被\"回声\"冒充。"
           "要可靠地定位，通常需要 SNR 达到 10 以上，比单纯\"探测到\"（SNR ≈ 5）要求更高。")
C.think("为什么关掉加权后经常找错？",
        "短波长的数据噪声最大、行星信号又最弱。不加权时，这些噪声和长波长的有用信号同等对待，把相关图搅乱了。")
C.think("找到位置以后，还能得到什么？",
        "在找到的位置上，逐个波长比较数据和指纹的幅度，就能得到行星在每个波长的亮度——也就是行星的**光谱**，可以用来研究它的温度和大气。")
