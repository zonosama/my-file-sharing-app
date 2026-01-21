import streamlit as st
import os
from pathlib import Path
import shutil
from datetime import datetime
import json
import hashlib
import uuid

# ページ設定
st.set_page_config(
    page_title="ファイル共有サイト",
    page_icon="📁",
    layout="wide"
)

# ディレクトリとファイルパスの設定
UPLOAD_DIR = Path("uploaded_files")
METADATA_FILE = Path("file_metadata.json")
USERS_FILE = Path("users.json")
SHARED_LINKS_FILE = Path("shared_links.json")

UPLOAD_DIR.mkdir(exist_ok=True)

# カスタムCSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .file-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
    }
    .tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        margin: 0.2rem;
        background-color: #e3f2fd;
        border-radius: 0.3rem;
        font-size: 0.85rem;
    }
    .folder-badge {
        background-color: #fff3cd;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ユーティリティ関数
def hash_password(password):
    """パスワードをハッシュ化"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """ユーザー情報を読み込み"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """ユーザー情報を保存"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_metadata():
    """ファイルメタデータを読み込み"""
    if METADATA_FILE.exists():
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    """ファイルメタデータを保存"""
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def load_shared_links():
    """共有リンク情報を読み込み"""
    if SHARED_LINKS_FILE.exists():
        with open(SHARED_LINKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_shared_links(links):
    """共有リンク情報を保存"""
    with open(SHARED_LINKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

def generate_share_link(file_path):
    """共有リンクを生成"""
    link_id = str(uuid.uuid4())[:8]
    links = load_shared_links()
    links[link_id] = {
        'file_path': str(file_path),
        'created_at': datetime.now().isoformat(),
        'file_name': file_path.name
    }
    save_shared_links(links)
    return link_id

def authenticate_user(username, password):
    """ユーザー認証"""
    users = load_users()
    if username in users:
        return users[username]['password'] == hash_password(password)
    return False

def register_user(username, password):
    """新規ユーザー登録"""
    users = load_users()
    if username in users:
        return False
    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    save_users(users)
    return True

# セッション状態の初期化
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_register' not in st.session_state:
    st.session_state.show_register = False

# 共有リンクからのアクセスをチェック
query_params = st.query_params
if 'share' in query_params and not st.session_state.authenticated:
    link_id = query_params['share']
    links = load_shared_links()
    
    if link_id in links:
        st.title("📤 共有ファイル")
        link_info = links[link_id]
        file_path = Path(link_info['file_path'])
        
        if file_path.exists():
            st.success(f"✅ ファイル: {link_info['file_name']}")
            st.info(f"🕐 共有日時: {link_info['created_at'][:19].replace('T', ' ')}")
            
            with open(file_path, 'rb') as f:
                st.download_button(
                    label=f"⬇️ {link_info['file_name']} をダウンロード",
                    data=f,
                    file_name=link_info['file_name'],
                    type="primary"
                )
        else:
            st.error("❌ ファイルが見つかりません")
        st.stop()
    else:
        st.error("❌ 無効な共有リンクです")
        st.stop()

# 認証画面
if not st.session_state.authenticated:
    st.title("🔐 ファイル共有サイト - ログイン")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.show_register:
            st.subheader("ログイン")
            username = st.text_input("ユーザー名", key="login_username")
            password = st.text_input("パスワード", type="password", key="login_password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("ログイン", type="primary", use_container_width=True):
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("❌ ユーザー名またはパスワードが間違っています")
            
            with col_b:
                if st.button("新規登録", use_container_width=True):
                    st.session_state.show_register = True
                    st.rerun()
        
        else:
            st.subheader("新規ユーザー登録")
            new_username = st.text_input("ユーザー名", key="reg_username")
            new_password = st.text_input("パスワード", type="password", key="reg_password")
            confirm_password = st.text_input("パスワード（確認）", type="password", key="reg_confirm")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("登録", type="primary", use_container_width=True):
                    if not new_username or not new_password:
                        st.error("❌ ユーザー名とパスワードを入力してください")
                    elif new_password != confirm_password:
                        st.error("❌ パスワードが一致しません")
                    elif len(new_password) < 4:
                        st.error("❌ パスワードは4文字以上にしてください")
                    else:
                        if register_user(new_username, new_password):
                            st.success("✅ 登録完了！ログインしてください")
                            st.session_state.show_register = False
                            st.rerun()
                        else:
                            st.error("❌ このユーザー名は既に使用されています")
            
            with col_b:
                if st.button("ログインに戻る", use_container_width=True):
                    st.session_state.show_register = False
                    st.rerun()
        
        st.markdown("---")
        st.info("💡 初回の方は「新規登録」からアカウントを作成してください")
    
    st.stop()

# メイン画面（認証後）
st.title(f"📁 マイファイル共有サイト - {st.session_state.username}さん")

# Streamlit Cloudでの実行を検知
if os.getenv("STREAMLIT_SHARING_MODE") or os.getenv("HOSTNAME", "").startswith("streamlit"):
    st.warning("⚠️ Streamlit Cloud上で動作中：アップロードファイルは一時的です（アプリ再起動時に消える可能性があります）")

# ログアウトボタン
col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🚪 ログアウト"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

st.markdown("---")

# メタデータの読み込み
metadata = load_metadata()

# タブを作成
tab1, tab2, tab3 = st.tabs(["📤 ファイルアップロード", "📂 ファイル一覧", "🗂️ フォルダ管理"])

# タブ1: ファイルアップロード
with tab1:
    st.header("ファイルをアップロード")
    
    # フォルダ選択
    folders = list(set([meta.get('folder', 'なし') for meta in metadata.values()]))
    if 'なし' not in folders:
        folders.insert(0, 'なし')
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_folder = st.selectbox("保存先フォルダ", folders)
    with col2:
        new_folder = st.text_input("新しいフォルダ名")
        if new_folder:
            selected_folder = new_folder
    
    uploaded_files = st.file_uploader(
        "ファイルを選択してください",
        accept_multiple_files=True,
        help="複数ファイルを同時にアップロードできます"
    )
    
    # メモとタグの入力
    memo = st.text_area("📝 メモ（オプション）", help="ファイルの説明やメモを記入できます")
    tags_input = st.text_input("🏷️ タグ（カンマ区切り）", help="例: 仕事, 重要, プロジェクトA")
    
    if uploaded_files:
        st.write(f"選択されたファイル数: {len(uploaded_files)}")
        
        if st.button("アップロード実行", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            
            for idx, uploaded_file in enumerate(uploaded_files):
                # ファイル名の重複を避ける
                file_path = UPLOAD_DIR / uploaded_file.name
                counter = 1
                original_name = uploaded_file.name
                name, ext = os.path.splitext(original_name)
                
                while file_path.exists():
                    new_name = f"{name}_{counter}{ext}"
                    file_path = UPLOAD_DIR / new_name
                    counter += 1
                
                # ファイルを保存
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # メタデータを保存
                metadata[str(file_path)] = {
                    'original_name': uploaded_file.name,
                    'upload_date': datetime.now().isoformat(),
                    'uploader': st.session_state.username,
                    'memo': memo,
                    'tags': tags,
                    'folder': selected_folder
                }
                save_metadata(metadata)
                
                # 進捗を更新
                progress = (idx + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"アップロード中: {uploaded_file.name}")
            
            status_text.empty()
            progress_bar.empty()
            st.success(f"✅ {len(uploaded_files)}個のファイルをアップロードしました！")
            st.balloons()

# タブ2: ファイル一覧
with tab2:
    st.header("アップロード済みファイル")
    
    # フィルター機能
    col1, col2, col3 = st.columns(3)
    with col1:
        search_query = st.text_input("🔍 ファイル名で検索", "")
    with col2:
        # フォルダフィルター
        all_folders = list(set([meta.get('folder', 'なし') for meta in metadata.values()]))
        all_folders.insert(0, "すべて")
        folder_filter = st.selectbox("フォルダで絞り込み", all_folders)
    with col3:
        sort_by = st.selectbox("並び替え", ["名前", "日付（新しい順）", "日付（古い順）", "サイズ"])
    
    # タグフィルター
    all_tags = set()
    for meta in metadata.values():
        all_tags.update(meta.get('tags', []))
    
    if all_tags:
        selected_tags = st.multiselect("🏷️ タグで絞り込み", sorted(all_tags))
    else:
        selected_tags = []
    
    # ファイル一覧を取得
    files = list(UPLOAD_DIR.glob("*"))
    files = [f for f in files if f.is_file()]
    
    # 検索フィルタ
    if search_query:
        files = [f for f in files if search_query.lower() in f.name.lower()]
    
    # フォルダフィルタ
    if folder_filter != "すべて":
        files = [f for f in files if metadata.get(str(f), {}).get('folder', 'なし') == folder_filter]
    
    # タグフィルタ
    if selected_tags:
        files = [f for f in files if all(tag in metadata.get(str(f), {}).get('tags', []) for tag in selected_tags)]
    
    # ソート
    if sort_by == "名前":
        files.sort(key=lambda x: x.name)
    elif sort_by == "日付（新しい順）":
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    elif sort_by == "日付（古い順）":
        files.sort(key=lambda x: x.stat().st_mtime)
    elif sort_by == "サイズ":
        files.sort(key=lambda x: x.stat().st_size, reverse=True)
    
    # ファイル情報を表示
    if files:
        st.write(f"📊 合計: {len(files)}個のファイル")
        
        # ファイルカードを表示
        for file_path in files:
            with st.container():
                # ファイル情報を取得
                file_size = file_path.stat().st_size
                file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
                file_meta = metadata.get(str(file_path), {})
                
                # サイズを読みやすく表示
                if file_size < 1024:
                    size_str = f"{file_size} B"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                elif file_size < 1024 * 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"
                else:
                    size_str = f"{file_size / (1024 * 1024 * 1024):.2f} GB"
                
                # ファイルヘッダー
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"📄 **{file_path.name}**")
                    if file_meta.get('folder', 'なし') != 'なし':
                        st.markdown(f'<span class="folder-badge">📁 {file_meta["folder"]}</span>', unsafe_allow_html=True)
                with col2:
                    st.write(f"📦 {size_str}")
                with col3:
                    st.write(f"🕐 {file_date.strftime('%Y-%m-%d %H:%M')}")
                
                # メモとタグ
                if file_meta.get('memo'):
                    st.write(f"📝 {file_meta['memo']}")
                
                if file_meta.get('tags'):
                    tags_html = ' '.join([f'<span class="tag">🏷️ {tag}</span>' for tag in file_meta['tags']])
                    st.markdown(tags_html, unsafe_allow_html=True)
                
                # アクション
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="⬇️ ダウンロード",
                            data=f,
                            file_name=file_path.name,
                            key=f"download_{file_path.name}_{file_path.stat().st_mtime}",
                            use_container_width=True
                        )
                
                with col2:
                    if st.button("🔗 共有リンク", key=f"share_{file_path.name}_{file_path.stat().st_mtime}",
                                use_container_width=True):
                        link_id = generate_share_link(file_path)
                        share_url = f"{st.query_params.get('', [''])}?share={link_id}"
                        st.code(share_url, language=None)
                        st.success("✅ 共有リンクを生成しました！このURLを相手に送信してください")
                
                with col3:
                    if st.button("✏️ 編集", key=f"edit_{file_path.name}_{file_path.stat().st_mtime}",
                                use_container_width=True):
                        st.session_state[f"editing_{file_path}"] = True
                
                with col4:
                    if st.button("🗑️ 削除", key=f"delete_{file_path.name}_{file_path.stat().st_mtime}",
                                use_container_width=True):
                        file_path.unlink()
                        if str(file_path) in metadata:
                            del metadata[str(file_path)]
                            save_metadata(metadata)
                        st.success(f"✅ {file_path.name} を削除しました")
                        st.rerun()
                
                # 編集モード
                if st.session_state.get(f"editing_{file_path}", False):
                    with st.expander("✏️ メタデータを編集", expanded=True):
                        new_memo = st.text_area("メモ", value=file_meta.get('memo', ''), 
                                               key=f"memo_edit_{file_path}")
                        new_tags = st.text_input("タグ（カンマ区切り）", 
                                                value=', '.join(file_meta.get('tags', [])),
                                                key=f"tags_edit_{file_path}")
                        new_folder = st.text_input("フォルダ", value=file_meta.get('folder', 'なし'),
                                                  key=f"folder_edit_{file_path}")
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("💾 保存", key=f"save_edit_{file_path}", type="primary",
                                       use_container_width=True):
                                file_meta['memo'] = new_memo
                                file_meta['tags'] = [tag.strip() for tag in new_tags.split(',') if tag.strip()]
                                file_meta['folder'] = new_folder
                                metadata[str(file_path)] = file_meta
                                save_metadata(metadata)
                                st.session_state[f"editing_{file_path}"] = False
                                st.success("✅ 更新しました")
                                st.rerun()
                        
                        with col_b:
                            if st.button("❌ キャンセル", key=f"cancel_edit_{file_path}",
                                       use_container_width=True):
                                st.session_state[f"editing_{file_path}"] = False
                                st.rerun()
                
                st.markdown("---")
    else:
        st.info("📭 条件に一致するファイルがありません")

# タブ3: フォルダ管理
with tab3:
    st.header("フォルダ管理")
    
    # フォルダ一覧
    folders = {}
    for file_path, meta in metadata.items():
        folder = meta.get('folder', 'なし')
        if folder not in folders:
            folders[folder] = []
        folders[folder].append(file_path)
    
    for folder, file_paths in sorted(folders.items()):
        with st.expander(f"📁 {folder} ({len(file_paths)}ファイル)", expanded=True):
            for fp in file_paths:
                file_path = Path(fp)
                if file_path.exists():
                    st.write(f"📄 {file_path.name}")
            
            # フォルダ名変更
            if folder != 'なし':
                new_name = st.text_input(f"フォルダ名を変更", value=folder, key=f"rename_{folder}")
                if st.button(f"名前を変更", key=f"btn_rename_{folder}"):
                    for fp in file_paths:
                        if fp in metadata:
                            metadata[fp]['folder'] = new_name
                    save_metadata(metadata)
                    st.success(f"✅ フォルダ名を '{new_name}' に変更しました")
                    st.rerun()

# サイドバー: 統計情報
with st.sidebar:
    st.header("📊 統計情報")
    
    all_files = list(UPLOAD_DIR.glob("*"))
    all_files = [f for f in all_files if f.is_file()]
    
    total_files = len(all_files)
    total_size = sum(f.stat().st_size for f in all_files)
    
    if total_size < 1024:
        size_str = f"{total_size} B"
    elif total_size < 1024 * 1024:
        size_str = f"{total_size / 1024:.2f} KB"
    elif total_size < 1024 * 1024 * 1024:
        size_str = f"{total_size / (1024 * 1024):.2f} MB"
    else:
        size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
    
    st.metric("総ファイル数", total_files)
    st.metric("総サイズ", size_str)
    st.metric("フォルダ数", len(folders))
    
    st.markdown("---")
    st.markdown("### ℹ️ 使い方")
    st.markdown("""
    1. **アップロード**タブでファイルを選択
    2. フォルダ、メモ、タグを設定（任意）
    3. **ファイル一覧**タブで管理
    4. **共有リンク**ボタンで他人と共有
    5. **フォルダ管理**タブでフォルダを整理
    """)
    
    st.markdown("---")
    
    # 共有リンク一覧
    links = load_shared_links()
    if links:
        st.markdown("### 🔗 共有リンク一覧")
        for link_id, link_info in list(links.items())[:5]:
            st.write(f"📄 {link_info['file_name']}")
            st.caption(f"ID: {link_id}")
    
    st.markdown("---")
    if st.button("🗑️ 全ファイル削除", type="secondary"):
        if all_files:
            for file in all_files:
                file.unlink()
            # メタデータもクリア
            save_metadata({})
            st.success("全ファイルを削除しました")
            st.rerun()
