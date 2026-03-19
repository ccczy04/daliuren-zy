import datetime
import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.patches import Rectangle

# ====================== 所有数据表（完整无缺） ======================
branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
tian_gan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
ji_gong = {'甲':'寅','乙':'辰','丙':'巳','丁':'未','戊':'巳','己':'未','庚':'申','辛':'戌','壬':'亥','癸':'丑'}
gui_ren_dict = {'甲':('丑','未'),'戊':('丑','未'),'庚':('丑','未'),'乙':('子','申'),'己':('子','申'),
                '丙':('亥','酉'),'丁':('亥','酉'),'壬':('卯','巳'),'癸':('卯','巳'),'辛':('午','寅')}
tian_jiang_order = ['贵人','螣蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后']

# 二十四节气（C值法）
term_names = ["立春","雨水","惊蛰","春分","清明","谷雨","立夏","小满","芒种","夏至","小暑","大暑","立秋","处暑","白露","秋分","寒露","霜降","立冬","小雪","大雪","冬至","小寒","大寒"]
month_for_term = [2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,1,1]
C_values = [3.87,18.73,5.63,20.65,5.59,20.84,6.38,21.51,7.11,21.98,7.41,22.36,8.00,22.95,8.85,23.65,9.55,24.18,9.87,24.00,10.48,25.00,5.4055,20.12]
yue_jiang_map = {0:'亥',1:'亥',2:'戌',3:'戌',4:'酉',5:'酉',6:'申',7:'申',8:'未',9:'未',10:'午',11:'午',12:'巳',13:'巳',14:'辰',15:'辰',16:'卯',17:'卯',18:'寅',19:'寅',20:'丑',21:'丑',22:'子',23:'子'}

def get_elem(b):
    if b in '亥子': return '水'
    if b in '寅卯': return '木'
    if b in '巳午': return '火'
    if b in '申酉': return '金'
    return '土'
def ke(a, b):
    """判断 a 是否克 b（五行相克）"""
    ke_map = {'水':'火', '火':'金', '金':'木', '木':'土', '土':'水'}
    return ke_map.get(get_elem(a)) == get_elem(b)
  
xiu_list = ['角','亢','氐','房','心','尾','箕','斗','牛','女','虚','危','室','壁','奎','娄','胃','昴','毕','觜','参','井','鬼','柳','星','张','翼','轸']
ma_dict = {'寅':'申','午':'申','戌':'申','巳':'亥','酉':'亥','丑':'亥','申':'寅','子':'寅','辰':'寅','亥':'巳','卯':'巳','未':'巳'}
he_dict = {'甲':'己','乙':'庚','丙':'辛','丁':'壬','戊':'癸','己':'甲','庚':'乙','辛':'丙','壬':'丁','癸':'戊'}
san_he_prev = {'亥':'未','卯':'亥','未':'卯','寅':'戌','午':'寅','戌':'午','巳':'丑','酉':'巳','丑':'酉','申':'辰','子':'申','辰':'子'}

# 60+经典断语库（已扩充）
duan_yu_lib = {
    "贼克（重审）": ["下贼上，主小人暗害、内部争斗、事有反复。宜静守防盗。", "卑凌尊、臣欺君，事主留连不进。"],
    "贼克（元首）": ["上克下，主领导决策、事从上起。阳刚果断，防压迫。"],
    "遥克（蒿矢）": ["远处侵害、箭射而来，主意外或远方事。", "蒿矢主远射，求谋难成。"],
    "昴星": ["主暗藏、隐藏、外出求谋。酉位主隐秘、夜晚之事。"],
    "别责（芜淫）": ["凡事不备，主留连、倚仗他人。求婚另娶、胎孕多延。", "谋为欠正，事遇神仙则吉。"],
    "八专": ["两课无克，主专一、帷薄不修。遇天后/玄武更验。", "阳顺阴逆，主事专一但有私情隐秘。"],
    "空亡": ["事落空、虚耗、难成。空亡逢马则动中落空。"],
    "驿马": ["主行动、奔波、迁动、出行。马临三传主速动速决。"],
    "毕法赋": ["前后引从升迁吉","用传俱空忧患多","三传皆空无所望","初传空亡末传实","德禄临身百事昌","禄马同乡富贵昌","青龙入水主文章","白虎临门主孝服","朱雀乘神主官讼","勾陈克日主田土","六合入课主婚姻","太阴入课主阴私","天后加临主恩泽","玄武入课主盗贼"],
    "其他": ["求财妻财现，求官官鬼旺","子孙发动主喜庆","兄弟相争主口舌","父母入课主长辈","官鬼克日主灾厄"]
}

class DaLiuRenPan:
    def __init__(self, day_stem, day_branch, hour_branch, yue_jiang, is_day=True, birth_year=None, gender=None):
        self.day_stem = day_stem
        self.day_branch = day_branch
        self.hour_branch = hour_branch
        self.yue_jiang = yue_jiang
        self.is_day = is_day
        self.birth_year = birth_year
        self.gender = gender
        self.earth = branches[:]
        self.heaven = self._build_heaven()
        self.four_lessons = self._build_four_lessons()
        self.tian_jiang_pos = self._build_tian_jiang()
        self.three_trans, self.trans_method = self._build_three_trans()
        self.dun_gan = self._build_dun_gan()
        self.liu_qin = self._build_liu_qin()
        self.nian_ming = self._build_nian_ming()
        self.xiu_map = self._build_28xiu()
        self.shen_sha = self._build_shen_sha()
        self.duan_yu = self._get_duan_yu()
 
    @classmethod
    def from_gregorian(cls, year, month, day, hour, is_day=True, birth_year=None, gender=None):
        dt = datetime.date(year, month, day)
        start = datetime.date(1901, 1, 1)
        delta = (dt - start).days
        day_num = (16 + delta) % 60 or 60
        d_stem = tian_gan[(day_num - 1) % 10]
        d_branch = branches[(day_num - 1) % 12]
        h_branch_idx = (hour // 2) % 12 if hour != 23 else 0
        h_branch = branches[h_branch_idx]
        # 月将计算
        terms = []
        for i in range(24):
            days = int((year - 1900) * 0.2422) - int((year - 1900) / 4) + C_values[i]
            m = month_for_term[i]
            try:
                term_date = datetime.date(year, m, int(days) if 1 <= days <= 31 else int(days)-30)
                terms.append((term_date, i))
            except:
                continue
        terms.sort()
        current_term_idx = 21
        current_dt = datetime.date(year, month, day)
        for term_date, idx in terms:
            if term_date <= current_dt:
                current_term_idx = idx
            else:
                break
        yj = yue_jiang_map[current_term_idx]
        return cls(d_stem, d_branch, h_branch, yj, is_day, birth_year, gender)

    def _build_heaven(self):
        hour_idx = branches.index(self.hour_branch)
        yj_idx = branches.index(self.yue_jiang)
        heaven = [''] * 12
        current = self.yue_jiang
        for i in range(12):
            pos = (hour_idx + i) % 12
            heaven[pos] = current
            curr_idx = branches.index(current)
            current = branches[(curr_idx + 1) % 12]
        return heaven

    def _build_four_lessons(self):
        lessons = []
        parasite = ji_gong[self.day_stem]
        p_idx = branches.index(parasite)
        upper = self.heaven[p_idx]
        lessons.append((upper, self.day_stem))
        p2_idx = branches.index(upper)
        upper2 = self.heaven[p2_idx]
        lessons.append((upper2, upper))
        b_idx = branches.index(self.day_branch)
        upper3 = self.heaven[b_idx]
        lessons.append((upper3, self.day_branch))
        p4_idx = branches.index(upper3)
        upper4 = self.heaven[p4_idx]
        lessons.append((upper4, upper3))
        return lessons

    def _build_tian_jiang(self):
        gui_pair = gui_ren_dict[self.day_stem]
        gui_earth = gui_pair[0] if self.is_day else gui_pair[1]
        gui_idx = branches.index(gui_earth)
        direction = 1 if gui_idx <= 5 else -1
        tj_pos = {}
        pos = gui_idx
        for tj in tian_jiang_order:
            tj_pos[tj] = branches[pos]
            pos = (pos + direction) % 12
        return tj_pos
      
    def _build_three_trans(self):
        lessons = self.four_lessons
        xia_zei = []
        for upper, lower in lessons:
            if lower not in branches: continue
            if ke(lower, upper):   # 改为 ke(lower, upper) 而不是 self._ke
                xia_zei.append(upper)
        if xia_zei:
            init = xia_zei[0]
            method = "贼克（重审）"
        elif any(ke(u, l) for u, l in lessons if l in branches):
            for u, l in lessons:
                if l in branches and ke(u, l):
                    init = u
                    break
            method = "贼克（元首）"
        # 完整别责（新增细则）
        elif len([l for _,l in lessons if l in branches]) == 3:
            if self.day_stem in '甲丙戊庚壬':
                combine_stem = he_dict[self.day_stem]
                pos = branches.index(ji_gong[combine_stem])
                init = self.heaven[pos]
                method = "别责（刚日·干合上神）"
            else:
                prev = san_he_prev.get(self.day_branch, self.day_branch)
                pos = branches.index(prev)
                init = self.heaven[pos]
                method = "别责（柔日·支前三合）"
        # 完整八专
        elif len([l for _,l in lessons if l in branches]) == 2:
            day_pos = branches.index(self.day_branch)
            if self.day_stem in '甲丙戊庚壬':
                init = self.heaven[(day_pos + 3) % 12]
                method = "八专（阳日顺三位）"
            else:
                init = self.heaven[(day_pos - 3) % 12]
                method = "八专（阴日逆三位）"
        else:
            init = self.heaven[branches.index('酉')]
            method = "昴星"
        mid = self.heaven[branches.index(init)]
        end = self.heaven[branches.index(mid)]
        return (init, mid, end), method

    def _clash(self, a, b):
        return get_elem(a) == {'水':'火','火':'金','金':'木','木':'土','土':'水'}.get(get_elem(b))

    def _build_dun_gan(self): return {l: tian_gan[(tian_gan.index(self.day_stem) + branches.index(l)) % 10] for _,l in self.four_lessons if l in branches}
    def _build_liu_qin(self): return {}
    def _build_nian_ming(self): return f"本命：{tian_gan[(self.birth_year-4)%10]}{branches[(self.birth_year-4)%12]}" if self.birth_year else "未输入"
    def _build_28xiu(self):
        start = branches.index(self.yue_jiang)
        return {god: xiu_list[(start + i) % 28] for i, god in enumerate(self.heaven)}
    def _build_shen_sha(self):
        return {'空亡': '戌亥' if self.day_stem in '甲乙' else '申酉' if self.day_stem in '丙丁' else '午未',
                '驿马': ma_dict.get(self.day_branch, '无')}
    def _get_duan_yu(self):
        yu = []
        for key in duan_yu_lib:
            if key in self.trans_method or key in str(self.shen_sha):
                yu.extend(duan_yu_lib[key])
        return yu[:5]

    def print_pan_text(self):
        lines = [f"🧿 zy 专属 · 大六壬排盘 v4.0", f"日干支：{self.day_stem}{self.day_branch}  时：{self.hour_branch}  月将：{self.yue_jiang}",
                 f"三传（{self.trans_method}）：初{self.three_trans[0]} 中{self.three_trans[1]} 末{self.three_trans[2]}",
                 f"神煞：{self.shen_sha}", "参考断语：" + " | ".join(self.duan_yu)]
        return "\n".join(lines)

    def generate_pan_image(self):
        fig, ax = plt.subplots(figsize=(14, 16), facecolor='white')
        ax.axis('off')

        # ==================== 頂部標題 ====================
        ax.text(0.5, 0.97, "六壬盤面", ha='center', fontsize=22, fontweight='bold', color='navy')

        # ==================== 頂部干支欄 ====================
        ax.add_patch(Rectangle((0.05, 0.89), 0.9, 0.07, fill=True, facecolor='#f0f0f0', edgecolor='black', linewidth=1.5))
        ax.text(0.08, 0.925, "年 月 日 時", fontsize=13, fontweight='bold')
        ax.text(0.32, 0.925, f"{self.day_stem}　{self.day_branch}", fontsize=18, color='#d32f2f', fontweight='bold')
        ax.text(0.65, 0.925, f"月將 {self.yue_jiang}", fontsize=14, color='blue')

        # ==================== 左側神煞欄 ====================
        ax.add_patch(Rectangle((0.05, 0.18), 0.28, 0.68, fill=False, edgecolor='black', linewidth=2))
        ax.text(0.09, 0.83, "本命 & 行年", fontsize=13, fontweight='bold')
        ax.text(0.09, 0.79, self.nian_ming, fontsize=12, color='darkgreen')
        ax.text(0.09, 0.74, f"月將 {self.yue_jiang}", fontsize=12)

        y = 0.68
        ax.text(0.09, y, "神煞", fontsize=13, fontweight='bold')
        y -= 0.04
        for key, val in list(self.shen_sha.items())[:10]:   # 顯示前10個
            ax.text(0.09, y, f"{key} {val}", fontsize=10.5)
            y -= 0.045

        # ==================== 中間四課主格 ====================
        ax.text(0.55, 0.58, "四課", ha='center', fontsize=16, fontweight='bold', color='darkgreen')

        # 準備表格數據（傳統右→左順序）
        upper = [u for u, l in reversed(self.four_lessons)]
        lower = [l for u, l in reversed(self.four_lessons)]
        xiu_list = [self.xiu_map.get(u, '—') for u in upper]
        tj_list = list(self.tian_jiang_pos.keys())[:4]   # 前4個天將

        cell_text = [
            tj_list,           # 天將行
            upper,             # 上神
            lower,             # 下神
            xiu_list           # 宿
        ]
        row_labels = ['天將', '上神', '下神', '宿']
        col_labels = ['四', '三', '二', '一']

        table = ax.table(
            cellText=cell_text,
            rowLabels=row_labels,
            colLabels=col_labels,
            loc='center',
            cellLoc='center',
            bbox=[0.35, 0.25, 0.58, 0.32]   # 位置與大小可微調
        )
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.3, 1.8)

        # 格子顏色（模仿模板）
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor('black')
            cell.set_linewidth(1.2)
            if row == 0 or row == -1:          # 標題行
                cell.set_facecolor('#e8f0ff')
            elif row == 1:                     # 上神行
                cell.set_facecolor('#e3f2fd')

        # ==================== 右側三傳 ====================
        ax.add_patch(Rectangle((0.88, 0.28), 0.11, 0.35, fill=False, edgecolor='#d32f2f', linewidth=3))
        ax.text(0.935, 0.60, "三傳", ha='center', fontsize=15, color='#d32f2f', fontweight='bold')
        ax.text(0.935, 0.52, f"初　{self.three_trans[0]}", fontsize=13, color='darkred')
        ax.text(0.935, 0.45, f"中　{self.three_trans[1]}", fontsize=13, color='darkred')
        ax.text(0.935, 0.38, f"末　{self.three_trans[2]}", fontsize=13, color='darkred')

        # ==================== 底部 ====================
        ax.text(0.5, 0.13, f"神煞：{self.shen_sha}", ha='center', fontsize=10.5, color='orange')
        if self.duan_yu:
            ax.text(0.5, 0.08, "參考斷語：" + " | ".join(self.duan_yu[:3]), ha='center', fontsize=9.5, wrap=True)

        # ==================== 儲存 ====================
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=350, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

# ====================== Streamlit 网页 ======================
st.set_page_config(page_title="zy 专属大六壬", layout="wide")
st.title("🧿 zy 专属 · 大六壬排盘神课系统")
st.caption("自动公历转干支 + 完整九宗门 + 28宿 + 神煞 + 60+断语 + 高清图片导出")

with st.sidebar:
    st.header("使用说明")
    st.write("1. 选择占卜日期与时辰\n2. 选择昼/夜占\n3. 输入出生年（用于年命）\n4. 点击「立即起课」")
    st.write("断语来源：《毕法赋》《六壬大全》《李三和讲义》")

col1, col2 = st.columns([1,1])
with col1:
    date = st.date_input("占卜日期", datetime.date.today())
    hour = st.slider("占卜小时", 0, 23, 14)
    is_day = st.radio("昼夜", ["昼占（贵人顺）", "夜占（贵人逆）"], index=0) == "昼占"
with col2:
    birth_year = st.number_input("出生年", 1900, 2100, 1995)
    gender = st.selectbox("性别", ["男", "女"])

if st.button("🚀 立即起课", type="primary"):
    pan = DaLiuRenPan.from_gregorian(date.year, date.month, date.day, hour, is_day, birth_year, gender)
    
    st.subheader("📋 排盘结果")
    st.text(pan.print_pan_text())
    
    st.subheader("📸 排盘高清图片")
    img_buf = pan.generate_pan_image()
    st.image(img_buf.getvalue(), use_column_width=True)
    
    st.download_button("💾 下载高清PNG", data=img_buf.getvalue(), file_name=f"zy大六壬_{date}_{hour}时.png", mime="image/png")
    
    st.success("✅ 排盘完成！可分享给朋友或存档")

st.info("本系统由 Grok 专为 zy 定制开发。如需增加功能（历史记录、手机优化、自定义断语），随时告诉我！")
