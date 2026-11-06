import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import app_common as C
import schematics as S
import core as nl

C.page("5  旋转阵列", "转起来，行星的位置变成一串\"指纹\"")
C.goal("为什么要让望远镜阵列绕着恒星方向旋转；行星的位置怎样被编码进一条随时间变化的信号。")

st.markdown("""
如果阵列不动，行星只停在百叶窗的某一点，我们每个波长只得到一个数，没法确认它是行星。

让整个阵列**绕着对准恒星的方向慢慢转一圈**（比如 10 小时转一圈）。站在阵列上看，行星就沿着一个圆圈走，
依次穿过斩波图的红区、白区、蓝区，信号一会儿正、一会儿负。**这条信号曲线的形状只由行星的位置决定**，就像它的指纹。
""")

c1, c2 = st.columns([1, 3.2])
with c1:
    phi = st.slider("阵列转过的角度（度）", 0, 359, 60, 1)
    lam = st.slider("波长 λ（微米）", 4.0, 18.0, 10.0, 0.5, key="lam5")
    sep = st.slider("行星离恒星的角距离（mas）", 40, 180, 100, 5, key="sep5")
    pa = st.slider("行星的方位角（度）", 0, 359, 40, 5)
L, q = 7.25, 6.0
ext = 250
g = np.linspace(-ext, ext, 241) * C.MAS
A, B = np.meshgrid(g, g)
T3, T4 = nl.transmission(A, B, lam * 1e-6, L, q)
phis = np.linspace(0, 2 * np.pi, 360, endpoint=False)
psky = np.array([sep * np.cos(np.deg2rad(pa)), sep * np.sin(np.deg2rad(pa))])
da, db = nl.sky_to_array(psky[0] * C.MAS, psky[1] * C.MAS, phis)
t3, t4 = nl.transmission(da, db, lam * 1e-6, L, q)
with c2:
    C.show(S.fig_rotation(phi, T3 - T4, ext, psky, (da / C.MAS, db / C.MAS), t3 - t4, np.rad2deg(phis)))
st.caption("左：在天空中，阵列（四个圆点）绕恒星旋转。中：站在阵列上看，斩波图不动，行星沿虚线圆反向转动。右：记录下来的斩波信号，圆点是当前时刻。")

st.header("不同位置，不同指纹")
st.markdown("下面把两颗位置不同的\"候选行星\"的信号画在一起。只要位置差一点，曲线就明显不同——这就是能从信号中找出行星位置的原因。")
c1, c2 = st.columns([1, 3.2])
with c1:
    dpa = st.slider("第二颗的方位角比第一颗多（度）", 0, 90, 10, 1)
    dsep = st.slider("第二颗的角距离比第一颗多（mas）", -30, 30, 0, 1)
psky2 = np.array([(sep + dsep) * np.cos(np.deg2rad(pa + dpa)), (sep + dsep) * np.sin(np.deg2rad(pa + dpa))])
da2, db2 = nl.sky_to_array(psky2[0] * C.MAS, psky2[1] * C.MAS, phis)
s2 = np.subtract(*nl.transmission(da2, db2, lam * 1e-6, L, q))
with c2:
    fig, ax = plt.subplots(figsize=(8.4, 2.8))
    ax.plot(np.rad2deg(phis), t3 - t4, color=S.PLANET, lw=1.6, label=f"位置 1：{sep} mas，{pa}°")
    ax.plot(np.rad2deg(phis), s2, color=S.RED, lw=1.2, ls="--", label=f"位置 2：{sep + dsep} mas，{pa + dpa}°")
    ax.set_xlim(0, 360); ax.set_ylim(-1.05, 1.05); ax.axhline(0, color="0.8", lw=0.6)
    ax.set_xlabel("阵列转过的角度（°）"); ax.set_ylabel("斩波信号"); ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=8.5)
    C.show(fig)
match = np.corrcoef(t3 - t4, s2)[0, 1]
st.markdown(f"两条曲线的相似度（相关系数，1 表示完全相同）：**{match:.2f}**")

st.success("**小结**：旋转把行星的**空间位置**变成了**时间上的信号**。每个波长都有一条这样的曲线，合起来就是行星独一无二的指纹。")
C.think("恒星和对称的尘埃在旋转时，斩波信号会变吗？",
        "不会。它们关于中心对称，转到哪个角度都还是对称的，斩波信号始终为零。只有行星会产生随旋转变化的信号。")
C.think("转了半圈之后，信号和前半圈有什么关系？",
        "正好反号。转半圈后，行星走到了对称点上，而斩波图在对称点上颜色相反。看右图：180° 之后的曲线是前 180° 的\"倒影\"。")
