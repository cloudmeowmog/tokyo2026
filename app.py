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
        /* 隱藏所有 Streamlit 預設的 UI 元素 */
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
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #f3f4f6; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; }
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        .safe-bottom { padding-bottom: env(safe-area-inset-bottom); padding-bottom: 20px; }
        
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
                    { name: 'Yamashiroya 玩具店', desc: 'JR 上野站對面。6 層樓玩具專賣店，寶可夢周邊齊全。', tag: '玩具百貨', icon: '🧸', mapQuery: 'ヤマシロヤ 上野' },
                    { name: '上野動物園', desc: '門票超便宜，適合早起帶小孩看熊貓散步放電。', tag: '動物園', icon: '🐼', mapQuery: '上野動物園' },
                    { name: 'Yodobashi 8F 美食街', desc: '有和幸豬排、Meat Rush，吃飽直攻6F寶可夢機台。', tag: '定食漢堡排', icon: '🍛', mapQuery: 'ヨドバシAkiba' },
                    { name: '九州 じゃんがら 拉麵', desc: '秋葉原本店。濃郁豚骨湯配超軟爛角肉。', tag: '豚骨拉麵', icon: '🍜', mapQuery: '九州じゃんがら 秋葉原本店' },
                    { name: '壽司郎 上野店', desc: '自動化點餐，小孩愛吃扭蛋好玩，優質備案。', tag: '迴轉壽司', icon: '🍣', mapQuery: 'スシロー 上野店' },
                    { name: '敘敘苑 上野不忍口店', desc: '頂級燒肉代名詞！環境舒適，適合犒賞全家。', tag: '高級燒肉', icon: '🥩', mapQuery: '叙々苑 上野不忍口店' },
                    { name: '鴨 to 蔥', desc: '上野超人氣排隊名店，清甜鴨蔥湯頭極獨特。', tag: '排隊拉麵', icon: '🍜', mapQuery: 'らーめん 鴨to葱 上野' }
                ]
            },
            toyosu: {
                name: '豐洲 / 市場',
                spots: [
                    { name: '千客萬來', desc: '市場旁最新溫泉美食街，復古江戶風情超好拍。', tag: '觀光美食', icon: '🏮', mapQuery: '豊洲 千客万来' },
                    { name: '茂助玉子燒', desc: '市場內百年老店，甜甜的日式煎蛋捲小孩絕對愛吃。', tag: '市場玉子燒', icon: '🍳', mapQuery: '豊洲市場 玉子焼' },
                    { name: '海鮮丼 大江戶', desc: '豐洲市場水產棟，超澎湃的新鮮海鮮丼。', tag: '豐盛海鮮', icon: '🍱', mapQuery: '海鮮丼 大江戸 豊洲市場' },
                    { name: '炸物 八千代', desc: '不吃生食的好選擇！炸大蝦與炸豬排定食。', tag: '熟食定食', icon: '🍤', mapQuery: 'とんかつ 八千代 豊洲市場' },
                    { name: '壽司大', desc: '豐洲市場超人氣排隊壽司，想吃需起個大早。', tag: '排隊壽司', icon: '🍣', mapQuery: '寿司大 豊洲市場' },
                    { name: 'teamLab Planets', desc: '需赤腳的水中光影美術館，小孩玩水超開心。', tag: '光影藝術', icon: '✨', mapQuery: 'teamLab Planets TOKYO' },
                    { name: '豐洲 LaLaport', desc: '超大商場！3樓有玩具店、扭蛋機，非常適合放電。', tag: '購物遊樂', icon: '🛍️', mapQuery: 'ららぽーと豊洲' },
                    { name: '100本のスプーン', desc: 'LaLaport 內親子餐廳。小孩可點大人一模一樣的半份餐。', tag: '親子餐廳', icon: '🍽️', mapQuery: '100本のスプーン ららぽーと豊洲' },
                    { name: '燒肉トラジ (Toraji)', desc: 'LaLaport 內吃厚切牛舌與和牛，舒適無煙味。', tag: '和牛燒肉', icon: '🥩', mapQuery: '焼肉トラジ ららぽーと豊洲店' },
                    { name: '築地食堂 源ちゃん', desc: 'LaLaport 內。提供美味生魚片丼與炸雞海鮮定食。', tag: '海鮮定食', icon: '🍱', mapQuery: '築地食堂 源ちゃん ららぽーと豊洲店' },
                    { name: '麵屋 黑琥', desc: 'LaLaport 內。豚骨與醬油拉麵，方便快速。', tag: '日式拉麵', icon: '🍜', mapQuery: '麺や 黒琥 ららぽーと豊洲' },
                    { name: '玉丁本店', desc: 'LaLaport 內。濃郁的味噌燉烏龍麵，麵條Q彈小孩好入口。', tag: '烏龍麵', icon: '🍲', mapQuery: '玉丁本店 ららぽーと豊洲店' }
                ]
            },
            odaiba: {
                name: '台場周邊',
                spots: [
                    { name: '獨角獸鋼彈', desc: 'DiverCity 前實物大鋼彈，變身秀父子必看！', tag: '地標', icon: '🤖', mapQuery: '実物大ユニコーンガンダム立像' },
                    { name: '鋼彈基地 (DiverCity)', desc: '滿滿的鋼彈模型與限定商品，買瘋的聖地。', tag: '模型', icon: '🛍️', mapQuery: 'ガンダムベース東京' },
                    { name: 'LEGOLAND 探索中心', desc: '室內樂高樂園，超多積木池與遊樂設施。', tag: '樂高樂園', icon: '🧱', mapQuery: 'レゴランド・ディスカバリー・センター東京' },
                    { name: '田中商店', desc: 'DiverCity 2F美食街。超濃郁豚骨拉麵，吃完馬上看鋼彈。', tag: '豚骨拉麵', icon: '🍜', mapQuery: '田中商店 ダイバーシティ東京プラザ店' },
                    { name: '金子半之助', desc: 'DiverCity 2F美食街。超人氣排隊天丼，炸蝦與炸半熟蛋必吃。', tag: '超值天丼', icon: '🍤', mapQuery: '日本橋 天丼 金子半之助 ダイバーシティ東京プラザ店' },
                    { name: '串家物語', desc: 'DiverCity 6F。自己動手炸串吃到飽，還有巧克力噴泉。', tag: '炸串吃到飽', icon: '🍡', mapQuery: '串家物語 ダイバーシティ東京プラザ店' },
                    { name: '蘋果樹蛋包飯', desc: 'Aqua City 5F。知名蛋包飯，口味極多小孩超愛。', tag: '蛋包飯', icon: '🍳', mapQuery: 'ポムの樹 アクアシティお台場店' },
                    { name: '燒肉 平城苑', desc: 'Aqua City 1F。看著東京灣美景吃黑毛和牛燒肉。', tag: '景觀燒肉', icon: '🥩', mapQuery: '焼肉 平城苑 アクアシティお台場店' }
                ]
            },
            asakusa: {
                name: '淺草周邊',
                spots: [
                    { name: '淺草寺 雷門', desc: '巨大的紅燈籠是東京象徵，體驗傳統文化。', tag: '傳統文化', icon: '🏮', mapQuery: '雷門' },
                    { name: '仲見世通', desc: '買人形燒、吃仙貝，感受濃濃的江戶風情。', tag: '商店街', icon: '🛍️', mapQuery: '浅草 仲見世商店街' },
                    { name: '藏壽司 淺草ROX店', desc: '全球最大旗艦店！有祭典裝潢、射擊遊戲與巨大扭蛋。', tag: '和食遊樂', icon: '🍣', mapQuery: 'くら寿司 浅草ROX店' },
                    { name: '一蘭拉麵 淺草店', desc: '獨立座位的經典豚骨，小朋友很喜歡這種包廂感。', tag: '經典拉麵', icon: '🍜', mapQuery: '一蘭 浅草店' },
                    { name: '平城苑 淺草雷門店', desc: '雷門旁的高級燒肉店，提供A5和牛。', tag: '和牛燒肉', icon: '🥩', mapQuery: '東京焼肉 平城苑 浅草雷門店' },
                    { name: '淺草今半', desc: '日本最知名的百年壽喜燒老店，和牛入口即化。', tag: '頂級壽喜燒', icon: '🍲', mapQuery: '浅草今半 国際通り本店' },
                    { name: '淺草炸肉餅', desc: '排隊名物，現炸的酥脆肉餅充滿肉汁。', tag: '街邊點心', icon: '🍘', mapQuery: '浅草メンチ' }
                ]
            },
            skytree: {
                name: '晴空塔周邊',
                spots: [
                    { name: '東京晴空塔', desc: '世界最高電波塔，上層有展望台。', tag: '地標', icon: '🗼', mapQuery: '東京スカイツリー' },
                    { name: '寶可夢中心 (4F)', desc: '烈空坐為主題的超大店面，旁邊有寶可夢機台。', tag: '寶可夢', icon: '🐾', mapQuery: 'ポケモンセンタースカイツリータウン' },
                    { name: 'KIRBY CAFÉ', desc: '4F。超可愛星之卡比主題餐點與專賣店。', tag: '主題餐廳', icon: '⭐', mapQuery: 'KIRBY CAFE TOKYO' },
                    { name: '六厘舍', desc: '6F。超人氣「沾麵」名店，粗麵配濃郁魚介豚骨湯。', tag: '排隊沾麵', icon: '🍜', mapQuery: '六厘舎 TOKYO スカイツリータウン・ソラマチ店' },
                    { name: '燒肉 ぴゅあ (Pure)', desc: '11F。農協開設，主打安心安全日本黑毛和牛。', tag: '農協燒肉', icon: '🥩', mapQuery: '焼肉 ぴゅあ 東京スカイツリータウン・ソラマチ店' },
                    { name: '迴轉壽司 根室花丸', desc: '6F。北海道超人氣名店，食材極新鮮需提早抽號。', tag: '排隊壽司', icon: '🍣', mapQuery: '東京スカイツリータウン 回転寿司' },
                    { name: '利久牛舌', desc: '6F。仙台厚切牛舌，有提供兒童咖哩飯套餐。', tag: '炭烤牛舌', icon: '🍱', mapQuery: '牛たん炭焼 利久 東京ソラマチ店' },
                    { name: 'Tabe-Terrace', desc: '3F。美食街選擇豐富且免排隊。', tag: '美食街', icon: '🍽️', mapQuery: '東京ソラマチ タベテラス' }
                ]
            },
            karuizawa: {
                name: '輕井澤周邊',
                spots: [
                    { name: '雲場池', desc: '騎腳踏車抵達，適合帶小朋友觀察鴨群生態。', tag: '自然生態', icon: '🦆', mapQuery: '雲場池' },
                    { name: '王子 Outlet', desc: '除了血拚，內有樂高專賣店與扭蛋機，草地可奔跑。', tag: '購物遊樂', icon: '🛍️', mapQuery: '輕井澤王子購物廣場' },
                    { name: '明治亭', desc: 'Outlet 內。長野名物「醬汁豬排丼」，甜鹹醬汁下飯。', tag: '醬汁豬排', icon: '🍱', mapQuery: '明治亭 輕井澤店' },
                    { name: '濃熟雞白湯 錦', desc: 'Outlet 內。湯頭溫和甘甜的雞白湯拉麵。', tag: '雞白湯拉麵', icon: '🍜', mapQuery: '濃熟鶏白湯 錦 輕井澤' },
                    { name: 'Aging Beef', desc: 'Outlet 內。主打熟成和牛燒肉，肉質柔軟。', tag: '熟成燒肉', icon: '🥩', mapQuery: 'Aging Beef 輕井澤' },
                    { name: 'Snoopy Village', desc: '舊輕井澤。超可愛的史努比茶屋與伴手禮。', tag: '卡通茶屋', icon: '🐶', mapQuery: 'SNOOPY Village 輕井澤' },
                    { name: '川上庵', desc: '舊輕井澤名店。信州蕎麥麵與炸天婦羅。', tag: '蕎麥麵', icon: '🥢', mapQuery: '輕井澤 川上庵 本店' }
                ]
            },
            tsukiji: {
                name: '築地市場',
                spots: [
                    { name: '築地場外市場', desc: '東京的廚房！早上充滿各式現做海鮮小吃與乾貨。', tag: '傳統市場', icon: '🐟', mapQuery: '築地場外市場' },
                    { name: '狐狸屋 牛雜/牛丼', desc: '超濃郁的排隊名店，適合喜歡重口味的爸爸。', tag: '排隊名店', icon: '🥘', mapQuery: 'きつねや 築地' },
                    { name: '築地 山長', desc: '街邊現煎玉子燒，100日圓一串，小孩最愛。', tag: '玉子燒', icon: '🍳', mapQuery: '築地山長' },
                    { name: '築地 可樂餅', desc: '現炸的明太子文字燒可樂餅，極推。', tag: '街邊點心', icon: '🍘', mapQuery: '築地コロッケ' },
                    { name: '黑銀 鮪魚店', desc: '頂級黑鮪魚生魚片與握壽司，立食體驗。', tag: '黑鮪魚', icon: '🍣', mapQuery: '築地黑銀' },
                    { name: '壽司三味 本店', desc: '知名連鎖壽司本店，價格透明、座位寬敞好排。', tag: '平價壽司', icon: '🍣', mapQuery: 'すしざんまい 本店' }
                ]
            },
            shibuya: {
                name: '澀谷周邊',
                spots: [
                    { name: 'SHIBUYA SKY', desc: '目前最熱門的露天展望台，360度無死角美景。', tag: '高空夜景', icon: '🏙️', mapQuery: 'SHIBUYA SKY' },
                    { name: 'Pokémon Center', desc: 'PARCO 6F。最潮的寶可夢中心，門口有1:1沉睡超夢。', tag: '寶可夢', icon: '🐾', mapQuery: 'Pokémon Center Shibuya' },
                    { name: '魚米 (Uobei)', desc: '全由「高速新幹線軌道」直送座位，平價極具娛樂性。', tag: '新幹線壽司', icon: '🍣', mapQuery: '魚べい 渋谷道玄坂店' },
                    { name: '鶴橋風月', desc: 'Scramble Square 12F。大阪燒桌邊現煎，吃飽去展望台最順。', tag: '大阪燒', icon: '🍳', mapQuery: '鶴橋風月 澀谷' },
                    { name: 'AFURI 阿夫利', desc: 'PARCO B1。帶有柚子清香的清爽拉麵，不油膩。', tag: '柚子拉麵', icon: '🍜', mapQuery: 'AFURI 澀谷' },
                    { name: '燒肉 牛角 澀谷店', desc: '平價連鎖燒肉，菜單豐富無壓力，適合親子。', tag: '平價燒肉', icon: '🥩', mapQuery: '牛角 澀谷' },
                    { name: '名代 かつくら', desc: 'Scramble Square 14F。京都知名炸豬排，飯湯可續。', tag: '炸豬排', icon: '🍱', mapQuery: '名代 かつくら 澀谷' }
                ]
            },
            shinjuku: {
                name: '新宿周邊',
                spots: [
                    { name: '新宿 3D 貓', desc: '東口廣場 4K 彎曲螢幕，巨大的三花貓會探頭打招呼。', tag: '科技看板', icon: '🐈', mapQuery: 'Cross Shinjuku Vision' },
                    { name: '歌舞伎町 哥吉拉', desc: '東寶大樓上方的巨大哥吉拉，整點會咆哮發光。', tag: '地標', icon: '🦖', mapQuery: 'Hotel Gracery Shinjuku Godzilla' },
                    { name: '串家物語', desc: '就在哥吉拉樓下！「自己動手炸串吃到飽」+巧克力噴泉。', tag: '炸串吃到飽', icon: '🍤', mapQuery: '串家物語 新宿' },
                    { name: '燒肉亭 六歌仙', desc: '新宿超人氣頂級和牛吃到飽，座位寬敞適合家庭。', tag: '和牛吃到飽', icon: '🥩', mapQuery: '燒肉亭 六歌仙' },
                    { name: '一蘭拉麵', desc: '中央東口店。小朋友最愛的獨立小包廂座位。', tag: '經典拉麵', icon: '🍜', mapQuery: '一蘭 新宿' },
                    { name: '名代 宇奈とと', desc: 'CP值超高的炭烤鰻魚飯，醬汁配飯非常香。', tag: '平價鰻魚飯', icon: '🍱', mapQuery: '名代 宇奈とと 新宿' },
                    { name: '高島屋 Times Square', desc: '12-14F 空間寬敞舒適，豐富和食美食街免排隊。', tag: '百貨美食街', icon: '🍽️', mapQuery: '新宿高島屋' }
                ]
            }
        };

        const itinerary = [
             { day: 1, date: "4/17 (五)", title: "抵達與鈴芽的起點", events: [ 
                 { time: "13:25", title: "抵達成田機場", desc: "T1 (長榮)", icon: "✈️", location: "成田国際空港 第1ターミナル", hideRoute: true, isMovement: true, tips: "抵達 T1 後，先前往 B1 辦理兒童版西瓜卡與領取 Skyliner 車票。",
                   stationGuide: {
                     name: "兒童版交通卡購買", desc: "機場實體卡申辦攻略",
                     tips: ["限 6-12 歲兒童購買 (半價)", "無法綁定手機，需持實體卡", "必須出示小孩本人護照"],
                     routes: ["抵達成田 T1 B1 鐵道樓層後，尋找「JR 東日本旅行服務中心」或藍色的「京成電鐵」櫃檯", "向櫃檯人員表示要購買兒童版 IC 卡 (Child Suica 或 Child PASMO)", "出示小孩的護照供人員核對年齡", "初次購買通常需付 2000 日圓 (含 500 日圓押金，可用額度 1500 日圓)", "進出車站閘門時，嗶卡會發出「小鳥叫聲(嗶嗶兩聲)」，即代表成功使用兒童票價"]
                   }
                 }, 
                 { time: "14:00", title: "往 Skyliner 乘車處", desc: "成田機場 T1 B1", icon: "🚶", location: "成田空港駅", transport: { route: "入境大廳 → B1 京成電鐵", line: "步行", time: "10分" }, isMovement: true }, 
                 { time: "14:30", title: "搭乘 Skyliner", desc: "往京成上野站", icon: "🚅", location: "京成上野駅", transport: { route: "成田機場 → 京成上野", line: "京成 Skyliner", time: "41分" }, isMovement: true }, 
                 { time: "16:00", title: "Check-in", desc: "Stayme Ueno", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "上野 → 飯店", line: "步行", time: "10分" } }, 
                 { time: "17:30", title: "御茶之水 聖橋", desc: "鈴芽場景", icon: "📸", location: "聖橋", transport: { route: "稻荷町 → 御茶之水", line: "地鐵+JR", time: "15分" } }, 
                 { time: "18:30", title: "秋葉原", desc: "逛街", icon: "🛍️", location: "秋葉原駅", transport: { route: "御茶之水 → 秋葉原", line: "步行", time: "10分" } }, 
                 { time: "19:00", title: "秋葉原晚餐", desc: "美食街或拉麵燒肉", icon: "🍛", location: "ヨドバシAkiba", transport: { route: "秋葉原 → 餐廳", line: "步行", time: "5分" }, tips: "💡 推薦在 Yodobashi 吃飽，直攻6F打寶可夢機台！" }, 
                 { time: "21:00", title: "返回飯店", desc: "休息", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "秋葉原 → 飯店", line: "地鐵", time: "20分" }, isMovement: true } 
             ] },
             { day: 2, date: "4/18 (六)", title: "台場鋼彈 & 豐洲", events: [ 
                 { time: "09:00", title: "豐洲市場 / 千客萬來", desc: "參觀/小吃", icon: "🏮", location: "豐洲市場", transport: { route: "稻荷町 → 豐洲", line: "地鐵", time: "30分" } }, 
                 { time: "11:50", title: "台場午餐", desc: "DiverCity 商場", icon: "🍔", location: "DiverCity Tokyo Plaza", tips: "💡 吃飽走到一樓廣場直接看 13:00 的鋼彈表演最順路！" }, 
                 { time: "13:00", title: "獨角獸鋼彈", desc: "變身秀", icon: "🤖", location: "實物大獨角獸鋼彈立像" }, 
                 { time: "17:30", title: "teamLab", desc: "需預約", icon: "✨", location: "teamLab Planets TOKYO", transport: { route: "台場 → 新豐洲", line: "海鷗號", time: "23分" } }, 
                 { time: "19:30", title: "豐洲 LaLaport", desc: "晚餐", icon: "🍽️", location: "ららぽーと豐洲", transport: { route: "新豐洲 → 豐洲", line: "海鷗號", time: "10分" } }, 
                 { time: "21:30", title: "返回飯店", desc: "休息", icon: "🏨", location: HOTEL_ADDRESS, isMovement: true } 
             ] },
             { day: 3, date: "4/19 (日)", title: "淺草與晴空塔", events: [ 
                 { time: "09:00", title: "淺草寺", desc: "雷門", icon: "🏮", location: "雷門", transport: { route: "稻荷町 → 淺草", line: "銀座線", time: "3分" } }, 
                 { time: "12:00", title: "晴空塔午餐", desc: "Solamachi", icon: "🍱", location: "東京晴空街道", transport: { route: "淺草 → 晴空塔", line: "步行", time: "20分" } }, 
                 { time: "13:30", title: "晴空塔寶可夢", desc: "Solamachi 4F", icon: "🛍️", location: "寶可夢中心晴空塔店" }, 
                 { time: "17:30", title: "淺草晚餐", desc: "藏壽司 ROX館", icon: "🍣", location: "藏壽司 淺草ROX店", transport: { route: "押上 → 淺草", line: "地鐵", time: "10分" } }, 
                 { time: "19:30", title: "返回飯店", desc: "回程", icon: "🏨", location: HOTEL_ADDRESS, isMovement: true } 
             ] },
             { day: 4, date: "4/20 (一)", title: "輕井澤一日遊", events: [ 
                 { time: "09:00", title: "上野站新幹線", desc: "搭新幹線", icon: "🚅", location: "上野駅", transport: { route: "飯店 → 上野", line: "步行", time: "10分" }, isMovement: true }, 
                 { time: "10:30", title: "舊輕井澤 & 雲場池", desc: "大自然散步", icon: "🦆", location: "雲場池", transport: { route: "車站 → 景點", line: "單車", time: "15分" } }, 
                 { time: "12:30", title: "輕井澤午餐", desc: "Outlet美食街", icon: "🍱", location: "輕井澤王子購物廣場", transport: { route: "雲場池 → Outlet", line: "單車", time: "10分" } }, 
                 { time: "14:30", title: "王子 Outlet", desc: "購物與樂高區", icon: "🛍️", location: "輕井澤王子購物廣場", tips: "💡 買完戰利品就能直接搭新幹線！" }, 
                 { time: "18:45", title: "上野晚餐", desc: "壽司郎/拉麵", icon: "🍣", location: "壽司郎 上野店", transport: { route: "上野站 → 餐廳", line: "步行", time: "5分" } }, 
                 { time: "20:30", title: "返回飯店", desc: "步行", icon: "🏨", location: HOTEL_ADDRESS, isMovement: true } 
             ] },
             { day: 5, date: "4/21 (二)", title: "築地・澀谷・新宿", events: [ 
                 { time: "09:00", title: "築地場外市場", desc: "早餐", icon: "🐟", location: "築地場外市場", transport: { route: "稻荷町 → 築地", line: "地鐵", time: "20分" } }, 
                 { time: "12:00", title: "澀谷 PARCO", desc: "寶可夢", icon: "🎮", location: "澀谷 PARCO", transport: { route: "築地 → 澀谷", line: "地鐵", time: "25分" } }, 
                 { time: "15:00", title: "SHIBUYA SKY", desc: "需預約", icon: "🏙️", location: "SHIBUYA SKY" }, 
                 { time: "17:30", title: "新宿 3D貓", desc: "東口", icon: "🐈", location: "Cross Shinjuku Vision", transport: { route: "澀谷 → 新宿", line: "JR", time: "7分" } }, 
                 { time: "18:30", title: "新宿晚餐", desc: "串家物語", icon: "🦖", location: "新宿東寶大樓", transport: { route: "東口 → 歌舞伎町", line: "步行", time: "10分" } }, 
                 { time: "20:30", title: "返回飯店", desc: "回程", icon: "🏨", location: HOTEL_ADDRESS, isMovement: true } 
             ] },
             { day: 6, date: "4/22 (三)", title: "返台", events: [ 
                 { time: "10:00", title: "Check-out", desc: "阿美橫丁", icon: "🛍️", location: "阿美橫丁", transport: { route: "飯店 → 阿美橫丁", line: "步行", time: "10分" } }, 
                 { time: "11:20", title: "往機場", desc: "搭 Skyliner", icon: "🚅", location: "京成上野駅", transport: { route: "上野 → 機場", line: "Skyliner", time: "41分" }, isMovement: true }, 
                 { time: "14:25", title: "起飛返台", desc: "長榮 BR197", icon: "✈️", location: "", transport: "", isMovement: true, hideRoute: true } 
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

        const AttractionView = () => {
            // 將 surroundingGuides 轉換為百科列表格式
            const list = Object.values(surroundingGuides);
            
            return (
                <div className="h-full overflow-y-auto p-4 pb-24 space-y-6 bg-gray-50">
                    <div className="text-center mb-6">
                        <h2 className="text-xl font-bold text-gray-800">景點百科</h2>
                        <p className="text-indigo-600 text-sm">各區推薦景點與美食</p>
                    </div>
                    {list.map((area, idx) => (
                        <div key={idx} className="space-y-3">
                            <h3 className="text-lg font-bold text-gray-700 flex items-center">
                                <span className="w-1.5 h-5 bg-indigo-500 mr-2 rounded-full"></span>
                                {area.name}
                            </h3>
                            <div className="space-y-3">
                                {area.spots.map((spot, sIdx) => (
                                    <div key={sIdx} className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm">
                                        <div className="flex items-center gap-3 mb-2">
                                            <div className="text-2xl">{spot.icon}</div>
                                            <div className="flex-1">
                                                <h4 className="font-bold text-gray-800">{spot.name}</h4>
                                                <span className="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded font-bold uppercase">{spot.tag}</span>
                                            </div>
                                            <a href={`http://maps.google.com/?q=${encodeURIComponent(spot.mapQuery)}`} target="_blank" className="text-indigo-500">
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                                            </a>
                                        </div>
                                        <p className="text-sm text-gray-600 leading-relaxed">{spot.desc}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            );
        };

        const ItineraryView = () => {
            const [activeDay, setActiveDay] = useState(0);
            return (
                <div className="flex flex-col h-full bg-gray-50">
                    <div className="sticky top-0 z-10 bg-white shadow-sm">
                        <div className="flex overflow-x-auto hide-scrollbar p-2 gap-2">
                            {itinerary.map((d, i) => (
                                <button key={i} onClick={() => setActiveDay(i)} 
                                    className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${activeDay === i ? 'bg-indigo-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>
                                    Day {d.day}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 pb-24">
                        <div className="text-center mb-4">
                            <h2 className="text-xl font-bold text-gray-800">{itinerary[activeDay].date}</h2>
                            <p className="text-indigo-600 font-medium">{itinerary[activeDay].title}</p>
                        </div>
                        <div className="relative pl-4 space-y-8 border-l-2 border-gray-200 ml-3">
                            {itinerary[activeDay].events.map((evt, i) => {
                                const mapUrl = `http://maps.google.com/?q=${encodeURIComponent(evt.location)}`;
                                const showMap = !evt.isMovement && evt.location;

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

                                            {evt.stationGuide && (
                                                <div className="mb-3 bg-blue-50/60 rounded-xl p-3 border border-blue-100">
                                                    <h4 className="font-bold text-blue-800 mb-1 flex items-center gap-1">🚉 {evt.stationGuide.name}</h4>
                                                    <div className="space-y-1.5 mb-3">
                                                        {evt.stationGuide.tips.map((t, idx) => (
                                                            <div key={idx} className="flex gap-1.5 text-[12px] items-start">
                                                                <span className="bg-blue-500 text-white px-1 rounded text-[9px] mt-0.5">TIP</span>
                                                                <span className="text-gray-700">{t}</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                    <ul className="space-y-1.5 border-t border-blue-200/60 pt-2">
                                                        {evt.stationGuide.routes.map((step, idx) => (
                                                            <li key={idx} className="text-[12px] text-gray-700 flex gap-2">
                                                                <span className="font-bold text-blue-500">{idx + 1}.</span>
                                                                <span>{step}</span>
                                                            </li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                            
                                            {showMap && (
                                                <a href={mapUrl} target="_blank" className="block w-full bg-gray-50 hover:bg-gray-100 text-gray-700 text-xs font-bold py-2 rounded-lg text-center no-underline">📍 查看地圖位置</a>
                                            )}
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

            return (
                <div className="h-full flex flex-col p-4 pb-24 overflow-y-auto">
                    <div className="sticky top-0 z-10 bg-white/95 backdrop-blur shadow-sm p-2 rounded-xl mb-4 overflow-x-auto flex gap-2 flex-shrink-0">
                        <button onClick={() => setMode('attraction')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold ${mode === 'attraction' ? 'bg-indigo-600 text-white' : 'bg-gray-100'}`}>🗺️ 全覽</button>
                        <button onClick={() => setMode('surrounding')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold ${mode === 'surrounding' ? 'bg-teal-600 text-white' : 'bg-gray-100'}`}>🏙️ 景點建議</button>
                        <button onClick={() => setMode('metro')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold ${mode === 'metro' ? 'bg-gray-800 text-white' : 'bg-gray-100'}`}>🚇 路線</button>
                    </div>
                    
                    <div className="flex-1 flex flex-col items-center w-full">
                        {mode === 'attraction' && (
                            <div className="w-full h-[60vh] bg-blue-50 rounded-xl overflow-hidden border border-blue-200 relative">
                                <img ref={tripImgRef} src={URL_TRIP} className="w-full h-auto object-contain" />
                            </div>
                        )}
                        
                        {mode === 'surrounding' && (
                            <div className="w-full flex flex-col items-center">
                                <div className="flex gap-2 mb-3 overflow-x-auto w-full hide-scrollbar">
                                    {Object.keys(surroundingGuides).map(id => (
                                        <button key={id} onClick={() => setSurrArea(id)} className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-bold ${surrArea === id ? 'bg-teal-600 text-white' : 'bg-white border'}`}>{surroundingGuides[id].name}</button>
                                    ))}
                                </div>
                                <div className="w-full space-y-3">
                                    {surroundingGuides[surrArea].spots.map((spot, idx) => (
                                        <div key={idx} className="bg-white border rounded-xl p-3 shadow-sm flex gap-3">
                                            <div className="text-2xl">{spot.icon}</div>
                                            <div>
                                                <h4 className="font-bold text-gray-800 text-sm">{spot.name}</h4>
                                                <p className="text-xs text-gray-500">{spot.desc}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {mode === 'metro' && (
                            <div className="w-full bg-white rounded-xl overflow-hidden shadow-inner border">
                                <img src={URL_NOTE} className="w-full h-auto" />
                            </div>
                        )}
                    </div>
                </div>
            );
        };

        const BookingView = () => (
            <div className="h-full overflow-y-auto p-4 pb-24 space-y-6">
                <div className="text-center mb-4"><h2 className="text-xl font-bold text-gray-800">預約管家</h2></div>
                {reservations.map((cat, i) => (
                    <div key={i}>
                        <h3 className="text-lg font-bold text-gray-700 mb-3 flex items-center"><span className="w-1 h-5 bg-indigo-500 mr-2 rounded-full"></span>{cat.cat}</h3>
                        <div className="space-y-4">
                            {cat.items.map((item, j) => (
                                <div key={j} className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm">
                                    <h4 className="font-bold text-gray-800 mb-2">{item.name}</h4>
                                    <p className="text-xs text-orange-600 bg-orange-50 p-2 rounded mb-3">💡 {item.tips}</p>
                                    <a href={item.url} target="_blank" className="block w-full bg-indigo-600 text-white text-center text-sm font-bold py-2.5 rounded-xl no-underline">前往預約</a>
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
                        <h1 className="text-2xl font-bold">東京親子之旅</h1>
                        <p className="text-indigo-100 text-sm mt-1">4/17 - 4/22 • 6天5夜</p>
                    </div>

                    <div className="flex-1 overflow-hidden relative">
                        {view === 'list' && <ItineraryView />}
                        {view === 'map' && <MapView />}
                        {view === 'attraction' && <AttractionView />}
                        {view === 'booking' && <BookingView />}
                    </div>

                    <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-200 pt-2 pb-8 safe-bottom flex justify-around items-center z-30 shadow-lg">
                        <button onClick={() => setView('list')} className={`flex flex-col items-center gap-1 transition-all ${view === 'list' ? 'text-indigo-600' : 'text-gray-400'}`}>{icons.list}<span className="text-[10px] font-bold">行程</span></button>
                        <button onClick={() => setView('map')} className={`flex flex-col items-center gap-1 transition-all ${view === 'map' ? 'text-indigo-600' : 'text-gray-400'}`}>{icons.map}<span className="text-[10px] font-bold">地圖</span></button>
                        <button onClick={() => setView('attraction')} className={`flex flex-col items-center gap-1 transition-all ${view === 'attraction' ? 'text-indigo-600' : 'text-gray-400'}`}>{icons.attraction}<span className="text-[10px] font-bold">百科</span></button>
                        <button onClick={() => setView('booking')} className={`flex flex-col items-center gap-1 transition-all ${view === 'booking' ? 'text-indigo-600' : 'text-gray-400'}`}>{icons.booking}<span className="text-[10px] font-bold">預約</span></button>
                    </div>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=True)