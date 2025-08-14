import streamlit as st
import pandas as pd
from logic import convert_name, get_pokemon_data, generate_rotom_comment, save_training_log, load_training_logs
import json

st.set_page_config(page_title="ロトム図鑑風ポケモン図鑑", page_icon="⚡", layout="wide")

# ロトム図鑑風のカスタムCSSを強化
st.markdown(
    """
    <style>
    /* 全体的な背景色を黒に設定 */
    .st-emotion-cache-184n34b {
        background-color: #1a1a1a;
        color: white;
    }
    
    /* ヘッダーの背景色も黒に */
    .st-emotion-cache-13m93i1 {
        background-color: #1a1a1a;
    }
    
    /* タイトルとサブタイトルをロトム風に */
    .title {
        color: #ff4500;  /* オレンジレッド */
        font-family: 'Press Start 2P', cursive; /* ドット絵風フォントがあれば理想 */
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        text-shadow: 2px 2px 4px #000000;
        letter-spacing: 2px;
    }
    .subtitle {
        color: #ffa500; /* オレンジ */
        text-align: center;
        font-style: italic;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    
    /* 入力ボックスとボタンのデザイン */
    .stTextInput > div > div > input {
        background-color: #333333;
        color: #ffffff;
        border: 2px solid #ff4500;
        border-radius: 5px;
        padding: 10px;
    }
    .stButton > button {
        background-color: #ff4500;
        color: white !important; /* !important で強制的に色を適用 */
        font-weight: bold;
        border: 2px solid #ffa500;
        border-radius: 5px;
        padding: 10px 20px;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #ffa500;
        border: 2px solid #ff4500;
    }
    
    /* ロトムの吹き出しコメント風UI */
    .comment-box {
        background-color: #333333;
        border: 3px solid #ff4500;
        border-radius: 15px;
        padding: 20px;
        position: relative;
        margin: 20px 0;
        color: white;
        font-size: 18px;
        line-height: 1.5;
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }
    .comment-box::before {
        content: '';
        width: 0;
        height: 0;
        border-style: solid;
        border-width: 20px 20px 0 20px;
        border-color: #ff4500 transparent transparent transparent;
        position: absolute;
        bottom: -20px;
        left: 40px;
    }
    .comment-box::after {
        content: '';
        width: 0;
        height: 0;
        border-style: solid;
        border-width: 17px 17px 0 17px;
        border-color: #333333 transparent transparent transparent;
        position: absolute;
        bottom: -17px;
        left: 43px;
    }

    /* ポケモン情報の表示スタイル */
    .pokemon-info {
        background-color: #2a2a2a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    /* ステータスバーのデザイン */
    .st-emotion-cache-1f8a846 {
        background-color: #ff4500; /* バーの色 */
    }
    </style>
    <link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">
    """, unsafe_allow_html=True
)

st.markdown('<div class="title">⚡ ロトムのポケモン育成図鑑 ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">名前か番号を入力して検索だ！日本語入力もOK！</div>', unsafe_allow_html=True)

# セッションステートの初期化
if 'pokemon_data' not in st.session_state:
    st.session_state.pokemon_data = None
if 'save_status' not in st.session_state:
    st.session_state.save_status = None
if 'search_error' not in st.session_state:
    st.session_state.search_error = False

tab1, tab2 = st.tabs(["📖 図鑑検索", "📝 みんなの育成記録"])

with tab1:
    user_input = st.text_input("ポケモン名または図鑑番号を入力", value="", key="search_input")
    
    if st.button("検索！", key="search_button"):
        if not user_input.strip():
            st.session_state.search_error = True
            st.session_state.pokemon_data = None
        else:
            st.session_state.search_error = False
            name_or_id = convert_name(user_input)
            data = get_pokemon_data(name_or_id)
            if data:
                st.session_state.pokemon_data = data
                st.session_state.save_status = None
            else:
                st.session_state.pokemon_data = None
                st.error("ポケモンが見つからないぞ…名前や番号を確認してくれ！⚡")
    
    if st.session_state.search_error:
        st.error("検索場所が空だぞ！何か入力してくれ！⚡")

    if st.session_state.pokemon_data:
        data = st.session_state.pokemon_data
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(data["image"], width=200)
            st.markdown(f'<div class="pokemon-info">', unsafe_allow_html=True)
            st.write(f"**名前:** {data['japanese_name']} ({data['name']})")
            st.write(f"**タイプ:** {', '.join(data['types'])}")
            st.markdown(f'</div>', unsafe_allow_html=True)
            
            with st.expander("📝 育成記録をメモする"):
                st.markdown("**努力値 (0-252)**")
                hp_ev = st.number_input("HP", min_value=0, max_value=252, step=1, key='hp_ev')
                attack_ev = st.number_input("攻撃", min_value=0, max_value=252, step=1, key='attack_ev')
                defense_ev = st.number_input("防御", min_value=0, max_value=252, step=1, key='defense_ev')
                sp_attack_ev = st.number_input("特攻", min_value=0, max_value=252, step=1, key='sp_attack_ev')
                sp_defense_ev = st.number_input("特防", min_value=0, max_value=252, step=1, key='sp_defense_ev')
                speed_ev = st.number_input("素早さ", min_value=0, max_value=252, step=1, key='speed_ev')
                
                total_ev = hp_ev + attack_ev + defense_ev + sp_attack_ev + sp_defense_ev + speed_ev
                st.info(f"合計努力値: {total_ev} / 510")

                memo = st.text_area("メモ", value="", key='memo_text_area')
                
                if st.button("育成完了！", key="save_training_button_final"):
                    if total_ev > 510:
                        st.error("努力値の合計は510を超えられないぞ！⚡")
                    else:
                        evs = {'HP': hp_ev, 'こうげき': attack_ev, 'ぼうぎょ': defense_ev, 'とくこう': sp_attack_ev, 'とくぼう': sp_defense_ev, 'すばやさ': speed_ev}
                        saved = save_training_log(data, evs, memo)
                        st.session_state.save_status = saved
                        st.rerun()

            if st.session_state.save_status == True:
                st.success(f"{data['japanese_name']} の育成記録を保存したぞ！⚡")
            elif st.session_state.save_status == False:
                st.error("育成記録の保存に失敗したぞ…⚡")

        with col2:
            comment = generate_rotom_comment(data)
            st.markdown(f'<div class="comment-box">{comment}</div>', unsafe_allow_html=True)

            st.subheader("ステータス")
            df_stats = pd.DataFrame({
                "種族値": list(data["stats"].values())
            }, index=list(data["stats"].keys()))
            st.bar_chart(df_stats)

with tab2:
    st.subheader("育成完了したポケモン一覧")
    training_logs = load_training_logs()
    if training_logs:
        df_logs = pd.DataFrame(training_logs)
        
        column_to_rename = 'evs' if 'evs' in df_logs.columns else 'ivs'
        
        if 'image' in df_logs.columns:
            df_logs = df_logs.drop(columns=['image'])
        
        st.table(df_logs[['japanese_name', 'types', column_to_rename, 'memo']].rename(columns={
            'japanese_name': 'ポケモン名',
            'types': 'タイプ',
            column_to_rename: '努力値',
            'memo': 'メモ'
        }))
    else:
        st.info("まだ育成記録が登録されていないぞ！⚡")