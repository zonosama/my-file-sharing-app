# 🚀 Streamlit Cloudへのデプロイ手順

## 前提条件

- GitHubアカウント
- Streamlit Cloudアカウント（GitHubでログイン可能）

## ステップ1: GitHubリポジトリの作成

1. [GitHub](https://github.com)にログイン
2. 「New repository」をクリック
3. リポジトリ名を入力（例: `my-file-sharing-app`）
4. 「Public」を選択（無料プランではPublicのみ）
5. 「Create repository」をクリック

## ステップ2: コードをGitHubにプッシュ

ローカルのPowerShellまたはコマンドプロンプトで以下を実行：

```bash
# Gitリポジトリを初期化
git init

# ファイルをステージング
git add .

# コミット


# GitHubリポジトリを追加（YOUR_USERNAMEとYOUR_REPOを自分のものに変更）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# mainブランチにプッシュ
git branch -M main
git push -u origin main
```

## ステップ3: Streamlit Cloudでデプロイ

1. [Streamlit Cloud](https://share.streamlit.io/)にアクセス
2. GitHubアカウントでサインイン
3. 「New app」をクリック
4. リポジトリ、ブランチ、メインファイル（`app.py`）を選択
5. 「Deploy!」をクリック

## ステップ4: アプリへのアクセス

デプロイが完了すると、以下のようなURLが発行されます：
```
https://YOUR_USERNAME-YOUR_REPO-app-xxxxx.streamlit.app/
```

## ⚠️ 重要な制限事項

### ファイルの永続性について

**現在のバージョンでは、アップロードされたファイルはアプリが再起動されると消えます。**

これは、Streamlit Cloudが永続的なファイルストレージを提供していないためです。

### 改善案

永続的なファイル保存が必要な場合は、以下のクラウドストレージサービスとの連携を検討してください：

1. **Google Drive API**（推奨・無料15GB）
2. **Dropbox API**（無料2GB）
3. **AWS S3**（有料だが信頼性高い）
4. **Cloudflare R2**（無料10GB/月）

## 📊 Streamlit Cloud無料プランの制限

- **ストレージ**: 永続的なストレージなし
- **メモリ**: 1GB
- **CPU**: 共有コア
- **アプリ数**: 無制限（Public）
- **訪問者数**: 無制限

## 🔐 セキュリティの推奨事項

Public Repositoryの場合：
- シークレット情報は`secrets.toml`を使用（Streamlit Cloud上で設定）
- APIキーやパスワードをコードに直接書かない
- `.env`ファイルはGitにコミットしない

## 🆘 トラブルシューティング

### アプリが起動しない場合

1. `requirements.txt`に必要なパッケージが全て記載されているか確認
2. Streamlit Cloudのログを確認
3. ローカルで`streamlit run app.py`が動作するか確認

### アプリが再起動を繰り返す場合

- メモリ使用量が1GBを超えている可能性
- 重い処理を軽減する必要がある

## 📝 更新方法

アプリを更新するには：

```bash
git add .
git commit -m "Update: 説明"
git push
```

GitHubにプッシュすると、Streamlit Cloudが自動的に再デプロイします。

## 🔗 便利なリンク

- [Streamlit Cloud公式ドキュメント](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit フォーラム](https://discuss.streamlit.io/)
- [GitHub Pages](https://github.com)
