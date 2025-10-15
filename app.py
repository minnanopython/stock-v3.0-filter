import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from datetime import timedelta, date
import pprint
import re # マルチセレクトの表示名からティッカーを抽出するために追加

# --- 銘柄・セクター定義（変更なし） ---
SECTORS = {
    "資源": {
        '5020.T': '5020 ＥＮＥＯＳ',
        '5019.T': '5019 出光興産',
        '5021.T': '5021 コスモエネルギー',
        '1605.T': '1605 ＩＮＰＥＸ',
        '1662.T': '1662 石油資源開発',
        '8031.T': '8031 三井物産',
        '8058.T': '8058 三菱商事',
        '8001.T': '8001 伊藤忠商事',
        '8002.T': '8002 丸紅',
        '8053.T': '8053 住友商事',
        '8015.T': '8015 豊田通商',
        '2768.T': '2768 双日'
    },
    "規模1": {
        '9984.T': '9984 ソフトバンク',
        '8411.T': '8411 みずほ',
        '7203.T': '7203 トヨタ自動車',
        '8306.T': '8306 三菱ＵＦＪ',
        '8316.T': '8316 三井住友',
        '6758.T': '6758 ソニー',
        '8766.T': '8766 東京海上',
        '7011.T': '7011 三菱重工業',
        '9432.T': '9432 ＮＴＴ',
        '6098.T': '6098 リクルート',
        '6861.T': '6861 キーエンス',
        '6501.T': '6501 日立製作所',
        '7974.T': '7974 任天堂',
        '4063.T': '4063 信越化学工業',
        '7267.T': '7267 本田技研工業',
        '7741.T': '7741 ＨＯＹＡ',
        '6857.T': '6857 アドバンテスト',
        '9434.T': '9434 ソフトバンク',
        '6503.T': '6503 三菱電機',
        '9433.T': '9433 ＫＤＤＩ',
        '6702.T': '6702 富士通',
        '9983.T': '9983 ファーストリテイリング',
        '4568.T': '4568 第一三共',
        '6701.T': '6701 日本電気',
        '8035.T': '8035 東京エレクトロン',
        '2914.T': '2914 日本たばこ産業',
        '6301.T': '6301 小松製作所',
        '8725.T': '8725 ＭＳ＆ＡＤ',
        '6367.T': '6367 ダイキン工業',
        '3382.T': '3382 セブン＆アイ・',
        '8750.T': '8750 第一生命',
        '8591.T': '8591 オリックス',
        '8630.T': '8630 ＳＯＭＰＯ',
        '6981.T': '6981 村田製作所',
        '4661.T': '4661 オリエンタルランド',
        '8801.T': '8801 三井不動産',
        '4901.T': '4901 富士フイルム',
        '6902.T': '6902 デンソー',
        '4519.T': '4519 中外製薬',
        '6146.T': '6146 ディスコ',
        '6954.T': '6954 ファナック',
        '5108.T': '5108 ブリヂストン',
        '7751.T': '7751 キヤノン',
        '2802.T': '2802 味の素',
        '6752.T': '6752 パナソニック',
        '8308.T': '8308 りそな',
        '8802.T': '8802 三菱地所',
        '4543.T': '4543 テルモ',
        '8604.T': '8604 野村',
        '4578.T': '4578 大塚',
        '6723.T': '6723 ルネサス',
        '6762.T': '6762 ＴＤＫ',
        '4452.T': '4452 花王',
        '5401.T': '5401 日本製鉄',
        '7269.T': '7269 スズキ',
        '1925.T': '1925 大和ハウス工業',
        '7936.T': '7936 アシックス',
        '9022.T': '9022 東海旅客鉄道',
        '5802.T': '5802 住友電気工業',
        '8309.T': '8309 三井住友トラスト'
    },
    "規模2": {
        '4503.T': '4503 アステラス製薬',
        '5803.T': '5803 フジクラ',
        '6201.T': '6201 豊田自動織機',
        '2502.T': '2502 アサヒ',
        '7832.T': '7832 バンダイナムコ',
        '6273.T': '6273 ＳＭＣ',
        '4307.T': '4307 野村総合研究所',
        '7013.T': '7013 ＩＨＩ',
        '7532.T': '7532 パン・パシフィック・インターナショナル',
        '9735.T': '9735 セコム',
        '8473.T': '8473 ＳＢＩ',
        '6988.T': '6988 日東電工',
        '9101.T': '9101 日本郵船',
        '9531.T': '9531 東京瓦斯',
        '9503.T': '9503 関西電力',
        '1928.T': '1928 積水ハウス',
        '8830.T': '8830 住友不動産',
        '4684.T': '4684 オービック',
        '1812.T': '1812 鹿島建設',
        '7733.T': '7733 オリンパス',
        '8697.T': '8697 日本取引所',
        '9104.T': '9104 商船三井',
        '1801.T': '1801 大成建設',
        '6326.T': '6326 クボタ',
        '7270.T': '7270 ＳＵＢＡＲＵ',
        '2503.T': '2503 キリン',
        '4507.T': '4507 塩野義製薬',
        '9766.T': '9766 コナミ',
        '3659.T': '3659 ネクソン',
        '9021.T': '9021 西日本旅客鉄道',
        '9532.T': '9532 大阪瓦斯',
        '8601.T': '8601 大和証券本社',
        '9202.T': '9202 ＡＮＡ',
        '6383.T': '6383 ダイフク',
        '9697.T': '9697 カプコン',
        '1802.T': '1802 大林組',
        '9502.T': '9502 中部電力',
        '7453.T': '7453 良品計画',
        '4689.T': '4689 ＬＩＮＥヤフー',
        '3402.T': '3402 東レ',
        '9201.T': '9201 日本航空',
        '7309.T': '7309 シマノ',
        '7012.T': '7012 川崎重工業',
        '8136.T': '8136 サンリオ',
        '6361.T': '6361 荏原製作所',
        '6532.T': '6532 ベイカレント',
        '6586.T': '6586 マキタ',
        '4188.T': '4188 三菱ケミカル',
        '8113.T': '8113 ユニ・チャーム',
        '6920.T': '6920 レーザーテック',
        '8593.T': '8593 三菱ＨＣキャピタル',
        '4523.T': '4523 エーザイ',
        '9024.T': '9024 西武',
        '6504.T': '6504 富士電機',
        '7186.T': '7186 コンコルディア',
        '5411.T': '5411 ＪＦＥ',
        '7202.T': '7202 いすゞ自動車',
        '4612.T': '4612 日本ペイント',
        '3088.T': '3088 マツキヨココカラ＆カンパニー',
        '7550.T': '7550 ゼンショー'
    },
    "規模3": {
        '4204.T': '4204 積水化学工業',
        '9602.T': '9602 東宝',
        '7272.T': '7272 ヤマハ発動機',
        '5713.T': '5713 住友金属鉱山',
        '1878.T': '1878 大東建託',
        '4091.T': '4091 日本酸素',
        '3626.T': '3626 ＴＩＳ',
        '9843.T': '9843 ニトリ',
        '9005.T': '9005 東急',
        '7701.T': '7701 島津製作所',
        '3563.T': '3563 ＦＯＯＤ＆ＬＩＦＥＣＯＭＰＡＮＩＥＳ',
        '9684.T': '9684 スクウェア・エニックス・',
        '9107.T': '9107 川崎汽船',
        '7259.T': '7259 アイシン',
        '7912.T': '7912 大日本印刷',
        '6869.T': '6869 シスメックス',
        '6841.T': '6841 横河電機',
        '5929.T': '5929 三和',
        '7735.T': '7735 ＳＣＲＥＥＮ',
        '2875.T': '2875 東洋水産',
        '8331.T': '8331 千葉銀行',
        '9435.T': '9435 光通信',
        '4704.T': '4704 トレンドマイクロ',
        '3003.T': '3003 ヒューリック',
        '6479.T': '6479 ミネベアミツミ',
        '2413.T': '2413 エムスリー',
        '7167.T': '7167 めぶき',
        '5334.T': '5334 日本特殊陶業',
        '1911.T': '1911 住友林業',
        '2702.T': '2702 日本マクドナルド',
        '4062.T': '4062 イビデン',
        '2801.T': '2801 キッコーマン',
        '6845.T': '6845 アズビル',
        '2269.T': '2269 明治',
        '9719.T': '9719 ＳＣＳＫ',
        '8354.T': '8354 ふくおか',
        '3064.T': '3064 ＭｏｎｏｔａＲＯ',
        '3038.T': '3038 神戸物産',
        '5406.T': '5406 神戸製鋼所',
        '4004.T': '4004 レゾナック・',
        '6465.T': '6465 ホシザキ',
        '9962.T': '9962 ミスミ本社',
        '9508.T': '9508 九州電力',
        '3289.T': '3289 東急不動産',
        '6645.T': '6645 オムロン',
        '4732.T': '4732 ユー・エス・エス',
        '9147.T': '9147 ＮＩＰＰＯＮＥＸＰＲＥＳＳ',
        '6417.T': '6417 三共',
        '4768.T': '4768 大塚商会',
        '4528.T': '4528 小野薬品工業',
        '2897.T': '2897 日清食品',
        '6448.T': '6448 ブラザー工業',
        '2267.T': '2267 ヤクルト本社',
        '4183.T': '4183 三井化学',
        '6506.T': '6506 安川電機',
        '3092.T': '3092 ＺＯＺＯ',
        '4403.T': '4403 日油',
        '9041.T': '9041 近鉄',
        '2587.T': '2587 サントリー食品',
        '4042.T': '4042 東ソー'
    },
    "規模4": {
        '9142.T': '9142 九州旅客鉄道',
        '7747.T': '7747 朝日インテック',
        '3861.T': '3861 王子',
        '5101.T': '5101 横浜ゴム',
        '7261.T': '7261 マツダ',
        '9064.T': '9064 ヤマト',
        '6028.T': '6028 テクノプロ・',
        '7459.T': '7459 メディパル',
        '4151.T': '4151 協和キリン',
        '9506.T': '9506 東北電力',
        '4716.T': '4716 日本オラクル',
        '3231.T': '3231 野村不動産',
        '6806.T': '6806 ヒロセ電機',
        '5332.T': '5332 ＴＯＴＯ',
        '3086.T': '3086 Ｊ．フロントリテイリング',
        '9007.T': '9007 小田急電鉄',
        '5706.T': '5706 三井金属鉱業',
        '8227.T': '8227 しまむら',
        '4021.T': '4021 日産化学',
        '4527.T': '4527 ロート製薬',
        '9143.T': '9143 ＳＧ',
        '8804.T': '8804 東京建物',
        '5333.T': '5333 日本碍子',
        '6965.T': '6965 浜松ホトニクス',
        '2181.T': '2181 パーソル',
        '6113.T': '6113 アマダ',
        '6460.T': '6460 セガサミー',
        '7003.T': '7003 三井Ｅ＆Ｓ',
        '3436.T': '3436 ＳＵＭＣＯ',
        '4088.T': '4088 エア・ウォーター',
        '5105.T': '5105 ＴＯＹＯＴＩＲＥ',
        '3288.T': '3288 オープンハウス',
        '6724.T': '6724 セイコーエプソン',
        '3405.T': '3405 クラレ',
        '9009.T': '9009 京成電鉄',
        '8253.T': '8253 クレディセゾン',
        '4186.T': '4186 東京応化工業',
        '1951.T': '1951 エクシオ',
        '1808.T': '1808 長谷工',
        '3291.T': '3291 飯田',
        '7276.T': '7276 小糸製作所',
        '8056.T': '8056 ＢＩＰＲＯＧＹ',
        '6141.T': '6141 ＤＭＧ森精機',
        '1942.T': '1942 関電工',
        '4182.T': '4182 三菱瓦斯化学',
        '1969.T': '1969 高砂熱学工業',
        '9513.T': '9513 電源開発',
        '7649.T': '7649 スギ',
        '3391.T': '3391 ツルハ',
        '6856.T': '6856 堀場製作所',
        '2371.T': '2371 カカクコム',
        '6269.T': '6269 三井海洋開発',
        '4613.T': '4613 関西ペイント',
        '5947.T': '5947 リンナイ',
        '8252.T': '8252 丸井',
        '9006.T': '9006 京浜急行電鉄',
        '5444.T': '5444 大和工業',
        '9065.T': '9065 山九',
        '3349.T': '3349 コスモス薬品',
        '1721.T': '1721 コムシス'
    },
    "規模5": {
        '6305.T': '6305 日立建機',
        '9008.T': '9008 京王電鉄',
        '4912.T': '4912 ライオン',
        '6368.T': '6368 オルガノ',
        '7164.T': '7164 全国保証',
        '4980.T': '4980 デクセリアルズ',
        '7729.T': '7729 東京精密',
        '3769.T': '3769 ＧＭＯペイメント',
        '8088.T': '8088 岩谷産業',
        '5344.T': '5344 ＭＡＲＵＷＡ',
        '7951.T': '7951 ヤマハ',
        '9989.T': '9989 サンドラッグ',
        '3132.T': '3132 マクニカ',
        '5991.T': '5991 日本発條',
        '7988.T': '7988 ニフコ',
        '4203.T': '4203 住友ベークライト',
        '7211.T': '7211 三菱自動車工業',
        '6544.T': '6544 ジャパンエレベーターサービス',
        '4681.T': '4681 リゾートトラスト',
        '3774.T': '3774 インターネットイニシアティブ',
        '2811.T': '2811 カゴメ',
        '5076.T': '5076 インフロニア・',
        '1959.T': '1959 九電工',
        '4202.T': '4202 ダイセル',
        '6849.T': '6849 日本光電工業',
        '3107.T': '3107 ダイワボウ',
        '4680.T': '4680 ラウンドワン',
        '3635.T': '3635 コーエーテクモ',
        '5714.T': '5714 ＤＯＷＡ',
        '7906.T': '7906 ヨネックス',
        '5393.T': '5393 ニチアス',
        '8174.T': '8174 日本瓦斯',
        '8060.T': '8060 キヤノンマーケティング',
        '4666.T': '4666 パーク二四',
        '3141.T': '3141 ウエルシア',
        '7867.T': '7867 タカラトミー',
        '4194.T': '4194 ビジョナル',
        '1332.T': '1332 ニッスイ',
        '4967.T': '4967 小林製薬',
        '1719.T': '1719 安藤・間',
        '4385.T': '4385 メルカリ',
        '8020.T': '8020 兼松',
        '3697.T': '3697 ＳＨＩＦＴ',
        '8439.T': '8439 東京センチュリー',
        '2670.T': '2670 エービーシー・マート',
        '4626.T': '4626 太陽',
        '6728.T': '6728 アルバック',
        '6005.T': '6005 三浦工業',
        '9069.T': '9069 センコー',
        '2871.T': '2871 ニチレイ',
        '9507.T': '9507 四国電力',
        '9302.T': '9302 三井倉庫',
        '8111.T': '8111 ゴールドウイン',
        '9449.T': '9449 ＧＭＯインターネット',
        '9759.T': '9759 ＮＳＤ',
        '2726.T': '2726 パル',
        '3923.T': '3923 ラクス',
        '9744.T': '9744 メイテック',
        '4816.T': '4816 東映アニメーション',
        '9509.T': '9509 北海道電力'
    },
    "規模6": {
        '6436.T': '6436 アマノ',
        '2264.T': '2264 森永乳業',
        '2229.T': '2229 カルビー',
        '2327.T': '2327 日鉄ソリューションズ',
        '8424.T': '8424 芙蓉総合リース',
        '4401.T': '4401 ＡＤＥＫＡ',
        '8279.T': '8279 ヤオコー',
        '7419.T': '7419 ノジマ',
        '5805.T': '5805 ＳＷＣＣ',
        '2127.T': '2127 日本Ｍ＆Ａセンター',
        '2531.T': '2531 宝',
        '8078.T': '8078 阪和興業',
        '8572.T': '8572 アコム',
        '6951.T': '6951 日本電子',
        '3549.T': '3549 クスリのアオキ',
        '2222.T': '2222 寿スピリッツ',
        '7282.T': '7282 豊田合成',
        '2201.T': '2201 森永製菓',
        '8410.T': '8410 セブン銀行',
        '3116.T': '3116 トヨタ紡織',
        '7014.T': '7014 名村造船所',
        '8876.T': '8876 リロ',
        '6632.T': '6632 ＪＶＣケンウッド',
        '6787.T': '6787 メイコー',
        '6323.T': '6323 ローツェ',
        '8098.T': '8098 稲畑産業',
        '8425.T': '8425 みずほリース',
        '6432.T': '6432 竹内製作所',
        '1414.T': '1414 ショーボンド',
        '7762.T': '7762 シチズン時計',
        '7716.T': '7716 ナカニシ',
        '3360.T': '3360 シップヘルスケア',
        '5857.T': '5857 ＡＲＥ',
        '6707.T': '6707 サンケン電気',
        '5471.T': '5471 大同特殊鋼',
        '4516.T': '4516 日本新薬',
        '7004.T': '7004 カナデビア',
        '8130.T': '8130 サンゲツ',
        '7564.T': '7564 ワークマン',
        '6590.T': '6590 芝浦メカトロニクス',
        '8850.T': '8850 スターツ',
        '4812.T': '4812 電通総研',
        '7148.T': '7148 ＦＰＧ',
        '8515.T': '8515 アイフル',
        '8154.T': '8154 加賀電子',
        '4587.T': '4587 ペプチドリーム',
        '7994.T': '7994 オカムラ',
        '2317.T': '2317 システナ',
        '8919.T': '8919 カチタス',
        '9418.T': '9418 Ｕ−ＮＥＸＴＨＯＬＤＩＮＧＳ',
        '7846.T': '7846 パイロット',
        '4686.T': '4686 ジャストシステム',
        '5032.T': '5032 ＡＮＹＣＯＬＯＲ',
        '3765.T': '3765 ガンホー・オンライン・エンターテイメント',
        '2154.T': '2154 オープンアップ',
        '8848.T': '8848 レオパレス２１',
        '6670.T': '6670 ＭＣＪ',
        '6254.T': '6254 野村マイクロ・サイエンス',
        '3186.T': '3186 ネクステージ',
        '7740.T': '7740 タムロン'
    },
    "規模7": {
        '3148.T': '3148 クリエイトＳＤ',
        '8133.T': '8133 伊藤忠エネクス',
        '8584.T': '8584 ジャックス',
        '8194.T': '8194 ライフコーポレーション',
        '4722.T': '4722 フューチャー',
        '5423.T': '5423 東京製鐵',
        '7744.T': '7744 ノーリツ鋼機',
        '8923.T': '8923 トーセイ',
        '6101.T': '6101 ツガミ',
        '2685.T': '2685 アダストリア',
        '9119.T': '9119 飯野海運',
        '1518.T': '1518 三井松島',
        '2379.T': '2379 ディップ',
        '2124.T': '2124 ジェイエイシーリクルートメント',
        '6966.T': '6966 三井ハイテック',
        '2678.T': '2678 アスクル',
        '9090.T': '9090 ＡＺ−ＣＯＭ丸和',
        '2767.T': '2767 円谷フィールズ',
        '7599.T': '7599 ＩＤＯＭ',
        '1419.T': '1419 タマホーム',
        '2384.T': '2384 ＳＢＳ',
        '9110.T': '9110 ＮＳユナイテッド海運',
        '5480.T': '5480 日本冶金工業',
        '2760.T': '2760 東京エレクトロンデバイス',
        '7105.T': '7105 三菱ロジスネクスト',
        '3465.T': '3465 ケイアイスター不動産',
        '7944.T': '7944 ローランド',
        '2168.T': '2168 パソナ'
    }
}

ALL_STOCKS_MAP = {ticker: name for sector in SECTORS.values() for ticker, name in sector.items()}
ALL_SECTOR_TICKERS = list(ALL_STOCKS_MAP.keys())
ALL_TICKERS_WITH_N225 = list(set(ALL_SECTOR_TICKERS + ['^N225']))
NUM_COLS = 6

# 💡 5年分キャッシュ対応の修正: ロード時に使用する最大期間とインターバル
MAX_PERIOD_KEY = "5年"
MAX_YF_PERIOD = "5y"
MAX_YF_INTERVAL = "1wk" # 5年データは週次で取得

# 🔥 変更箇所 1: 期間選択と、その期間に相当するtimedeltaを「5日」に変更
PERIOD_MAP = {
    "5日": timedelta(days=7), # '5d' 相当 (ただし、日次データ取得時はyf_period="5d"を使う。バッファを考慮し7日とする)
    "1ヶ月": timedelta(days=31), # '1mo' 相当 (ただし、日次データ取得時はyf_period="1mo"を使う)
    "1年": timedelta(days=365), # '1y' 相当 (週次データから切り出し)
    "3年": timedelta(days=365*3), # '3y' 相当 (週次データから切り出し)
    "5年": timedelta(days=365*5), # '5y' 相当 (週次データ全体)
}
DEFAULT_PERIOD_KEY = "5日" # 🔥 変更箇所 2: デフォルト選択肢を「5日」に変更

# --- ユーティリティ関数（変更なし） ---
def get_stock_name(ticker_code):
    """ティッカーコードに対応する銘柄名を取得する。"""
    if ticker_code == '^N225':
        return "日経平均"
    return ALL_STOCKS_MAP.get(ticker_code, ticker_code)

# --- Streamlit設定 ---
st.set_page_config(
    page_title="stock-v2.0-filter",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

# --- 期間選択ロジック ---
period_options = list(PERIOD_MAP.keys())
selected_period_key = st.session_state.get("selectbox_period", DEFAULT_PERIOD_KEY)

st.markdown(f"# 📈 Stock Price Analysis")

# --------------------------------------------------------------------------------------
# --- データ取得とキャッシュ（週次データ: 5年分） ---
# --------------------------------------------------------------------------------------
@st.cache_data(show_spinner=True, ttl=timedelta(hours=6))
def load_all_data_cached(tickers_list):
    """
    全銘柄と日経平均のデータを最大期間(5年)分(週次)一度に取得しキャッシュする。
    """
    if not tickers_list:
        return pd.DataFrame()
    unique_tickers = list(set(tickers_list))
    
    # 💡 期間を MAX_YF_PERIOD ('5y') と MAX_YF_INTERVAL ('1wk') に固定
    try:
        tickers_obj = yf.Tickers(unique_tickers)
        # 期間とインターバルを指定してデータを取得 (5年分、週次)
        data = tickers_obj.history(period=MAX_YF_PERIOD, interval=MAX_YF_INTERVAL, auto_adjust=True)
        
        if 'Close' in data.columns.get_level_values(0):
            data_close = data["Close"]
        elif len(unique_tickers) == 1 and 'Close' in data.columns:
            data_close = data["Close"].to_frame(name=unique_tickers[0])
        else:
            return pd.DataFrame(index=pd.to_datetime([]), columns=unique_tickers)
            
    except yf.exceptions.YFRateLimitError:
        raise
    except Exception as e:
        st.error(f"yfinanceデータ取得エラー (週次): {e}")
        return pd.DataFrame()
        
    return data_close.dropna(axis=0, how='all').sort_index()

# --------------------------------------------------------------------------------------
# 🔥 変更点 3: 短い期間の日次データ取得関数（yf_period_strが'5d'にも対応）
# --------------------------------------------------------------------------------------
@st.cache_data(show_spinner=True, ttl=timedelta(minutes=30))
def load_daily_data_cached(tickers_list, yf_period_str):
    """
    短い期間（日次: '5d' または '1mo'）のデータを取得する。
    """
    if not tickers_list:
        return pd.DataFrame()
    unique_tickers = list(set(tickers_list))
    
    # 日次 (1d) のインターバルでデータを取得
    try:
        tickers_obj = yf.Tickers(unique_tickers)
        # 💡 インターバルを "1d" (日次) に固定
        data = tickers_obj.history(period=yf_period_str, interval="1d", auto_adjust=True)
        
        if 'Close' in data.columns.get_level_values(0):
            data_close = data["Close"]
        elif len(unique_tickers) == 1 and 'Close' in data.columns:
            data_close = data["Close"].to_frame(name=unique_tickers[0])
        else:
            return pd.DataFrame(index=pd.to_datetime([]), columns=unique_tickers)
            
    except yf.exceptions.YFRateLimitError:
        raise
    except Exception as e:
        st.error(f"yfinanceデータ取得エラー (日次): {e}")
        return pd.DataFrame()
        
    return data_close.dropna(axis=0, how='all').sort_index()


# 💡 5年分キャッシュ対応の修正: キャッシュされた週次データから指定期間を切り出す関数 (ロジック変更なし)
@st.cache_data(show_spinner=False)
def filter_data_by_period(data_raw_5y, period_key):
    """
    5年分の生データ（週次）から、指定された期間分（1年、3年、5年）のデータのみを抽出する。
    """
    if data_raw_5y.empty:
        return pd.DataFrame()
        
    delta = PERIOD_MAP[period_key]
    end_date = data_raw_5y.index.max()
    start_date = end_date - delta
    
    # 選択期間に応じたデータの切り出し
    filtered_data = data_raw_5y[data_raw_5y.index >= start_date].copy()
    
    # 欠損値を埋める（グラフ描画のために）
    filtered_data_filled = filtered_data.apply(lambda col: col.bfill().ffill(), axis=0)
    
    return filtered_data_filled

# 1. キャッシュされた5年分の週次データ取得 (初回のみロード)
try:
    with st.spinner(f"最大データ（{MAX_PERIOD_KEY}）をロード中..."):
        data_raw_5y = load_all_data_cached(ALL_TICKERS_WITH_N225) 
        
    if data_raw_5y.empty:
        # data_raw_5yが空の場合でも、日次データ取得に進めるよう st.stop() は呼ばない
        pass
        
except yf.exceptions.YFRateLimitError:
    st.warning("YFinanceの接続制限が発生しています。しばらくしてから再試行してください。")
    load_all_data_cached.clear()
    st.stop()
except Exception as e:
    st.error(f"データ読み込みエラー: {e}")
    st.stop()

# --- 柔軟な上昇率設定と抽出関数（変更なし） ---
def filter_stocks_by_gain(all_data, stocks_map, min_gain_percent, max_gain_percent, selected_period_key):
    """
    全銘柄について、株価変動率が指定の範囲内（最小〜最大）のものを抽出し、
    ティッカーコードをキー、銘柄名を値とする単一の辞書として返す。
    使用する all_data は、既に期間でフィルタリングされたデータ（日次または週次）であると想定。
    """
    if all_data.empty or all_data.shape[0] < 2:
        return {}, {} 
        
    # 期間の最初と最後を取得するロジックを統一
    start_prices = all_data.iloc[0].bfill()
    end_prices = all_data.iloc[-1].ffill()
    
    # 日経平均 '^N225' は除外
    valid_tickers = [t for t in stocks_map.keys() if t in start_prices.index and t in end_prices.index and start_prices[t] > 0]
    
    start_prices = start_prices[valid_tickers]
    end_prices = end_prices[valid_tickers]
    
    # 上昇率（%）を計算
    gain_percents = ((end_prices / start_prices) - 1) * 100
    
    # 最小閾値以上、最大閾値以下の銘柄を抽出
    filtered_gain_tickers = gain_percents[
        (gain_percents >= min_gain_percent) & 
        (gain_percents <= max_gain_percent)
    ].index.tolist()
    
    filtered_stocks = {
        ticker: stocks_map[ticker]
        for ticker in filtered_gain_tickers
    } 
    return filtered_stocks, gain_percents.to_dict() # 銘柄ごとの上昇率を返す

# --------------------------------------------------------------------------------------
# --- グラフ描画関数（ロジック変更なし、表示名の変更あり） ---
# --------------------------------------------------------------------------------------
def create_and_display_charts(normalized_data, period_label, y_min=0.9, y_max=1.1, selected_period_key=DEFAULT_PERIOD_KEY):
    """
    正規化されたデータを用いて、指定された期間のグラフを描画する。
    """
    current_plot_tickers = [t for t in normalized_data.columns if t != '^N225']
    if normalized_data is None or current_plot_tickers == []:
        st.info(f"{period_label}のグラフを表示するためのデータがありません。")
        return 
        
    has_nikkei = '^N225' in normalized_data.columns
    nikkei_data = pd.DataFrame()
    if has_nikkei:
        nikkei_data = normalized_data[['^N225']].rename(columns={'^N225': 'Price'})
        nikkei_data['Date'] = nikkei_data.index
        nikkei_data['z_index'] = 0
        
    y_domain = [y_min, y_max] 
    
    date_range = normalized_data.index.max() - normalized_data.index.min()
    
    # 期間によるX軸フォーマットの判定
    # 🔥 変更箇所 4: "1日" を "5日" に変更して判定
    if selected_period_key in ["5日", "1ヶ月"]: 
        x_format = "%m/%d" # 短い期間は月日表示
    elif date_range.days <= 400: # 1年以内
        x_format = "%m/%d" # 月日表示
    elif date_range.days <= 365 * 4: # 4年以内
        x_format = "%m" # 月表示
    else:
        x_format = "%Y" # 年表示

    for row_i in range((len(current_plot_tickers) + NUM_COLS - 1) // NUM_COLS):
        cols = st.columns(NUM_COLS)
        for col_i in range(NUM_COLS):
            idx = row_i * NUM_COLS + col_i
            if idx < len(current_plot_tickers):
                ticker = current_plot_tickers[idx]
                
                stock_data = pd.DataFrame({
                    "Date": normalized_data.index,
                    "Price": normalized_data[ticker],
                })
                stock_data['z_index'] = 1
                
                # Nikkeiと銘柄のデータを結合（Nikkeiが存在する場合）
                combined_data = pd.concat([stock_data, nikkei_data]).dropna(subset=['Price'])
                
                title_text = get_stock_name(ticker)
                
                base_chart = alt.Chart(combined_data).encode(
                    alt.X("Date:T", axis=alt.Axis(
                        format=x_format,
                        title=None,
                        labelAngle=0
                    )),
                    alt.Y("Price:Q", axis=alt.Axis(title=None, format=".2f")).scale(zero=False, domain=y_domain),
                ) 
                
                nikkei_line = alt.Chart(pd.DataFrame())
                if has_nikkei:
                    nikkei_line = base_chart.transform_filter(
                        alt.datum.z_index == 0
                    ).mark_line(
                        color="#A9A9A9",
                        strokeWidth=1.5
                    ).encode(
                        alt.Order("z_index:Q"),
                        tooltip=[
                            alt.Tooltip("Date:T", title="日付", format=x_format),
                            alt.Tooltip("Price:Q", title="日経変動率", format=".2f")
                        ]
                    ) 
                
                stock_line = base_chart.transform_filter(
                    alt.datum.z_index == 1
                ).mark_line(
                    color="#C70025",
                    strokeWidth=2
                ).encode(
                    alt.Order("z_index:Q"),
                    tooltip=[
                        alt.Tooltip("Date:T", title="日付", format=x_format),
                        alt.Tooltip("Price:Q", title=f"{title_text}変動率", format=".2f")
                    ]
                ) 
                
                chart = (
                    nikkei_line + stock_line
                ).properties(title=f"{title_text}", height=300, width='container') 
                cell = cols[col_i].container(border=False)
                cell.altair_chart(chart, use_container_width=True)

# --------------------------------------------------------------------------------------
# --- メインロジック ---
# --------------------------------------------------------------------------------------

# --- 2. 状態管理（UI） ---
col_period, col_gain_container, col_y_axis_container = st.columns([1, 1, 1])

# --- 分析期間の選択（左側） ---
with col_period:
    st.markdown("期間")
    selected_period_key = st.selectbox(
        "分析期間を選択",
        options=period_options,
        index=period_options.index(st.session_state.get("selectbox_period", DEFAULT_PERIOD_KEY)) 
              if st.session_state.get("selectbox_period", DEFAULT_PERIOD_KEY) in period_options else 
              period_options.index(DEFAULT_PERIOD_KEY) if DEFAULT_PERIOD_KEY in period_options else 0,
        key="selectbox_period",
        label_visibility="collapsed"
    )

# 🔥 変更箇所 5: 選択期間に応じてデータ取得ロジックを切り替える
data_for_analysis = pd.DataFrame()
if selected_period_key in ["5日", "1ヶ月"]:
    # 短い期間の場合: 日次データを取得
    # 🔥 "5日"のとき、yfinanceのperiod文字列は "5d" を使用
    yf_period_str = "5d" if selected_period_key == "5日" else "1mo"
    with st.spinner(f"日次データ（{selected_period_key}）をロード中..."):
        data_for_analysis = load_daily_data_cached(ALL_TICKERS_WITH_N225, yf_period_str) 
    
    # 日次データは期間で絞る必要がないため、そのまま使用
    data_filtered_by_period = data_for_analysis
    
    # 5日選択時、データポイントが2つ未満の場合はエラーとする
    if selected_period_key == "5日" and data_filtered_by_period.shape[0] < 2:
        st.warning("「5日」の分析に必要なデータポイント（最低2つ）が取得できませんでした。土日や祝日など、市場が閉まっている可能性があります。")
        # 閾値計算・グラフ描画でエラーが出ないよう、空のデータに置き換える
        data_filtered_by_period = pd.DataFrame()
    
elif data_raw_5y.empty:
    st.error("最大期間データがロードされていないため、分析を続行できません。")
    st.stop()
else:
    # 長い期間の場合: キャッシュされた週次データから抽出
    data_filtered_by_period = filter_data_by_period(data_raw_5y, selected_period_key)


if data_filtered_by_period.empty:
    # データが空の場合でも、閾値入力やY軸設定は表示を続ける
    pass # 警告はデータ取得ロジック内で行うか、結果表示時に行う


# --- 閾値設定（中央） ---
with col_gain_container:
    default_min_gain = 12.0
    default_max_gain = 100.0
    max_range = 2000.0
    min_range = -100.0    
    if selected_period_key == "5日": 
        default_min_gain = 1.0 
        default_max_gain = 10.0
    elif selected_period_key == "1ヶ月":
        default_min_gain = 5.0
        default_max_gain = 30.0
    elif selected_period_key == "1年":
        default_min_gain = 50.0
    elif selected_period_key == "3年":
        default_min_gain = 300.0
    elif selected_period_key == "5年":
        default_min_gain = 500.0
    st.markdown("変動率") 
    max_gain_threshold = st.number_input(
        "最大変動率 (%)",
        min_value=min_range,
        max_value=max_range,
        value=default_max_gain,
        step=1.0,
        format="%.2f",
        key="max_gain_threshold_input",
        label_visibility="collapsed"
    )    
    min_gain_threshold = st.number_input(
        "最小変動率 (%)",
        min_value=min_range,
        max_value=max_range,
        value=default_min_gain,
        step=1.0,
        format="%.2f",
        key="min_gain_threshold_input",
        label_visibility="collapsed"
    )    
    if min_gain_threshold >= max_gain_threshold:
        st.error("最小変動率は最大変動率よりも小さく設定してください。")
        pass

# --- 抽出銘柄 Y軸 最大値/最小値設定（右側）（変更なし） ---
with col_y_axis_container:
    min_ratio = 1.0 + min_gain_threshold / 100.0
    max_ratio = 1.0 + max_gain_threshold / 100.0
    buffer = 0.1 
    y_min_default = min(min_ratio, 1.0) - buffer
    y_max_default = max(max_ratio, 1.0) + buffer
    max_value_extracted_input = max(5.0, y_max_default + 1.0) 
    min_value_extracted_input = min(0.1, y_min_default - 0.5)
    st.markdown("Y軸") 
    y_max_extracted = st.number_input(
        "抽出銘柄 Y軸 最大値",
        min_value=y_min_default + 0.05,
        max_value=max_value_extracted_input,
        value=y_max_default,
        step=0.05,
        format="%.2f",
        key="y_max_extracted_top", 
        label_visibility="collapsed"    )

    y_min_extracted = st.number_input(
        "抽出銘柄 Y軸 最小値",
        min_value=min_value_extracted_input,
        max_value=y_max_default - 0.05,
        value=y_min_default,
        step=0.05,
        format="%.2f",
        key="y_min_extracted_bottom", 
        label_visibility="collapsed"
    )
    
    y_min_for_chart = y_min_extracted
    y_max_for_chart = y_max_extracted


# --- 4. 抽出結果の表示（テーブルと辞書）（変更なし） ---
FILTERED_STOCKS, all_gain_percents = filter_stocks_by_gain(data_filtered_by_period, ALL_STOCKS_MAP, min_gain_threshold, max_gain_threshold, selected_period_key)

st.markdown("---")
if FILTERED_STOCKS:
    col_table, col_dict = st.columns(2) 
    
    # 終値の取得
    end_prices = data_filtered_by_period.iloc[-1].ffill()
    current_prices = end_prices 
    
    results = []
    for ticker, name in FILTERED_STOCKS.items():
        if ticker in all_gain_percents:
            gain_percent = all_gain_percents[ticker]
            current_price = current_prices[ticker] 
            
            # gain_percent に基づいて色分け用のマークを追加
            mark = "📈" if gain_percent >= 0 else "📉"
            
            results.append({
                "マーク": mark,
                "ティッカー": ticker,
                "銘柄名": name,
                "変動率 (%)": gain_percent,
                "現在の株価": current_price
            }) 
            
    if results:
        df_results = pd.DataFrame(results).set_index("ティッカー").sort_values("変動率 (%)", ascending=False)
        display_df = df_results.copy()
        display_df["変動率 (%)"] = display_df["変動率 (%)"].apply(lambda x: f"{x:+.2f}") # プラス/マイナス記号を追加
        display_df["現在の株価"] = display_df["現在の株価"].apply(lambda x: f"{x:,.2f}")
        
        with col_table:
            st.markdown(f"### 📊 抽出銘柄")
            st.data_editor(
                data=display_df,
                width='stretch', 
                disabled=True
            )
            
        with col_dict:
            DISPLAY_SECTORS = {
                "FILTERED": FILTERED_STOCKS,
            }
            st.markdown("### 📋 Python")
            formatted_dict = pprint.pformat(DISPLAY_SECTORS, indent=4) # DISPLAY_SECTORS を整形
            st.code(f"SECTORS = {formatted_dict}", language='python', height=350) # 変数名を SECTORS に変更
            
        st.markdown("---")
        st.markdown("### 📈 株価変動率")
        
        if y_min_extracted >= y_max_extracted:
            st.warning("抽出銘柄の Y軸の最小値は最大値よりも小さく設定してください。デフォルト値で描画します。")
            y_min_for_chart = y_min_default
            y_max_for_chart = y_max_default
        else:
            y_min_for_chart = y_min_extracted
            y_max_for_chart = y_max_extracted


        extracted_tickers = list(FILTERED_STOCKS.keys()) 
        
        # 1つ目のグラフの描画対象銘柄（抽出銘柄全て）
        plot_targets_1 = extracted_tickers 
        
        if not plot_targets_1:
            st.info("グラフを表示するための抽出銘柄がありません。")
        else:
            plot_tickers = [t for t in plot_targets_1 if t in data_filtered_by_period.columns]
            if '^N225' in data_filtered_by_period.columns:
                plot_tickers.append('^N225') 
                
            if plot_tickers and not data_filtered_by_period.empty:
                plot_data_raw = data_filtered_by_period[[c for c in plot_tickers if c in data_filtered_by_period.columns]].copy()
                
                # 正規化の基準は期間の最初のデータ
                first_valid_price = plot_data_raw.iloc[0]
                extracted_normalized = plot_data_raw / first_valid_price
                
                # 🔥 変更箇所 7: selected_period_keyが「5日」に対応
                create_and_display_charts(extracted_normalized, "", y_min_for_chart, y_max_for_chart, selected_period_key)
            else:
                st.info("抽出された銘柄に有効なデータがありませんでした。") 

        # ====================================================================
        # 💡 追加: 2つ目のグラフ（異なる期間とY軸設定）- マルチセレクト対応
        # ====================================================================
        st.markdown("---")
        st.markdown("### 📈 中期間")
        
        target_period_key_2 = "1ヶ月"
        target_index_2 = period_options.index(target_period_key_2) if target_period_key_2 in period_options else 0
        
        # マルチセレクトのオプションを準備（銘柄コードを削除）
        extracted_stock_options = [FILTERED_STOCKS[t] for t in extracted_tickers] # 銘柄名のみ
        
        # セッションステートに抽出銘柄リストを保存（初期値として使用）
        if "selected_plot_tickers_2" not in st.session_state:
             # 初回ロード時、または抽出銘柄が変更された際に更新
            st.session_state.selected_plot_tickers_2 = extracted_tickers
            
        # 描画対象をマルチセレクトで選択
        # Y軸設定用の列を1つにまとめる
        col_plot_period, col_plot_y_setting, col_multiselect = st.columns([1, 1, 4]) # 列幅を調整
        
        # 銘柄名からティッカーコードを逆引きするための辞書を作成
        # この辞書は、このセクションの外側のスコープで定義されていると想定されます
        # 例: name_to_ticker = {v: k for k, v in FILTERED_STOCKS.items()}
        # 安全のため、このブロック内でも定義（または利用可能なスコープにあることを確認）
        # 例として、ここで定義します（実際の環境に合わせて調整してください）
        name_to_ticker = {v: k for k, v in FILTERED_STOCKS.items()}
        
        with col_plot_period:
            st.markdown("期間") 
            selected_plot_period_key = st.selectbox(
                "グラフ描画期間を選択",
                options=period_options,
                index=period_options.index(st.session_state.get("selectbox_plot_period", target_period_key_2)) 
                             if st.session_state.get("selectbox_plot_period", target_period_key_2) in period_options else 
                             target_index_2,
                key="selectbox_plot_period",
                label_visibility="collapsed"
            )
            
        with col_multiselect:
            st.markdown("銘柄") 
            selected_plot_ticker_names_2 = st.multiselect(
                "描画銘柄を選択",
                options=extracted_stock_options,
                default=[FILTERED_STOCKS[t] for t in st.session_state.selected_plot_tickers_2 if FILTERED_STOCKS[t] in extracted_stock_options],
                key="multiselect_plot_tickers_2",
                label_visibility="collapsed"
            )
            # 選択された銘柄名からティッカーコードを抽出し、セッションステートを更新
            selected_plot_tickers_2 = [name_to_ticker.get(name) for name in selected_plot_ticker_names_2 if name in name_to_ticker]
            st.session_state.selected_plot_tickers_2 = selected_plot_tickers_2 # 次回の初期値のために保存
            
        # 🔥 変更箇所 8: 2つ目のグラフのデータ取得ロジックも「5日」に対応
        data_plot_for_analysis_2 = pd.DataFrame()
        if selected_plot_period_key in ["5日", "1ヶ月"]:
            yf_period_str_2 = "5d" if selected_plot_period_key == "5日" else "1mo"
            with st.spinner(f"日次データ（{selected_plot_period_key}）をロード中..."):
                data_plot_for_analysis_2 = load_daily_data_cached(ALL_TICKERS_WITH_N225, yf_period_str_2) 
            data_plot_filtered_by_period = data_plot_for_analysis_2
        else:
            data_plot_filtered_by_period = filter_data_by_period(data_raw_5y, selected_plot_period_key)

        # 3. 2つ目のグラフ用のY軸設定
        plot_y_min_default = 0.9
        plot_y_max_default = 1.1
        
        # 修正: Y軸 最大値と最小値を col_plot_y_setting 内に縦に配置
        with col_plot_y_setting:
             st.markdown("Y軸") 
             y_max_plot_period = st.number_input(
                "Y軸 最大値",
                min_value=0.1,
                max_value=5.0,
                value=plot_y_max_default,
                step=0.05,
                format="%.2f",
                key="y_max_plot_period",
                label_visibility="collapsed"
            )        
             y_min_plot_period = st.number_input(
                "Y軸 最小値",
                min_value=0.0,
                max_value=4.9,
                value=plot_y_min_default,
                step=0.05,
                format="%.2f",
                key="y_min_plot_period",
                label_visibility="collapsed"
            )

        if y_min_plot_period >= y_max_plot_period:
            st.warning("グラフ描画の Y軸の最小値は最大値よりも小さく設定してください。デフォルト値で描画します。")
            y_min_plot_period = plot_y_min_default
            y_max_plot_period = plot_y_max_default
            
        # 4. 2つ目のグラフの描画 (変更なし)
        if not data_plot_filtered_by_period.empty and selected_plot_tickers_2: # <--- 選択された銘柄を使用
            plot_tickers_new = [t for t in selected_plot_tickers_2 if t in data_plot_filtered_by_period.columns]
            if '^N225' in data_plot_filtered_by_period.columns:
                plot_tickers_new.append('^N225')
                
            if plot_tickers_new:
                plot_data_raw_new = data_plot_filtered_by_period[[c for c in plot_tickers_new if c in data_plot_filtered_by_period.columns]].copy()
                
                if not plot_data_raw_new.empty and plot_data_raw_new.shape[0] > 1:
                    # 正規化の基準は期間の最初のデータ
                    first_valid_price_new = plot_data_raw_new.iloc[0]
                    extracted_normalized_new = plot_data_raw_new / first_valid_price_new
                    
                    # 🔥 変更箇所 9: selected_plot_period_keyが「5日」に対応
                    create_and_display_charts(extracted_normalized_new, selected_plot_period_key, y_min_plot_period, y_max_plot_period, selected_plot_period_key)
                else:
                    st.info(f"選択期間 ({selected_plot_period_key}) で有効なデータ（複数日）が取得できませんでした。")
            else:
                st.info("抽出された銘柄に、選択期間で有効なデータがありませんでした。")
        elif extracted_tickers:
            st.info(f"選択期間 ({selected_plot_period_key}) のデータがロードできませんでした、または銘柄が選択されていません。")
        
        # ====================================================================
        # 💡 追加: 3つ目のグラフ（さらに別期間での株価変動率グラフ）- マルチセレクト対応
        # ====================================================================
        st.markdown("---")
        st.markdown("### 📈 長期間")
        
        target_period_key_3 = "3年"
        target_index_3 = period_options.index(target_period_key_3) if target_period_key_3 in period_options else 0

        # セッションステートに抽出銘柄リストを保存（初期値として使用）
        if "selected_plot_tickers_3" not in st.session_state:
             # 初回ロード時、または抽出銘柄が変更された際に更新
            st.session_state.selected_plot_tickers_3 = extracted_tickers
            
        # Y軸設定用の列を1つにまとめる
        col_plot_period_3,col_plot_y_setting_3 , col_multiselect_3 = st.columns([1, 1, 4]) # 列幅を調整

        with col_plot_period_3:
            st.markdown("期間") 
            selected_plot_period_key_3 = st.selectbox(
                "3つ目のグラフ描画期間を選択",
                options=period_options,
                index=period_options.index(st.session_state.get("selectbox_plot_period_3", target_period_key_3)) 
                             if st.session_state.get("selectbox_plot_period_3", target_period_key_3) in period_options else 
                             target_index_3,
                key="selectbox_plot_period_3",
                label_visibility="collapsed"
            )

        with col_multiselect_3:
            st.markdown("銘柄") 
            selected_plot_ticker_names_3 = st.multiselect(
                "描画銘柄を選択（3つ目）",
                options=extracted_stock_options,
                default=[FILTERED_STOCKS[t] for t in st.session_state.selected_plot_tickers_3 if FILTERED_STOCKS[t] in extracted_stock_options],
                key="multiselect_plot_tickers_3",
                label_visibility="collapsed"
            )
            # 選択された銘柄名からティッカーコードを抽出し、セッションステートを更新
            selected_plot_tickers_3 = [name_to_ticker.get(name) for name in selected_plot_ticker_names_3 if name in name_to_ticker]
            st.session_state.selected_plot_tickers_3 = selected_plot_tickers_3 # 次回の初期値のために保存

        # 🔥 変更箇所 10: 3つ目のグラフのデータ取得ロジックも「5日」に対応
        data_plot_for_analysis_3 = pd.DataFrame()
        if selected_plot_period_key_3 in ["5日", "1ヶ月"]:
            yf_period_str_3 = "5d" if selected_plot_period_key_3 == "5日" else "1mo"
            with st.spinner(f"日次データ（{selected_plot_period_key_3}）をロード中..."):
                data_plot_for_analysis_3 = load_daily_data_cached(ALL_TICKERS_WITH_N225, yf_period_str_3)
            data_plot_filtered_by_period_3 = data_plot_for_analysis_3
        else:
            data_plot_filtered_by_period_3 = filter_data_by_period(data_raw_5y, selected_plot_period_key_3)

        plot_y_min_default_3 = 0.9
        plot_y_max_default_3 = 5.0
        with col_plot_y_setting_3:
            st.markdown("Y軸") 
            y_max_plot_period_3 = st.number_input(
                "Y軸 最大値（3つ目）",
                min_value=0.1,
                max_value=10.0,
                value=plot_y_max_default_3,
                step=0.05,
                format="%.2f",
                key="y_max_plot_period_3",
                label_visibility="collapsed"
            )
            y_min_plot_period_3 = st.number_input(
                "Y軸 最小値（3つ目）",
                min_value=0.0,
                max_value=4.9,
                value=plot_y_min_default_3,
                step=0.05,
                format="%.2f",
                key="y_min_plot_period_3",
                label_visibility="collapsed"
            )

        if y_min_plot_period_3 >= y_max_plot_period_3:
            st.warning("3つ目のグラフのY軸設定が不正です。デフォルトで描画します。")
            y_min_plot_period_3 = plot_y_min_default_3
            y_max_plot_period_3 = plot_y_max_default_3

        # 💡 修正後: 日次データまたは週次データから描画 (変更なし)
        if not data_plot_filtered_by_period_3.empty and selected_plot_tickers_3: # <--- 選択された銘柄を使用
            plot_tickers_new_3 = [t for t in selected_plot_tickers_3 if t in data_plot_filtered_by_period_3.columns]
            if '^N225' in data_plot_filtered_by_period_3.columns:
                plot_tickers_new_3.append('^N225')

            if plot_tickers_new_3:
                plot_data_raw_new_3 = data_plot_filtered_by_period_3[[c for c in plot_tickers_new_3 if c in data_plot_filtered_by_period_3.columns]].copy()
                
                if not plot_data_raw_new_3.empty and plot_data_raw_new_3.shape[0] > 1:
                    # 正規化の基準は期間の最初のデータ
                    first_valid_price_3 = plot_data_raw_new_3.iloc[0]
                    extracted_normalized_new_3 = plot_data_raw_new_3 / first_valid_price_3
                    
                    # 🔥 変更箇所 11: selected_plot_period_key_3が「5日」に対応
                    create_and_display_charts(
                        extracted_normalized_new_3,
                        selected_plot_period_key_3,
                        y_min_plot_period_3,
                        y_max_plot_period_3,
                        selected_plot_period_key_3
                    )
                else:
                    st.info(f"選択期間 ({selected_plot_period_key_3}) で有効なデータ（複数日）が取得できませんでした。")
            else:
                st.info("抽出された銘柄に有効なデータがありませんでした。")
        elif extracted_tickers:
            st.info(f"選択期間 ({selected_plot_period_key_3}) のデータがロードできませんでした、または銘柄が選択されていません。")
        # ====================================================================
        # 💡 追加ここまで
        # ====================================================================
            
        else:
            st.info(f"この期間に株価変動率が {min_gain_threshold:.2f}% ～ {max_gain_threshold:.2f}% の銘柄はありませんでした。") 
else:
    if data_filtered_by_period.empty:
        # データが空の場合、より具体的なメッセージを出す
        # 🔥 変更箇所 12: "1日" を "5日" に変更
        if selected_period_key in ["5日", "1ヶ月"]:
            st.info(f"選択期間 ({selected_period_key}) の日次データが取得できなかったため、銘柄抽出が行えませんでした。")
        else:
             st.info(f"選択期間 ({selected_period_key}) のデータがロードされていません。")
    else:
        st.info(f"この期間に株価変動率が {min_gain_threshold:.2f}% ～ {max_gain_threshold:.2f}% の銘柄はありませんでした。")