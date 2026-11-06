import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import app_common as C
import schematics as S

C.page("8  参数实验室", "自己设计望远镜，挑选观测目标")
C.goal("把前面学到的东西合起来：距离、尘埃、恒星类型和基线怎样决定一颗类地行星能不能被看见。")

st.markdown("行星总是放在它的恒星的**宜居带**里（接收到的光和地球从太阳接收到的一样多，温度约 255 K）。")
c1, c2, c3 = st.columns(3)
with c1:
    star = st.radio("恒星类型", list(C.STAR_TYPES))
    T_star, R_star = C.STAR_TYPES[star]
with c2:
    d = st.slider("恒星距离（pc）", 4.0, 20.0, 10.0, 0.5)
    z = st.select_slider("尘埃量（外黄道光，单位：太阳系的倍数）", options=[0.5, 1, 2, 3, 5, 10, 20, 30, 50], value=1)
with c3:
    b = st.slider("基线 b（米）", 6.0, 80.0, 14.5, 0.5)
    hours = st.slider("观测时间（小时）", 1.0, 50.0, 10.0, 1.0, key="h8")

L_star = R_star**2 * (T_star / 5780) ** 4
a_au = np.sqrt(L_star)
sep_mas = a_au / d * 1000
bd = C.bundle(baseline=b, distance=d, exozodi=float(z), T_star=T_star, R_star=R_star)
scale = np.sqrt(hours / 10.0)           # SNR ∝ √观测时间
snr = bd["bud"]["snr_total"] * scale
need = hours * (5 / snr) ** 2

m1, m2, m3, m4 = st.columns(4)
m1.metric("宜居带离恒星", f"{a_au:.2f} au")
m2.metric("看起来的角距离", f"{sep_mas:.0f} mas")
m3.metric(f"SNR（{hours:g} 小时）", f"{snr:.1f}", delta="可以探测" if snr >= 5 else "还不够", delta_color="normal" if snr >= 5 else "inverse")
m4.metric("达到 SNR = 5 需要", f"{need:.1f} 小时" if need < 1e4 else "> 10000 小时")

st.subheader("哪个基线最好？")
bs = np.array([6, 8, 10, 12, 14.5, 18, 22, 28, 36, 46, 60, 80.0])
snrs = np.array([C.bundle(baseline=x, distance=d, exozodi=float(z), T_star=T_star, R_star=R_star)["bud"]["snr_total"] for x in bs]) * scale
fig, ax = plt.subplots(figsize=(8.4, 3.0))
ax.plot(bs, snrs, "o-", color=S.PLANET)
ax.plot(b, snr, "*", color=S.RED, ms=16, label="当前选择")
ax.axhline(5, color="0.5", ls=":", lw=1); ax.text(bs[0], 5.2, "SNR = 5", fontsize=8.5, color="0.4")
ax.set_xscale("log"); ax.set_xticks(bs); ax.set_xticklabels([f"{x:g}" for x in bs]); ax.xaxis.set_minor_formatter(plt.NullFormatter())
ax.set_xlabel("基线 b（米）"); ax.set_ylabel(f"SNR（{hours:g} 小时）"); ax.legend(loc="upper left")
C.show(fig)
best = bs[np.argmax(snrs)]
st.markdown(f"在这组条件下，SNR 最高的基线约为 **{best:g} m**（上面只计算了图中这几个基线）。"
            f"粗略估计：让行星落在第一条亮纹上的基线 b ≈ λ/(2θ)，在 10 µm 处约为 **{10e-6 / (2 * sep_mas * C.MAS):.0f} m**。")

st.subheader("挑战任务")
st.markdown("""
1. 选择**红矮星**、10 pc。用 14.5 m 的基线能看到它的宜居带行星吗？要多长的基线？
2. 选择**类太阳恒星**、1 倍尘埃。最远能到多少 pc，仍可在 10 小时内达到 SNR = 5？
3. 把尘埃量从 1 调到 30，需要的观测时间变成多少倍？
4. 对于一颗 15 pc 外的类太阳恒星，如果只有 10 小时，你会选择什么基线？
""")
C.think("红矮星的宜居带很近（十几 mas），为什么在合适的基线下反而容易观测？",
        "红矮星本身很暗、看起来很小，漏光少；而宜居带行星的温度和大小和地球一样，发出的红外光一样多。"
        "只要基线足够长（几十米），让行星落在亮纹上，SNR 反而更高。")
C.think("这个实验室假设了一台\"完美\"的仪器。真实的仪器还要考虑什么？",
        "例如四路光的强度能否做到完全相等、光程能否控制到纳米级、望远镜指向是否稳定。这些都会让恒星多漏光，是更深入的课题。")
