# AtCoder Python Manager

AtCoderをはじめとする競技プログラミング向けの管理・支援アプリケーションです。

Pythonで競技プログラミングを行うユーザーを対象として、以下の機能を提供することを目的としています。

* AtCoderのレート・成績管理
* レート推移のグラフ表示
* Python向け競技プログラミングテンプレート
* コードスニペット管理
* Pythonコードの実行
* テストケース管理
* 今後、問題管理や実力分析などの機能を追加予定

現在はプロトタイプを開発中です。

## 開発環境

* Python 3.12+
* PySide6
* SQLite
* requests
* pyqtgraph

## セットアップ

### 1. リポジトリを取得

```bash
git clone <repository-url>
cd atcoder-python-manager
```

### 2. 仮想環境を作成

Windows:

```powershell
python -m venv .venv
```

### 3. 仮想環境を有効化

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. 依存パッケージをインストール

```powershell
pip install -r requirements.txt
```

## 起動方法

```powershell
python main.py
```

※ 現在はプロトタイプ開発中のため、実装状況によって起動方法が変更される可能性があります。

## ディレクトリ構成

```text
project/
│
├── main.py
├── config.json
├── database.db
├── requirements.txt
├── README.md
│
├── ui/
│   ├── dashboard.py
│   ├── settings.py
│   ├── snippets.py
│   └── template.py
│
├── core/
│   ├── atcoder.py
│   ├── database.py
│   └── runner.py
│
├── templates/
│   ├── unionfind.py
│   ├── bfs.py
│   └── dfs.py
│
├── assets/
│
└── tests/
```

## 開発状況

### Prototype v0.1

* [x] プロジェクト作成
* [x] Gitリポジトリ作成
* [x] Python仮想環境構築
* [x] ディレクトリ構成作成
* [ ] requirements.txt作成
* [ ] README作成
* [ ] GUI基盤
* [ ] AtCoder情報取得
* [ ] レートグラフ
* [ ] Pythonテンプレート管理
* [ ] コード実行
* [ ] テストケース管理
* [ ] スニペット管理

## 開発方針

まずは最小限の機能を持つプロトタイプを完成させ、その後、実際に競技プログラミングで使用しながら必要な機能を追加していきます。

特にPythonでの競技プログラミングを効率化できる機能を重視します。

## License

未定
