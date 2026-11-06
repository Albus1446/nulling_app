import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import app_common as C
import schematics as S

C.page("6  光子噪声与信噪比", "光是一颗一颗到来的")
C.goal("什么是光子噪声；为什么观测时间越长越好；信噪比（SNR）怎么理解。")

st.header("像接雨滴一样数光子")
st.markdown("""
探测器接收光，其实是在**数光子**。光子到达是随机的，就像下雨时数一个杯子里接到的雨滴：
平均每次接到 N 滴，但每次实际接到的数会上下浮动，浮动大小约为 **√N**。这种随机起伏叫做**光子噪声**。
""")
c1, c2 = st.columns([1, 2.4])
with c1:
    N = st.select_slider("平均每次接到的光子数 N", options=[10, 30, 100, 300, 1000, 3000, 10000], value=100)
    st.metric("起伏大小 √N", f"{np.sqrt(N):.0f}")
    st.metric("相对起伏 √N / N", f"{1 / np.sqrt(N):.1%}")
with c2:
    rng = np.random.default_rng(0)
    x = rng.poisson(N, 3000)
    fig, ax = plt.subplots(figsize=(7, 2.6))
    ax.hist(x, bins=40, color=S.GREY)
    ax.axvline(N, color="k", lw=1.5); ax.axvspan(N - np.sqrt(N), N + np.sqrt(N), color=S.BRIGHT, alpha=0.35)
    ax.set_xlabel("一次接到的光子数"); ax.set_ylabel("次数"); ax.set_title("重复 3000 次的结果：黄色带宽约 ±√N")
    C.show(fig)
st.markdown("N 越大，起伏的绝对值越大，但**相对**起伏越小。所以光子越多，测量越准。")

st.header("暗输出里的光子从哪里来")
bd = C.bundle()
bud, inst = bd["bud"], bd["inst"]
wl = inst["wl"] * 1e6
k = bd["samp"]["t_int"] * inst["eta"]
parts = {"恒星漏光": (bud["sl3"] + bud["sl4"]) * k, "本地黄道光（太阳系内的尘埃）": (bud["lz3"] + bud["lz4"]) * k,
         "外黄道光（目标恒星的尘埃）": (bud["ez3"] + bud["ez4"]) * k, "行星": bud["P"]}
fig, ax = plt.subplots(figsize=(8.4, 3.0))
bottom = np.zeros_like(wl)
tot = sum(parts.values())
for (name, v), col in zip(parts.items(), [S.STAR, "#2CA02C", S.DUST, S.PLANET]):
    ax.bar(wl, v / tot, bottom=bottom, width=inst["dwl"] * 1e6 * 0.92, color=col, label=name)
    bottom += v / tot
ax.set_xlabel("波长（微米）"); ax.set_ylabel("所占比例"); ax.set_ylim(0, 1)
ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8.5)
ax.set_title("10 秒差距外的类太阳恒星，观测 10 小时：两路暗输出里的光子来源")
C.show(fig)
st.markdown("""
短波长时几乎全是恒星漏光（第 3 页），长波长时以尘埃的光为主。行星只占极小一部分——
它们的平均值被斩波去掉了，但它们的**光子噪声**还在，这才是真正限制我们的东西。
""")

st.header("信噪比：信号比噪声大多少倍")
st.latex(r"\text{SNR} = \frac{\text{行星信号}}{\text{噪声}} \approx \frac{\text{行星光子数}}{\sqrt{\text{背景光子数}}}")
st.markdown("""
观测时间加倍，行星光子数加倍，噪声只增加 √2 倍，所以 **SNR ∝ √时间**。
天文学家通常要求 **SNR ≥ 5** 才算"探测到"。
""")
c1, c2 = st.columns([1, 2.4])
with c1:
    hours = st.slider("观测时间（小时）", 1.0, 50.0, 10.0, 1.0)
    w = st.select_slider("看哪个波长的数据（微米）", options=[f"{v:.1f}" for v in wl], value=f"{wl[22]:.1f}")
    wi = [f"{v:.1f}" for v in wl].index(w)
    snr = bud["snr_total"] * np.sqrt(hours / 10)
    st.metric("全部波长合起来的 SNR", f"{snr:.1f}", delta="已达到 5" if snr >= 5 else "还不到 5")
    st.metric("达到 SNR = 5 需要", f"{10 * (5 / bud['snr_total']) ** 2:.1f} 小时")
with c2:
    f = hours / 10
    rng = np.random.default_rng(1)
    e3, e4 = bd["e3"][wi] * f, bd["e4"][wi] * f
    data = rng.poisson(e3) - rng.poisson(e4)
    phis = np.rad2deg(bd["samp"]["phi"])
    sig = np.sqrt((e3 + e4).mean())
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    ax.plot(phis, data, ".", ms=3, color=S.GREY, label=f"测到的斩波数据（每 1° 一个点，噪声约 ±{sig:.0f}）")
    ax.plot(phis, bd["pchop"][wi] * f, color=S.PLANET, lw=1.8, label="行星信号（没有噪声时）")
    ax.axhline(0, color="0.8", lw=0.6)
    ax.set_xlabel("阵列转过的角度（°）"); ax.set_ylabel("光子数")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8.5)
    ax.set_title(f"{wl[wi]:.1f} µm 处，观测 {hours:g} 小时的单个波长数据", pad=24)
    C.show(fig)
st.markdown("单个波长的数据噪声很大，几乎看不出行星。把所有波长、所有旋转角度的信息合在一起，SNR 才够大。")

st.success("**小结**：光子噪声 ≈ √N；SNR ∝ √观测时间；尘埃和漏光越多，噪声越大，需要的时间越长。")
C.think("要把 SNR 从 5 提高到 10，观测时间要变成多少倍？", "SNR ∝ √时间，SNR 翻倍需要 4 倍的时间。")
C.think("为什么短波长的数据几乎没用？",
        "短波长时行星本身很暗（它的温度只有约 255 K，主要在长波长发光），而恒星漏光又最多（零深 ∝ 1/λ²）。信号小、噪声大。")
