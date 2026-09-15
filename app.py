# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
import streamlit as st

# スマホ向け画面設定
st.set_page_config(
    page_title="RETRO GAME VAULT",
    page_icon="🎮",
    layout="centered"
)

MANUAL_DATA_FILE = "manuals_data.json" # 説明書アプリのデータ(342本)

# --- どんな文字コードでも100%安全に読み込む関数 ---
def load_manual_data():
    combined = {}
    if os.path.exists(MANUAL_DATA_FILE):
        manual_data = None
        for enc in ["utf-8-sig", "utf-8", "cp932"]:
            try:
                with open(MANUAL_DATA_FILE, "r", encoding=enc) as f:
                    manual_data = json.load(f)
                    break
            except Exception:
                continue

        if manual_data and isinstance(manual_data, dict):
            for console, games in manual_data.items():
                if console.startswith("_"): continue
                if console not in combined:
                    combined[console] = []
                if isinstance(games, dict):
                    for game_title in games.keys():
                        combined[console].append({
                            "title": game_title
                        })

    return combined

game_data = load_manual_data()

# ----------------- UI構築（極限シンプル） -----------------
st.title("🎮 RETRO GAME VAULT")

# タブは2つだけ！
tab1, tab2 = st.tabs(["🔍 所持チェック", "📊 所有リスト"])

# 1. 所持チェック
with tab1:
    query = st.text_input("タイトル検索", placeholder="例: マリオ, レガイア, ゼルダ").strip().lower()

    if query:
        results = []
        for console, games in game_data.items():
            for game in games:
                title = game.get("title", "")
                if query in title.lower() or query in console.lower():
                    results.append({
                        "機種": console,
                        "タイトル": title
                    })

        if results:
            st.error(f"❌ **【所持中！】** {len(results)} 件ヒットしました")
            for r in results:
                st.write(f"🎮 **[{r['機種']}] {r['タイトル']}**")
        else:
            st.success(f"⭕️ **【未所持】** 「{query}」は未登録です（購入可）")

# 2. 所有ゲーム一覧
with tab2:
    total_games = sum(len(games) for games in game_data.values())
    st.metric("総所有数", f"{total_games} 本")
    st.divider()

    consoles_options = ["すべて表示"] + list(game_data.keys())
    selected_console = st.selectbox("機種フィルター", consoles_options)
    view_style = st.radio("表示形式", ["リスト", "テーブル"], horizontal=True)

    all_flat_list = []
    for console, games in game_data.items():
        if selected_console == "すべて表示" or selected_console == console:
            for g in games:
                all_flat_list.append({
                    "機種": console,
                    "タイトル": g.get("title", "")
                })

    all_flat_list.sort(key=lambda x: x["タイトル"].lower())
    st.caption(f"件数: {len(all_flat_list)} 本")

    if view_style == "リスト":
        for item in all_flat_list:
            st.write(f"・**[{item['機種']}] {item['タイトル']}**")
    else:
        if all_flat_list:
            df = pd.DataFrame(all_flat_list)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("該当なし")