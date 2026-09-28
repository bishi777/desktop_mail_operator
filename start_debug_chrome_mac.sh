#!/bin/bash
# デバッグ用Chrome起動スクリプト
# 使い方: ./start_debug_chrome_mac.sh [ポート番号] [プロキシキー]
# 例:     ./start_debug_chrome_mac.sh 9222            ← プロキシなし(直結)
#         ./start_debug_chrome_mac.sh 9222 erika      ← erika のIPで出る
#         ./start_debug_chrome_mac.sh 9223 sui        ← 別ポート/別IP
#
# プロキシキー (第2引数):
#   settings.py の JPROXY_PROXYS のキー名 (例: erika)。
#   省略時はプロキシなし(直結)。
#   Chrome の --proxy-server は user:pass 付きURLを受け付けず認証ダイアログが
#   出るため、proxy_auth_relay.py をローカルに立てて認証を肩代わりさせ、
#   Chrome には認証不要の 127.0.0.1:<中継ポート> を渡す。
#   中継ポートは 10000+PORT (例: 9222 → 19222)。
#
# ※ --proxy-server は Chrome プロセス全体に効くため、タブ単位でIPは分けられない。
#   キャラごとにIPを変えたい場合は、キャラごとにポートを分けて起動すること。
#     ./start_debug_chrome_mac.sh 9222 erika
#     ./start_debug_chrome_mac.sh 9223 sui
#
# ※ プロファイルは DebugProfile_<port>_<プロキシキー> となり、プロキシごとに
#   セッションが分離される。PCMAX 等は IP とセッションを紐付けるため、
#   同じキャラは常に同じプロキシキーで起動すること。
#
# 自動化(ロボット)判定の回避 (start_debug_chrome_win.bat と同一構成):
#   1) --disable-blink-features=AutomationControlled で
#      navigator.webdriver=false になり自動化バナーも消える。
#   2) 起動前に patch_chromedriver_cdc.py を実行し、chromedriver の
#      cdc_ 痕跡を除去する(Chromeが更新されても起動のたびに再パッチ)。
#   ※ platform/touch/vendor/WebGL 等の stealth は接続側(debug_drivers)で注入。
#
# 2026-07-19修正: Chromeを open 経由（launchd管理下）で起動する。
# 以前はシェルの子プロセスとして起動していたため、起動元のClaude Code
# セッションが終了するとChromeが道連れで終了していた。

PORT=${1:-9222}
PROXY_KEY=${2:-}

# このスクリプトのあるディレクトリ
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- cdc_ パッチを起動前に実行(Chrome更新で新ドライバが来ても毎回パッチ) ---
# venv の python を優先。無ければ system の python3 にフォールバック
PYEXE="$SCRIPT_DIR/myenv/bin/python"
if [ ! -x "$PYEXE" ]; then
  PYEXE="$(command -v python3 || command -v python)"
fi
if [ -n "$PYEXE" ] && [ -f "$SCRIPT_DIR/patch_chromedriver_cdc.py" ]; then
  echo "[cdc_パッチ] chromedriver をパッチします..."
  "$PYEXE" "$SCRIPT_DIR/patch_chromedriver_cdc.py"
fi

# ロボット判定回避フラグ (起動フラグとして実効性があるものだけ)
BOT_OPTS="--disable-blink-features=AutomationControlled"

# --- プロキシ設定を解決 ---
# Chrome に渡す --proxy-server 系フラグ（プロキシ未指定なら空配列）
PROXY_OPTS=()
PROXY_TAG="noproxy"
if [ -n "$PROXY_KEY" ]; then
  # 認証情報を Chrome に渡せないため、ローカル中継を立てて肩代わりさせる
  RELAY_PORT=$((10000 + PORT))
  PROXY_TAG="$PROXY_KEY"

  if [ ! -f "$SCRIPT_DIR/proxy_auth_relay.py" ]; then
    echo "エラー: proxy_auth_relay.py が見つかりません: $SCRIPT_DIR"
    exit 1
  fi

  # 既に同じ中継ポートで動いていれば再利用、いなければ起動
  if lsof -nP -iTCP:${RELAY_PORT} -sTCP:LISTEN >/dev/null 2>&1; then
    echo "[proxy] 中継は既に起動しています (127.0.0.1:${RELAY_PORT})"
  else
    RELAY_LOG="$SCRIPT_DIR/logs/proxy_relay_${PORT}.log"
    mkdir -p "$SCRIPT_DIR/logs"
    echo "[proxy] '${PROXY_KEY}' の認証中継を 127.0.0.1:${RELAY_PORT} で起動します"
    # Chrome より長生きさせる (nohup + 独立プロセス)
    nohup "$PYEXE" "$SCRIPT_DIR/proxy_auth_relay.py" \
      --key "$PROXY_KEY" --listen "$RELAY_PORT" \
      >>"$RELAY_LOG" 2>&1 &

    # 待受開始を最大5秒待つ
    for _ in $(seq 1 25); do
      lsof -nP -iTCP:${RELAY_PORT} -sTCP:LISTEN >/dev/null 2>&1 && break
      sleep 0.2
    done
    if ! lsof -nP -iTCP:${RELAY_PORT} -sTCP:LISTEN >/dev/null 2>&1; then
      echo "エラー: 中継の起動に失敗しました。ログを確認してください: $RELAY_LOG"
      tail -n 20 "$RELAY_LOG" 2>/dev/null
      exit 1
    fi
  fi

  # localhost を除外すると remote-debugging が中継を経由せず安定する
  # ('<-loopback>' はシェルのリダイレクトと解釈されないよう配列で渡す)
  PROXY_OPTS=(
    "--proxy-server=127.0.0.1:${RELAY_PORT}"
    "--proxy-bypass-list=<-loopback>"
  )
fi

# 既に同ポートで起動済みなら二重起動しない
if curl -s -m 2 "http://localhost:${PORT}/json/version" >/dev/null 2>&1; then
  echo "port ${PORT} のデバッグChromeは既に起動しています"
  exit 0
fi

# プロキシ有無・キーごとにプロファイルを分ける(IPとセッションの紐付け対策)
PROFILE_DIR="$HOME/Library/Application Support/Google/Chrome/DebugProfile_${PORT}_${PROXY_TAG}"

echo "デバッグ用Chromeを起動します (port: $PORT, proxy: $PROXY_TAG, bot回避: ON)"
open -na "Google Chrome" --args \
  --remote-debugging-port=$PORT \
  --user-data-dir="$PROFILE_DIR" \
  $BOT_OPTS \
  ${PROXY_OPTS[@]+"${PROXY_OPTS[@]}"} \
  --disable-popup-blocking \
  --disk-cache-size=104857600 \
  --media-cache-size=52428800
