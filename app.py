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

        // ==========================================
        // ▼▼▼ 圖片路徑 (Github Raw) ▼▼▼
        // ==========================================
        const URL_TRIP = "https://raw.githubusercontent.com/cloudmeowmog/tokyo2026/main/trip.jpg";
        const URL_NOTE = "https://raw.githubusercontent.com/cloudmeowmog/tokyo2026/main/note.jpg";
        const URL_MAP = "https://raw.githubusercontent.com/cloudmeowmog/tokyo2026/main/map.jpg";
        // ==========================================

        const HOTEL_ADDRESS = "Stayme THE HOTEL Ueno, Higashiueno, Taito City, Tokyo";

        // SVG Icons
        const icons = {
            list: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>,
            map: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path></svg>,
            attraction: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>,
            guide: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="16" y2="12"/><line x1="12" x2="12.01" y1="8" y2="8"/></svg>,
            booking: <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
        };

        // 親子周邊景點推薦資料 (含 Google Maps 搜尋關鍵字)
        const surroundingGuides = {
            toyosu: {
                name: '豐洲周邊',
                spots: [
                    { name: '豐洲 LaLaport', desc: '超大型商場！內有 KidZania (兒童職業體驗)，3樓有玩具店、扭蛋機，非常適合放電。', tag: '購物遊樂', icon: '🛍️', mapQuery: 'Urban Dock LaLaport Toyosu' },
                    { name: '茂助玉子燒', desc: '豐洲市場百年老店，甜甜的日式煎蛋捲小孩最愛。', tag: '和食', icon: '🍳', mapQuery: 'Mosuke Tamagoyaki Toyosu Market' },
                    { name: '炸物 八千代', desc: '提供美味的炸海鮮與豬排定食，適合不吃生食的孩子。', tag: '和食', icon: '🍤', mapQuery: 'Tonkatsu Yachiyo Toyosu Market' },
                    { name: '海鮮丼 大江戶', desc: '超豐盛海鮮丼，海鮮種類多，滿足爸媽的胃。', tag: '和食', icon: '🍣', mapQuery: 'Kaisen Don Oedo Toyosu Market' }
                ]
            },
            odaiba: {
                name: '台場周邊',
                spots: [
                    { name: '鋼彈基地 (Gundam Base)', desc: '位於 DiverCity 7F。滿滿的鋼彈模型與限定商品，父子一起買瘋的聖地！', tag: '模型', icon: '🤖', mapQuery: 'THE GUNDAM BASE TOKYO' },
                    { name: 'LEGOLAND 探索中心', desc: '位於 Decks 商場內。室內樂高樂園，超多互動設施與積木池，完全為小孩打造。', tag: '樂高樂園', icon: '🧱', mapQuery: 'LEGOLAND Discovery Center Tokyo' },
                    { name: '台場一丁目商店街', desc: '位於 Decks 4F。充滿復古童玩、零食，還有「一整排的扭蛋機」，便宜又好逛。', tag: '扭蛋童玩', icon: '🍬', mapQuery: 'DECKS Tokyo Beach Odaiba 1-chome Shotengai' }
                ]
            },
            skytree: {
                name: '晴空塔周邊',
                spots: [
                    { name: '寶可夢中心 (Solamachi 4F)', desc: '以烈空坐為主題的超大店面，商品極度齊全，旁邊通常會有寶可夢機台可以玩。', tag: '寶可夢', icon: '🐾', mapQuery: 'Pokemon Center Skytree Town' },
                    { name: 'KIRBY CAFÉ 星之卡比 (4F)', desc: '超可愛主題咖啡廳，門口的專賣店免預約就能買伴手禮。', tag: '主題餐廳', icon: '⭐', mapQuery: 'Kirby Cafe Tokyo' },
                    { name: '迴轉壽司 根室花丸 (6F)', desc: '來自北海道的超人氣排隊名店，食材極度新鮮。', tag: '和食', icon: '🍣', mapQuery: 'Kaitensushi Nemuro Hanamaru Tokyo Skytree Town Solamachi' },
                    { name: '利久牛舌 (6F)', desc: '厚切牛舌名店，有提供兒童咖哩飯套餐。', tag: '和食', icon: '🍱', mapQuery: 'Gyutan Rikyu Tokyo Skytree Town Solamachi' }
                ]
            },
            ueno: {
                name: '上野 / 秋葉原',
                spots: [
                    { name: 'Yodobashi Akiba 8F/6F', desc: '8F有和幸豬排、Meat Rush漢堡排；吃飽到6F有整層玩具與寶可夢機台。', tag: '機台美食', icon: '🕹️', mapQuery: 'Yodobashi Akiba' },
                    { name: 'Yamashiroya 玩具店', desc: 'JR 上野站對面。整整 6 層樓的玩具專賣店，寶可夢周邊極度齊全。', tag: '玩具百貨', icon: '🧸', mapQuery: 'Yamashiroya Ueno' },
                    { name: '壽司郎 上野店', desc: '自動化無壓力點餐，小孩愛吃扭蛋好玩，上野晚餐優質備案。', tag: '和食', icon: '🍣', mapQuery: 'Sushiro Ueno' }
                ]
            },
            karuizawa: {
                name: '輕井澤周邊',
                spots: [
                    { name: '明治亭 (Outlet 內)', desc: '主打長野名物「醬汁豬排丼」，甜鹹醬汁很受小朋友歡迎。', tag: '和食', icon: '🍱', mapQuery: 'Meijitei Karuizawa Prince Shopping Plaza' },
                    { name: '太陽與綠的美食街', desc: 'Outlet 內座位多，提供拉麵、烏龍麵等多種快速餐飲選擇。', tag: '美食街', icon: '🍜', mapQuery: 'Karuizawa Prince Shopping Plaza Food Court' },
                    { name: '舊輕井澤 Snoopy Village', desc: '超可愛的史努比茶屋與伴手禮店，旁邊還有米飛兔森林廚房！', tag: '卡通主題', icon: '🐶', mapQuery: 'Snoopy Village Karuizawa' },
                    { name: '雲場池', desc: '騎腳踏車抵達，適合帶小朋友一起觀察豐富的水岸植物與鴨群生態。', tag: '自然生態', icon: '🦆', mapQuery: 'Kumoba Pond' }
                ]
            },
            shibuya: {
                name: '渋谷周邊',
                spots: [
                    { name: 'Pokémon Center Shibuya', desc: 'PARCO 6F。最潮的寶可夢中心，門口有一隻 1:1 的沉睡超夢。', tag: '寶可夢', icon: '🐾', mapQuery: 'Pokemon Center Shibuya' },
                    { name: '魚米 (Uobei) 道玄坂店', desc: '無迴轉輸送帶，全由「高速新幹線軌道」直送座位，平價且極具娛樂性。', tag: '和食', icon: '🍣', mapQuery: 'Uobei Shibuya Dogenzaka' },
                    { name: '藏壽司 全球旗艦店', desc: '店內有專屬的日本祭典裝潢與超大型扭蛋機，好吃又好拍。', tag: '和食', icon: '🍣', mapQuery: 'Kura Sushi Global Flagship Store Shibuya' },
                    { name: '鶴橋風月 (Scramble Square)', desc: '12F 人氣大阪燒，師傅桌邊現煎，吃飽直接去展望台最順路。', tag: '和食', icon: '🍳', mapQuery: 'Tsuruhashi Fugetsu Shibuya Scramble Square' }
                ]
            },
            shinjuku: {
                name: '新宿周邊',
                spots: [
                    { name: '串家物語 新宿東寶大樓店', desc: '主打「自己動手炸串吃到飽」，還有巧克力噴泉，小孩絕對瘋狂！', tag: '美食DIY', icon: '🍤', mapQuery: 'Kushiya Monogatari Shinjuku Toho Building' },
                    { name: '高島屋 Times Square 美食街', desc: '12-14F 空間寬敞舒適，有精緻的鰻魚飯、天婦羅等料理。', tag: '和食', icon: '🍱', mapQuery: 'Takashimaya Times Square Shinjuku' },
                    { name: '新宿 3D 貓', desc: '東口廣場對面 4K 彎曲螢幕，巨大的三花貓會探頭打招呼。', tag: '科技看板', icon: '🐈', mapQuery: 'Cross Shinjuku Vision' }
                ]
            }
        };

        // 行程資料 (內嵌 tips 飲食建議)
        const itinerary = [
             { day: 1, date: "4/17 (五)", title: "抵達與鈴芽的起點", events: [ 
                 { time: "13:25", title: "抵達成田機場", desc: "T1 (長榮)", icon: "✈️", location: "Narita International Airport Terminal 1", hideRoute: true }, 
                 { time: "14:30", title: "搭 Skyliner", desc: "往上野", icon: "🚅", location: "Keisei Ueno Station", transport: { route: "T1 機場站 → 上野", line: "Skyliner", time: "41分" } }, 
                 { time: "16:00", title: "Check-in", desc: "Stayme Ueno", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "上野 → 飯店", line: "計程車", time: "10分" } }, 
                 { time: "17:15", title: "往稻荷町站", desc: "步行", icon: "🚶", location: "Inaricho Station", transport: { route: "飯店 → 車站", line: "步行", time: "5分" } }, 
                 { time: "17:30", title: "御茶之水 聖橋", desc: "鈴芽場景", icon: "📸", location: "Hijiri-bashi Bridge, Tokyo", transport: { route: "稻荷町 → 御茶之水", line: "銀座線+JR", time: "15分" } }, 
                 { time: "18:30", title: "秋葉原", desc: "逛街", icon: "🛍️", location: "Akihabara Station", transport: { route: "御茶之水 → 秋葉原", line: "步行", time: "10分" } }, 
                 { time: "19:00", title: "Yodobashi 8F", desc: "晚餐美食街", icon: "🍛", location: "Yodobashi Akiba", transport: { route: "秋葉原 → Yodobashi", line: "步行", time: "5分" }, tips: "推薦【和幸豬排】白飯高麗菜可續；【Meat Rush】鐵板漢堡排。吃飽直攻6F打寶可夢機台！" }, 
                 { time: "21:00", title: "返回飯店", desc: "休息", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "秋葉原 → 飯店", line: "JR+步行", time: "20分" } } 
             ] },
             { day: 2, date: "4/18 (六)", title: "台場鋼彈 & 豐洲", events: [ 
                 { time: "08:45", title: "往稻荷町站", desc: "出發", icon: "🚶", location: "Inaricho Station", transport: { route: "飯店 → 車站", line: "步行", time: "5分" } }, 
                 { time: "09:00", title: "豐洲市場", desc: "早午餐", icon: "🍣", location: "Toyosu Market", transport: { route: "稻荷町 → 豐洲", line: "銀座線+有樂町線", time: "30分" }, tips: "和食推薦【茂助玉子燒】甜煎蛋捲；【八千代】炸物定食；【大江戶】海鮮丼(皆在水產棟3F)。" }, 
                 { time: "11:30", title: "往台場", desc: "海鷗號", icon: "🚅", location: "Daiba Station", transport: { route: "豐洲 → 台場", line: "海鷗號", time: "20分" } }, 
                 { time: "13:00", title: "獨角獸鋼彈", desc: "變身秀", icon: "🤖", location: "Unicorn Gundam Statue" }, 
                 { time: "17:30", title: "teamLab", desc: "需預約", icon: "✨", location: "teamLab Planets TOKYO", transport: { route: "台場 → 新豐洲", line: "海鷗號", time: "23分" } }, 
                 { time: "19:30", title: "豐洲 LaLaport", desc: "晚餐", icon: "🍽️", location: "Urban Dock LaLaport Toyosu", transport: { route: "新豐洲 → 豐洲", line: "海鷗號/步行", time: "10分" } }, 
                 { time: "21:30", title: "返回飯店", desc: "休息", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "豐洲 → 稻荷町", line: "有樂町線+銀座線", time: "30分" } } 
             ] },
             { day: 3, date: "4/19 (日)", title: "淺草與晴空塔", events: [ 
                 { time: "08:45", title: "往稻荷町站", desc: "出發", icon: "🚶", location: "Inaricho Station", transport: { route: "飯店 → 車站", line: "步行", time: "5分" } }, 
                 { time: "09:00", title: "淺草寺", desc: "雷門", icon: "🏮", location: "Senso-ji", transport: { route: "稻荷町 → 淺草", line: "銀座線", time: "3分" } }, 
                 { time: "11:00", title: "隅田川步道", desc: "散步", icon: "🚶", location: "Sumida River Walk", transport: { route: "淺草 → 晴空塔", line: "步行", time: "20分" } }, 
                 { time: "12:30", title: "晴空塔寶可夢", desc: "Solamachi 4F", icon: "🛍️", location: "Pokemon Center Skytree Town" }, 
                 { time: "17:00", title: "晴空塔晚餐", desc: "Solamachi 6F/3F", icon: "🍱", location: "Tokyo Skytree Town Solamachi", tips: "推薦【利久牛舌】有兒童咖哩；【根室花丸】超人氣壽司(需提早抽號碼牌)；【3F美食街】選擇多免排隊。" }, 
                 { time: "19:00", title: "返回飯店", desc: "回程", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "押上 → 稻荷町", line: "淺草線+銀座線", time: "20分" } } 
             ] },
             { day: 4, date: "4/20 (一)", title: "輕井澤一日遊", events: [ 
                 { time: "09:00", title: "往上野站", desc: "搭新幹線", icon: "🚶", location: "Ueno Station", transport: { route: "飯店 → 上野", line: "步行", time: "10分" } }, 
                 { time: "10:10", title: "抵達輕井澤", desc: "Outlet", icon: "🛍️", location: "Karuizawa Prince Shopping Plaza", transport: { route: "上野 → 輕井澤", line: "新幹線", time: "60分" } }, 
                 { time: "12:30", title: "輕井澤午餐", desc: "明治亭/美食街", icon: "🍱", location: "Karuizawa Prince Shopping Plaza Food Court", transport: { route: "Outlet 內", line: "步行", time: "5分" }, tips: "推薦【明治亭】長野名物醬汁豬排丼；或直接到【太陽與綠的美食街】有各式拉麵與烏龍麵。" }, 
                 { time: "14:00", title: "舊輕井澤", desc: "騎車", icon: "🚲", location: "Kyu-Karuizawa Ginza Street", transport: { route: "車站 → 舊輕井澤", line: "巴士/單車", time: "15分" } }, 
                 { time: "17:30", title: "返回上野", desc: "回程", icon: "🚅", location: "Ueno Station", transport: { route: "輕井澤 → 上野", line: "新幹線", time: "60分" } }, 
                 { time: "18:45", title: "壽司郎", desc: "上野分店", icon: "🍣", location: "Sushiro Ueno", transport: { route: "上野站 → 壽司郎", line: "步行", time: "5分" }, tips: "回程新幹線上可先開 App 抽號碼牌，減少現場排隊時間。" }, 
                 { time: "20:30", title: "返回飯店", desc: "步行", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "上野 → 飯店", line: "步行", time: "10分" } } 
             ] },
             { day: 5, date: "4/21 (二)", title: "築地・渋谷・新宿", events: [ 
                 { time: "08:40", title: "往稻荷町站", desc: "出發", icon: "🚶", location: "Inaricho Station", transport: { route: "飯店 → 車站", line: "步行", time: "5分" } }, 
                 { time: "09:00", title: "築地場外市場", desc: "早餐", icon: "🐟", location: "Tsukiji Outer Market", transport: { route: "稻荷町 → 築地", line: "銀座線+日比谷線", time: "20分" } }, 
                 { time: "12:00", title: "渋谷 PARCO", desc: "寶可夢", icon: "🎮", location: "Shibuya PARCO", transport: { route: "築地 → 渋谷", line: "日比谷線+銀座線", time: "25分" } }, 
                 { time: "13:30", title: "澀谷午餐", desc: "魚米/藏壽司/美食街", icon: "🍽️", location: "Shibuya Scramble Square", transport: { route: "PARCO → 餐廳", line: "步行", time: "10分" }, tips: "推薦【魚米】新幹線送餐小孩超愛；【藏壽司】大型扭蛋；或直接到展望台樓下的【Scramble Square】吃大阪燒。" }, 
                 { time: "15:00", title: "SHIBUYA SKY", desc: "需預約", icon: "🏙️", location: "SHIBUYA SKY", transport: { route: "餐廳 → 展望台", line: "步行/電梯", time: "5-10分" } }, 
                 { time: "17:30", title: "新宿 3D貓", desc: "東口", icon: "🐈", location: "Cross Shinjuku Vision", transport: { route: "渋谷 → 新宿", line: "山手線", time: "7分" } }, 
                 { time: "18:30", title: "哥吉拉 & 晚餐", desc: "串家物語 等", icon: "🦖", location: "Shinjuku Toho Building", transport: { route: "東口 → 歌舞伎町", line: "步行", time: "10分" }, tips: "推薦【串家物語】(哥吉拉大樓內) 體驗自己炸串+巧克力噴泉；或【高島屋美食街】舒適吃和食。" }, 
                 { time: "20:30", title: "返回飯店", desc: "回程", icon: "🏨", location: HOTEL_ADDRESS, transport: { route: "新宿 → 稻荷町", line: "中央線+銀座線", time: "30分" } } 
             ] },
             { day: 6, date: "4/22 (三)", title: "返台", events: [ 
                 { time: "10:00", title: "Check-out", desc: "阿美橫丁", icon: "🛍️", location: "Ameyoko Shopping Street", transport: { route: "飯店 → 阿美橫丁", line: "步行", time: "10分" } }, 
                 { time: "11:20", title: "往機場", desc: "搭 Skyliner", icon: "🚅", location: "Keisei Ueno Station", transport: { route: "京成上野 → 成田T1", line: "Skyliner", time: "41分" } }, 
                 { time: "12:25", title: "抵達機場", desc: "成田 T1 (南翼)", icon: "✈️", location: "Narita Airport Terminal 1" }, 
                 { time: "14:25", title: "起飛返台", desc: "長榮 BR197", icon: "✈️", location: "", transport: "" } 
             ] }
        ];

        const stationGuides = [
            { 
                id: "child_ic", name: "兒童版交通卡購買", desc: "機場實體卡申辦攻略", 
                tips: ["限 6-12 歲兒童購買 (半價)", "無法綁定手機，需持實體卡", "必須出示小孩本人護照"], 
                routes: [
                    "抵達成田 T1 B1 鐵道樓層後，尋找「JR 東日本旅行服務中心」或藍色的「京成電鐵」櫃檯",
                    "向櫃檯人員表示要購買兒童版 IC 卡 (Child Suica 或 Child PASMO)",
                    "出示小孩的護照供人員核對年齡",
                    "初次購買通常需付 2000 日圓 (含 500 日圓押金，可用額度 1500 日圓)",
                    "進出車站閘門時，嗶卡會發出「小鳥叫聲(嗶嗶兩聲)」，即代表成功使用兒童票價"
                ],
                links: [
                    { title: "Suica 官網說明", url: "https://www.jreast.co.jp/multi/zh-CHT/pass/suica.html" },
                    { title: "PASMO 兒童卡說明", url: "https://www.pasmo.co.jp/visitors/tc/buy/" }
                ] 
            },
            { 
                id: "narita", name: "成田機場 T1", desc: "Skyliner 起點站", 
                tips: ["長榮位於南翼 (South Wing)", "Skyliner 全車對號座"], 
                routes: [
                    "入境大廳位於 1F，領完行李後尋找「鐵道」指標",
                    "搭乘手扶梯下樓至 B1",
                    "尋找藍色櫃台「KEISEI (京成電鐵)」購票",
                    "通過橘色剪票口，前往 4 或 5 號月台",
                    "上車後行李放置於車廂前後的行李架"
                ],
                links: [{ title: "T1 樓層圖 (官網)", url: "https://www.narita-airport.jp/ch2/map/?terminal=1&map=1" }] 
            },
            { 
                id: "ueno_keisei", name: "京成上野站", desc: "轉乘與計程車", 
                tips: ["抵達時在地下月台", "行李多強烈建議搭計程車"], 
                routes: [
                    "下車後搭手扶梯往上，尋找「正面口」出口",
                    "出改札口後直走，不要往地鐵連絡通道走",
                    "出站到地面，右手邊即是計程車招呼站",
                    "出示飯店地址給司機 (車程約 5-10 分)"
                ],
                links: [{ title: "京成上野構內圖", url: "https://www.keisei.co.jp/keisei/tetudou/stationmap/pdf/us/101.pdf" }] 
            },
            { 
                id: "ueno_jr", name: "JR 上野站", desc: "搭乘新幹線", 
                tips: ["新幹線入口在站內深處", "必走「中央改札」"], 
                routes: [
                    "從地面進入 JR 上野站，請認明最大的「中央改札」",
                    "進站後抬頭看綠色新幹線標示，直走約 3 分鐘",
                    "通過第二道「新幹線專用改札」",
                    "搭乘手扶梯向下至 B3/B4 月台 (通常往輕井澤在 19/20 月台)"
                ],
                links: [{ title: "JR 構內圖", url: "https://www.jreast.co.jp/estation/stations/204.html" }] 
            },
            { 
                id: "shibuya", name: "渋谷站", desc: "銀座線動線", 
                tips: ["銀座線抵達時在 3F", "SHIBUYA SKY 直結"], 
                routes: [
                    "銀座線下車後位於 3F，跟隨 Scramble Square 指標",
                    "SHIBUYA SKY 入口位於該棟大樓 14F (需搭專用電梯)",
                    "若要看八公/過馬路：從 3F 搭很長的手扶梯下到 1F 廣場",
                    "避開地下迷宮，盡量走地面或天橋"
                ],
                links: [{ title: "立體圖", url: "https://www.tokyometro.jp/station/shibuya/index.html" }] 
            },
            { 
                id: "shinjuku", name: "新宿站", desc: "東口攻略", 
                tips: ["3D 貓在東口", "歌舞伎町在東口"], 
                routes: [
                    "下車後請務必尋找黃色招牌「東改札 (East Exit)」",
                    "出站後到達地面，會看到一個大廣場",
                    "3D 貓：往左前方看，大樓頂端的彎曲螢幕即是",
                    "哥吉拉：沿著東口街道往「歌舞伎町」牌樓走，抬頭看電影院大樓"
                ],
                links: [{ title: "JR 新宿構內圖", url: "https://www.jreast.co.jp/estation/stations/866.html" }] 
            }
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
                    { name: "東京晴空塔", url: "https://www.tokyo-skytree.jp/cn_t/ticket/", tips: "Day 3 (12:30)，30天前開放預約" }, 
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

        // 依時序 Day 1 -> Day 5 排序
        const attractionInfos = [
            // --- Day 1 ---
            { id: "hijiri", name: "御茶之水 聖橋", icon: "🌉", tag: "聖地巡禮", desc: "電影《鈴芽之旅》經典場景。站在橋上可以同時看到紅、黃、橘三色電車交錯而過，是鐵道迷與影迷必拍聖地。", tips: "下午前往順光，拍攝效果最好。" },
            { id: "akiba", name: "秋葉原 Electric Town", icon: "⚡", tag: "動漫/電器", desc: "日本次文化中心。滿街的動漫周邊、模型店、女僕咖啡廳與大型電器行。Yodobashi Akiba 是必逛地標。", tips: "旁邊的 Yodobashi 是吃喝玩樂一站式滿足的好地方！" },
            { id: "akiba_food", name: "秋葉原親子晚餐", icon: "🍛", tag: "美食", desc: "推薦：【Yodobashi Akiba 8F 美食街】。包含：【和幸豬排】白飯高麗菜可免費續加；【Meat Rush】鐵板漢堡排與牛排。商場環境寬敞，對推車與小孩非常友善！", tips: "吃飽後直接下樓到 6 樓玩具專區，有滿滿的寶可夢 Frienda 機台與扭蛋海可以讓小朋友玩樂！" },
            
            // --- Day 2 ---
            { id: "toyosu", name: "豐洲市場 (和食推薦)", icon: "🍣", tag: "海鮮/和食", desc: "東京最新海鮮廚房。推薦和食：【茂助玉子燒】甜甜的日式煎蛋捲小孩最愛；【八千代】炸海鮮與豬排定食，適合不吃生食的孩子；【大江戶】超豐盛海鮮丼，滿足爸媽的胃。", tips: "餐廳多集中在「水產仲卸賣場棟 3F」，建議避開排隊名店（如壽司大），選擇有提供熟食定食的店家。" },
            { id: "odaiba", name: "台場 獨角獸鋼彈", icon: "🤖", tag: "鋼彈", desc: "位於 DiverCity 廣場前。白天有 4 場變身秀(獨角獸模式->毀滅模式)，晚上有燈光秀。", tips: "變身時間：11:00, 13:00, 15:00, 17:00。" },
            { id: "teamlab", name: "teamLab Planets", icon: "✨", tag: "沉浸式藝術", desc: "需赤腳進入的水中美術館。光影與水面的結合非常夢幻，適合大人小孩互動。", tips: "建議穿著短褲或易捲起的褲子(水深及膝)。" },
            
            // --- Day 3 ---
            { id: "sensoji", name: "淺草寺 & 雷門", icon: "🏮", tag: "傳統文化", desc: "東京最古老的寺廟。巨大的紅燈籠「雷門」是東京象徵。仲見世通有許多人形燒、仙貝等傳統小吃。", tips: "遊客非常多，建議早上9點前抵達拍照。" },
            { id: "skytree", name: "東京晴空塔", icon: "🗼", tag: "地標/寶可夢", desc: "世界最高電波塔。樓下 Solamachi 商場有寶可夢中心(烈空坐鎮店)與 Kirby Cafe。", tips: "4F 戶外露台是拍攝晴空塔全貌的好位置。" },
            { id: "skytree_food", name: "晴空塔親子餐飲", icon: "🍽️", tag: "美食", desc: "推薦：【3F Tabe-Terrace 美食街】選擇多免排隊，有章魚燒與各式麵食；【6F 迴轉壽司 根室花丸】來自北海道的超人氣壽司，記得先抽號碼牌；【6F 利久牛舌】厚切牛舌名店，有提供兒童咖哩飯；【4F 星之卡比咖啡廳】餐點極度可愛，就在寶可夢中心旁。", tips: "晴空塔餐廳每到用餐時間人潮眾多，若想吃名店建議 11:30 前先去抽號碼牌，或善用 3F 美食街。" },
            
            // --- Day 4 ---
            { id: "karuizawa", name: "輕井澤", icon: "🚲", tag: "度假勝地", desc: "避暑勝地，充滿歐風建築與森林。車站旁就是超大 Outlet，舊輕井澤銀座通適合騎車漫遊。", tips: "一定要吃 Sawaya 果醬與 Mikado 摩卡霜淇淋。" },
            { id: "karuizawa_food", name: "輕井澤親子午餐", icon: "🍱", tag: "美食", desc: "推薦：【明治亭】位於 Outlet 內，主打長野名物「醬汁豬排丼」，份量足且小孩接受度高；或直接到【太陽與綠的美食街】(Food Court)，座位多且選擇豐富（拉麵、烏龍麵等和食都有）。", tips: "Outlet 餐廳假日容易客滿，建議 11:30 前就先入座用餐！" },
            
            // --- Day 5 ---
            { id: "shibuya_food", name: "澀谷親子午餐", icon: "🍽️", tag: "美食", desc: "推薦：【魚米 Uobei】平價且用新幹線軌道送餐，小孩超愛；【藏壽司 澀谷全球旗艦店】有獨家扭蛋與祭典裝潢；【Scramble Square 12/13F】在 SHIBUYA SKY 樓下，吃飽直接上樓最順路，有鶴橋風月大阪燒、Katsukura豬排。", tips: "澀谷平日上班族也多，建議在 11:30 前或 13:30 後用餐避開人潮。" },
            { id: "shibuya", name: "SHIBUYA SKY", icon: "🏙️", tag: "高空夜景", desc: "目前東京最熱門的露天展望台，360度無死角美景。角落的玻璃扶手是網美必拍點。", tips: "日落時段最美，但需提早一個月搶票。" },
            { id: "shinjuku", name: "新宿 3D 貓", icon: "🐈", tag: "科技看板", desc: "新宿東口廣場對面大樓的 4K 彎曲螢幕。巨大的三花貓會探頭打招呼，非常逼真可愛。", tips: "每 15 分鐘會有一次特殊演出。" },
            { id: "shinjuku_food", name: "新宿親子晚餐", icon: "🍤", tag: "美食", desc: "推薦：【串家物語 新宿東寶大樓店】就在哥吉拉頭像那棟！主打「自己動手炸串吃到飽」，還有巧克力噴泉，充滿DIY樂趣，小孩絕對瘋狂；若想吃安靜的和食，推薦【高島屋 Times Square 12-14F 美食街】（名代宇奈とと鰻魚飯、天婦羅等）。", tips: "哥吉拉頭像每整點會咆哮發光，帶小朋友吃串家物語剛好可以就近觀賞！" }
        ];

        // --- View Components ---
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
                                let prevLoc = i === 0 ? HOTEL_ADDRESS : itinerary[activeDay].events[i-1].location;
                                if (activeDay === 0 && i < 2) prevLoc = null; 
                                const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(evt.location)}`;
                                const dirUrl = prevLoc ? `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(evt.location)}&origin=${encodeURIComponent(prevLoc)}&travelmode=transit` : null;

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
                                            
                                            {/* 新增：在行程表直接顯示飲食 Tips */}
                                            {evt.tips && (
                                                <div className="mb-3 bg-yellow-50 text-yellow-800 text-[13px] p-2.5 rounded-lg border border-yellow-100 leading-relaxed">
                                                    <span className="font-bold">💡 美食推薦：</span>{evt.tips}
                                                </div>
                                            )}

                                            {evt.transport && (
                                                <div className="mb-3 bg-gray-50 p-2 rounded text-xs text-gray-600 flex items-center gap-2">
                                                    <span>🚇 {evt.transport.route}</span>
                                                    <span className="text-gray-400">|</span>
                                                    <span>{evt.transport.time}</span>
                                                </div>
                                            )}
                                            <div className="flex gap-2">
                                                <a href={mapUrl} target="_blank" className="flex-1 bg-gray-50 hover:bg-gray-100 text-gray-700 text-xs font-bold py-2 rounded-lg text-center no-underline">📍 地圖</a>
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
            const [surrArea, setSurrArea] = useState('toyosu');
            const imgRef = useRef(null);

            useEffect(() => {
                if (mode === 'full' && imgRef.current) {
                    const pz = Panzoom(imgRef.current, {
                        maxScale: 8,     
                        minScale: 1,     
                        contain: null,   
                        startScale: 1
                    });
                    
                    if(imgRef.current.parentElement) {
                        imgRef.current.parentElement.addEventListener('wheel', pz.zoomWithWheel);
                    }
                }
            }, [mode]);

            // 渲染取代原本 SVG 的親子景點卡片，並加入 Google Maps 動態連結
            const renderSurrounding = () => {
                const guide = surroundingGuides[surrArea];
                if (!guide) return null;

                return (
                    <div className="w-full flex flex-col gap-3 p-2">
                        {guide.spots.map((spot, idx) => {
                            const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(spot.mapQuery)}`;
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
                <div className="h-full flex flex-col p-4 pb-24 overflow-y-auto">
                    <div className="sticky top-0 z-10 bg-white/95 backdrop-blur shadow-sm p-2 rounded-xl mb-4 overflow-x-auto flex gap-2 flex-shrink-0">
                         <button onClick={() => setMode('attraction')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${mode === 'attraction' ? 'bg-indigo-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🗺️ 全覽</button>
                        <button onClick={() => setMode('surrounding')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${mode === 'surrounding' ? 'bg-teal-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🏙️ 景點建議</button>
                        <button onClick={() => setMode('metro')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${mode === 'metro' ? 'bg-gray-800 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>🚇 路線</button>
                        <button onClick={() => setMode('full')} className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${mode === 'full' ? 'bg-orange-600 text-white shadow scale-105' : 'bg-gray-100 text-gray-500'}`}>📑 完整地鐵</button>
                    </div>
                    
                    <div className="flex-1 flex flex-col items-center w-full">
                        
                        {mode === 'attraction' && (
                            <div className="w-full max-w-sm bg-blue-50 rounded-xl overflow-hidden shadow-inner border-2 border-blue-100 p-0">
                                <img src={URL_TRIP} alt="行程全覽地圖" className="w-full h-auto" />
                            </div>
                        )}
                        
                        {mode === 'surrounding' && (
                            <div className="w-full flex flex-col items-center">
                                <div className="flex gap-2 mb-3 overflow-x-auto w-full justify-start flex-shrink-0 hide-scrollbar px-1 py-1">
                                    {[
                                        {id: 'toyosu', name: '豐洲'}, 
                                        {id: 'odaiba', name: '台場'}, 
                                        {id: 'skytree', name: '晴空塔'},
                                        {id: 'ueno', name: '上野/秋葉原'},
                                        {id: 'karuizawa', name: '輕井澤'},
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
            );
        };

        const StationView = () => (
            <div className="h-full overflow-y-auto p-4 pb-24 space-y-4">
                <div className="text-center mb-6"><h2 className="text-xl font-bold text-gray-800">車站攻略</h2><p className="text-indigo-600 text-sm">迷路救星</p></div>
                {stationGuides.map(s => (
                    <div key={s.id} className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
                        <h3 className="font-bold text-lg text-gray-800 flex items-center gap-2"><span className="w-2 h-6 bg-indigo-500 rounded-full"></span>{s.name}</h3>
                        <p className="text-sm text-gray-500 mb-4 ml-4">{s.desc}</p>
                        <div className="space-y-2 mb-4">
                            {s.tips.map((t, idx) => (
                                <div key={idx} className="flex gap-2 bg-gray-50 p-2 rounded-lg text-sm items-center">
                                    <span className="bg-white text-indigo-600 border border-indigo-100 text-xs font-bold px-2 py-0.5 rounded">Tip</span>
                                    <span className="text-gray-700">{t}</span>
                                </div>
                            ))}
                        </div>
                        {s.routes && (
                            <div className="mb-4 bg-indigo-50/50 rounded-xl p-3 border border-indigo-100">
                                <h4 className="text-xs font-bold text-indigo-800 mb-2 flex items-center gap-1">🚏 導航路徑</h4>
                                <ul className="relative space-y-3">
                                    {s.routes.map((step, idx) => (
                                        <li key={idx} className="text-sm text-gray-700 flex gap-3 relative pl-2">
                                            {idx !== s.routes.length - 1 && <div className="absolute left-[9px] top-5 bottom-[-12px] w-0.5 bg-indigo-200"></div>}
                                            <div className="flex-shrink-0 w-4 h-4 rounded-full bg-indigo-500 text-white text-[10px] flex items-center justify-center font-bold mt-0.5">{idx + 1}</div>
                                            <span className="leading-snug">{step}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        <div className="flex flex-wrap gap-2">{s.links.map((l, idx) => <a key={idx} href={l.url} target="_blank" className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-1 rounded-full font-bold no-underline transition-colors">🔗 {l.title}</a>)}</div>
                    </div>
                ))}
            </div>
        );
        
        const AttractionView = () => (
             <div className="h-full overflow-y-auto p-4 pb-24 space-y-4">
                <div className="text-center mb-6"><h2 className="text-xl font-bold text-gray-800">景點百科</h2><p className="text-indigo-600 text-sm">依行程順序排列</p></div>
                {attractionInfos.map((item, idx) => (
                    <div key={idx} className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm flex flex-col gap-2">
                        <div className="flex items-center gap-3">
                             <div className="text-3xl">{item.icon}</div>
                             <div>
                                 <h3 className="font-bold text-gray-800">{item.name}</h3>
                                 <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">{item.tag}</span>
                             </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-2">{item.desc}</p>
                        <div className="bg-yellow-50 text-yellow-800 text-xs p-2 rounded mt-1">💡 {item.tips}</div>
                    </div>
                ))}
             </div>
        );

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
                        <a href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(HOTEL_ADDRESS)}`} target="_blank" className="mt-4 bg-indigo-700/50 p-3 rounded-xl flex items-center gap-3 backdrop-blur-sm active:scale-95 transition-transform border border-indigo-500/30 text-left no-underline">
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
                        {view === 'guide' && <StationView />}
                        {view === 'booking' && <BookingView />}
                    </div>

                    <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-1 pt-2 pb-8 safe-bottom flex justify-around items-center z-30 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
                        <button onClick={() => setView('list')} className={`flex flex-col items-center gap-1 p-1 rounded-xl min-w-[55px] transition-all ${view === 'list' ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400'}`}>{icons.list}<span className="text-[10px] font-bold">行程</span></button>
                        <button onClick={() => setView('map')} className={`flex flex-col items-center gap-1 p-1 rounded-xl min-w-[55px] transition-all ${view === 'map' ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400'}`}>{icons.map}<span className="text-[10px] font-bold">地圖</span></button>
                        <button onClick={() => setView('attraction')} className={`flex flex-col items-center gap-1 p-1 rounded-xl min-w-[55px] transition-all ${view === 'attraction' ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400'}`}>{icons.attraction}<span className="text-[10px] font-bold">百科</span></button>
                        <button onClick={() => setView('guide')} className={`flex flex-col items-center gap-1 p-1 rounded-xl min-w-[55px] transition-all ${view === 'guide' ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400'}`}>{icons.guide}<span className="text-[10px] font-bold">車站</span></button>
                        <button onClick={() => setView('booking')} className={`flex flex-col items-center gap-1 p-1 rounded-xl min-w-[55px] transition-all ${view === 'booking' ? 'text-indigo-600 bg-indigo-50' : 'text-gray-400'}`}>{icons.booking}<span className="text-[10px] font-bold">預約</span></button>
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
components.html(html_code, height=800, scrolling=True)