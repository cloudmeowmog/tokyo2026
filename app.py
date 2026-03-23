import streamlit as st
import streamlit.components.v1 as components

# --- 1. 設定頁面配置 ---
st.set_page_config(
    page_title="東京親子寶可夢之旅",
    page_icon="🗼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS 樣式修正 (全螢幕手機體驗與隱藏官方圖示) ---
st.markdown("""
    <style>
        /* 隱藏所有 Streamlit 預設的 UI 元素 (包含右下角圖示、選單與標頭) */
        header {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        .stDeployButton {display: none !important;}
        [data-testid="stToolbar"] {visibility: hidden !important;}
        [data-testid="stDecoration"] {display: none !important;}
        
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        iframe {
            height: 100vh !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. React 應用程式 (HTML) ---
html_code = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>東京親子寶可夢之旅</title>
    
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
    
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 0; }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        .safe-bottom { padding-bottom: max(env(safe-area-inset-bottom), 20px); }
        
        #loading { position: fixed; top: 0; left: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; background: #f3f4f6; z-index: 9999; transition: opacity 0.5s ease; flex-direction: column;}
        .spinner { border: 4px solid rgba(0, 0, 0, 0.1); width: 36px; height: 36px; border-radius: 50%; border-left-color: #4f46e5; animation: spin 1s linear infinite; margin-bottom: 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="h-screen flex flex-col overflow-hidden text-gray-800">

    <div id="loading">
        <div class="spinner"></div>
        <div style="color: #666; font-size: 14px;">正在載入旅程...</div>
    </div>

    <div id="root" class="flex-1 flex flex-col h-full"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef } = React;

        const URL_TRIP = "https://raw.githubusercontent.com/cloudmeowmog/tokyo2026/main/trip.jpg";
        const URL_NOTE = "https://raw.githubusercontent.com/cloudmeowmog/tokyo2026/main/note.jpg";
        const URL_MAP = "https://raw.githubusercontent.com/cloudmeowmog/tokyo2026/main/map.jpg";

        const HOTEL_ADDRESS = "Stayme THE HOTEL Ueno, Higashiueno, Taito City, Tokyo";

        // SVG Icons
        const icons = {
            list: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>,
            map: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path></svg>,
            attraction: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>,
            booking: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
        };

        const surroundingGuides = {
            ueno: {
                name: '上野 / 秋葉原',
                spots: [
                    { name: '御茶之水 聖橋', desc: '鈴芽之旅經典場景，三線電車交會。', tag: '聖地巡禮', icon: '📸', mapQuery: '聖橋' },
                    { name: 'Yamashiroya 玩具店（ヤマシロヤ，Yamashiroya）', desc: 'JR 上野站對面。6 層樓玩具專賣店，寶可夢周邊齊全。', tag: '玩具百貨', icon: '🧸', mapQuery: 'ヤマシロヤ 上野' },
                    { name: '上野動物園', desc: '門票超便宜，適合早起帶小孩看熊貓散步放電。', tag: '動物園', icon: '🐼', mapQuery: '上野動物園' },
                    { name: 'Yodobashi 8F 美食街（ヨドバシ，Yodobashi）', desc: '美食街有和幸豬排、Meat Rush，吃飽直攻6F寶可夢機台。', tag: '定食漢堡排', icon: '🍛', mapQuery: 'ヨドバシAkiba' },
                    { name: '九州 じゃんがら（九州じゃんがら，Kyushu Jangara）', desc: '秋葉原本店。濃郁豚骨湯配超軟爛角肉。', tag: '豚骨拉麵', icon: '🍜', mapQuery: '九州じゃんがら 秋葉原本店' },
                    { name: '壽司郎 上野店（スシロー，Sushiro）', desc: '自動化點餐，小孩愛吃扭蛋好玩，優質備案。', tag: '迴轉壽司', icon: '🍣', mapQuery: 'スシロー 上野店' },
                    { name: '敘敘苑 上野不忍口店（叙々苑，Jojoen）', desc: '頂級燒肉代名詞！環境舒適，適合犒賞全家。', tag: '高級燒肉', icon: '🥩', mapQuery: '叙々苑 上野不忍口店' },
                    { name: '鴨 to 蔥（らーめん 鴨 to 葱，Kamo to Negi）', desc: "上野超人氣排隊名店，清甜鴨蔥湯頭極獨特。", tag: '排隊拉麵', icon: '🍜', mapQuery: 'らーめん 鴨to葱 上野' },
                    { name: "客美多咖啡 上野廣小路店（コメダ珈琲店，Komeda's Coffee）", desc: '點飲料送早餐吐司，必吃「冰與火」甜點，歇腳好去處。', tag: '連鎖咖啡', icon: '☕', mapQuery: 'コメダ珈琲店 上野広小路店' }
                ]
            },
            toyosu: {
                name: '豐洲 / 市場',
                spots: [
                    { name: '千客萬來（豊洲 千客万来，Senkyaku Banrai）', desc: '市場旁最新溫泉美食街，復古江戶風情超好拍。', tag: '觀光美食', icon: '🏮', mapQuery: '豊洲 千客万来' },
                    { name: '茂助糰子/玉子燒（茂助だんご，Mosuke）', desc: '市場內百年老店，除了甜點也有日式煎蛋捲小孩絕對愛吃。', tag: '市場玉子燒', icon: '🍳', mapQuery: '茂助だんご 豊洲市場' },
                    { name: '海鮮丼 大江戶（海鮮丼 大江戸，Oedo）', desc: '豐洲市場水產棟，超澎湃的新鮮海鮮丼。', tag: '豐盛海鮮', icon: '🍱', mapQuery: '海鮮丼 大江戸 豊洲市場' },
                    { name: '炸物 八千代（とんかつ 八千代，Tonkatsu Yachiyo）', desc: '不吃生食的好選擇！炸大蝦與炸豬排定食。', tag: '熟食定食', icon: '🍤', mapQuery: 'とんかつ 八千代 豊洲市場' },
                    { name: '壽司大（寿司大，Sushidai）', desc: '豐洲市場超人氣排隊壽司，想吃需起個大早。', tag: '排隊壽司', icon: '🍣', mapQuery: '寿司大 豊洲市場' },
                    { name: 'teamLab Planets', desc: '需赤腳的水中光影美術館，小孩玩水超開心。', tag: '光影藝術', icon: '✨', mapQuery: 'teamLab Planets TOKYO' },
                    { name: '豐洲 LaLaport（ららぽーと豊洲，LaLaport Toyosu）', desc: '超大商場！3樓有玩具店、扭蛋機，非常適合放電。', tag: '購物遊樂', icon: '🛍️', mapQuery: 'ららぽーと豊洲' },
                    { name: '100支湯匙（100本のスプーン，100 Spoons）', desc: 'LaLaport 內親子餐廳。小孩可點大人一模一樣的半份餐。', tag: '親子餐廳', icon: '🍽️', mapQuery: '100本のスプーン ららぽーと豊洲' },
                    { name: '燒肉 Toraji（焼肉トラジ，Yakiniku Toraji）', desc: 'LaLaport 內吃厚切牛舌與和牛，舒適無煙味。', tag: '和牛燒肉', icon: '🥩', mapQuery: '焼肉トラジ ららぽーと豊洲店' },
                    { name: '築地食堂 源ちゃん（築地食堂 源ちゃん，Genchan）', desc: 'LaLaport 內。提供美味生魚片丼與炸雞海鮮定食。', tag: '海鮮定食', icon: '🍱', mapQuery: '築地食堂 源ちゃん ららぽーと豊洲店' },
                    { name: '麵屋 黑琥（麺や 黒琥，Kuroko）', desc: 'LaLaport 內。豚骨與醬油拉麵，方便快速。', tag: '日式拉麵', icon: '🍜', mapQuery: '麺や 黒琥 豊洲' },
                    { name: '玉丁本店（玉丁本店，Tamacho Honten）', desc: 'LaLaport 內。濃郁的味噌燉烏龍麵，麵條Q彈小孩好入口。', tag: '烏龍麵', icon: '🍲', mapQuery: '玉丁本店 ららぽーと豊洲店' },
                    { name: "客美多咖啡 豐洲店（コメダ珈琲店，Komeda's Coffee）", desc: '豐洲站旁，逛完市場或LaLaport可以來這裡喝杯咖啡休息。', tag: '連鎖咖啡', icon: '☕', mapQuery: 'コメダ珈琲店 豊洲店' }
                ]
            },
            odaiba: {
                name: '台場周邊',
                spots: [
                    { name: '獨角獸鋼彈', desc: 'DiverCity 前實物大鋼彈，變身秀父子必看！', tag: '地標', icon: '🤖', mapQuery: '実物大ユニコーンガンダム立像' },
                    { name: '鋼彈基地 (DiverCity)', desc: '滿滿的鋼彈模型與限定商品，買瘋的聖地。', tag: '模型', icon: '🛍️', mapQuery: 'ガンダムベース東京' },
                    { name: 'LEGOLAND 探索中心', desc: '室內樂高樂園，超多積木池與遊樂設施。', tag: '樂高樂園', icon: '🧱', mapQuery: 'レゴランド・ディスカバリー・センター東京' },
                    { name: '田中商店（博多長浜らーめん 田中商店，Tanaka Shoten）', desc: 'DiverCity 2F美食街。超濃郁豚骨拉麵，吃完馬上看鋼彈。', tag: '豚骨拉麵', icon: '🍜', mapQuery: '田中商店 ダイバーシティ東京プラザ店' },
                    { name: '金子半之助（日本橋 天丼 金子半之助，Kaneko Hannosuke）', desc: 'DiverCity 2F美食街。超人氣排隊天丼，炸蝦與炸半熟蛋必吃。', tag: '超值天丼', icon: '🍤', mapQuery: '日本橋 天丼 金子半之助 ダイバーシティ東京プラザ店' },
                    { name: '傳說的斯塔丼屋（伝説のすた丼屋，Densetsu no Sutadon-ya）', desc: 'DiverCity 2F美食街。超人氣蒜香豬肉丼飯，份量十足豪邁過癮。', tag: '日式丼飯', icon: '🍚', mapQuery: '伝説のすた丼屋 ダイバーシティ東京プラザ店' },
                    { name: '蘋果樹蛋包飯（ポムの樹，Pomme-no-ki）', desc: 'Aqua City 5F。知名蛋包飯，口味極多小孩超愛。', tag: '蛋包飯', icon: '🍳', mapQuery: 'ポムの樹 アクアシティお台場店' },
                    { name: '燒肉 平城苑（東京焼肉 平城苑，Heijoen）', desc: 'Aqua City 1F。看著東京灣美景吃黑毛和牛燒肉。', tag: '景觀燒肉', icon: '🥩', mapQuery: '焼肉 平城苑 アクアシティお台場店' }
                ]
            },
            asakusa: {
                name: '淺草周邊',
                spots: [
                    { name: '淺草寺 雷門', desc: '巨大的紅燈籠是東京象徵，體驗傳統文化。', tag: '傳統文化', icon: '🏮', mapQuery: '雷門' },
                    { name: '仲見世通', desc: '買人形燒、吃仙貝，感受濃濃的江戶風情。', tag: '商店街', icon: '🛍️', mapQuery: '浅草 仲見世商店街' },
                    { name: '藏壽司 淺草ROX店（くら寿司，Kura Sushi）', desc: '全球最大旗艦店！有祭典裝潢、射擊遊戲與巨大扭蛋。', tag: '和食遊樂', icon: '🍣', mapQuery: 'くら寿司 浅草ROX店' },
                    { name: '一蘭拉麵 淺草店（一蘭，Ichiran）', desc: '獨立座位的經典豚骨，小朋友很喜歡這種包廂感。', tag: '經典拉麵', icon: '🍜', mapQuery: '一蘭 浅草店' },
                    { name: '平城苑 淺草雷門店（東京焼肉 平城苑，Heijoen）', desc: '雷門旁的高級燒肉店，提供A5和牛。', tag: '和牛燒肉', icon: '🥩', mapQuery: '東京焼肉 平城苑 浅草雷門店' },
                    { name: '淺草今半（浅草今半，Asakusa Imahan）', desc: '日本最知名的百年壽喜燒老店，和牛入口即化。', tag: '頂級壽喜燒', icon: '🍲', mapQuery: '浅草今半 国際通り本店' },
                    { name: '淺草炸肉餅（浅草メンチ，Asakusa Menchi）', desc: '排隊名物，現炸的酥脆肉餅充滿肉汁。', tag: '街邊點心', icon: '🍘', mapQuery: '浅草メンチ' },
                    { name: "客美多咖啡 田原町站前店（コメダ珈琲店，Komeda's Coffee）", desc: '離淺草ROX與飯店都很近，吃點心休息的絕佳備案。', tag: '連鎖咖啡', icon: '☕', mapQuery: 'コメダ珈琲店 田原町駅前店' }
                ]
            },
            skytree: {
                name: '晴空塔周邊',
                spots: [
                    { name: '東京晴空塔', desc: '世界最高電波塔，上層有展望台。', tag: '地標', icon: '🗼', mapQuery: '東京スカイツリー' },
                    { name: '寶可夢中心 (4F)', desc: '烈空坐為主題的超大店面，旁邊有寶可夢機台。', tag: '寶可夢', icon: '🐾', mapQuery: 'ポケモンセンタースカイツリータウン' },
                    { name: '星之卡比咖啡廳（KIRBY CAFÉ / カービィカフェ，Kirby Cafe）', desc: '4F。超可愛星之卡比主題餐點與專賣店。', tag: '主題餐廳', icon: '⭐', mapQuery: 'KIRBY CAFE TOKYO' },
                    { name: '六厘舍（六厘舎，Rokurinsha）', desc: '6F。超人氣「沾麵」名店，粗麵配濃郁魚介豚骨湯。', tag: '排隊沾麵', icon: '🍜', mapQuery: '六厘舎 TOKYO スカイツリータウン・ソラマチ店' },
                    { name: '燒肉 Pure（焼肉 ぴゅあ，Pure）', desc: '11F。農協開設，主打安心安全日本黑毛和牛。', tag: '農協燒肉', icon: '🥩', mapQuery: '焼肉 ぴゅあ 東京スカイツリータウン・ソラマチ店' },
                    { name: '迴轉壽司 根室花丸（回転寿司 根室花丸，Nemuro Hanamaru）', desc: '6F。北海道超人氣名店，食材極新鮮需提早抽號。', tag: '排隊壽司', icon: '🍣', mapQuery: '東京スカイツリータウン 回転寿司' },
                    { name: '利久牛舌（牛たん炭焼 利久，Rikyu）', desc: '6F。仙台厚切牛舌，有提供兒童咖哩飯套餐。', tag: '炭烤牛舌', icon: '🍱', mapQuery: '牛たん炭焼 利久 東京ソラマチ店' },
                    { name: 'Tabe-Terrace 美食街（タベテラス，Tabe-Terrace）', desc: '3F。美食街選擇豐富且免排隊。', tag: '美食街', icon: '🍽️', mapQuery: '東京ソラマチ タベテラス' }
                ]
            },
            karuizawa: {
                name: '輕井澤周邊',
                spots: [
                    { name: '雲場池', desc: '騎腳踏車抵達，適合帶小朋友觀察鴨群生態。', tag: '自然生態', icon: '🦆', mapQuery: '長野県 雲場池' },
                    { name: '王子 Outlet', desc: '除了血拚，內有樂高專賣店與扭蛋機，草地可奔跑。', tag: '購物遊樂', icon: '🛍️', mapQuery: '軽井沢プリンスショッピングプラザ' },
                    { name: '明治亭（ソースかつ丼 明治亭，Meijitei）', desc: 'Outlet 內。長野名物「醬汁豬排丼」，甜鹹醬汁下飯。', tag: '醬汁豬排', icon: '🍱', mapQuery: 'ソースかつ丼 明治亭 軽井沢店' },
                    { name: '濃熟雞白湯 錦（濃熟鶏白湯 錦，Nishiki）', desc: 'Outlet 內。湯頭溫和甘甜的雞白湯拉麵。', tag: '雞白湯拉麵', icon: '🍜', mapQuery: '濃熟鶏白湯 錦 軽井沢・プリンスショッピングプラザ店' },
                    { name: '熟成和牛燒肉 Aging Beef（熟成和牛焼肉エイジング・ビーフ，Aging Beef）', desc: 'Outlet 內。主打熟成和牛燒肉，肉質柔軟。', tag: '熟成燒肉', icon: '🥩', mapQuery: '熟成和牛焼肉エイジング・ビーフ 軽井沢' },
                    { name: '史努比村（SNOOPY Village / スヌーピービレッジ，Snoopy Village）', desc: '舊輕井澤。超可愛的史努比茶屋與伴手禮。', tag: '卡通茶屋', icon: '🐶', mapQuery: 'SNOOPY Village 軽井沢' },
                    { name: '清安庵（御曹司 きよやす庵，Kiyoyasuan）', desc: 'Outlet 內。超多汁的黑毛和牛漢堡排與牛排。', tag: '漢堡排', icon: '🍽️', mapQuery: '御曹司 きよやす庵 軽井沢プリンスショッピングプラザ店' }
                ]
            },
            tsukiji: {
                name: '築地市場',
                spots: [
                    { name: '築地場外市場', desc: '東京的廚房！早上充滿各式現做海鮮小吃與乾貨。', tag: '傳統市場', icon: '🐟', mapQuery: '築地場外市場' },
                    { name: '狐狸屋（きつねや，Kitsuneya）', desc: '超濃郁的牛雜/牛丼排隊名店，適合喜歡重口味的爸爸。', tag: '排隊名店', icon: '🥘', mapQuery: 'きつねや 築地' },
                    { name: '築地 山長（築地山長，Yamacho）', desc: '街邊現煎玉子燒，100日圓一串，小孩最愛。', tag: '玉子燒', icon: '🍳', mapQuery: '築地山長' },
                    { name: '築地 可樂餅（築地コロッケ，Tsukiji Croquette）', desc: '現炸的明太子文字燒可樂餅，極推。', tag: '街邊點心', icon: '🍘', mapQuery: '築地コロッケ' },
                    { name: '黑銀 鮪魚店（築地黒銀 まぐろや，Kurogin）', desc: '頂級黑鮪魚生魚片與握壽司，立食體驗。', tag: '黑鮪魚', icon: '🍣', mapQuery: '築地黒銀 まぐろや' },
                    { name: '壽司三味 本店（すしざんまい，Sushizanmai）', desc: '知名連鎖壽司本店，價格透明、座位寬敞好排。', tag: '平價壽司', icon: '🍣', mapQuery: 'すしざんまい 本店' }
                ]
            },
            shibuya: {
                name: '渋谷周邊',
                spots: [
                    { name: 'SHIBUYA SKY', desc: '目前最熱門的露天展望台，360度無死角美景。', tag: '高空夜景', icon: '🏙️', mapQuery: 'SHIBUYA SKY' },
                    { name: 'Pokémon Center', desc: 'PARCO 6F。最潮的寶可夢中心，門口有1:1沉睡超夢。', tag: '寶可夢', icon: '🐾', mapQuery: 'ポケモンセンターシブヤ' },
                    { name: '魚米（魚べい，Uobei）', desc: '全由「高速新幹線軌道」直送座位，平價極具娛樂性。', tag: '新幹線壽司', icon: '🍣', mapQuery: '魚べい 渋谷道玄坂店' },
                    { name: '鶴橋風月（鶴橋風月，Tsuruhashi Fugetsu）', desc: 'Scramble Square 12F。大阪燒桌邊現煎，吃飽去展望台最順。', tag: '大阪燒', icon: '🍳', mapQuery: '鶴橋風月 渋谷スクランブルスクエア店' },
                    { name: '阿夫利（AFURI，Afuri）', desc: '原宿店。從澀谷散步或搭一站到原宿，超人氣柚子鹽拉麵。', tag: '柚子拉麵', icon: '🍜', mapQuery: 'AFURI 原宿' },
                    { name: '燒肉 牛角 澀谷店（牛角，Gyukaku）', desc: '平價連鎖燒肉，菜單豐富無壓力，適合親子。', tag: '平價燒肉', icon: '🥩', mapQuery: '牛角 渋谷センター街店' },
                    { name: '名代 豬排（名代 かつくら，Katsukura）', desc: 'Scramble Square 14F。京都知名炸豬排，飯湯可續。', tag: '炸豬排', icon: '🍱', mapQuery: '名代 かつくら 渋谷スクランブルスクエア店' }
                ]
            },
            shinjuku: {
                name: '新宿周邊',
                spots: [
                    { name: '新宿 3D 貓', desc: '東口廣場 4K 彎曲螢幕，巨大的三花貓會探頭打招呼。', tag: '科技看板', icon: '🐈', mapQuery: 'クロス新宿ビジョン' },
                    { name: '歌舞伎町 哥吉拉', desc: '東寶大樓上方的巨大哥吉拉，整點會咆哮發光。', tag: '地標', icon: '🦖', mapQuery: '新宿東宝ビル' },
                    { name: '天丼 Tenya（天丼てんや，Tenya）', desc: '新宿東口店。高CP值的平價日式炸蝦天婦羅丼飯，大人小孩都愛。', tag: '日式丼飯', icon: '🍤', mapQuery: '天丼てんや 新宿東口店' },
                    { name: '燒肉亭 六歌仙（焼肉亭 六歌仙，Rokkasen）', desc: '新宿超人氣頂級和牛吃到飽，座位寬敞適合家庭。', tag: '和牛吃到飽', icon: '🥩', mapQuery: '焼肉亭 六歌仙 新宿' },
                    { name: '一蘭拉麵 新宿中央東口店（一蘭，Ichiran）', desc: '小朋友最愛的獨立小包廂座位。', tag: '經典拉麵', icon: '🍜', mapQuery: '一蘭 新宿中央東口店' },
                    { name: '名代 宇奈とと（名代 宇奈とと，Unatoto）', desc: 'CP值超高的炭烤鰻魚飯，醬汁配飯非常香。', tag: '平價鰻魚飯', icon: '🍱', mapQuery: '名代 宇奈とと 新宿' },
                    { name: '高島屋 Times Square（新宿タカシマヤ，Takashimaya）', desc: '12-14F 空間寬敞舒適，豐富和食美食街免排隊。', tag: '百貨美食街', icon: '🍽️', mapQuery: '新宿タカシマヤ タイムズスクエア' },
                    { name: "客美多咖啡 新宿靖國通店（コメダ珈琲店，Komeda's Coffee）", desc: '位於歌舞伎町旁，逛街逛累了可以隨時進來坐坐。', tag: '連鎖咖啡', icon: '☕', mapQuery: 'コメダ珈琲店 新宿靖国通り店' }
                ]
            }
        };

        const attractionInfos = [
            // --- Day 1 ---
            { id: "hijiri", name: "御茶之水 聖橋", icon: "🌉", tag: "聖地巡禮", desc: "電影《鈴芽之旅》經典場景。站在橋上可以同時看到紅、黃、橘三色電車交錯而過，是鐵道迷與影迷必拍聖地。", tips: "下午前往順光，拍攝效果最好。" },
            { id: "akiba", name: "秋葉原 Electric Town", icon: "⚡", tag: "動漫/電器", desc: "日本次文化中心。滿街的動漫周邊、模型店、女僕咖啡廳與大型電器行。Yodobashi Akiba 是必逛地標。", tips: "旁邊的 Yodobashi 是吃喝玩樂一站式滿足的好地方！" },
            { id: "akiba_food", name: "上野/秋葉原 飲食 (6選)", icon: "🍛", tag: "美食", desc: "Day 1 晚餐與備案推薦：", tips: "推薦在 Yodobashi 吃飽，直攻 6F 打寶可夢機台！",
                foodSpots: [
                    { icon: "🍱", name: "Yodobashi 8F 美食街（ヨドバシ，Yodobashi）", desc: "和幸豬排/Meat Rush漢堡排，吃飽直接下樓玩", mapQuery: "ヨドバシAkiba" },
                    { icon: "🍜", name: "九州 じゃんがら（九州じゃんがら，Kyushu Jangara）", desc: "秋葉原人氣豚骨拉麵，角肉軟爛", mapQuery: "九州じゃんがら 秋葉原本店" },
                    { icon: "🍣", name: "壽司郎 上野店（スシロー，Sushiro）", desc: "扭蛋迴轉壽司，小孩最愛", mapQuery: "スシロー 上野店" },
                    { icon: "🥩", name: "敘敘苑 上野不忍口店（叙々苑，Jojoen）", desc: "高級和牛燒肉，環境舒適", mapQuery: "叙々苑 上野不忍口店" },
                    { icon: "🍜", name: "鴨 to 蔥（らーめん 鴨 to 葱，Kamo to Negi）", desc: "上野排隊人氣清湯拉麵", mapQuery: "らーめん 鴨to葱 上野" },
                    { icon: "☕", name: "客美多咖啡 上野廣小路店（コメダ珈琲店，Komeda's Coffee）", desc: "點飲料送早餐吐司，歇腳與下午茶好去處", mapQuery: "コメダ珈琲店 上野広小路店" }
                ]
            },
            
            // --- Day 2 ---
            { id: "toyosu_market_morning", name: "豐洲市場 早上/點心", icon: "🐟", tag: "市場", desc: "Day 2 早上行程：逛逛千客萬來與市場水產棟，吃點海鮮與玉子燒墊胃。", tips: "因主力午餐將前往台場享用，建議在此與小孩分享小吃即可。",
                foodSpots: [
                    { icon: "🏮", name: "千客萬來（豊洲 千客万来，Senkyaku Banrai）", desc: "市場旁最新溫泉美食街，復古江戶風情", mapQuery: "豊洲 千客万来" },
                    { icon: "🍳", name: "茂助糰子/玉子燒（茂助だんご，Mosuke）", desc: "市場內百年老店，甜甜的日式煎蛋捲", mapQuery: "茂助だんご 豊洲市場" },
                    { icon: "🍱", name: "海鮮丼 大江戶（海鮮丼 大江戸，Oedo）", desc: "超澎湃的新鮮海鮮丼", mapQuery: "海鮮丼 大江戸 豊洲市場" },
                    { icon: "🍤", name: "炸物 八千代（とんかつ 八千代，Tonkatsu Yachiyo）", desc: "炸大蝦與炸豬排定食", mapQuery: "とんかつ 八千代 豊洲市場" },
                    { icon: "🍣", name: "壽司大（寿司大，Sushidai）", desc: "超人氣排隊壽司", mapQuery: "寿司大 豊洲市場" }
                ]
            },
            { id: "odaiba", name: "台場 獨角獸鋼彈", icon: "🤖", tag: "鋼彈", desc: "位於 DiverCity 廣場前。白天有 4 場變身秀(獨角獸模式->毀滅模式)，晚上有燈光秀。", tips: "變身時間：11:00, 13:00, 15:00, 17:00。" },
            { id: "odaiba_food", name: "台場 午餐 (5選)", icon: "🍔", tag: "美食", desc: "Day 2 午餐推薦 (方便銜接鋼彈表演)：", tips: "在 DiverCity 用餐，吃完剛好出去廣場看變身秀！",
                foodSpots: [
                    { icon: "🍜", name: "田中商店（博多長浜らーめん 田中商店，Tanaka Shoten）", desc: "DiverCity 2F 超濃郁豚骨拉麵", mapQuery: "田中商店 ダイバーシティ東京プラザ店" },
                    { icon: "🍤", name: "金子半之助（日本橋 天丼 金子半之助，Kaneko Hannosuke）", desc: "DiverCity 2F 超人氣排隊天丼", mapQuery: "日本橋 天丼 金子半之助 ダイバーシティ東京プラザ店" },
                    { icon: "🍚", name: "傳說的斯塔丼屋（伝説のすた丼屋，Densetsu no Sutadon-ya）", desc: "DiverCity 2F 超人氣大份量蒜香豬肉丼飯", mapQuery: "伝説のすた丼屋 ダイバーシティ東京プラザ店" },
                    { icon: "🍳", name: "蘋果樹蛋包飯（ポムの樹，Pomme-no-ki）", desc: "Aqua City 5F 知名蛋包飯", mapQuery: "ポムの樹 アクアシティお台場店" },
                    { icon: "🥩", name: "燒肉 平城苑（東京焼肉 平城苑，Heijoen）", desc: "Aqua City 1F 看海景吃黑毛和牛燒肉", mapQuery: "焼肉 平城苑 アクアシティお台場店" }
                ]
            },
            { id: "teamlab", name: "teamLab Planets", icon: "✨", tag: "沉浸式藝術", desc: "需赤腳進入的水中美術館。光影與水面的結合非常夢幻，適合大人小孩互動。", tips: "這天會在台場周邊頻繁轉車，建議直接購買「百合海鷗號一日券」！" },
            { id: "toyosu_food", name: "豐洲 晚餐 (6選)", icon: "🍽️", tag: "美食", desc: "Day 2 晚餐推薦 (teamLab後，LaLaport內)：", tips: "LaLaport 3樓有扭蛋機與玩具專賣店喔！",
                foodSpots: [
                    { icon: "🍽️", name: "100支湯匙（100本のスプーン，100 Spoons）", desc: "LaLaport 內，高質感親子餐廳，可點半份", mapQuery: "100本のスプーン ららぽーと豊洲" },
                    { icon: "🥩", name: "燒肉 Toraji（焼肉トラジ，Yakiniku Toraji）", desc: "LaLaport 內，爽吃厚切牛舌與和牛", mapQuery: "焼肉トラジ ららぽーと豊洲店" },
                    { icon: "🍱", name: "築地食堂 源ちゃん（築地食堂 源ちゃん，Genchan）", desc: "LaLaport 內，熟食海鮮定食", mapQuery: "築地食堂 源ちゃん ららぽーと豊洲店" },
                    { icon: "🍜", name: "麵屋 黑琥（麺や 黒琥，Kuroko）", desc: "LaLaport 內，豚骨醬油日式拉麵", mapQuery: "麺や 黒琥 豊洲" },
                    { icon: "🍲", name: "玉丁本店（玉丁本店，Tamacho Honten）", desc: "LaLaport 內，濃郁的味噌燉烏龍麵", mapQuery: "玉丁本店 ららぽーと豊洲店" },
                    { icon: "☕", name: "客美多咖啡 豐洲店（コメダ珈琲店，Komeda's Coffee）", desc: "豐洲站旁，買飲料送早餐，休息吃甜點", mapQuery: "コメダ珈琲店 豊洲店" }
                ]
            },
            
            // --- Day 3 ---
            { id: "sensoji", name: "淺草寺 & 雷門", icon: "🏮", tag: "傳統文化", desc: "東京最古老的寺廟。巨大的紅燈籠「雷門」是東京象徵。仲見世通有許多人形燒、仙貝等傳統小吃。", tips: "遊客非常多，建議早上9點前抵達拍照。" },
            { id: "skytree", name: "東京晴空塔", icon: "🗼", tag: "地標/寶可夢", desc: "世界最高電波塔。樓下 Solamachi 商場有寶可夢中心(烈空坐鎮店)與 Kirby Cafe。" },
            { id: "skytree_food", name: "晴空塔 午餐 (5選)", icon: "🍱", tag: "美食", desc: "Day 3 午餐推薦：", tips: "假日時晴空塔餐廳人潮多，建議提早抽號或選美食街。",
                foodSpots: [
                    { icon: "🍜", name: "六厘舍（六厘舎，Rokurinsha）", desc: "晴空塔 6F 超人氣排隊沾麵", mapQuery: "六厘舎 TOKYO スカイツリータウン・ソラマチ店" },
                    { icon: "🍣", name: "迴轉壽司 根室花丸（回転寿司 根室花丸，Nemuro Hanamaru）", desc: "晴空塔 6F 北海道新鮮壽司 (需提早抽號)", mapQuery: "東京スカイツリータウン 回転寿司" },
                    { icon: "🍱", name: "利久牛舌（牛たん炭焼 利久，Rikyu）", desc: "晴空塔 6F 炭烤厚切牛舌 (有兒童咖哩)", mapQuery: "牛たん炭焼 利久 東京ソラマチ店" },
                    { icon: "🥩", name: "燒肉 Pure（焼肉 ぴゅあ，Pure）", desc: "晴空塔 11F 農協直送黑毛和牛", mapQuery: "焼肉 ぴゅあ 東京スカイツリータウン・ソラマチ店" },
                    { icon: "🍽️", name: "Tabe-Terrace 美食街（タベテラス，Tabe-Terrace）", desc: "晴空塔 3F 美食街免排隊挑選", mapQuery: "東京ソラマチ タベテラス" }
                ]
            },
            { id: "asakusa_food", name: "淺草 晚餐 (6選)", icon: "🍣", tag: "美食", desc: "Day 3 晚餐推薦：", tips: "藏壽司 ROX店有專屬祭典遊戲，小孩最愛！",
                foodSpots: [
                    { icon: "🍣", name: "藏壽司 淺草ROX店（くら寿司，Kura Sushi）", desc: "全球旗艦店，有祭典遊戲區與巨大扭蛋", mapQuery: "くら寿司 浅草ROX店" },
                    { icon: "🍜", name: "一蘭拉麵 淺草店（一蘭，Ichiran）", desc: "獨立包廂位的經典豚骨拉麵", mapQuery: "一蘭 浅草店" },
                    { icon: "🥩", name: "平城苑 淺草雷門店（東京焼肉 平城苑，Heijoen）", desc: "雷門旁的高級和牛燒肉", mapQuery: "東京焼肉 平城苑 浅草雷門店" },
                    { icon: "🍲", name: "淺草今半（浅草今半，Asakusa Imahan）", desc: "百年壽喜燒老店，黑毛和牛入口即化", mapQuery: "浅草今半 国際通り本店" },
                    { icon: "🍘", name: "淺草炸肉餅（浅草メンチ，Asakusa Menchi）", desc: "街邊現炸酥脆小吃", mapQuery: "浅草メンチ" },
                    { icon: "☕", name: "客美多咖啡 田原町站前店（コメダ珈琲店，Komeda's Coffee）", desc: "離飯店和ROX近，逛累了吃甜點的絕佳備案", mapQuery: "コメダ珈琲店 田原町駅前店" }
                ]
            },
            
            // --- Day 4 ---
            { id: "karuizawa", name: "輕井澤", icon: "🚲", tag: "度假勝地", desc: "避暑勝地，充滿歐風建築與森林。車站旁就是超大 Outlet，舊輕井澤銀座通適合騎車漫遊。", tips: "將逛 Outlet 改到下午，買完戰利品就能直接搭新幹線，免提重物騎車！" },
            { id: "karuizawa_food", name: "輕井澤 飲食 (5選)", icon: "🍱", tag: "美食", desc: "Day 4 午餐推薦：", tips: "Outlet 餐廳容易客滿，建議 11:30 前入座。",
                foodSpots: [
                    { icon: "🍱", name: "明治亭（ソースかつ丼 明治亭，Meijitei）", desc: "Outlet 內，長野名物醬汁豬排丼", mapQuery: "ソースかつ丼 明治亭 軽井沢店" },
                    { icon: "🍜", name: "濃熟雞白湯 錦（濃熟鶏白湯 錦，Nishiki）", desc: "Outlet 美食街內，湯頭甘甜拉麵", mapQuery: "濃熟鶏白湯 錦 軽井沢・プリンスショッピングプラザ店" },
                    { icon: "🥩", name: "熟成和牛燒肉 Aging Beef（熟成和牛焼肉エイジング・ビーフ，Aging Beef）", desc: "Outlet 內，熟成和牛燒肉", mapQuery: "熟成和牛焼肉エイジング・ビーフ 軽井沢" },
                    { icon: "🍽️", name: "清安庵（御曹司 きよやす庵，Kiyoyasuan）", desc: "Outlet 內。超多汁的黑毛和牛漢堡排與牛排。", mapQuery: "御曹司 きよやす庵 軽井沢プリンスショッピングプラザ店" },
                    { icon: "🐶", name: "史努比村（SNOOPY Village / スヌーピービレッジ，Snoopy Village）", desc: "舊輕井澤 史努比主題茶屋", mapQuery: "SNOOPY Village 軽井沢" }
                ]
            },
            
            // --- Day 5 ---
            { id: "tsukiji", name: "築地場外市場", icon: "🐟", tag: "傳統市場", desc: "被稱為東京的廚房。早上充滿各式現做海鮮小吃、玉子燒與乾貨，是體驗日本飲食文化的好地方。", tips: "築地市場多為街邊小吃或立食，請留意不要邊走邊吃（需在店家指定區域吃完）。" },
            { id: "tsukiji_food", name: "築地市場 飲食 (5選)", icon: "🥘", tag: "美食", desc: "Day 5 早餐推薦：", tips: "狐狸屋極受歡迎，建議一早就去排隊！",
                foodSpots: [
                    { icon: "🥘", name: "狐狸屋（きつねや，Kitsuneya）", desc: "超濃郁的排隊名店，適合喜歡重口味的爸爸", mapQuery: "きつねや 築地" },
                    { icon: "🍳", name: "築地 山長（築地山長，Yamacho）", desc: "街邊現煎玉子燒，100日圓一串，小孩最愛", mapQuery: "築地山長" },
                    { icon: "🍘", name: "築地 可樂餅（築地コロッケ，Tsukiji Croquette）", desc: "現炸的明太子文字燒可樂餅，極推", mapQuery: "築地コロッケ" },
                    { icon: "🍣", name: "黑銀 鮪魚店（築地黒銀 まぐろや，Kurogin）", desc: "頂級黑鮪魚生魚片與握壽司，立食體驗", mapQuery: "築地黒銀 まぐろや" },
                    { icon: "🍣", name: "壽司三味 本店（すしざんまい，Sushizanmai）", desc: "知名連鎖壽司本店，價格透明、座位寬敞", mapQuery: "すしざんまい 本店" }
                ]
            },
            { id: "shibuya", name: "SHIBUYA SKY", icon: "🏙️", tag: "高空夜景", desc: "目前最熱門的露天展望台，360度無死角美景。角落的玻璃扶手是網美必拍點。", tips: "日落時段最美，但需提早一個月搶票。" },
            { id: "shinjuku", name: "新宿 3D 貓", icon: "🐈", tag: "科技看板", desc: "新宿東口廣場對面大樓的 4K 彎曲螢幕。巨大的三花貓會探頭打招呼，非常逼真可愛。", tips: "每 15 分鐘會有一次特殊演出。" },
            { id: "shibuya_food", name: "澀谷 午餐 (5選)", icon: "🍣", tag: "美食", desc: "Day 5 午餐推薦：", tips: "吃飽直接搭電梯上 SHIBUYA SKY 最順路！",
                foodSpots: [
                    { icon: "🍣", name: "魚米（魚べい，Uobei）", desc: "新幹線軌道送餐壽司，平價好玩", mapQuery: "魚べい 渋谷道玄坂店" },
                    { icon: "🍳", name: "鶴橋風月（鶴橋風月，Tsuruhashi Fugetsu）", desc: "Scramble Square 12F 大阪燒", mapQuery: "鶴橋風月 渋谷スクランブルスクエア店" },
                    { icon: "🍜", name: "阿夫利（AFURI，Afuri）", desc: "原宿店。從澀谷搭一站或散步至原宿，超人氣柚子鹽拉麵", mapQuery: "AFURI 原宿" },
                    { icon: "🥩", name: "燒肉 牛角 澀谷店（牛角，Gyukaku）", desc: "平價連鎖燒肉，菜單豐富", mapQuery: "牛角 渋谷センター街店" },
                    { icon: "🍱", name: "名代 豬排（名代 かつくら，Katsukura）", desc: "Scramble Square 14F 京都炸豬排", mapQuery: "名代 かつくら 渋谷スクランブルスクエア店" }
                ]
            },
            { id: "shinjuku_food", name: "新宿 晚餐 (6選)", icon: "🍤", tag: "美食", desc: "Day 5 晚餐推薦：", tips: "哥吉拉頭像每整點會咆哮，在歌舞伎町吃晚餐剛好可以看！",
                foodSpots: [
                    { icon: "🍤", name: "天丼 Tenya（天丼てんや，Tenya）", desc: "高CP值的平價日式炸蝦天婦羅丼飯", mapQuery: "天丼てんや 新宿東口店" },
                    { icon: "🥩", name: "燒肉亭 六歌仙（焼肉亭 六歌仙，Rokkasen）", desc: "頂級和牛吃到飽", mapQuery: "焼肉亭 六歌仙 新宿" },
                    { icon: "🍜", name: "一蘭拉麵 新宿中央東口店（一蘭，Ichiran）", desc: "經典獨立包廂拉麵", mapQuery: "一蘭 新宿中央東口店" },
                    { icon: "🍱", name: "名代 宇奈とと（名代 宇奈とと，Unatoto）", desc: "平價高CP值炭烤鰻魚飯", mapQuery: "名代 宇奈とと 新宿" },
                    { icon: "🍽️", name: "高島屋 Times Square（新宿タカシマヤ，Takashimaya）", desc: "12-14F 美食街，免排隊挑選", mapQuery: "新宿タカシマヤ タイムズスクエア" },
                    { icon: "☕", name: "客美多咖啡 新宿靖國通店（コメダ珈琲店，Komeda's Coffee）", desc: "歌舞伎町旁，逛街逛累了隨時進來坐坐", mapQuery: "コメダ珈琲店 新宿靖国通り店" }
                ]
            },
            
            // --- Day 6 (機場推薦) ---
            { id: "narita_food", name: "成田 T1 餐廳 (5選)", icon: "🍜", tag: "美食", desc: "回程搭機前的最後一餐（多位於中央大樓 4F）：", tips: "若時間充裕，強烈推薦吃碗「とみ田」沾麵！",
                foodSpots: [
                    { icon: "🍜", name: "中華蕎麥 富田（中華蕎麦 とみ田，Tomita）", desc: "千葉松戶超人氣沾麵名店，機場就能吃到", mapQuery: "中華蕎麦 とみ田 成田空港" },
                    { icon: "🍚", name: "八代目儀兵衛（八代目儀兵衛，Hachidaime Gihey）", desc: "京都百年米店，極致美味的白飯與和食定食", mapQuery: "八代目儀兵衛 成田空港" },
                    { icon: "🍲", name: "高湯茶泡飯 燕（だし茶漬け えん，En）", desc: "高湯茶泡飯，清爽暖胃，適合搭機前享用", mapQuery: "だし茶漬け えん 成田空港" },
                    { icon: "🥢", name: "杵屋麥丸（杵屋麦丸，Kineya Mugimaru）", desc: "中央大樓 5F。平價美味的自助式讚岐烏龍麵", mapQuery: "杵屋麦丸 成田空港" },
                    { icon: "🍣", name: "壽司 京辰（寿司 京辰，Kyotatsu）", desc: "入關後(免稅區)的高品質江戶前壽司", mapQuery: "寿司 京辰 成田空港" }
                ]
            },
            { id: "narita_souvenir", name: "成田 T1 伴手禮 (5選)", icon: "🎁", tag: "購物", desc: "最後衝刺！入關前或 FaSoLa 免稅店必買清單：", tips: "液體或果凍狀伴手禮務必放托運行李，過安檢入關後再買免稅品最方便直接手提上機！",
                foodSpots: [
                    { icon: "🍌", name: "東京ばな奈", desc: "經典不敗，常有寶可夢或聯名限定包裝", mapQuery: "FaSoLa 成田空港" },
                    { icon: "🍪", name: "PRESS BUTTER SAND", desc: "酥脆外皮與焦糖奶油夾心，質感極佳", mapQuery: "FaSoLa 成田空港" },
                    { icon: "🧀", name: "NY PERFECT CHEESE", desc: "超人氣排起司奶油脆餅，送禮超有面子", mapQuery: "FaSoLa 成田空港" },
                    { icon: "🍫", name: "ROYCE 生巧克力", desc: "北海道名產，機場免稅店永遠的熱銷冠軍", mapQuery: "FaSoLa 成田空港" },
                    { icon: "✈️", name: "TRAVELER'S FACTORY", desc: "中央大樓 4F(入關前)。機場限定版文具與筆記本", mapQuery: "TRAVELERS FACTORY AIRPORT" }
                ]
            }
        ];

        const itinerary = [
             { day: 1, date: "4/17 (五)", title: "抵達與鈴芽的起點", events: [ 
                 { time: "13:25", title: "抵達成田機場", desc: "T1 (長榮)", icon: "✈️", location: "成田国際空港 第1ターミナル", hideRoute: true, tips: "抵達 T1 後，先前往 B1 辦理兒童版西瓜卡與領取 Skyliner 車票。",
                   stationGuide: {
                     name: "兒童版交通卡購買", desc: "機場實體卡申辦攻略",
                     tips: ["限 6-12 歲兒童購買 (半價)", "無法綁定手機，需持實體卡", "必須出示小孩本人護照"],
                     routes: ["抵達成田 T1 B1 鐵道樓層後，尋找「JR 東日本旅行服務中心」或藍色的「京成電鐵」櫃檯", "向櫃檯人員表示要購買兒童版 IC 卡 (Child Suica 或 Child PASMO)", "出示小孩的護照供人員核對年齡", "初次購買通常需付 2000 日圓 (含 500 日圓押金，可用額度 1500 日圓)", "進出車站閘門時，嗶卡會發出「小鳥叫聲(嗶嗶兩聲)」，即代表成功使用兒童票價"]
                   }
                 }, 
                 { time: "14:00", title: "往 Skyliner 乘車處", desc: "成田機場 T1 B1", icon: "🚶", location: "成田空港駅（第1旅客ターミナル）", transport: { route: "入境大廳 → B1 京成電鐵", line: "步行", time: "10分" },
                   stationGuide: {
                     name: "成田機場 T1 車站", desc: "Skyliner 乘車指引",
                     tips: ["長榮位於南翼 (South Wing)", "Skyliner 全車對號座"],
                     routes: ["入境大廳位於 1F，領完行李後尋找「鐵道」指標", "搭乘手扶梯下樓至 B1", "尋找藍色櫃台「KEISEI (京成電鐵)」購票", "通過橘色剪票口，前往 4 或 5 號月台", "上車後行李放置於車廂前後的行李架"]
                   }
                 }, 
                 { time: "14:30", title: "搭乘 Skyliner", desc: "往京成上野站", icon: "🚅", location: "京成上野駅", transport: { route: "成田機場 → 京成上野", line: "京成 Skyliner", time: "41分" }, hideMap: true }, 
                 { time: "16:00", title: "Check-in", desc: "Stayme Ueno", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "上野 → 飯店", line: "步行", time: "10分" }, hideMap: true,
                   stationGuide: {
                     name: "京成上野站", desc: "前往飯店路線",
                     tips: ["抵達時在地下月台", "往稻荷町方向步行約 10 分鐘"],
                     routes: ["下車後搭手扶梯往上，尋找「正面口」出口", "出改札口後直走，不要往地鐵連絡通道走", "出站到地面後，開啟 Google Map 導航前往飯店", "沿著淺草通直走即可抵達 (步行約 10 分)"]
                   }
                 }, 
                 { time: "17:15", title: "前往秋葉原", desc: "從飯店出發", icon: "🚇", location: "秋葉原駅", transport: { route: "飯店 → 上野站 → 秋葉原", line: "步行轉 JR", time: "20分" }, hideMap: true, 
                   stationGuide: {
                     name: "前往秋葉原", desc: "搭乘 JR 直達",
                     tips: ["從飯店步行至上野站搭車", "免換線轉乘最方便", "請認明『JR 上野站』的綠色標誌，不要走進地下鐵(Tokyo Metro)"],
                     routes: ["從飯店出發，沿著淺草通往西(上野站方向)直行約 10 分鐘", "抵達「JR 上野站」後，從「淺草口」或「廣小路口」進站", "使用西瓜卡(Suica)進站，尋找 3 號月台(山手線外回) 或 4 號月台(京濱東北線往大船方向)", "搭乘 2 站 (上野 -> 御徒町 -> 秋葉原)，在「秋葉原站」下車", "車程僅約 4 分鐘，請留意下車站點"]
                   }
                 }, 
                 { time: "17:45", title: "御茶之水 聖橋", desc: "鈴芽場景", icon: "📸", location: "聖橋", transport: { route: "秋葉原 → 聖橋", line: "步行", time: "10分" }, hideMap: true,
                   stationGuide: {
                     name: "前往聖橋", desc: "秋葉原出發散步",
                     tips: ["出站後開啟路線導航步行前往"],
                     routes: ["出秋葉原站後，往西邊(御茶之水方向)散步約 10 分鐘，即可抵達「聖橋」拍攝點"]
                   }
                 }, 
                 { time: "18:30", title: "秋葉原", desc: "逛街", icon: "🛍️", location: "秋葉原駅", transport: { route: "聖橋 → 秋葉原", line: "步行", time: "10分" }, hideMap: true }, 
                 { time: "19:00", title: "秋葉原晚餐", desc: "美食街或拉麵燒肉", icon: "🍛", location: "ヨドバシAkiba", transport: { route: "秋葉原 → 餐廳", line: "步行", time: "5分" }, tips: "【上野/秋葉原 飲食6選】\\n1. Yodobashi 8F美食街（ヨドバシ，Yodobashi）\\n2. 九州 じゃんがら（九州じゃんがら，Kyushu Jangara）\\n3. 壽司郎 上野店（スシロー，Sushiro）\\n4. 敘敘苑 上野不忍口店（叙々苑，Jojoen）\\n5. 鴨 to 蔥（らーめん 鴨 to 葱，Kamo to Negi）\\n6. 客美多咖啡 上野廣小路店（コメダ珈琲店，Komeda's Coffee）\\n💡 推薦在 Yodobashi 吃飽，直攻6F打寶可夢機台！" }, 
                 { time: "21:00", title: "返回飯店", desc: "休息", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "秋葉原 → 上野 → 飯店", line: "JR 直達轉步行", time: "15分" }, hideMap: true,
                   stationGuide: {
                     name: "返回飯店 (秋葉原出發)", desc: "搭乘 JR 至上野後步行",
                     tips: ["在上野站下車", "免轉乘地鐵，直接散步回去", "注意月台方向，搭乘山手線外回或京濱東北線北行"],
                     routes: ["在秋葉原站進入 JR 閘口，尋找 2號月台(山手線外回) 或 3號月台(京濱東北線往大宮方向)", "搭乘 2 站 (秋葉原 -> 御徒町 -> 上野) 至「上野站」下車", "抵達上野站後，請跟隨黃色指標尋找「淺草口」或「入谷口」出閘門", "出站後來到地面，沿著高架橋旁的『淺草通』往東（稻荷町站方向）直走", "步行約 8-10 分鐘即可看見左側的 Stayme THE HOTEL Ueno 飯店"]
                   }
                 } 
             ] },
             { day: 2, date: "4/18 (六)", title: "台場鋼彈 & 豐洲", events: [ 
                 { time: "08:45", title: "往上野站", desc: "出發", icon: "🚶", location: "上野駅", transport: { route: "飯店 → 上野站", line: "步行", time: "10分" }, hideMap: true }, 
                 { time: "09:00", title: "豐洲市場 / 千客萬來", desc: "參觀/小吃", icon: "🏮", location: "豊洲市場", transport: { route: "上野 → 豐洲", line: "JR山手線 轉 有樂町線", time: "30分" }, hideMap: true, tips: "💡 早上先在豐洲周邊逛逛，可吃點玉子燒等小點心墊胃，將主力午餐移至台場商場內享用。",
                   stationGuide: {
                     name: "前往豐洲市場", desc: "JR山手線轉乘有樂町線",
                     tips: ["在有樂町站轉乘", "有樂町線往新木場方向"],
                     routes: ["從飯店步行約 10 分鐘至「JR上野站」", "搭乘「JR山手線(綠色)」往東京/品川方向，搭至「有樂町站」", "出 JR 閘門，依循指標前往地下鐵轉乘「有樂町線(金色)」往新木場方向", "搭乘至終點「豐洲站」下車，可步行或轉乘百合海鷗號至市場前站"]
                   }
                 }, 
                 { time: "11:30", title: "往台場 DiverCity", desc: "海鷗號", icon: "🚅", location: "台場駅", transport: { route: "豐洲 → 台場", line: "百合海鷗號 (ゆりかもめ)", time: "20分" }, hideMap: true, tips: "💡 今日搭乘海鷗號的次數不多，直接使用西瓜卡(Suica)進出站即可，最為方便！",
                   stationGuide: {
                     name: "搭乘百合海鷗號", desc: "直接刷西瓜卡最划算",
                     tips: ["今日僅搭乘兩次，不需買一日券", "直接刷西瓜卡進站即可"],
                     routes: ["在「豐洲站」依循百合海鷗號指標", "直接使用西瓜卡(Suica/PASMO)嗶卡進站", "搭乘往「台場/新橋」方向的列車"]
                   }
                 }, 
                 { time: "11:50", title: "台場午餐", desc: "DiverCity 商場", icon: "🍔", location: "ダイバーシティ東京 プラザ", transport: { route: "台場站 → DiverCity", line: "步行", time: "5分" }, tips: "【台場 午餐5選】\\n1. 田中商店（博多長浜らーめん 田中商店，Tanaka Shoten）\\n2. 金子半之助（日本橋 天丼 金子半之助，Kaneko Hannosuke）\\n3. 傳說的斯塔丼屋（伝説のすた丼屋，Densetsu no Sutadon-ya）\\n4. 蘋果樹蛋包飯（ポムの樹，Pomme-no-ki）\\n5. 燒肉 平城苑（東京焼肉 平城苑，Heijoen）\\n💡 在 DiverCity 用餐，吃飽走到一樓廣場直接看 13:00 的鋼彈表演最順路！" }, 
                 { time: "13:00", title: "獨角獸鋼彈", desc: "變身秀", icon: "🤖", location: "実物大ユニコーンガンダム立像" }, 
                 { time: "17:30", title: "teamLab", desc: "需預約", icon: "✨", location: "teamLab Planets TOKYO", transport: { route: "台場 → 新豐洲", line: "百合海鷗號 (ゆりかもめ)", time: "23分" }, hideMap: true,
                   stationGuide: {
                     name: "前往 teamLab", desc: "百合海鷗號直達",
                     tips: ["往豐洲方向"],
                     routes: ["從「台場站」使用西瓜卡進入百合海鷗號閘口", "搭乘往「豐洲」方向的列車", "搭乘至「新豐洲站」下車，出站即可看見 teamLab 展館"]
                   }
                 }, 
                 { time: "19:30", title: "豐洲 LaLaport", desc: "晚餐", icon: "🍽️", location: "ららぽーと豊洲", transport: { route: "新豐洲 → 豐洲", line: "步行", time: "10分" }, hideMap: true, tips: "【豐洲 LaLaport 晚餐6選】\\n1. 100支湯匙（100本のスプーン，100 Spoons）\\n2. 燒肉 Toraji（焼肉トラジ，Yakiniku Toraji）\\n3. 築地食堂 源ちゃん（築地食堂 源ちゃん，Genchan）\\n4. 麵屋 黑琥（麺や 黒琥，Kuroko）\\n5. 玉丁本店（玉丁本店，Tamacho Honten）\\n6. 客美多咖啡 豐洲店（コメダ珈琲店，Komeda's Coffee）\\n💡 商場 3F 還有玩具專賣店與扭蛋機，吃飽可以逛！",
                   stationGuide: {
                     name: "前往 LaLaport", desc: "步行前往",
                     tips: ["散步約 10 分鐘即可抵達"],
                     routes: ["從 teamLab (新豐洲站) 出發", "沿著晴海通往豐洲站方向直走", "步行約 10 分鐘即可看見 LaLaport 商場"]
                   }
                 }, 
                 { time: "21:30", title: "返回飯店", desc: "休息", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "豐洲 → 上野 → 飯店", line: "有樂町線 轉 JR山手線", time: "30分" }, hideMap: true,
                   stationGuide: {
                     name: "返回飯店 (豐洲出發)", desc: "有樂町線轉乘JR山手線",
                     tips: ["需在有樂町站轉乘", "轉乘需出閘門但指標清楚", "回到上野站後一樣走『淺草口』出站"],
                     routes: ["從 LaLaport 步行回「豐洲站」，搭乘地下鐵「有樂町線(金色)」往池袋/和光市方向", "搭乘 4 站至「有樂町站」下車，依循『JR 線』指標出地下鐵閘門", "進入 JR 有樂町站，尋找 4號月台(山手線內回) 或 4號月台(京濱東北線北行) 往東京/上野方向", "搭乘至「上野站」下車，尋找「淺草口」或「入谷口」出閘門", "出站後來到地面，沿著『淺草通』往東（稻荷町站方向）直走約 10 分鐘即可抵達飯店"]
                   }
                 } 
             ] },
             { day: 3, date: "4/19 (日)", title: "淺草與晴空塔", events: [ 
                 { time: "08:45", title: "往上野站", desc: "出發", icon: "🚶", location: "上野駅", transport: { route: "飯店 → 上野站", line: "步行", time: "10分" }, hideMap: true }, 
                 { time: "09:00", title: "淺草寺", desc: "雷門", icon: "🏮", location: "雷門", transport: { route: "上野 → 淺草", line: "東京地鐵銀座線 直達", time: "5分" }, hideMap: true,
                   stationGuide: {
                     name: "前往淺草", desc: "銀座線直達",
                     tips: ["從上野站搭乘，指標明確"],
                     routes: ["從飯店步行約 10 分鐘至「上野站」", "搭乘「銀座線(黃色)」往淺草方向", "搭乘 3 站即可抵達終點「淺草站」", "出站後依循「雷門」指標步行約 3 分鐘即可抵達"]
                   }
                 }, 
                 { time: "11:00", title: "隅田川步道", desc: "散步", icon: "🚶", location: "すみだリバーウォーク", transport: { route: "淺草 → 晴空塔", line: "步行", time: "20分" }, hideMap: true }, 
                 { time: "12:00", title: "晴空塔午餐", desc: "Solamachi 6F/3F", icon: "🍱", location: "東京ソラマチ", tips: "【晴空塔 飲食5選】\\n1. 六厘舍（六厘舎，Rokurinsha）\\n2. 迴轉壽司 根室花丸（回転寿司 根室花丸，Nemuro Hanamaru）\\n3. 利久牛舌（牛たん炭焼 利久，Rikyu）\\n4. 燒肉 Pure（焼肉 ぴゅあ，Pure）\\n5. Tabe-Terrace 美食街（タベテラス，Tabe-Terrace）" }, 
                 { time: "13:30", title: "晴空塔寶可夢", desc: "Solamachi 4F", icon: "🛍️", location: "ポケモンセンタースカイツリータウン" }, 
                 { time: "17:30", title: "淺草晚餐", desc: "藏壽司 ROX館", icon: "🍣", location: "くら寿司 浅草ROX店", transport: { route: "押上 → 淺草", line: "都營淺草線", time: "10分" }, hideMap: true, tips: "【淺草 飲食6選】\\n1. 藏壽司 淺草ROX店（くら寿司，Kura Sushi）\\n2. 一蘭拉麵 淺草店（一蘭，Ichiran）\\n3. 平城苑 淺草雷門店（東京焼肉 平城苑，Heijoen）\\n4. 淺草今半（浅草今半，Asakusa Imahan）\\n5. 淺草炸肉餅（浅草メンチ，Asakusa Menchi）\\n6. 客美多咖啡 田原町站前店（コメダ珈琲店，Komeda's Coffee）",
                   stationGuide: {
                     name: "前往淺草藏壽司", desc: "都營淺草線直達",
                     tips: ["從晴空塔旁的「押上站」出發"],
                     routes: ["從晴空塔樓下依循指標前往「押上站」，尋找『都營淺草線(玫瑰紅色)』的專屬閘口", "進站後，前往搭乘往「西馬込/羽田機場」方向的列車", "搭乘 2 站至「淺草站」下車 (車程約 3 分鐘)", "出站後開啟導航，沿著大馬路『雷門通』往西直行", "步行約 8-10 分鐘即可看見『淺草 ROX 商場』，藏壽司位於 4F"]
                   }
                 }, 
                 { time: "19:30", title: "返回飯店", desc: "回程", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "淺草/田原町 → 上野站 → 飯店", line: "銀座線 直達轉步行", time: "15分" }, hideMap: true,
                   stationGuide: {
                     name: "返回飯店 (淺草出發)", desc: "搭乘銀座線至上野後步行",
                     tips: ["從田原町站或淺草站上車皆可", "搭乘銀座線回到熟悉的『上野站』", "認明『淺草口』出站"],
                     routes: ["吃飽後步行至銀座線「田原町站」或「淺草站」", "搭乘「銀座線(黃色)」往澀谷方向", "搭乘至「上野站」下車 (從田原町出發為 2 站)", "抵達上野站後，請跟隨黃色指標尋找「淺草口」出閘門", "出站後來到地面，沿著『淺草通』往東（稻荷町方向）直走約 10 分鐘即可輕鬆抵達飯店"]
                   }
                 } 
             ] },
             { day: 4, date: "4/20 (一)", title: "輕井澤一日遊", events: [ 
                 { time: "09:00", title: "往上野站", desc: "搭新幹線", icon: "🚶", location: "JR 上野駅", transport: { route: "飯店 → 上野", line: "步行", time: "10分" }, hideMap: true,
                   stationGuide: {
                     name: "JR 上野站", desc: "搭乘新幹線攻略",
                     tips: ["新幹線入口在站內深處", "必走「中央改札」"],
                     routes: ["從地面進入 JR 上野站，請認明最大的「中央改札」", "進站後抬頭看綠色新幹線標示，直走約 3 分鐘", "通過第二道「新幹線專用改札」", "搭乘手扶梯向下至 B3/B4 月台 (通常往輕井澤在 19/20 月台)"]
                   }
                 }, 
                 { time: "10:10", title: "抵達輕井澤", desc: "北口租單車", icon: "🚲", location: "軽井沢駅", transport: { route: "上野 → 輕井澤", line: "JR 北陸新幹線", time: "60分" }, hideMap: true }, 
                 { time: "10:30", title: "雲場池", desc: "大自然散步", icon: "🦆", location: "長野県 雲場池", transport: { route: "車站 → 雲場池", line: "單車", time: "10分" }, hideMap: true }, 
                 { time: "11:15", title: "舊輕井澤", desc: "老街漫遊", icon: "🏘️", location: "旧軽井沢銀座通り", transport: { route: "雲場池 → 舊輕井澤", line: "單車", time: "10分" }, hideMap: true }, 
                 { time: "12:30", title: "輕井澤午餐", desc: "美食街/餐廳", icon: "🍱", location: "軽井沢プリンスショッピングプラザ 太陽と緑のキッチン", transport: { route: "舊輕井澤 → Outlet", line: "單車", time: "15分" }, hideMap: true, tips: "【輕井澤 飲食5選】\\n1. 明治亭（ソースかつ丼 明治亭，Meijitei）\\n2. 濃熟雞白湯 錦（濃熟鶏白湯 錦，Nishiki）\\n3. 熟成和牛燒肉 Aging Beef（熟成和牛焼肉エイジング・ビーフ，Aging Beef）\\n4. 清安庵（御曹司 きよやす庵，Kiyoyasuan）\\n5. 史努比村（SNOOPY Village / スヌーピービレッジ，Snoopy Village）" }, 
                 { time: "14:30", title: "王子 Outlet", desc: "購物與樂高區", icon: "🛍️", location: "軽井沢プリンスショッピングプラザ", hideRoute: true, tips: "💡 將 Outlet 移到下午，買完戰利品就能直接搭新幹線，不用提著大包小包騎腳踏車！" }, 
                 { time: "17:30", title: "返回上野", desc: "回程", icon: "🚅", location: "JR 上野駅", transport: { route: "輕井澤 → 上野", line: "JR 北陸新幹線", time: "60分" }, hideMap: true,
                   stationGuide: {
                     name: "返回上野", desc: "搭乘新幹線",
                     tips: ["確認票面座位", "上野是終點東京的前一站，注意聽廣播"],
                     routes: ["在輕井澤站進入「新幹線」專用閘口", "尋找往「東京」方向的月台 (通常是上行月台)", "確認車票上的車次與座位，搭乘約 1 小時抵達「上野站」"]
                   }
                 }, 
                 { time: "18:45", title: "上野晚餐", desc: "壽司郎/拉麵", icon: "🍣", location: "スシロー 上野店", transport: { route: "上野站 → 餐廳", line: "步行", time: "5分" }, hideMap: true, tips: "回程新幹線上可先開 App 抽號碼牌，減少壽司郎現場排隊時間。(若想換口味，上野有鴨to蔥、敘敘苑可選)" }, 
                 { time: "20:30", title: "返回飯店", desc: "步行", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "上野 → 飯店", line: "步行", time: "10分" }, hideMap: true,
                   stationGuide: {
                     name: "返回飯店 (上野市區出發)", desc: "散步回飯店路線",
                     tips: ["吃飽後直接散步消化", "沿著大馬路『淺草通』直行最安全不會迷路"],
                     routes: ["從壽司郎上野店出來後，先往 JR 上野站方向走，回到大馬路", "找到主要幹道『淺草通』(留意上方有高速公路高架橋)", "沿著淺草通往東（稻荷町站/淺草方向）直走", "大約步行 8-10 分鐘，即可看見位於道路左側邊的 Stayme THE HOTEL Ueno 飯店"]
                   }
                 } 
             ] },
             { day: 5, date: "4/21 (二)", title: "築地・渋谷・新宿", events: [ 
                 { time: "08:40", title: "往上野站", desc: "出發", icon: "🚶", location: "上野駅", transport: { route: "飯店 → 上野站", line: "步行", time: "10分" }, hideMap: true }, 
                 { time: "09:00", title: "築地場外市場", desc: "早餐", icon: "🐟", location: "築地場外市場", transport: { route: "上野 → 築地", line: "東京地鐵日比谷線 直達", time: "12分" }, hideMap: true, tips: "【築地市場 飲食5選】\\n1. 狐狸屋（きつねや，Kitsuneya）\\n2. 築地 山長（築地山長，Yamacho）\\n3. 築地 可樂餅（築地コロッケ，Tsukiji Croquette）\\n4. 黑銀 鮪魚店（築地黒銀 まぐろや，Kurogin）\\n5. 壽司三味 本店（すしざんまい，Sushizanmai）\\n💡 狐狸屋極受歡迎，建議一早就去排隊！",
                   stationGuide: {
                     name: "前往築地市場", desc: "日比谷線直達 (免轉乘)",
                     tips: ["從上野站搭乘，免換線直達"],
                     routes: ["從飯店步行約 10 分鐘至「上野站」", "依循指標前往地下鐵「日比谷線(銀色)」", "搭乘往中目黑/六本木方向列車，約 12 分鐘直達「築地站」下車", "出站步行約 3 分鐘即可抵達場外市場"]
                   }
                 }, 
                 { time: "12:00", title: "渋谷 PARCO", desc: "寶可夢", icon: "🎮", location: "渋谷パルコ", transport: { route: "銀座站 → 渋谷", line: "東京地鐵銀座線 直達", time: "16分" }, hideMap: true,
                   stationGuide: {
                     name: "前往澀谷", desc: "銀座線直達 (免轉乘)",
                     tips: ["從築地散步至銀座站搭車", "抵達後先逛 PARCO 或去吃飯"],
                     routes: ["從築地場外市場步行約 10-12 分鐘至「銀座站」", "進入地鐵站搭乘「銀座線(黃色)」往澀谷方向", "直達終點「澀谷站」下車", "下車後位於 3F，可跟隨 Scramble Square 指標或下至 1F 廣場過馬路前往 PARCO"]
                   }
                 }, 
                 { time: "13:30", title: "澀谷午餐", desc: "魚米/美食街", icon: "🍽️", location: "渋谷スクランブルスクエア", transport: { route: "PARCO → 餐廳", line: "步行", time: "10分" }, tips: "【澀谷 飲食5選】\\n1. 魚米（魚べい，Uobei）\\n2. 鶴橋風月（鶴橋風月，Tsuruhashi Fugetsu）\\n3. 阿夫利（AFURI，Afuri）\\n4. 燒肉 牛角 渋谷店（牛角，Gyukaku）\\n5. 名代 豬排（名代 かつくら，Katsukura）\\n💡 吃飽直接搭電梯上 SHIBUYA SKY 最順路！" }, 
                 { time: "15:00", title: "SHIBUYA SKY", desc: "需預約", icon: "🏙️", location: "SHIBUYA SKY", transport: { route: "餐廳 → 展望台", line: "步行", time: "5分" }, hideMap: true }, 
                 { time: "17:30", title: "新宿 3D貓", desc: "東口", icon: "🐈", location: "クロス新宿ビジョン", transport: { route: "渋谷 → 新宿", line: "JR 山手線", time: "7分" }, hideMap: true,
                   stationGuide: {
                     name: "前往新宿", desc: "JR 山手線動線",
                     tips: ["3D 貓與歌舞伎町都在東口"],
                     routes: ["從澀谷站進入 JR 閘口，搭乘「山手線(綠色)」往新宿/池袋方向", "搭乘約 7 分鐘抵達「新宿站」", "下車後請務必尋找黃色招牌「東改札 (East Exit)」", "出站到達地面廣場，往左前方抬頭即可看見 3D 貓"]
                   }
                 }, 
                 { time: "18:30", title: "新宿晚餐", desc: "天婦羅丼飯/燒肉", icon: "🦖", location: "新宿東宝ビル", transport: { route: "東口 → 歌舞伎町", line: "步行", time: "10分" }, hideMap: true, tips: "【新宿 飲食6選】\\n1. 天丼 Tenya（天丼てんや，Tenya）\\n2. 燒肉亭 六歌仙（焼肉亭 六歌仙，Rokkasen）\\n3. 一蘭拉麵 新宿中央東口店（一蘭，Ichiran）\\n4. 名代 宇奈とと（名代 宇奈とと，Unatoto）\\n5. 高島屋 Times Square（新宿タカシマヤ，Takashimaya）\\n6. 客美多咖啡 新宿靖國通店（コメダ珈琲店，Komeda's Coffee）\\n💡 哥吉拉頭像每整點會咆哮發光，在歌舞伎町吃晚餐剛好可以看！" }, 
                 { time: "20:30", title: "返回飯店", desc: "回程", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "新宿 → 上野 → 飯店", line: "JR 山手線 直達轉步行", time: "35分" }, hideMap: true,
                   stationGuide: {
                     name: "返回飯店 (新宿出發)", desc: "JR 山手線直達 (免轉乘)",
                     tips: ["搭乘山手線外回(池袋/上野方向)", "車程較長(約25分)可以讓小孩在車上稍作休息", "認明『淺草口』出站"],
                     routes: ["從新宿東寶大樓(哥吉拉)步行回「JR 新宿站」東口", "進站後尋找 15號月台「山手線外回」(往池袋・上野方向)", "搭乘約 25 分鐘，不需轉車，直達「上野站」下車", "抵達上野站後，請跟隨黃色指標尋找「淺草口」或「入谷口」出閘門", "出站後來到地面，沿著『淺草通』往東（稻荷町方向）直走約 10 分鐘即可抵達飯店"]
                   }
                 } 
             ] },
             { day: 6, date: "4/22 (三)", title: "返台", events: [ 
                 { time: "10:00", title: "Check-out", desc: "上野站寄放行李", icon: "🧳", location: "京成上野駅", transport: { route: "飯店 → 京成上野站", line: "步行", time: "10分" }, hideMap: true,
                   stationGuide: {
                     name: "京成上野站 置物櫃", desc: "大型行李寄放攻略",
                     tips: ["搭 Skyliner 最順路，強烈建議寄放於此", "可使用 Suica 扣款，省去準備硬幣麻煩", "大型置物櫃易滿，若全滿可尋找人工寄託服務"],
                     routes: ["從飯店提行李步行至「京成上野站」", "在剪票口外有大量置物櫃 (Coin Lockers)", "找到可容納大型行李的空櫃，放入後依照螢幕指示操作付款", "保留好密碼券或西瓜卡，以利稍後取件"]
                   }
                 },
                 { time: "10:20", title: "阿美橫丁", desc: "最後血拼/點心", icon: "🛍️", location: "アメ横商店街", transport: { route: "京成上野站 → 阿美橫丁", line: "步行", time: "3分" }, hideMap: true, tips: "把握最後時間採買藥妝或零食，京成上野站過個馬路就是阿美橫丁入口！" },
                 { time: "11:20", title: "往機場", desc: "搭 Skyliner", icon: "🚅", location: "京成上野駅", transport: { route: "京成上野 → 成田T1", line: "京成 Skyliner", time: "41分" }, hideMap: true,
                   stationGuide: {
                     name: "前往成田機場", desc: "搭乘 Skyliner",
                     tips: ["先去置物櫃取回行李！", "全車對號入座"],
                     routes: ["取回行李後，使用事先買好的車票或兌換券進入閘口", "搭乘手扶梯前往地下月台，確認車次與座位", "約 41 分鐘直達「成田機場 T1」站"]
                   }
                 }, 
                 { time: "12:25", title: "抵達機場", desc: "成田 T1 (南翼)", icon: "✈️", location: "成田国際空港 第1ターミナル", hideRoute: true, tips: "【成田 T1 必吃美食 5選】\\n1. 中華蕎麥 富田（中華蕎麦 とみ田，Tomita）\\n2. 八代目儀兵衛（八代目儀兵衛，Hachidaime Gihey）\\n3. 高湯茶泡飯 燕（だし茶漬け えん，En）\\n4. 杵屋麥丸（杵屋麦丸，Kineya Mugimaru）\\n5. 壽司 京辰（寿司 京辰，Kyotatsu）\\n\\n【必買伴手禮 5選】\\n1. 東京ばな奈 (推薦於 FaSoLa TAX FREE 購買)\\n2. PRESS BUTTER SAND (推薦於 FaSoLa 購買)\\n3. NY PERFECT CHEESE (推薦於 FaSoLa 購買)\\n4. ROYCE' 生巧克力 (機場免稅店皆有)\\n5. TRAVELER'S FACTORY (推薦於 第一航廈 4F 專賣店 購買)" }, 
                 { time: "14:25", title: "起飛返台", desc: "長榮 BR197", icon: "✈️", location: "", hideRoute: true, transport: "" } 
             ] }
        ];

        const reservations = [
            { 
                cat: "交通", 
                items: [
                    { name: "京成 Skyliner", url: "https://www.keisei.co.jp/keisei/tetudou/skyliner/e-ticket/zht/", tips: "Day 1 & Day 6 機場來回，線上買便宜" }, 
                    { name: "JR 新幹線 (e5489)", url: "https://www.eki-net.com/zh-CHT/jreast-train-reservation/Top/Index", tips: "Day 4 輕井澤來回，1個月前預訂" }
                ] 
            },
            { 
                cat: "景點", 
                items: [
                    { name: "teamLab Planets", url: "https://planets.teamlab.art/tokyo/zh-hant/", tips: "Day 2 (17:30)，建議提前1個月" },
                    { name: "東京晴空塔", url: "https://www.tokyo-skytree.jp/cn_t/ticket/", tips: "Day 3 下午，30天前開放預約" }, 
                    { name: "SHIBUYA SKY", url: "https://www.shibuya-scramble-square.com/sky/ticket/", tips: "Day 5 (15:00)，4週前必搶" }
                ] 
            },
            { 
                cat: "實用/餐廳", 
                items: [
                    { name: "壽司郎 (Sushiro) 官方 App", url: "https://www.akindo-sushiro.co.jp/app/", tips: "Day 4 晚餐，先下載 App 抽號碼牌免排隊" },
                    { name: "KIRBY CAFÉ (星之卡比)", url: "https://kirbycafe.jp/tokyo/", tips: "晴空塔 4F，每月 10 號開放搶下個月的位子" }
                ] 
            }
        ];

        const travelInfos = [
            { id: "narita", name: "成田機場 第1航廈", icon: "✈️", tag: "機場", desc: "本次搭乘長榮航空，起降皆位於 T1 南翼 (South Wing)。", tips: "【入境第一站】領完行李後前往 B1 鐵道樓層，可購買兒童版西瓜卡並搭乘 Skyliner 前往市區。" },
            { id: "keisei_ueno", name: "京成上野站", icon: "🚄", tag: "車站/行李", desc: "Skyliner 起訖站。距離住宿飯店步行約 10 分鐘，站內設有大量置物櫃。", tips: "【行李寄放】Day 6 退房後，強烈建議將大型行李寄放於此站剪票口外的置物櫃 (可用 Suica 扣款)。寄放後可直接步行去對面逛阿美橫丁，時間到再回來搭 Skyliner 直達機場。" },
            { id: "jr_ueno", name: "JR 上野站", icon: "🚉", tag: "車站/新幹線", desc: "Day 4 搭乘新幹線前往輕井澤的出發站。站體龐大，擁有多個出入口。", tips: "【新幹線搭乘】入口位於站內深處，請務必認明一樓最大的「中央改札」進站。直走通過第二道「新幹線專用改札」後，搭乘手扶梯下樓至 B3/B4 月台搭車。" },
            { id: "shinjuku_sta", name: "JR 新宿站", icon: "🏢", tag: "車站/迷宮", desc: "號稱日本第一大迷宮，擁有眾多私鐵與出口，容易迷路。", tips: "【前往東口】Day 5 前往 3D 貓與歌舞伎町哥吉拉，下車後請務必尋找黃色招牌「東改札 (East Exit)」出站，到達地面廣場即可抵達，切勿亂走其他出口。" }
        ];

        // Google TTS 發音功能
        const speakJapanese = (text) => {
            const audio = new Audio(
                'https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=ja&q=' + encodeURIComponent(text)
            );
            audio.play().catch(() => {
                // fallback: 使用 Web Speech API
                if ('speechSynthesis' in window) {
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = 'ja-JP';
                    utterance.rate = 0.85;
                    window.speechSynthesis.cancel();
                    window.speechSynthesis.speak(utterance);
                }
            });
        };

        const japaneseData = {
            locations: [
                { ch: "上野", jp: "うえの", romaji: "Ueno" },
                { ch: "淺草", jp: "あさくさ", romaji: "Asakusa" },
                { ch: "晴空塔", jp: "スカイツリー", romaji: "Sukai Tsurī" },
                { ch: "豐洲", jp: "とよす", romaji: "Toyosu" },
                { ch: "台場", jp: "おだいば", romaji: "Odaiba" },
                { ch: "秋葉原", jp: "あきはばら", romaji: "Akihabara" },
                { ch: "澀谷", jp: "しぶや", romaji: "Shibuya" },
                { ch: "新宿", jp: "しんじゅく", romaji: "Shinjuku" },
                { ch: "輕井澤", jp: "かるいざわ", romaji: "Karuizawa" },
                { ch: "成田機場", jp: "なりたくうこう", romaji: "Narita Kūkō" }
            ],
            scenarios: [
                {
                    title: "🍽️ 餐廳點餐",
                    icon: "🍽️",
                    phrases: [
                        { ch: "（進門時店員說）歡迎光臨！", jp: "いらっしゃいませ！", romaji: "Irasshaimase!", note: "店員招呼語，微笑點頭即可" },
                        { ch: "不好意思，請問有幾位？", jp: "何名様ですか？", romaji: "Nan-mei-sama desu ka?", note: "店員會問你幾位" },
                        { ch: "兩個大人、一個小孩", jp: "大人二人、子供一人です。", romaji: "Otona futari, kodomo hitori desu.", note: "" },
                        { ch: "不好意思，我要點餐", jp: "すみません、注文をお願いします。", romaji: "Sumimasen, chūmon o onegai shimasu.", note: "先說すみません引起注意" },
                        { ch: "請給我這個", jp: "これをお願いします。", romaji: "Kore o onegai shimasu.", note: "手指菜單即可" },
                        { ch: "請給我兩份這個", jp: "これを二つお願いします。", romaji: "Kore o futatsu onegai shimasu.", note: "" },
                        { ch: "有兒童餐嗎？", jp: "お子様メニューはありますか？", romaji: "Okosama menyū wa arimasu ka?", note: "" },
                        { ch: "不要辣 / 不加辣", jp: "辛くしないでください。", romaji: "Karaku shinaide kudasai.", note: "帶小孩很實用" },
                        { ch: "我要結帳", jp: "お会計をお願いします。", romaji: "Okaikei o onegai shimasu.", note: "" },
                        { ch: "可以刷卡嗎？", jp: "カードは使えますか？", romaji: "Kādo wa tsukaemasu ka?", note: "" },
                        { ch: "非常好吃！謝謝招待", jp: "とてもおいしかったです！ごちそうさまでした。", romaji: "Totemo oishikatta desu! Gochisōsama deshita.", note: "離開餐廳時說，很有禮貌" }
                    ]
                },
                {
                    title: "🚃 交通移動",
                    icon: "🚃",
                    phrases: [
                        { ch: "請問○○站怎麼走？", jp: "すみません、○○駅はどう行けばいいですか？", romaji: "Sumimasen, ○○ eki wa dō ikeba ii desu ka?", note: "把○○換成站名" },
                        { ch: "到○○站要多久？", jp: "○○駅まで何分くらいですか？", romaji: "○○ eki made nan-pun kurai desu ka?", note: "" },
                        { ch: "這班電車到○○嗎？", jp: "この電車は○○に行きますか？", romaji: "Kono densha wa ○○ ni ikimasu ka?", note: "" },
                        { ch: "我要買兒童票", jp: "子供の切符をお願いします。", romaji: "Kodomo no kippu o onegai shimasu.", note: "" },
                        { ch: "下一班幾點？", jp: "次は何時ですか？", romaji: "Tsugi wa nanji desu ka?", note: "" }
                    ]
                },
                {
                    title: "🛍️ 購物逛街",
                    icon: "🛍️",
                    phrases: [
                        { ch: "這個多少錢？", jp: "これはいくらですか？", romaji: "Kore wa ikura desu ka?", note: "" },
                        { ch: "可以試穿嗎？", jp: "試着してもいいですか？", romaji: "Shichaku shitemo ii desu ka?", note: "" },
                        { ch: "有別的顏色嗎？", jp: "他の色はありますか？", romaji: "Hoka no iro wa arimasu ka?", note: "" },
                        { ch: "可以免稅嗎？", jp: "免税できますか？", romaji: "Menzei dekimasu ka?", note: "消費滿 5000 日圓可問" },
                        { ch: "請幫我包起來（送禮用）", jp: "プレゼント用に包んでいただけますか？", romaji: "Purezento-yō ni tsutsunde itadakemasu ka?", note: "非常有禮貌的說法" },
                        { ch: "請給我袋子", jp: "袋をお願いします。", romaji: "Fukuro o onegai shimasu.", note: "日本超商需自費購袋" }
                    ]
                },
                {
                    title: "🏨 飯店住宿",
                    icon: "🏨",
                    phrases: [
                        { ch: "我要辦理入住", jp: "チェックインをお願いします。", romaji: "Chekkuin o onegai shimasu.", note: "" },
                        { ch: "我姓○○，有預約", jp: "○○と申します。予約しています。", romaji: "○○ to mōshimasu. Yoyaku shiteimasu.", note: "把○○換成你的姓" },
                        { ch: "可以寄放行李嗎？", jp: "荷物を預かっていただけますか？", romaji: "Nimotsu o azukatte itadakemasu ka?", note: "check-in 前或 check-out 後都適用" },
                        { ch: "請問 Wi-Fi 密碼是？", jp: "Wi-Fiのパスワードを教えていただけますか？", romaji: "Waifai no pasuwādo o oshiete itadakemasu ka?", note: "" },
                        { ch: "我要退房", jp: "チェックアウトをお願いします。", romaji: "Chekkuauto o onegai shimasu.", note: "" }
                    ]
                },
                {
                    title: "🆘 緊急求助",
                    icon: "🆘",
                    phrases: [
                        { ch: "請幫幫我", jp: "助けてください。", romaji: "Tasukete kudasai.", note: "" },
                        { ch: "小孩走丟了", jp: "子供が迷子になりました。", romaji: "Kodomo ga maigo ni narimashita.", note: "趕快找工作人員" },
                        { ch: "請叫救護車", jp: "救急車を呼んでください。", romaji: "Kyūkyūsha o yonde kudasai.", note: "" },
                        { ch: "洗手間在哪裡？", jp: "トイレはどこですか？", romaji: "Toire wa doko desu ka?", note: "帶小孩最常用！" },
                        { ch: "我不會說日文", jp: "日本語が話せません。", romaji: "Nihongo ga hanasemasen.", note: "" },
                        { ch: "有會說英文的人嗎？", jp: "英語を話せる方はいますか？", romaji: "Eigo o hanaseru kata wa imasu ka?", note: "" }
                    ]
                },
                {
                    title: "🔢 實用數字",
                    icon: "🔢",
                    phrases: [
                        { ch: "1 / 2 / 3", jp: "いち / に / さん", romaji: "Ichi / Ni / San", note: "" },
                        { ch: "4 / 5 / 6", jp: "よん / ご / ろく", romaji: "Yon / Go / Roku", note: "" },
                        { ch: "7 / 8 / 9 / 10", jp: "なな / はち / きゅう / じゅう", romaji: "Nana / Hachi / Kyū / Jū", note: "" },
                        { ch: "100 / 1000 / 10000", jp: "ひゃく / せん / いちまん", romaji: "Hyaku / Sen / Ichiman", note: "日圓常用單位" }
                    ]
                }
            ]
        };

        const ItineraryView = () => {
            const [activeDay, setActiveDay] = useState(0);
            return (
                <div className="flex flex-col h-full bg-gray-50">
                    <div className="sticky top-0 z-10 bg-white/95 backdrop-blur shadow-sm p-2 flex gap-2 flex-shrink-0 overflow-x-auto hide-scrollbar">
                        {itinerary.map((d, i) => (
                            <button key={i} onClick={() => setActiveDay(i)} 
                                className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${activeDay === i ? 'bg-indigo-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>
                                Day {d.day}
                            </button>
                        ))}
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 pb-24">
                        <div className="text-center mb-4">
                            <h2 className="text-xl font-bold text-gray-800">{itinerary[activeDay].date}</h2>
                            <p className="text-indigo-600 font-medium">{itinerary[activeDay].title}</p>
                        </div>
                        <div className="relative pl-4 space-y-8 border-l-2 border-gray-200 ml-3">
                            {itinerary[activeDay].events.map((evt, i) => {
                                let prevLoc = i === 0 ? HOTEL_ADDRESS : itinerary[activeDay].events[i-1].location;
                                if (activeDay === 0 && i < 2) prevLoc = null; 
                                
                                const mapUrl = "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(evt.location);
                                const dirUrl = prevLoc ? "https://www.google.com/maps/dir/?api=1&origin=" + encodeURIComponent(prevLoc) + "&destination=" + encodeURIComponent(evt.location) + "&travelmode=transit" : null;

                                return (
                                    <div key={i} className="relative pl-6">
                                        <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-indigo-500 border-2 border-white shadow"></div>
                                        <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
                                            <div className="flex justify-between items-start mb-1">
                                                <span className="bg-indigo-50 text-indigo-700 text-xs font-bold px-2 py-1 rounded">{evt.time}</span>
                                                <span className="text-2xl">{evt.icon}</span>
                                            </div>
                                            <h3 className="font-bold text-gray-800 text-lg">{evt.title}</h3>
                                            <p className="text-sm text-gray-500 mb-2">{evt.desc}</p>
                                            
                                            {evt.tips && (
                                                <div className="mb-3 bg-yellow-50 text-yellow-800 text-[13px] p-2.5 rounded-lg border border-yellow-100 leading-relaxed whitespace-pre-line">
                                                    <span className="font-bold">💡 </span>{evt.tips}
                                                </div>
                                            )}

                                            {evt.transport && (
                                                <div className="mb-3 bg-slate-50 p-2.5 rounded-lg text-xs text-slate-600 flex flex-col gap-1.5 border border-slate-200">
                                                    <div className="flex items-center gap-2 font-medium">
                                                        <span>{evt.transport.line.includes('步行') && !evt.transport.line.includes('轉') ? '🚶' : '🚇'} {evt.transport.route}</span>
                                                        <span className="text-slate-300">|</span>
                                                        <span>⏱️ {evt.transport.time}</span>
                                                    </div>
                                                    {evt.transport.line && evt.transport.line !== '步行' && (
                                                        <div className="mt-0.5">
                                                            <span className={`inline-block px-2 py-1 rounded text-[11px] font-bold ${
                                                                evt.transport.line.includes('計程車') ? 'bg-yellow-100 text-yellow-700 border border-yellow-200' : 
                                                                evt.transport.line.includes('單車') ? 'bg-green-100 text-green-700 border border-green-200' :
                                                                'bg-blue-100 text-blue-700 border border-blue-200'
                                                            }`}>
                                                                {evt.transport.line.includes('計程車') ? '🚕 ' : 
                                                                 evt.transport.line.includes('單車') ? '🚲 ' : '🚊 '}
                                                                {evt.transport.line}
                                                            </span>
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                            
                                            {evt.stationGuide && (
                                                <div className="mb-3 bg-blue-50/60 rounded-xl p-3 border border-blue-100">
                                                    <h4 className="font-bold text-blue-800 mb-1 flex items-center gap-1">🚉 {evt.stationGuide.name}</h4>
                                                    <p className="text-[12px] text-blue-600 mb-2 font-medium">{evt.stationGuide.desc}</p>
                                                    <div className="space-y-1.5 mb-3">
                                                        {evt.stationGuide.tips.map((t, idx) => (
                                                            <div key={idx} className="flex gap-1.5 text-[12px] items-start">
                                                                <span className="bg-white border border-blue-200 text-blue-600 px-1 rounded text-[10px] mt-0.5 leading-none py-0.5 font-bold">Tip</span>
                                                                <span className="text-gray-700 leading-tight">{t}</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                    <div className="border-t border-blue-200/60 pt-2.5">
                                                        <h5 className="text-[11px] font-bold text-blue-800 mb-2">🚏 導航路徑</h5>
                                                        <ul className="space-y-2 pl-1">
                                                            {evt.stationGuide.routes.map((step, idx) => (
                                                                <li key={idx} className="text-[12px] text-gray-700 flex gap-2.5 items-start">
                                                                    <span className="flex-shrink-0 w-4 h-4 rounded-full bg-blue-500 text-white text-[9px] flex items-center justify-center font-bold mt-0.5">{idx + 1}</span>
                                                                    <span className="leading-snug">{step}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                </div>
                                            )}
                                            
                                            <div className="flex gap-2">
                                                {!evt.hideMap && <a href={mapUrl} target="_blank" className="flex-1 bg-gray-50 hover:bg-gray-100 text-gray-700 text-xs font-bold py-2 rounded-lg text-center no-underline">📍 地圖</a>}
                                                {!evt.hideRoute && dirUrl && <a href={dirUrl} target="_blank" className="flex-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 text-xs font-bold py-2 rounded-lg text-center no-underline">🚀 路線</a>}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            );
        };

        const MapView = () => {
            const [mode, setMode] = useState('attraction');
            const [surrArea, setSurrArea] = useState('ueno');
            const imgRef = useRef(null);
            const tripImgRef = useRef(null);

            useEffect(() => {
                if (mode === 'full' && imgRef.current) {
                    const pz = Panzoom(imgRef.current, { maxScale: 8, minScale: 1, contain: null, startScale: 1 });
                    if(imgRef.current.parentElement) imgRef.current.parentElement.addEventListener('wheel', pz.zoomWithWheel);
                }
            }, [mode]);

            useEffect(() => {
                if (mode === 'attraction' && tripImgRef.current) {
                    const pz = Panzoom(tripImgRef.current, { maxScale: 8, minScale: 1, contain: null, startScale: 1 });
                    if(tripImgRef.current.parentElement) tripImgRef.current.parentElement.addEventListener('wheel', pz.zoomWithWheel);
                }
            }, [mode]);

            const renderSurrounding = () => {
                const guide = surroundingGuides[surrArea];
                if (!guide) return null;

                return (
                    <div className="w-full flex flex-col gap-3 p-2">
                        {guide.spots.map((spot, idx) => {
                            const mapUrl = "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(spot.mapQuery);
                            return (
                                <div key={idx} className="bg-white border border-gray-200 rounded-xl p-3 shadow-sm flex flex-col gap-2 w-full">
                                    <div className="flex items-start gap-3">
                                        <div className="text-3xl mt-1">{spot.icon}</div>
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <h4 className="font-bold text-gray-800 text-[15px] m-0">{spot.name}</h4>
                                                <span className="bg-indigo-50 text-indigo-600 text-[10px] px-2 py-0.5 rounded font-bold whitespace-nowrap">{spot.tag}</span>
                                            </div>
                                            <p className="text-[13px] text-gray-600 leading-relaxed m-0">{spot.desc}</p>
                                        </div>
                                    </div>
                                    <div className="flex justify-end border-t border-gray-50 pt-2 mt-1">
                                         <a href={mapUrl} target="_blank" className="bg-blue-50 hover:bg-blue-100 text-blue-600 border border-blue-100 text-xs font-bold py-1.5 px-3 rounded-lg flex items-center gap-1 no-underline transition-colors">
                                            📍 開啟地圖
                                        </a>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                );
            };

            return (
                <div className="flex flex-col h-full bg-gray-50">
                    <div className="sticky top-0 z-10 bg-white/95 backdrop-blur shadow-sm p-2 flex gap-2 flex-shrink-0 overflow-x-auto hide-scrollbar">
                         <button onClick={() => setMode('attraction')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${mode === 'attraction' ? 'bg-indigo-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🗺️ 全覽</button>
                        <button onClick={() => setMode('surrounding')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${mode === 'surrounding' ? 'bg-teal-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🏙️ 景點建議</button>
                        <button onClick={() => setMode('metro')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${mode === 'metro' ? 'bg-gray-800 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🚇 路線</button>
                        <button onClick={() => setMode('full')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${mode === 'full' ? 'bg-orange-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>📑 完整地鐵</button>
                    </div>
                    
                    <div className="flex-1 overflow-y-auto p-4 pb-24">
                        <div className="flex flex-col items-center w-full">
                            {mode === 'attraction' && (
                                <div className="w-full h-[65vh] bg-blue-50 rounded-xl overflow-hidden border border-blue-200 relative">
                                     <div className="w-full h-full flex items-center justify-center overflow-hidden">
                                        <img ref={tripImgRef} src={URL_TRIP} alt="行程全覽地圖" className="w-full h-auto object-contain cursor-grab" />
                                     </div>
                                     <div className="absolute bottom-2 left-0 right-0 text-center pointer-events-none">
                                        <span className="bg-black/50 text-white text-[10px] px-2 py-1 rounded-full">雙指或滾輪可縮放移動</span>
                                     </div>
                                </div>
                            )}
                            
                            {mode === 'surrounding' && (
                                <div className="w-full flex flex-col items-center">
                                    <div className="flex gap-2 mb-3 overflow-x-auto w-full justify-start flex-shrink-0 hide-scrollbar px-1 py-1">
                                        {[
                                            {id: 'ueno', name: '上野/秋葉原'},
                                            {id: 'toyosu', name: '豐洲'}, 
                                            {id: 'odaiba', name: '台場'}, 
                                            {id: 'asakusa', name: '淺草'},
                                            {id: 'skytree', name: '晴空塔'},
                                            {id: 'karuizawa', name: '輕井澤'},
                                            {id: 'tsukiji', name: '築地'},
                                            {id: 'shibuya', name: '渋谷'},
                                            {id: 'shinjuku', name: '新宿'}
                                        ].map(area => (
                                            <button key={area.id} onClick={() => setSurrArea(area.id)} className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-bold transition-colors ${surrArea === area.id ? 'bg-teal-600 text-white shadow-md' : 'bg-white text-gray-600 border border-gray-200'}`}>{area.name}</button>
                                        ))}
                                    </div>
                                    <div className="w-full max-w-sm">{renderSurrounding()}</div>
                                </div>
                            )}

                            {mode === 'metro' && (
                                <div className="w-full max-w-sm bg-white rounded-xl overflow-hidden shadow-inner border-2 border-gray-200 p-0">
                                    <img src={URL_NOTE} alt="路線手稿" className="w-full h-auto" />
                                </div>
                            )}

                            {mode === 'full' && (
                                <div className="w-full h-[65vh] bg-gray-100 rounded-xl overflow-hidden border border-gray-300 relative">
                                     <div className="w-full h-full flex items-center justify-center overflow-hidden">
                                        <img ref={imgRef} src={URL_MAP} alt="完整地鐵圖" className="w-full h-auto object-contain cursor-grab" />
                                     </div>
                                     <div className="absolute bottom-2 left-0 right-0 text-center pointer-events-none">
                                        <span className="bg-black/50 text-white text-[10px] px-2 py-1 rounded-full">雙指或滾輪可縮放</span>
                                     </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            );
        };

        const WeatherPanel = () => {
            const [weather, setWeather] = useState(null);
            const [loading, setLoading] = useState(true);
            const [error, setError] = useState(null);

            const WMO_CODES = {
                0: { icon: '☀️', desc: '晴天' }, 1: { icon: '🌤️', desc: '大致晴朗' }, 2: { icon: '⛅', desc: '局部多雲' }, 3: { icon: '☁️', desc: '多雲' },
                45: { icon: '🌫️', desc: '霧' }, 48: { icon: '🌫️', desc: '霜霧' },
                51: { icon: '🌦️', desc: '小毛毛雨' }, 53: { icon: '🌦️', desc: '毛毛雨' }, 55: { icon: '🌧️', desc: '密集毛毛雨' },
                61: { icon: '🌧️', desc: '小雨' }, 63: { icon: '🌧️', desc: '中雨' }, 65: { icon: '🌧️', desc: '大雨' },
                71: { icon: '🌨️', desc: '小雪' }, 73: { icon: '🌨️', desc: '中雪' }, 75: { icon: '❄️', desc: '大雪' },
                80: { icon: '🌦️', desc: '小陣雨' }, 81: { icon: '🌧️', desc: '中陣雨' }, 82: { icon: '⛈️', desc: '強陣雨' },
                95: { icon: '⛈️', desc: '雷陣雨' }, 96: { icon: '⛈️', desc: '雷陣雨夾冰雹' }, 99: { icon: '⛈️', desc: '強雷陣雨' }
            };

            const TRIP_DAYS = [
                { date: '2026-04-17', day: 'Day 1', title: '抵達東京', area: '上野' },
                { date: '2026-04-18', day: 'Day 2', title: '台場&豐洲', area: '台場' },
                { date: '2026-04-19', day: 'Day 3', title: '淺草&晴空塔', area: '淺草' },
                { date: '2026-04-20', day: 'Day 4', title: '輕井澤', area: '輕井澤' },
                { date: '2026-04-21', day: 'Day 5', title: '築地&澀谷&新宿', area: '澀谷' },
                { date: '2026-04-22', day: 'Day 6', title: '返台', area: '成田' }
            ];

            const WEEKDAY_MAP = ['日', '一', '二', '三', '四', '五', '六'];

            useEffect(() => {
                const fetchWeather = async () => {
                    try {
                        setLoading(true);
                        // 東京 (35.6762, 139.6503) 和輕井澤 (36.3486, 138.5970)
                        const [tokyoRes, karuizawaRes] = await Promise.all([
                            fetch('https://api.open-meteo.com/v1/forecast?latitude=35.6762&longitude=139.6503&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,windspeed_10m_max&timezone=Asia/Tokyo&forecast_days=16'),
                            fetch('https://api.open-meteo.com/v1/forecast?latitude=36.3486&longitude=138.5970&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,windspeed_10m_max&timezone=Asia/Tokyo&forecast_days=16')
                        ]);
                        const tokyo = await tokyoRes.json();
                        const karuizawa = await karuizawaRes.json();
                        setWeather({ tokyo, karuizawa });
                    } catch (err) {
                        setError('無法取得天氣資料，請確認網路連線');
                    } finally {
                        setLoading(false);
                    }
                };
                fetchWeather();
            }, []);

            const getDayWeather = (data, dateStr) => {
                if (!data || !data.daily) return null;
                const idx = data.daily.time.indexOf(dateStr);
                if (idx === -1) return null;
                return {
                    code: data.daily.weathercode[idx],
                    max: Math.round(data.daily.temperature_2m_max[idx]),
                    min: Math.round(data.daily.temperature_2m_min[idx]),
                    rainProb: data.daily.precipitation_probability_max[idx],
                    rainMm: data.daily.precipitation_sum[idx],
                    wind: Math.round(data.daily.windspeed_10m_max[idx])
                };
            };

            const getUmbrellaAdvice = (rainProb, rainMm) => {
                if (rainProb >= 60 || rainMm >= 5) return { text: '帶傘', color: 'text-blue-600', bg: 'bg-blue-50 border-blue-200' };
                if (rainProb >= 30) return { text: '備傘', color: 'text-yellow-600', bg: 'bg-yellow-50 border-yellow-200' };
                return { text: '免傘', color: 'text-green-600', bg: 'bg-green-50 border-green-200' };
            };

            const getClothingAdvice = (max, min) => {
                const avg = (max + min) / 2;
                if (avg >= 25) return '短袖短褲即可';
                if (avg >= 20) return '薄長袖或襯衫';
                if (avg >= 15) return '外套+長袖';
                if (avg >= 10) return '保暖外套+長褲';
                return '厚外套+圍巾';
            };

            if (loading) return (
                <div className="flex flex-col items-center justify-center py-20">
                    <div className="spinner" style={{borderLeftColor: '#0284c7'}}></div>
                    <p className="text-gray-500 text-sm mt-3">正在取得天氣預報...</p>
                </div>
            );

            if (error) return (
                <div className="text-center py-16">
                    <div className="text-4xl mb-3">⚠️</div>
                    <p className="text-gray-600 text-sm">{error}</p>
                    <p className="text-gray-400 text-xs mt-2">天氣預報僅在出發前 14 天內可顯示</p>
                </div>
            );

            const hasTripData = TRIP_DAYS.some(td => getDayWeather(weather.tokyo, td.date));

            return (
                <>
                    <div className="text-center mb-5">
                        <h2 className="text-xl font-bold text-gray-800">旅程天氣</h2>
                        <p className="text-sky-600 text-sm">4/17 ~ 4/22 東京 & 輕井澤</p>
                    </div>

                    {!hasTripData && (
                        <div className="bg-sky-50 border border-sky-200 rounded-xl p-4 mb-4 text-center">
                            <p className="text-sky-700 text-sm font-bold mb-1">尚未進入預報範圍</p>
                            <p className="text-sky-600 text-xs">天氣預報通常在出發前 7~14 天才會出現，以下先顯示東京近日天氣供參考。</p>
                        </div>
                    )}

                    {hasTripData ? (
                        <div className="space-y-3">
                            {TRIP_DAYS.map((td, idx) => {
                                const isKaruizawa = td.date === '2026-04-20';
                                const src = isKaruizawa ? weather.karuizawa : weather.tokyo;
                                const w = getDayWeather(src, td.date);
                                if (!w) return (
                                    <div key={idx} className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm opacity-60">
                                        <div className="flex items-center gap-3">
                                            <span className="bg-sky-100 text-sky-700 text-xs font-bold px-2 py-1 rounded">{td.day}</span>
                                            <span className="text-gray-500 text-sm">{td.title}</span>
                                        </div>
                                        <p className="text-gray-400 text-xs mt-2">尚無預報資料</p>
                                    </div>
                                );
                                const wmo = WMO_CODES[w.code] || { icon: '❓', desc: '未知' };
                                const umbrella = getUmbrellaAdvice(w.rainProb, w.rainMm);
                                const dateObj = new Date(td.date);
                                const weekday = WEEKDAY_MAP[dateObj.getDay()];

                                return (
                                    <div key={idx} className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center gap-2">
                                                <span className="bg-sky-100 text-sky-700 text-xs font-bold px-2 py-1 rounded">{td.day}</span>
                                                <span className="text-gray-700 text-sm font-bold">{td.date.slice(5)} ({weekday})</span>
                                            </div>
                                            <span className="text-gray-400 text-xs">{isKaruizawa ? '📍 輕井澤' : '📍 東京'}</span>
                                        </div>
                                        <div className="flex items-center gap-4 mb-3">
                                            <div className="text-5xl leading-none">{wmo.icon}</div>
                                            <div className="flex-1">
                                                <div className="font-bold text-gray-800 text-lg">{wmo.desc}</div>
                                                <div className="text-gray-500 text-sm mt-0.5">{td.title} · {td.area}</div>
                                            </div>
                                            <div className="text-right">
                                                <div className="font-bold text-2xl text-gray-800">{w.max}°</div>
                                                <div className="text-gray-400 text-sm">{w.min}°</div>
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-3 gap-2 mb-3">
                                            <div className="bg-gray-50 rounded-lg p-2 text-center border border-gray-100">
                                                <div className="text-gray-400 text-[10px]">降雨機率</div>
                                                <div className="font-bold text-sky-600 text-sm">{w.rainProb}%</div>
                                            </div>
                                            <div className="bg-gray-50 rounded-lg p-2 text-center border border-gray-100">
                                                <div className="text-gray-400 text-[10px]">降雨量</div>
                                                <div className="font-bold text-sky-600 text-sm">{w.rainMm}mm</div>
                                            </div>
                                            <div className="bg-gray-50 rounded-lg p-2 text-center border border-gray-100">
                                                <div className="text-gray-400 text-[10px]">最大風速</div>
                                                <div className="font-bold text-sky-600 text-sm">{w.wind}km/h</div>
                                            </div>
                                        </div>
                                        <div className="flex gap-2">
                                            <div className={`flex-1 rounded-lg p-2 text-center border ${umbrella.bg}`}>
                                                <span className={`text-xs font-bold ${umbrella.color}`}>☂️ {umbrella.text}</span>
                                            </div>
                                            <div className="flex-1 bg-purple-50 border border-purple-200 rounded-lg p-2 text-center">
                                                <span className="text-xs font-bold text-purple-600">👕 {getClothingAdvice(w.max, w.min)}</span>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <div className="space-y-3">
                            <h3 className="text-base font-bold text-gray-700 ml-1 flex items-center"><span className="w-1 h-5 bg-sky-400 mr-2 rounded-full"></span>東京近日天氣</h3>
                            {weather.tokyo.daily.time.slice(0, 7).map((date, idx) => {
                                const w = {
                                    code: weather.tokyo.daily.weathercode[idx],
                                    max: Math.round(weather.tokyo.daily.temperature_2m_max[idx]),
                                    min: Math.round(weather.tokyo.daily.temperature_2m_min[idx]),
                                    rainProb: weather.tokyo.daily.precipitation_probability_max[idx]
                                };
                                const wmo = WMO_CODES[w.code] || { icon: '❓', desc: '未知' };
                                const dateObj = new Date(date);
                                const weekday = WEEKDAY_MAP[dateObj.getDay()];
                                return (
                                    <div key={idx} className="bg-white border border-gray-200 rounded-xl p-3 shadow-sm flex items-center gap-3">
                                        <div className="text-3xl">{wmo.icon}</div>
                                        <div className="flex-1">
                                            <div className="font-bold text-gray-700 text-sm">{date.slice(5)} ({weekday})</div>
                                            <div className="text-gray-400 text-xs">{wmo.desc}</div>
                                        </div>
                                        <div className="text-right">
                                            <div className="font-bold text-gray-800">{w.max}° / {w.min}°</div>
                                            <div className="text-sky-500 text-xs">💧 {w.rainProb}%</div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    <div className="mt-5 bg-gray-50 border border-gray-200 rounded-xl p-3">
                        <p className="text-gray-400 text-[11px] text-center">資料來源：Open-Meteo · 每次開啟自動更新</p>
                    </div>
                </>
            );
        };

        const ChecklistPanel = () => {
            const CHECKLIST_DATA = [
                {
                    cat: '📄 證件文件',
                    color: 'red',
                    items: [
                        { name: '護照（確認效期 6 個月以上）', critical: true },
                        { name: '護照影本 / 手機翻拍備份', critical: true },
                        { name: '兒童護照', critical: true },
                        { name: '機票電子確認信（長榮 BR196 / BR197）', critical: true },
                        { name: '飯店預約確認信', critical: false },
                        { name: 'teamLab Planets 門票 QR Code', critical: false },
                        { name: 'SHIBUYA SKY 門票 QR Code', critical: false },
                        { name: 'Skyliner 車票 / 兌換憑證', critical: false },
                        { name: '新幹線車票 (e5489)', critical: false },
                        { name: '旅遊平安險保單號碼', critical: false }
                    ]
                },
                {
                    cat: '💰 金錢支付',
                    color: 'amber',
                    items: [
                        { name: '日圓現金（建議 5~8 萬日圓）', critical: true },
                        { name: '信用卡（Visa / Master 為主）', critical: true },
                        { name: '西瓜卡 Suica（大人）', critical: false },
                        { name: '兒童版西瓜卡（機場現場辦）', critical: false }
                    ]
                },
                {
                    cat: '📱 3C 電子',
                    color: 'blue',
                    items: [
                        { name: '手機 + 充電線', critical: true },
                        { name: '行動電源', critical: true },
                        { name: '萬用轉接頭（日本為 A 型兩扁腳）', critical: false },
                        { name: '相機 / GoPro + 記憶卡', critical: false },
                        { name: '日本上網 eSIM / Wi-Fi 分享器', critical: true },
                        { name: '耳機（飛機上用）', critical: false }
                    ]
                },
                {
                    cat: '👕 衣物穿著',
                    color: 'purple',
                    items: [
                        { name: '換洗衣物（6 天份）', critical: false },
                        { name: '薄外套 / 防風外套（4月早晚涼）', critical: true },
                        { name: '好走的鞋（每天走超多路！）', critical: true },
                        { name: '拖鞋（飛機上 / teamLab 後穿）', critical: false },
                        { name: '帽子 / 墨鏡', critical: false },
                        { name: '摺疊雨傘', critical: true },
                        { name: '小孩替換衣物（多帶 1~2 套）', critical: false }
                    ]
                },
                {
                    cat: '🧴 盥洗藥品',
                    color: 'teal',
                    items: [
                        { name: '牙刷牙膏 / 毛巾', critical: false },
                        { name: '防曬乳', critical: false },
                        { name: '面紙 / 濕紙巾', critical: true },
                        { name: '常備藥品（感冒、腸胃、退燒）', critical: true },
                        { name: '小孩藥品（退燒藥水、止瀉）', critical: true },
                        { name: 'OK 繃 / 痠痛貼布', critical: false },
                        { name: '保溫瓶 / 水壺', critical: false }
                    ]
                },
                {
                    cat: '🧸 小孩專區',
                    color: 'orange',
                    items: [
                        { name: '兒童背包（裝自己的零食和玩具）', critical: false },
                        { name: '小零食（飛機上、排隊時用）', critical: true },
                        { name: '小玩具 / 畫筆著色本', critical: false },
                        { name: '平板 / 兒童耳機（飛機救星）', critical: false },
                        { name: '輕便推車（視需要）', critical: false }
                    ]
                },
                {
                    cat: '🧳 行李收納',
                    color: 'gray',
                    items: [
                        { name: '行李箱（留空間裝戰利品！）', critical: false },
                        { name: '摺疊購物袋（買太多時用）', critical: true },
                        { name: '夾鏈袋（分裝零食/液體）', critical: false },
                        { name: '行李秤（避免超重）', critical: false },
                        { name: '頸枕（飛機 / 新幹線上用）', critical: false }
                    ]
                }
            ];

            const [checked, setChecked] = useState(() => {
                try {
                    const saved = localStorage.getItem('trip_checklist');
                    return saved ? JSON.parse(saved) : {};
                } catch { return {}; }
            });

            const toggle = (key) => {
                const next = { ...checked, [key]: !checked[key] };
                setChecked(next);
                try { localStorage.setItem('trip_checklist', JSON.stringify(next)); } catch {}
            };

            const resetAll = () => {
                setChecked({});
                try { localStorage.removeItem('trip_checklist'); } catch {}
            };

            const totalItems = CHECKLIST_DATA.reduce((sum, cat) => sum + cat.items.length, 0);
            const checkedCount = Object.values(checked).filter(Boolean).length;
            const progress = totalItems > 0 ? Math.round((checkedCount / totalItems) * 100) : 0;

            const colorMap = {
                red: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', bar: 'bg-red-400', check: 'bg-red-500' },
                amber: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', bar: 'bg-amber-400', check: 'bg-amber-500' },
                blue: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', bar: 'bg-blue-400', check: 'bg-blue-500' },
                purple: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700', bar: 'bg-purple-400', check: 'bg-purple-500' },
                teal: { bg: 'bg-teal-50', border: 'border-teal-200', text: 'text-teal-700', bar: 'bg-teal-400', check: 'bg-teal-500' },
                orange: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', bar: 'bg-orange-400', check: 'bg-orange-500' },
                gray: { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-700', bar: 'bg-gray-400', check: 'bg-gray-500' }
            };

            return (
                <>
                    <div className="text-center mb-4"><h2 className="text-xl font-bold text-gray-800">行李清單</h2><p className="text-emerald-600 text-sm">出發前逐項打勾確認</p></div>

                    <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm mb-5">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-bold text-gray-700">打包進度</span>
                            <span className="text-sm font-bold text-emerald-600">{checkedCount} / {totalItems}</span>
                        </div>
                        <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600 rounded-full transition-all duration-500" style={{width: progress + '%'}}></div>
                        </div>
                        <div className="flex justify-between items-center mt-2">
                            <span className="text-xs text-gray-400">{progress === 100 ? '✅ 全部打包完成！準備出發！' : progress >= 80 ? '🎉 快完成了！' : progress >= 50 ? '💪 加油，過半了！' : '📦 開始打包吧～'}</span>
                            <button onClick={resetAll} className="text-[11px] text-gray-400 underline active:text-red-500">清除全部</button>
                        </div>
                    </div>

                    {CHECKLIST_DATA.map((cat, cIdx) => {
                        const c = colorMap[cat.color] || colorMap.gray;
                        const catChecked = cat.items.filter((_, idx) => checked[`${cIdx}-${idx}`]).length;
                        return (
                            <div key={cIdx} className={`${c.bg} border ${c.border} rounded-2xl p-4 mb-4`}>
                                <div className="flex items-center justify-between mb-3">
                                    <h3 className={`font-bold text-base ${c.text}`}>{cat.cat}</h3>
                                    <span className="text-xs text-gray-400 font-bold">{catChecked}/{cat.items.length}</span>
                                </div>
                                <div className="space-y-1.5">
                                    {cat.items.map((item, iIdx) => {
                                        const key = `${cIdx}-${iIdx}`;
                                        const isChecked = !!checked[key];
                                        return (
                                            <div key={iIdx} onClick={() => toggle(key)} className={`flex items-center gap-3 bg-white rounded-xl p-2.5 border border-gray-100 active:scale-[0.98] transition-all cursor-pointer ${isChecked ? 'opacity-50' : ''}`}>
                                                <div className={`w-5 h-5 rounded-md border-2 flex-shrink-0 flex items-center justify-center transition-colors ${isChecked ? c.check + ' border-transparent' : 'border-gray-300 bg-white'}`}>
                                                    {isChecked && <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>}
                                                </div>
                                                <span className={`text-sm ${isChecked ? 'line-through text-gray-400' : 'text-gray-700'}`}>{item.name}</span>
                                                {item.critical && !isChecked && <span className="ml-auto text-[10px] bg-red-100 text-red-600 px-1.5 py-0.5 rounded font-bold flex-shrink-0">必帶</span>}
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        );
                    })}
                </>
            );
        };

        const AttractionView = () => {
            const [subTab, setSubTab] = useState('attractions');
            
            return (
                <div className="flex flex-col h-full bg-gray-50">
                    <div className="sticky top-0 z-10 bg-white/95 backdrop-blur shadow-sm p-2 flex gap-2 flex-shrink-0 overflow-x-auto hide-scrollbar">
                        <button onClick={() => setSubTab('attractions')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${subTab === 'attractions' ? 'bg-indigo-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🏞️ 景點百科</button>
                        <button onClick={() => setSubTab('travel_info')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${subTab === 'travel_info' ? 'bg-teal-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🚉 旅遊資訊</button>
                        <button onClick={() => setSubTab('weather')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${subTab === 'weather' ? 'bg-sky-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🌤️ 天氣</button>
                        <button onClick={() => setSubTab('japanese')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${subTab === 'japanese' ? 'bg-orange-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🗣️ 實用日文</button>
                        <button onClick={() => setSubTab('emergency')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${subTab === 'emergency' ? 'bg-red-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🆘 緊急卡</button>
                        <button onClick={() => setSubTab('checklist')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${subTab === 'checklist' ? 'bg-emerald-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>✅ 行李</button>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 pb-24 space-y-4">
                        
                        {/* 子分頁 1：景點百科 */}
                        {subTab === 'attractions' && (
                            <>
                                <div className="text-center mb-6"><h2 className="text-xl font-bold text-gray-800">景點百科</h2><p className="text-indigo-600 text-sm">依行程時序 Day 1 ~ Day 6 排序</p></div>
                                {attractionInfos.map((item, idx) => (
                                    <div key={idx} className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm flex flex-col gap-2">
                                        <div className="flex items-center gap-3">
                                            <div className="text-3xl">{item.icon}</div>
                                            <div>
                                                <h3 className="font-bold text-gray-800">{item.name}</h3>
                                                <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">{item.tag}</span>
                                            </div>
                                        </div>
                                        {item.desc && <p className="text-sm text-gray-600 mt-2 whitespace-pre-line">{item.desc}</p>}
                                        
                                        {item.foodSpots && (
                                            <div className="mt-2 space-y-2">
                                                {item.foodSpots.map((spot, sIdx) => {
                                                    const mapUrl = "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(spot.mapQuery);
                                                    return (
                                                        <div key={sIdx} className="bg-gray-50 p-2 rounded-lg flex items-start gap-2 border border-gray-100">
                                                            <div className="text-lg leading-none mt-0.5">{spot.icon}</div>
                                                            <div className="flex-1">
                                                                <a href={mapUrl} target="_blank" className="font-bold text-indigo-600 hover:text-indigo-800 text-[14px] no-underline flex items-center gap-1 transition-colors">
                                                                    {spot.name} 
                                                                    <svg className="w-3 h-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                                                                </a>
                                                                <p className="text-[12px] text-gray-500 mt-1 m-0 leading-snug">{spot.desc}</p>
                                                            </div>
                                                        </div>
                                                    )
                                                })}
                                            </div>
                                        )}
                                        {item.tips && <div className="bg-yellow-50 text-yellow-800 text-[13px] p-2 rounded-lg border border-yellow-100 mt-2 leading-relaxed font-medium">💡 {item.tips}</div>}
                                    </div>
                                ))}
                            </>
                        )}

                        {/* 子分頁 2：旅遊資訊 */}
                        {subTab === 'travel_info' && (
                            <>
                                <div className="text-center mb-6"><h2 className="text-xl font-bold text-gray-800">旅遊資訊</h2><p className="text-teal-600 text-sm">機場、車站與行李寄放</p></div>
                                {travelInfos.map((item, idx) => (
                                    <div key={idx} className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm flex flex-col gap-2">
                                        <div className="flex items-center gap-3">
                                            <div className="text-3xl">{item.icon}</div>
                                            <div>
                                                <h3 className="font-bold text-gray-800">{item.name}</h3>
                                                <span className="text-xs bg-teal-50 text-teal-600 px-2 py-0.5 rounded font-bold border border-teal-100">{item.tag}</span>
                                            </div>
                                        </div>
                                        {item.desc && <p className="text-sm text-gray-600 mt-2 whitespace-pre-line">{item.desc}</p>}
                                        {item.tips && <div className="bg-teal-50 text-teal-800 text-[13px] p-2.5 rounded-lg border border-teal-100 mt-2 leading-relaxed font-medium"><span className="font-bold">💡 實用提示：</span>{item.tips}</div>}
                                    </div>
                                ))}
                            </>
                        )}

                        {/* 子分頁 2.5：天氣預報 */}
                        {subTab === 'weather' && <WeatherPanel />}

                        {/* 子分頁 3：實用日文 */}
                        {subTab === 'japanese' && (
                            <>
                                <div className="text-center mb-6"><h2 className="text-xl font-bold text-gray-800">實用日文</h2><p className="text-orange-600 text-sm">點擊 🔊 即可聽發音</p></div>
                                
                                <h3 className="text-lg font-bold text-gray-700 mb-3 ml-1 flex items-center"><span className="w-1 h-5 bg-orange-400 mr-2 rounded-full"></span>重要地名讀法</h3>
                                <div className="grid grid-cols-2 gap-3 mb-6">
                                    {japaneseData.locations.map((loc, idx) => (
                                        <div key={idx} onClick={() => speakJapanese(loc.jp)} className="bg-white border border-gray-200 rounded-xl p-3 shadow-sm flex flex-col items-center text-center active:scale-95 active:bg-orange-50 transition-all cursor-pointer relative">
                                            <span className="absolute top-2 right-2 text-orange-400 text-xs">🔊</span>
                                            <span className="font-bold text-gray-800 text-[15px]">{loc.ch}</span>
                                            <span className="text-orange-600 font-bold text-sm mt-1">{loc.jp}</span>
                                            <span className="text-gray-400 text-xs mt-0.5">{loc.romaji}</span>
                                        </div>
                                    ))}
                                </div>

                                <h3 className="text-lg font-bold text-gray-700 mb-3 ml-1 flex items-center"><span className="w-1 h-5 bg-orange-400 mr-2 rounded-full"></span>情境對話</h3>
                                {japaneseData.scenarios.map((scenario, sIdx) => (
                                    <div key={sIdx} className="mb-5">
                                        <div className="bg-orange-50 border border-orange-200 rounded-xl px-3 py-2 mb-3 font-bold text-orange-700 text-[15px]">{scenario.title}</div>
                                        <div className="space-y-2.5">
                                            {scenario.phrases.map((phrase, pIdx) => (
                                                <div key={pIdx} onClick={() => speakJapanese(phrase.jp)} className="bg-white border border-gray-200 rounded-xl p-3 shadow-sm active:scale-[0.98] active:bg-orange-50 transition-all cursor-pointer">
                                                    <div className="flex items-start justify-between gap-2">
                                                        <div className="flex-1 min-w-0">
                                                            <div className="text-gray-500 text-xs mb-1">{phrase.ch}</div>
                                                            <div className="font-bold text-orange-600 text-[15px] mb-0.5">{phrase.jp}</div>
                                                            <div className="text-gray-400 text-xs">{phrase.romaji}</div>
                                                            {phrase.note && <div className="text-teal-600 text-[11px] mt-1 bg-teal-50 rounded px-1.5 py-0.5 inline-block">💡 {phrase.note}</div>}
                                                        </div>
                                                        <span className="text-orange-400 text-lg mt-1 flex-shrink-0">🔊</span>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </>
                        )}

                        {/* 子分頁 4：緊急聯絡卡 */}
                        {subTab === 'emergency' && (
                            <>
                                <div className="text-center mb-5"><h2 className="text-xl font-bold text-gray-800">緊急聯絡卡</h2><p className="text-red-500 text-sm">存到手機截圖，以備不時之需</p></div>

                                <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-4 mb-4">
                                    <h3 className="font-bold text-red-700 text-base mb-3 flex items-center gap-2">🚨 日本緊急電話</h3>
                                    <div className="space-y-2.5">
                                        {[
                                            { label: '報警（警察）', number: '110', note: '遺失物品、犯罪事件' },
                                            { label: '火災 / 救護車', number: '119', note: '受傷、生病、火災' },
                                            { label: '海上事故', number: '118', note: '海上急難救助' }
                                        ].map((item, idx) => (
                                            <div key={idx} className="flex items-center justify-between bg-white rounded-xl p-3 border border-red-100">
                                                <div>
                                                    <div className="font-bold text-gray-800 text-sm">{item.label}</div>
                                                    <div className="text-gray-400 text-xs">{item.note}</div>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className="font-black text-red-600 text-xl">{item.number}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="mt-3 bg-red-100/60 rounded-lg p-2.5 text-[11px] text-red-700 leading-relaxed">
                                        💡 日本報警/叫救護車<strong>免費</strong>，可用任何電話撥打。接通後說「English please」可轉英語服務。
                                    </div>
                                </div>

                                <div className="bg-blue-50 border-2 border-blue-200 rounded-2xl p-4 mb-4">
                                    <h3 className="font-bold text-blue-700 text-base mb-3 flex items-center gap-2">🏥 旅外求助</h3>
                                    <div className="space-y-2.5">
                                        {[
                                            { label: '台灣駐日代表處（東京）', number: '+81-3-3280-7811', note: '平日 9:00-12:00 / 13:00-18:00' },
                                            { label: '急難救助（24hr）', number: '+81-80-6552-4764', note: '非上班時間、假日專線' },
                                            { label: '旅外國人急難救助全球專線', number: '+886-800-085-095', note: '24小時免費（海外撥打需付費）' }
                                        ].map((item, idx) => (
                                            <div key={idx} className="flex items-center justify-between bg-white rounded-xl p-3 border border-blue-100">
                                                <div className="flex-1 min-w-0 mr-2">
                                                    <div className="font-bold text-gray-800 text-sm">{item.label}</div>
                                                    <div className="text-gray-400 text-[11px]">{item.note}</div>
                                                </div>
                                                <div className="flex items-center gap-1.5 flex-shrink-0">
                                                    <span className="font-bold text-blue-600 text-[13px]">{item.number}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="bg-amber-50 border-2 border-amber-200 rounded-2xl p-4 mb-4">
                                    <h3 className="font-bold text-amber-700 text-base mb-3 flex items-center gap-2">🏨 住宿資訊（給計程車看）</h3>
                                    <div className="bg-white rounded-xl p-4 border border-amber-100">
                                        <div className="text-center">
                                            <div className="text-lg font-black text-gray-800 mb-1">Stayme THE HOTEL Ueno</div>
                                            <div className="text-base font-bold text-amber-700 mb-2">ステイミー ザ ホテル 上野</div>
                                            <div className="bg-amber-50 rounded-lg p-2 text-sm text-gray-700">
                                                〒110-0015<br/>
                                                東京都台東区東上野2丁目18-4
                                            </div>
                                            <a href={"https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent("Stayme THE HOTEL Ueno, Higashiueno, Taito City, Tokyo")} target="_blank" className="inline-block mt-3 bg-amber-500 text-white text-sm font-bold px-5 py-2 rounded-xl no-underline active:scale-95 transition-transform">📍 開啟 Google Map</a>
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-purple-50 border-2 border-purple-200 rounded-2xl p-4 mb-4">
                                    <h3 className="font-bold text-purple-700 text-base mb-3 flex items-center gap-2">📋 重要資訊速查</h3>
                                    <div className="space-y-2">
                                        {[
                                            { label: '航班去程', value: '長榮 BR196 · 4/17 桃園→成田' },
                                            { label: '航班回程', value: '長榮 BR197 · 4/22 成田→桃園' },
                                            { label: '日本國碼', value: '+81' },
                                            { label: '台灣國碼', value: '+886' },
                                            { label: '日本電壓', value: '100V / 60Hz（A型兩扁腳）' },
                                            { label: '時差', value: '日本比台灣快 1 小時' }
                                        ].map((item, idx) => (
                                            <div key={idx} className="flex justify-between items-center bg-white rounded-lg p-2.5 border border-purple-100">
                                                <span className="text-gray-500 text-xs font-bold">{item.label}</span>
                                                <span className="text-gray-800 text-xs font-bold text-right">{item.value}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="bg-green-50 border-2 border-green-200 rounded-2xl p-4">
                                    <h3 className="font-bold text-green-700 text-base mb-3 flex items-center gap-2">💬 求助日文（點擊發音）</h3>
                                    <div className="space-y-2">
                                        {[
                                            { ch: '請幫幫我', jp: '助けてください。' },
                                            { ch: '請叫救護車', jp: '救急車を呼んでください。' },
                                            { ch: '小孩走丟了', jp: '子供が迷子になりました。' },
                                            { ch: '我不會說日文', jp: '日本語が話せません。' },
                                            { ch: '請帶我去這個地址', jp: 'この住所までお願いします。' }
                                        ].map((item, idx) => (
                                            <div key={idx} onClick={() => speakJapanese(item.jp)} className="flex items-center justify-between bg-white rounded-lg p-2.5 border border-green-100 active:bg-green-50 active:scale-[0.98] transition-all cursor-pointer">
                                                <div>
                                                    <div className="text-gray-500 text-[11px]">{item.ch}</div>
                                                    <div className="font-bold text-green-700 text-sm">{item.jp}</div>
                                                </div>
                                                <span className="text-green-400 text-lg flex-shrink-0">🔊</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </>
                        )}

                        {/* 子分頁 5：行李清單 */}
                        {subTab === 'checklist' && <ChecklistPanel />}
                    </div>
                </div>
            );
        };

        const BookingView = () => (
            <div className="h-full overflow-y-auto p-4 pb-24 space-y-6">
                <div className="text-center mb-4"><h2 className="text-xl font-bold text-gray-800">預約管家</h2><p className="text-indigo-600 text-sm">必備連結</p></div>
                {reservations.map((cat, i) => (
                    <div key={i}>
                        <h3 className="text-lg font-bold text-gray-700 mb-3 ml-1 flex items-center"><span className="w-1 h-5 bg-indigo-500 mr-2 rounded-full"></span>{cat.cat}</h3>
                        <div className="space-y-4">
                            {cat.items.map((item, j) => (
                                <div key={j} className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm relative overflow-hidden">
                                    <div className="flex justify-between mb-2"><div><h4 className="font-bold text-gray-800">{item.name}</h4></div></div>
                                    <div className="bg-orange-50 border border-orange-100 rounded-lg p-2 mb-3"><p className="text-xs text-orange-700">💡 {item.tips}</p></div>
                                    <a href={item.url} target="_blank" className="block w-full bg-indigo-600 hover:bg-indigo-700 text-white text-center text-sm font-bold py-2.5 rounded-xl no-underline">前往預約</a>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        );

        const App = () => {
            const [view, setView] = useState('list');
            
            useEffect(() => {
                const el = document.getElementById('loading');
                if(el) el.style.display = 'none';
            }, []);

            return (
                <div className="h-screen flex flex-col bg-gray-50">
                    <div className="bg-indigo-600 text-white p-5 pt-12 rounded-b-3xl shadow-lg z-20 flex-shrink-0">
                        <div className="flex justify-between items-start">
                            <div><h1 className="text-2xl font-bold">東京親子之旅</h1><p className="text-indigo-100 text-sm mt-1">4/17 - 4/22 • 6天5夜</p></div>
                        </div>
                        <a href={"https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(HOTEL_ADDRESS)} target="_blank" className="mt-4 bg-indigo-700/50 p-3 rounded-xl flex items-center gap-3 backdrop-blur-sm active:scale-95 transition-transform border border-indigo-500/30 text-left no-underline">
                            <div className="bg-white p-2 rounded-full text-indigo-600">
                                {icons.map}
                            </div>
                            <div className="flex-1 min-w-0"><p className="text-xs text-indigo-200 uppercase font-semibold">住宿</p><p className="font-bold text-sm truncate text-white">Stayme THE HOTEL Ueno</p></div>
                        </a>
                    </div>

                    <div className="flex-1 overflow-hidden relative">
                        {view === 'list' && <ItineraryView />}
                        {view === 'map' && <MapView />}
                        {view === 'attraction' && <AttractionView />}
                        {view === 'booking' && <BookingView />}
                    </div>

                    <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-200 pl-4 pr-20 pt-2 pb-8 safe-bottom flex justify-start gap-5 items-center z-30 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
                        <button onClick={() => setView('list')} className={`flex flex-col items-center gap-1 p-1 rounded-xl min-w-[60px] transition-all ${view === 'list' ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400'}`}>{icons.list}<span className="text-[11px] font-bold">行程</span></button>
                        <button onClick={() => setView('map')} className={`flex flex-col items-center gap-1 p-1 rounded-xl min-w-[60px] transition-all ${view === 'map' ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400'}`}>{icons.map}<span className="text-[11px] font-bold">地圖</span></button>
                        <button onClick={() => setView('attraction')} className={`flex flex-col items-center gap-1 p-1 rounded-xl min-w-[60px] transition-all ${view === 'attraction' ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400'}`}>{icons.attraction}<span className="text-[11px] font-bold">百科</span></button>
                        <button onClick={() => setView('booking')} className={`flex flex-col items-center gap-1 p-1 rounded-xl min-w-[60px] transition-all ${view === 'booking' ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400'}`}>{icons.booking}<span className="text-[11px] font-bold">預約</span></button>
                    </div>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
        
        setTimeout(() => {
            const loadingEl = document.getElementById('loading');
            if (loadingEl && loadingEl.style.display !== 'none') {
                loadingEl.style.display = 'none';
            }
        }, 3000);
    </script>
</body>
</html>
"""

# 使用 components.html 渲染，設定高度為 800 (或更高) 以適應手機長滑動
components.html(html_code, height=900, scrolling=False)