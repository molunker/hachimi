import tkinter as tk
from tkinter import messagebox, Text, simpledialog
import random
import pygame
import sys
import os
from importlib.resources import files, as_file

class TouhouGachaSimulator:
    def __init__(self):
        # 初始化主窗口
        self.root = tk.Tk()
        self.root.title("touhou抽卡模拟器")
        self.root.geometry("1x1")
        self.root.withdraw()  # 隐藏主窗口
        
        # 初始化计数器和资源
        self.draw_count = 0  # 抽卡次数计数
        self.golden_time = 0  # SSR保底计数变量
        self.special_card_prob = 0.0001  # ？？？卡触发概率（万分之一）
        self.last_word_prob_single = 0.001  # 单抽时LAST WORD卡触发概率（千分之一）
        self.last_word_prob_ten = 0.01  # 十连抽时LAST WORD卡触发概率（百分之一）
        self.spirit = 100  # 灵的数量，初始100
        
        # 卡牌图鉴：记录已收集的卡牌（键为卡牌名，值为数量）
        self.collected_cards = {}
        
        # 定义各品质总概率（R卡90%，SR卡9%）
        self.rarity_total_prob = {
            "R": 0.90,    # R卡总概率90%
            "SR": 0.09,   # SR卡总概率9%
            "SSR": 0.01   # SSR卡总概率1%
        }
        
        # 灵返还规则（SR=2灵，SSR=10灵）
        self.spirit_refund = {
            "R": 1,       # R卡保持1灵
            "SR": 2,      # SR卡2灵
            "SSR": 10,    # SSR卡10灵
            "LAST WORD": 20,  # LAST WORD卡20灵
            "???": 50     # ???卡50灵
        }
        
        # 东方Project角色按作品分类（恢复完整角色列表并为每个角色添加"spirit": 100）
        self.character_categories = {
            # th06：东方红魔乡
            "th06 东方红魔乡": {
                "博丽灵梦": {"names": ["博丽灵梦", "灵梦", "红白", "博丽"], "spirit": 100},
                "雾雨魔理沙": {"names": ["雾雨魔理沙", "魔理沙", "黑白", "雾雨"], "spirit": 100},
                "露米娅": {"names": ["露米娅", "露米"], "spirit": 100},
                "琪露诺": {"names": ["琪露诺", "⑨", "冰之妖精", "琪露"], "spirit": 100},
                "红美铃": {"names": ["红美铃", "美铃", "门番"], "spirit": 100},
                "小恶魔": {"names": ["小恶魔", "恶魔"], "spirit": 100},
                "帕秋莉·诺蕾姬": {"names": ["帕秋莉·诺蕾姬", "帕秋莉", "图书"], "spirit": 100},
                "十六夜咲夜": {"names": ["十六夜咲夜", "咲夜", "女仆长"], "spirit": 100},
                "蕾米莉亚·斯卡雷特": {"names": ["蕾米莉亚·斯卡雷特", "蕾米莉亚", "红魔馆主", "大小姐"], "spirit": 100},
                "芙兰朵露·斯卡雷特": {"names": ["芙兰朵露·斯卡雷特", "芙兰朵露", "芙兰", "二小姐"], "spirit": 100},
                "***":{"names":["冴月麟","阿麟","麟"],"spirit":0}
            },
            # th07：东方妖妖梦
            "th07 东方妖妖梦": {
                "魂魄妖梦": {"names": ["魂魄妖梦", "妖梦", "半灵", "魂魄"], "spirit": 50},
                "西行寺幽幽子": {"names": ["西行寺幽幽子", "幽幽子", "亡灵公主", "西行寺"], "spirit": 100},
                "八云蓝": {"names": ["八云蓝", "蓝", "九尾"], "spirit": 100},
                "八云紫": {"names": ["八云紫", "紫", "间隙妖怪"], "spirit": 100},
                "蕾蒂·霍瓦特洛克": {"names": ["蕾蒂·霍瓦特洛克", "蕾蒂", "冬之妖精"], "spirit": 100},
                "橙": {"names": ["橙", "二尾猫", "猫妖"], "spirit": 100},
                "大妖精": {"names": ["大妖精", "大妖"], "spirit": 100}
            },
            # th08：东方永夜抄
            "th08 东方永夜抄": {
                "蓬莱山辉夜": {"names": ["蓬莱山辉夜", "辉夜", "月公主"], "spirit": 100},
                "八意永琳": {"names": ["八意永琳", "永琳", "月人", "药师"], "spirit": 100},
                "藤原妹红": {"names": ["藤原妹红", "妹红", "不死鸟"], "spirit": 100},
                "上白泽慧音": {"names": ["上白泽慧音", "慧音", "白泽"], "spirit": 100},
                "因幡帝": {"names": ["因幡帝", "帝", "兔子", "因幡"], "spirit": 100},
                "铃仙·优昙华院·因幡": {"names": ["铃仙·优昙华院·因幡", "铃仙", "铃仙优昙华院", "月兔"], "spirit": 100}
            },
            # th09：东方花映冢
            "th09 东方花映冢": {
                "梅蒂欣·梅兰可莉": {"names": ["梅蒂欣·梅兰可莉", "梅蒂欣", "毒人偶"], "spirit": 100},
                "风见幽香": {"names": ["风见幽香", "幽香", "花之妖怪"], "spirit": 100},
                "小野冢小町": {"names": ["小野冢小町", "小町", "死神"], "spirit": 100},
                "四季映姬·亚玛萨那度": {"names": ["四季映姬·亚玛萨那度", "映姬", "阎魔"], "spirit": 100},
                "射命丸文": {"names": ["射命丸文", "文", "鸦天狗"], "spirit": 100},
                "河城荷取": {"names": ["河城荷取", "荷取", "河童"], "spirit": 100}
            },
            # th10：东方风神录
            "th10 东方风神录": {
                "秋静叶": {"names": ["秋静叶", "静叶", "红叶"], "spirit": 100},
                "秋穣子": {"names": ["秋穣子", "穣子", "丰收"], "spirit": 100},
                "键山雏": {"names": ["键山雏", "小雏", "厄运"], "spirit": 100},
                "河童": {"names": ["河童"], "spirit": 100},
                "犬走椛": {"names": ["犬走椛", "椛", "白狼天狗"], "spirit": 100},
                "东风谷早苗": {"names": ["东风谷早苗", "早苗", "风祝"], "spirit": 100},
                "八坂神奈子": {"names": ["八坂神奈子", "神奈子", "山神"], "spirit": 100},
                "洩矢诹访子": {"names": ["洩矢诹访子", "诹访子", "水神"], "spirit": 100}
            },
            # th11：东方地灵殿
            "th11 东方地灵殿": {
                "琪斯美": {"names": ["琪斯美", "钓瓶妖"], "spirit": 100},
                "黑谷山女": {"names": ["黑谷山女", "山女", "幽谷响"], "spirit": 100},
                "水桥帕露西": {"names": ["水桥帕露西", "帕露西", "嫉妒"], "spirit": 100},
                "星熊勇仪": {"names": ["星熊勇仪", "勇仪", "鬼"], "spirit": 100},
                "古明地觉": {"names": ["古明地觉", "觉", "读心"], "spirit": 100},
                "火焰猫燐": {"names": ["火焰猫燐", "燐", "火车"], "spirit": 100},
                "灵乌路空": {"names": ["灵乌路空", "空", "地狱鸦"], "spirit": 100},
                "古明地恋": {"names": ["古明地恋", "恋", "紧闭的恋之瞳"], "spirit": 100}
            },
            # th12：东方星莲船
            "th12 东方星莲船": {
                "娜兹玲": {"names": ["娜兹玲", "小老鼠"], "spirit": 100},
                "多多良小伞": {"names": ["多多良小伞", "小伞", "伞妖"], "spirit": 100},
                "云居一轮": {"names": ["云居一轮", "一轮", "念佛"], "spirit": 100},
                "村纱水蜜": {"names": ["村纱水蜜", "水蜜", "幽灵船"], "spirit": 100},
                "寅丸星": {"names": ["寅丸星", "星", "老虎"], "spirit": 100},
                "圣白莲": {"names": ["圣白莲", "白莲", "魔法使"], "spirit": 100},
                "封兽鵺": {"names": ["封兽鵺", "鵺", "幻兽"], "spirit": 100}
            },
            # th13：东方神灵庙
            "th13 东方神灵庙": {
                "苏我屠自古": {"names": ["苏我屠自古", "屠自古", "雷公"], "spirit": 100},
                "物部布都": {"names": ["物部布都", "布都", "亡灵"], "spirit": 100},
                "丰聪耳神子": {"names": ["丰聪耳神子", "神子", "圣人"], "spirit": 100},
                "二岩猯藏": {"names": ["二岩猯藏", "猯藏", "化狸"], "spirit": 100},
                "霍青娥": {"names": ["霍青娥", "青娥", "仙人"], "spirit": 100},
                "宫古芳香": {"names": ["宫古芳香", "芳香", "僵尸"], "spirit": 100},
                "幽谷响子": {"names": ["幽谷响子", "响子", "山彦"], "spirit": 100}
            },
            # th14：东方辉针城
            "th14 东方辉针城": {
                "鬼人正邪": {"names": ["鬼人正邪", "正邪", "天狗"], "spirit": 100},
                "少名针妙丸": {"names": ["少名针妙丸", "针妙丸", "小人"], "spirit": 100},
                "今泉影狼": {"names": ["今泉影狼", "影狼", "狼人"], "spirit": 100},
                "赤蛮奇": {"names": ["赤蛮奇", "赤蛮奇", "鬼"], "spirit": 100},
                "觉妖怪·秦心": {"names": ["秦心", "面灵气"], "spirit": 100},
                "坂田合欢乃": {"names": ["坂田合欢乃", "合欢乃", "付丧神"], "spirit": 100}
            },
            # th15：东方绀珠传
            "th15 东方绀珠传": {
                "清兰": {"names": ["清兰"], "spirit": 100},
                "铃奈庵": {"names": ["铃奈庵"], "spirit": 100},
                "哆来咪·苏伊特": {"names": ["哆来咪·苏伊特", "哆来咪", "梦之妖怪"], "spirit": 100},
                "稀神探女": {"names": ["稀神探女", "探女", "天女"], "spirit": 100},
                "纯狐": {"names": ["纯狐"], "spirit": 100},
                "赫卡提亚·拉碧斯拉祖利": {"names": ["赫卡提亚·拉碧斯拉祖利", "赫卡提亚"], "spirit": 100}
            },
            # th16：东方天空璋
            "th16 东方天空璋": {
                "矢田寺成美": {"names": ["矢田寺成美", "成美", "青蛙"], "spirit": 100},
                "尔子田里乃": {"names": ["尔子田里乃", "里乃"], "spirit": 100},
                "丁礼田舞": {"names": ["丁礼田舞", "舞"], "spirit": 100},
                "比那名居天子": {"names": ["比那名居天子","天子"], "spirit": 100},
                "高丽野阿吽": {"names": ["高丽野阿吽", "阿吽"], "spirit": 100},
                "摩多罗隐岐奈": {"names": ["摩多罗隐岐奈", "隐岐奈"], "spirit": 100}
            },
            # th17：东方鬼形兽
            "th17 东方鬼形兽": {
                "骊驹早鬼": {"names": ["骊驹早鬼", "早鬼"], "spirit": 100},
                "华扇": {"names": ["华扇", "茨木华扇"], "spirit": 100},
                "橙": {"names": ["橙", "二尾猫又"], "spirit": 100},
                "庭渡久侘歌": {"names": ["庭渡久侘歌", "久侘歌"], "spirit": 100},
                "尔子田里乃": {"names": ["尔子田里乃", "里乃"], "spirit": 100},
                "丁礼田舞": {"names": ["丁礼田舞", "舞"], "spirit": 100},
                "吉吊八千慧": {"names": ["吉吊八千慧", "八千慧"], "spirit": 100}
            },
            # th18：东方虹龙洞
            "th18 东方虹龙洞": {
                "宇佐见堇子": {"names": ["宇佐见堇子", "堇子", "秘封俱乐部"], "spirit": 100},
                "饭纲丸龙": {"names": ["饭纲丸龙", "龙", "天狗"], "spirit": 100},
                "骊驹早鬼": {"names": ["骊驹早鬼", "早鬼"], "spirit": 100},
                "天弓千亦": {"names": ["天弓千亦", "千亦"], "spirit": 100},
                "虹龙": {"names": ["虹龙"], "spirit": 100},
                "哆来咪·苏伊特": {"names": ["哆来咪·苏伊特", "哆来咪"], "spirit": 100},
                "鬼人正邪": {"names": ["鬼人正邪", "正邪"], "spirit": 100}
            }
        }
        
        # 构建扁平查找字典（所有名称映射到灵值）
        self.touhou_characters = {}
        for category, chars in self.character_categories.items():
            for char_name, char_info in chars.items():
                for name in char_info["names"]:
                    self.touhou_characters[name] = char_info["spirit"]
        
        # 初始化卡牌池（包含新添加的卡牌）
        self.init_card_pool()
        
        # 初始化背景音乐
        self.init_background_music()
        
        # 显示抽卡选择窗口
        self.create_choice_window()
        
        # 启动主循环
        self.root.mainloop()
    
    def init_card_pool(self):
        """初始化卡牌池（包含新添加的卡牌）"""
        # 初始化卡牌字典
        self.cards = {}
        
        # 添加新的R卡（从Excel数据提取）
        r_cards = [
            "凍符「パーフェクトフリーズ」", "彩符「極彩颱風」", "水符「ベリーインレイク」",
            "幻在「クロックコープス」", "奇術「幻惑ミスディレクション」", "神罰「幼きデーモンロード」",
            "禁忌「カゴメカゴメ」", "寒符「リンガリングコールド」", "方符「奇門遁甲」",
            "亡郷「亡我郷 -さまよえる魂-」", "鬼符「青鬼赤鬼」", "幻神「飯綱権現降臨」",
            "結界「光と闇の網目」", "魍魎「二重黒死蝶」", "声符「梟の夜鳴声」",
            "始符「エフェメラリティ137」", "夢符「封魔陣」", "魔空「アステロイドベルト」",
            "魔符「ミルキーウェイ」", "幻波「赤眼催眠（マインドブローイング）」", 
            "天丸「壺中の天地」", "薬符「壺中の大銀河」", "騒符「リリカ・ソロライブ」",
            "騒符「メルラン・ハッピーライブ」", "騒符「ルナサ・ソロライブ」", "兎符「開運大紋」",
            "凍符「マイナスＫ」", "豊作「穀物神の約束」", "疵痕「壊されたお守り」",
            "漂溺「光り輝く水底のトラウマ」", "開海「海が割れる日」", "天流「お天水の奇跡」",
            "開宴「二拝二拍一拝」", "花咲爺「シロの灰」", "瘴気「原因不明の熱病」",
            "力業「大江山颪」", "四天王奥義「三歩必殺」", "猫符「怨霊猫乱歩」",
            "核熱「核反応制御不能」", "焔星「十凶星」", "秘法「九字刺し」",
            "「殺意の百合」", "「アポロ捏造説」", "夢符「夢我夢中」",
            "夢符「刈安色の迷夢」", "月見酒「ルナティックセプテンバー」",
            "秘儀「後戸の狂言」","玉符「神々の弾冠」","玉符「烏合の逆呪」","断命剣「冥想斬」",
            "秘儀「穢那の火」","炎符「フェニックスの羽」","不死「火の鳥　-鳳翼天翔-」",
            "熾撃「大鵬墜撃拳」","彩華「虹色太極拳」","天神剣「三魂七魄」","獄神剣「業風神閃斬」",
            "「裏・エクストリームウィンター」","裏・クレイジーフォールウィンド」",
            "「裏・パーフェクトサマーアイス」","「裏・ブリージーチェリーブロッサム」",
            "深層「無意識の遺伝子」","抑制「スーパーエゴ」","本能「イドの解放」","表象「弾幕パラノイア」",
            "表象「夢枕にご先祖総立ち」"

        ]
        for card_name in r_cards:
            self.cards[card_name] = {"rarity": "R", "color": "#1E90FF"}
        
        # 添加新的SR卡（从Excel数据提取）
        sr_cards = [
            "夢符「封魔陣」", "魔符「スターダストレヴァリエ」", "メイド秘技「殺人ドール」",
            "禁忌「フォーオブアカインド」", "咒詛「首吊り蓬莱人形」", "幽曲「リポジトリ・オブ・ヒロカワ -神霊-」",
            "式輝「四面楚歌チャーミング」", "罔両「八雲紫の神隠し」", "隠蟲「永夜蟄居」",
            "夜雀「真夜中のコーラスマスター」", "終符「幻想天皇」", "魔砲「ファイナルマスタースパーク」",
            "神霊「夢想封印　瞬」", "散符「真実の月（インビジブルフルムーン）」", "蘇活「生命遊戯　-ライフゲーム-」",
            "秘術「天文密葬法」", "難題「龍の頸の玉　-五色の弾丸-」", "難題「火鼠の皮衣　-焦れぬ心-」",
            "難題「仏の御石の鉢　-砕けぬ意思-」", "難題「蓬莱の弾の枝　-虹色の弾幕-」", "不死「火の鳥　-鳳翼天翔-」",
            "大奇跡「八坂の神風」", "「風神様の神徳」", "協力技「フェアリーオーバードライブ」",
            "月符「紺色の狂夢」", "「震え凍える星」", "「人を殺める為の純粋な弾幕」","「片翼の白鷺」",
            "滅罪「正直者の死」","後符「絶対秘神の後光」","六道剣「一念無量劫」"
        ]
        for card_name in sr_cards:
            self.cards[card_name] = {"rarity": "SR", "color": "#9932CC"}
        
        # 添加新的SSR卡（从Excel数据提取）
        ssr_cards = [
            "霊符「夢想封印」", "恋符「マスタースパーク」", "幻世「ザ・ワールド」",
            "「紅色の幻想郷」", "QED「４９５年の波紋」", "「反魂蝶 -八分咲-」",
            "結界「生と死の境界」", "禁薬「蓬莱の薬」", "「永夜返し　-世明け-」",
            "「永夜返し　-明けの明星-」", "「インペリシャブルシューティング」", 
            "「人を殺める為の純粋な弾幕」","秘儀「七星の剣」","「サブタレイニアンローズ」"
        ]
        for card_name in ssr_cards:
            self.cards[card_name] = {"rarity": "SSR", "color": "#F2CF06FF"}
        
        # 添加LAST WORD卡（从Excel数据提取），采用白色背景+白色字
        last_word_cards = [
            "「季節外れのバタフライストーム」", "「ブラインドナイトバード」", 
            "「日出づる国の天子」", "「幻朧月睨（ルナティックレッドアイズ）」",
            "「天網蜘網捕蝶の法」", "「蓬莱の樹海」", "「フェニックス再誕」",
            "「エンシェントデューパー」", "「無何有浄化」", "「夢想天生」",
            "「ブレイジングスター」", "「デフレーションワールド」", "「待宵反射衛星斬」",
            "「グランギニョル座の怪人」", "「スカーレットディスティニー」", 
            "「西行寺無余涅槃」", "「深弾幕結界　-夢幻泡影-」",
            "土着神「ケロちゃん風雨に負けず」", "「地獄の人工太陽」", 
            "純符「純粋な弾幕地獄」"
        ]
        for card_name in last_word_cards:
            self.cards[card_name] = {"rarity": "LAST WORD", "color": "#FFFFFF", "bg_color": "#FFFFFF"}
        
        # 添加？？？卡
        self.cards["「胎児の夢」"] = {"rarity": "???", "color": "#000000", "probability": 0.0}
        
        # 按品质分组统计卡牌数量，并计算单卡概率
        rarity_counts = {"R": 0, "SR": 0, "SSR": 0, "LAST WORD": 0}
        for card in self.cards.values():
            if card["rarity"] in rarity_counts:
                rarity_counts[card["rarity"]] += 1
        
        # 为每张卡设置概率（品质总概率÷同品质卡数量）
        for card_name, card_info in self.cards.items():
            if card_info["rarity"] in self.rarity_total_prob:
                card_info["probability"] = self.rarity_total_prob[card_info["rarity"]] / rarity_counts[card_info["rarity"]]
        
        # 常规卡牌列表和概率列表
        self.normal_card_list = [card for card in self.cards.keys() if self.cards[card]["rarity"] not in ["???", "LAST WORD"]]
        self.normal_probabilities = [self.cards[card]["probability"] for card in self.normal_card_list]
        
        # LAST WORD卡列表
        self.last_word_cards = [card for card in self.cards.keys() if self.cards[card]["rarity"] == "LAST WORD"]
        
        # 其他分类卡牌列表
        self.ssr_cards = [card for card in self.cards.keys() if self.cards[card]["rarity"] == "SSR"]
        self.sr_cards = [card for card in self.cards.keys() if self.cards[card]["rarity"] == "SR"]
        self.special_card = "「胎児の夢」"
    
    def init_background_music(self):
        """初始化背景音乐（适配打包后的资源路径）"""
        try:
            pygame.mixer.init()
            # 定义BGM文件名
            bgm_filename = "bgm.mp3"  # 与你的BGM文件名一致
            
            # 获取资源路径：打包后从sys._MEIPASS读取，未打包时用当前目录
            import sys
            if getattr(sys, 'frozen', False):
                # 打包后的环境（EXE运行时）
                base_path = sys._MEIPASS
            else:
                # 开发环境（直接运行Python脚本时）
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            # 拼接完整BGM路径
            bgm_path = os.path.join(base_path, bgm_filename)
            
            # 加载并播放BGM
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)  # -1表示循环播放
            self.bgm_loaded = True
            
        except Exception as e:
            print(f"背景音乐加载失败: {e}")
            self.bgm_loaded = False
    
    def create_choice_window(self):
        """创建抽卡选择窗口（包含卡牌图鉴按钮）"""
        self.choice_window = tk.Toplevel(self.root)
        self.choice_window.title("touhou抽卡模拟器")
        self.choice_window.geometry("400x300")
        self.choice_window.resizable(False, False)
        self.choice_window.lift()
        
        # 密令按钮（左上角）
        self.command_btn = tk.Button(
            self.choice_window,
            text="密令",
            font=("Arial", 12, "bold"),
            width=8,
            height=1,
            command=self.enter_command
        )
        self.command_btn.place(x=20, y=15)
        
        # 抽卡次数显示（右上角）
        self.count_label = tk.Label(
            self.choice_window, 
            text=f"抽卡次数: {self.draw_count}",
            font=("Arial", 12, "bold"),
            padx=5
        )
        self.count_label.place(x=230, y=15)
        
        # 按钮框架（居中放置）
        btn_frame = tk.Frame(self.choice_window)
        btn_frame.pack(pady=60)
        
        # 单抽按钮及消耗显示
        single_frame = tk.Frame(btn_frame)
        single_frame.pack(side=tk.LEFT, padx=20)
        
        self.single_btn = tk.Button(
            single_frame, 
            text="单抽", 
            width=12,
            height=2,
            font=("Arial", 11),
            command=self.single_draw
        )
        self.single_btn.pack()
        
        # 单抽消耗显示（2灵）
        tk.Label(
            single_frame,
            text="消耗: 2灵",
            font=("Arial", 9),
            fg="#666666"
        ).pack(pady=5)
        
        # 十连抽按钮及消耗显示
        ten_frame = tk.Frame(btn_frame)
        ten_frame.pack(side=tk.LEFT, padx=20)
        
        self.ten_btn = tk.Button(
            ten_frame, 
            text="十连抽", 
            width=12,
            height=2,
            font=("Arial", 11),
            command=self.ten_draws
        )
        self.ten_btn.pack()
        
        # 十连抽消耗显示（20灵）
        tk.Label(
            ten_frame,
            text="消耗: 20灵",
            font=("Arial", 9),
            fg="#666666"
        ).pack(pady=5)
        
        # 卡牌图鉴按钮（位于灵显示上方）
        self.album_btn = tk.Button(
            self.choice_window,
            text="卡牌图鉴",
            font=("Arial", 10, "bold"),
            width=10,
            command=self.show_card_album
        )
        self.album_btn.pack(pady=(20, 5))  # 放置在灵显示上方
        
        # 灵的数量显示
        self.spirit_label = tk.Label(
            self.choice_window,
            text=f"灵: {self.spirit}",
            font=("Arial", 11, "bold")
        )
        self.spirit_label.pack(pady=(5, 5))
        
        # 查看概率链接
        self.prob_link = tk.Label(
            self.choice_window,
            text="查看概率",
            font=("Arial", 9),
            fg="blue",
            cursor="hand2",
            underline=1
        )
        self.prob_link.pack(pady=(5, 15))
        self.prob_link.bind("<Button-1>", lambda e: self.show_probability())
    
    def show_card_album(self):
        """显示卡牌图鉴窗口（包含LAST WORD卡与???卡）"""
        album_window = tk.Toplevel(self.choice_window)
        album_window.title("卡牌图鉴")
        album_window.geometry("600x550")
        album_window.resizable(False, False)
        
        # 按稀有度分类显示已收集卡牌
        tk.Label(
            album_window,
            text="已收集卡牌",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # 按稀有度分组（包含LAST WORD和???）
        rarity_groups = {
            "SSR": [],
            "SR": [],
            "R": [],
            "LAST WORD": [],
            "???": []
        }
        for card_name in self.collected_cards.keys():
            rarity = self.cards[card_name]["rarity"]
            rarity_groups[rarity].append(card_name)
        
        # 显示区域（带滚动条）
        frame = tk.Frame(album_window)
        frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        album_text = Text(
            frame, 
            font=("Arial", 12), 
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            bg="#F0F0F0"  # 浅灰色背景，增强LAST WORD卡的神秘感
        )
        album_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=album_text.yview)
        
        # 按稀有度顺序显示（包含LAST WORD和???）
        for rarity in ["SSR", "SR", "R", "LAST WORD", "???"]:
            if rarity_groups[rarity]:
                album_text.insert(tk.END, f"【{rarity}】\n", f"title_{rarity}")
                for card in sorted(rarity_groups[rarity]):
                    count = self.collected_cards[card]
                    album_text.insert(tk.END, f"- {card}（{count}张）\n", f"card_{rarity}")
                album_text.insert(tk.END, "\n")
        
        # 设置文本样式
        for rarity in ["SSR", "SR", "R", "LAST WORD", "???"]:
            if rarity_groups[rarity]:
                # LAST WORD卡使用白色背景+白色文字，增强神秘感
                if rarity == "LAST WORD":
                    album_text.tag_configure(
                        f"title_{rarity}", 
                        font=("Arial", 12, "bold"), 
                        foreground=self.cards[rarity_groups[rarity][0]]["color"],
                        background=self.cards[rarity_groups[rarity][0]]["bg_color"]
                    )
                    album_text.tag_configure(
                        f"card_{rarity}", 
                        foreground=self.cards[rarity_groups[rarity][0]]["color"],
                        background=self.cards[rarity_groups[rarity][0]]["bg_color"]
                    )
                else:
                    album_text.tag_configure(
                        f"title_{rarity}", 
                        font=("Arial", 12, "bold"), 
                        foreground=self.cards[rarity_groups[rarity][0]]["color"]
                    )
                    album_text.tag_configure(
                        f"card_{rarity}", 
                        foreground=self.cards[rarity_groups[rarity][0]]["color"]
                    )
        
        album_text.config(state=tk.DISABLED)
        
        # 关闭按钮
        tk.Button(
            album_window,
            text="关闭",
            width=10,
            command=album_window.destroy
        ).pack(pady=10)
    
    def enter_command(self):
        """密令输入功能"""
        command = simpledialog.askstring("输入密令", "请输入密令:", parent=self.choice_window)
        
        if command and command.strip():
            command = command.strip()
            
            if command in self.touhou_characters:
                self.spirit += self.touhou_characters[command]
                self.update_spirit_display()
                messagebox.showinfo("成功", f"获得{self.touhou_characters[command]}灵！")
            else:
                messagebox.showinfo("无效", "无效的密令")
    
    def update_spirit_display(self):
        """更新灵的数量显示"""
        self.spirit_label.config(text=f"灵: {self.spirit}")
    
    def show_probability(self):
        """显示抽卡概率窗口"""
        prob_window = tk.Toplevel(self.choice_window)
        prob_window.title("抽卡概率")
        prob_window.geometry("450x400")
        prob_window.resizable(False, False)
        
        tk.Label(
            prob_window,
            text="抽卡概率分布",
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        prob_text = Text(prob_window, font=("Arial", 10), wrap=tk.WORD)
        prob_text.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        # 总概率信息
        rarity_counts = {"R": 0, "SR": 0, "SSR": 0, "LAST WORD": 0}
        for card in self.cards.values():
            if card["rarity"] in rarity_counts:
                rarity_counts[card["rarity"]] += 1
        
        prob_text.insert(tk.END, "基础卡牌概率分布：\n")
        for rarity in ["R", "SR", "SSR"]:
            prob_text.insert(tk.END, f"{rarity}卡：{self.rarity_total_prob[rarity]*100:.1f}% "
                                   f"（共{rarity_counts[rarity]}张卡）\n")
        
        # LAST WORD卡概率
        prob_text.insert(tk.END, "\nLAST WORD卡概率：\n")
        prob_text.insert(tk.END, f"单抽：{self.last_word_prob_single*100:.2f}%\n")
        prob_text.insert(tk.END, f"十连抽：{self.last_word_prob_ten*100:.1f}%\n")
        
        # ???卡概率
        prob_text.insert(tk.END, "\n???卡概率：\n")
        prob_text.insert(tk.END, f"所有抽取：{self.special_card_prob*100:.04f}%\n")
        
        # 抽卡消耗
        prob_text.insert(tk.END, "\n抽卡消耗：\n")
        prob_text.insert(tk.END, "单抽：2灵\n")
        prob_text.insert(tk.END, "十连抽：20灵\n")
        
        # 灵返还规则
        prob_text.insert(tk.END, "\n灵返还规则（抽到已有卡时）：\n")
        prob_text.insert(tk.END, f"R卡：{self.spirit_refund['R']}灵\n")
        prob_text.insert(tk.END, f"SR卡：{self.spirit_refund['SR']}灵\n")
        prob_text.insert(tk.END, f"SSR卡：{self.spirit_refund['SSR']}灵\n")
        prob_text.insert(tk.END, f"LAST WORD卡：{self.spirit_refund['LAST WORD']}灵\n")
        prob_text.insert(tk.END, f"???卡：{self.spirit_refund['???']}灵\n")
        
        prob_text.config(state=tk.DISABLED)
        
        tk.Button(
            prob_window,
            text="关闭",
            width=10,
            command=prob_window.destroy
        ).pack(pady=10)
    
    def update_count_display(self):
        """更新抽卡次数显示"""
        self.count_label.config(text=f"抽卡次数: {self.draw_count}")
    
    def check_special_card(self, cards):
        """检查是否触发？？？卡（先于LAST WORD卡判定）"""
        if random.random() <= self.special_card_prob:
            if len(cards) == 1:
                return [self.special_card]
            else:
                replace_idx = random.randint(0, 9)
                cards[replace_idx] = self.special_card
                return cards
        return cards
    
    def check_last_word_card(self, cards, is_single_draw):
        """检查是否触发LAST WORD卡（后于???卡判定，且不替换???卡）"""
        # 确定概率
        prob = self.last_word_prob_single if is_single_draw else self.last_word_prob_ten
        
        if random.random() <= prob:
            # 寻找可以替换的卡牌（不是???卡的卡牌）
            replaceable_indices = [i for i, card in enumerate(cards) if self.cards[card]["rarity"] != "???"]
            
            if replaceable_indices:
                replace_idx = random.choice(replaceable_indices)
                cards[replace_idx] = random.choice(self.last_word_cards)
        
        return cards
    
    def check_ssr_guarantee(self, cards):
        """检查并应用SSR保底机制"""
        has_ssr = any(self.cards[card]["rarity"] == "SSR" for card in cards)
        has_last_word = any(self.cards[card]["rarity"] == "LAST WORD" for card in cards)
        has_special = any(self.cards[card]["rarity"] == "???" for card in cards)
        
        if not has_ssr and not has_last_word and not has_special and self.golden_time >= 70:
            if len(cards) == 1:
                return [random.choice(self.ssr_cards)]
            else:
                replace_idx = random.randint(0, 9)
                cards[replace_idx] = random.choice(self.ssr_cards)
        return cards
    
    def check_ten_draw_guarantee(self, cards):
        """检查并应用十连抽保底"""
        has_sr = any(self.cards[card]["rarity"] == "SR" for card in cards)
        has_ssr = any(self.cards[card]["rarity"] == "SSR" for card in cards)
        has_last_word = any(self.cards[card]["rarity"] == "LAST WORD" for card in cards)
        has_special = any(self.cards[card]["rarity"] == "???" for card in cards)
        
        if not has_sr and not has_ssr and not has_last_word and not has_special:
            replace_idx = random.randint(0, 9)
            cards[replace_idx] = random.choice(self.sr_cards)
        return cards
    
    def draw_normal_card(self):
        """抽取一张常规卡牌"""
        return random.choices(self.normal_card_list, weights=self.normal_probabilities, k=1)[0]
    
    def update_collected_cards(self, cards):
        """更新卡牌图鉴并计算灵返还"""
        refund = 0
        new_cards = []  # 记录新获得的卡牌
        
        for card in cards:
            # 更新图鉴
            if card in self.collected_cards:
                self.collected_cards[card] += 1
                # 计算返还
                rarity = self.cards[card]["rarity"]
                if rarity in self.spirit_refund:
                    refund += self.spirit_refund[rarity]
            else:
                self.collected_cards[card] = 1
                new_cards.append(card)
        
        # 返还灵
        if refund > 0:
            self.spirit += refund
            self.update_spirit_display()
        
        return refund, new_cards
    
    def show_colorful_result(self, cards, is_single_draw, refund):
        """显示抽卡结果（含灵返还信息）"""
        # 关闭可能存在的旧结果窗口
        if hasattr(self, 'result_window') and isinstance(self.result_window, tk.Toplevel) and self.result_window.winfo_exists():
            self.result_window.destroy()
            
        self.result_window = tk.Toplevel(self.choice_window)
        self.result_window.title("touhou抽卡模拟器 - 抽卡结果")
        self.result_window.geometry("550x500")
        self.result_window.resizable(False, False)
        
        # 结果标题
        title_label = tk.Label(
            self.result_window, 
            text="本次抽卡结果", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # 灵返还提示（如有）
        if refund > 0:
            tk.Label(
                self.result_window,
                text=f"获得灵返还：{refund}灵",
                font=("Arial", 10, "bold"),
                fg="#228B22"
            ).pack()
        
        # 文本显示区域（带滚动条）
        frame = tk.Frame(self.result_window)
        frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        result_text = Text(
            frame, 
            font=("Arial", 12), 
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            bg="#F0F0F0"  # 浅灰色背景，增强LAST WORD卡的神秘感
        )
        result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=result_text.yview)
        
        # 写入结果并设置颜色
        for idx, card in enumerate(cards, 1):
            card_info = self.cards[card]
            line = f"{idx}. {card} 【{card_info['rarity']}】\n\n"
            
            result_text.insert(tk.END, line)
            start_idx = f"{idx}.0" if idx == 1 else f"{idx*2-1}.0"
            end_idx = f"{idx*2-1}.end"
            result_text.tag_add(f"color_{idx}", start_idx, end_idx)
            
            # LAST WORD卡使用白色背景+白色文字，增强神秘感
            if card_info["rarity"] == "LAST WORD":
                result_text.tag_configure(
                    f"color_{idx}", 
                    foreground=card_info["color"],
                    background=card_info["bg_color"]
                )
            else:
                result_text.tag_configure(f"color_{idx}", foreground=card_info["color"])
        
        result_text.config(state=tk.DISABLED)
        
        # 按钮框架（再来一次和关闭）
        btn_frame = tk.Frame(self.result_window)
        btn_frame.pack(pady=10)
        
        # 再来一次按钮
        again_btn = tk.Button(
            btn_frame, 
            text="再来一次", 
            width=10, 
            height=1, 
            font=("Arial", 10),
            command=lambda: self.single_draw() if is_single_draw else self.ten_draws()
        )
        again_btn.pack(side=tk.LEFT, padx=10)
        
        # 关闭按钮
        close_btn = tk.Button(
            btn_frame, 
            text="关闭", 
            width=10, 
            height=1, 
            font=("Arial", 10),
            command=self.result_window.destroy
        )
        close_btn.pack(side=tk.LEFT, padx=10)
    
    def single_draw(self):
        """单抽逻辑（消耗2灵）"""
        if self.spirit < 2:
            messagebox.showinfo("灵不足", "单抽需要消耗2灵，请获取更多灵后再试！")
            return
            
        self.spirit -= 2
        self.update_spirit_display()
        
        # 抽取常规卡牌
        cards = [self.draw_normal_card()]
        
        # 先判定???卡
        cards = self.check_special_card(cards)
        
        # 再判定LAST WORD卡（单抽概率1‰）
        cards = self.check_last_word_card(cards, is_single_draw=True)
        
        # 检查SSR保底
        cards = self.check_ssr_guarantee(cards)
        
        # 更新图鉴并计算返还
        refund, new_cards = self.update_collected_cards(cards)
        
        self.draw_count += 1
        self.golden_time += 1
        
        # 显示结果（含返还信息）
        self.show_colorful_result(cards, is_single_draw=True, refund=refund)
        self.update_count_display()
        
        # 重置保底计数
        if any(self.cards[card]["rarity"] in ["SSR", "LAST WORD", "???"] for card in cards):
            self.golden_time = 0
    
    def ten_draws(self):
        """十连抽逻辑（消耗20灵）"""
        if self.spirit < 20:
            messagebox.showinfo("灵不足", "十连抽需要消耗20灵，请获取更多灵后再试！")
            return
            
        self.spirit -= 20
        self.update_spirit_display()
        
        # 抽取常规卡牌
        cards = [self.draw_normal_card() for _ in range(10)]
        
        # 先判定???卡
        cards = self.check_special_card(cards)
        
        # 再判定LAST WORD卡（十连抽概率1%）
        cards = self.check_last_word_card(cards, is_single_draw=False)
        
        # 检查十连保底
        cards = self.check_ten_draw_guarantee(cards)
        
        # 检查SSR保底
        cards = self.check_ssr_guarantee(cards)
        
        # 更新图鉴并计算返还
        refund, new_cards = self.update_collected_cards(cards)
        
        self.draw_count += 10
        self.golden_time += 10
        
        # 显示结果（含返还信息）
        self.show_colorful_result(cards, is_single_draw=False, refund=refund)
        self.update_count_display()
        
        # 重置保底计数
        if any(self.cards[card]["rarity"] in ["SSR", "LAST WORD", "???"] for card in cards):
            self.golden_time = 0

if __name__ == "__main__":
    try:
        app = TouhouGachaSimulator()
    finally:
        if 'pygame' in sys.modules and pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
