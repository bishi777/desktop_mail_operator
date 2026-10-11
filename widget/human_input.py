"""CDP(Chrome DevTools Protocol) ベースの人間らしい入力操作。

JS による直接操作（execute_script の click / value 代入）は
  - click   : isTrusted:false / 先行イベントなし / 座標0
  - value代入: keydown も input も一切発生しない
となり Bot 判定の決定的な材料になる（9222 で実測確認済み）。

CDP の Input.* はブラウザの入力層に直接イベントを注入するので
isTrusted:true になり、実際の操作と区別がつかない。

全プラットフォーム（happymail / pcmax / ikukuru / jmail）共通で使う。
循環 import を避けるため widget.func からは独立させている。
"""
import time
import random

from selenium.common.exceptions import ElementClickInterceptedException


def _fire_mouse_move(driver, x, y, wait=None):
  """mouseMoved を送る。

  Chrome はアイドル後の最初の mouseMoved に応答を返さず、
  CDP 側が 5 秒きっかりでタイムアウトすることがある（9222 で実測）。
  ただし別スレッドに逃がすと Selenium の HTTP 接続を占有して
  後続コマンドが詰まるため、素直に同期で送る。
  BAN されるより遅い方がよいという方針なので、待たされても許容する。
  """
  try:
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
      "type": "mouseMoved", "x": x, "y": y, "button": "none"})
  except Exception:
    pass  # 応答待ちのタイムアウトは無視（イベント自体は届いている）
  if wait:
    time.sleep(wait)


def human_sleep(min_sec=1.0, max_sec=3.0):
  """人間的なランダム待機（正規分布寄り）"""
  mean = (min_sec + max_sec) / 2
  std = (max_sec - min_sec) / 4
  t = max(min_sec, min(max_sec, random.gauss(mean, std)))
  time.sleep(t)


def _element_center(driver, element):
  """要素の中心のビューポート座標 (x, y) を返す。画面外なら中央へスクロールしてから測る。"""
  driver.execute_script(
    "arguments[0].scrollIntoView({block:'center', inline:'center'});", element)
  time.sleep(random.uniform(0.15, 0.4))
  rect = driver.execute_script(
    "const r = arguments[0].getBoundingClientRect();"
    "return {x: r.left + r.width/2, y: r.top + r.height/2, w: r.width, h: r.height};",
    element)
  # クリック位置を中心から少しずらす（毎回ぴったり中心は不自然）
  x = rect["x"] + random.uniform(-rect["w"] / 6, rect["w"] / 6)
  y = rect["y"] + random.uniform(-rect["h"] / 6, rect["h"] / 6)
  return x, y


# 直前のカーソル位置を覚えておく（毎回ワープせず、前の位置から動かすため）
_last_cursor = {"x": None, "y": None}


def _bezier_point(p0, p1, p2, p3, t):
  """3次ベジェ曲線上の点を返す。"""
  u = 1 - t
  return (u * u * u * p0 + 3 * u * u * t * p1
          + 3 * u * t * t * p2 + t * t * t * p3)


def human_click(driver, element, move_steps=None):
  """CDP で実際のマウス操作を再現してクリックする。

  直前のカーソル位置からベジェ曲線を描いて対象まで移動し、
  mouseMoved（複数回）→ mousePressed → mouseReleased を送る。
  isTrusted:true かつ先行イベント付きになり、JS クリックの痕跡が残らない。

  mouseMoved はホバー処理やレイアウト再計算の完了を待つため
  1回あたり数秒かかることがあるが、BAN されるよりは遅い方がよいので
  既定で軌跡を多めに刻む。急ぎたい場合のみ move_steps=1 を指定する。
  CDP が使えない場合は通常クリック → JS クリックの順にフォールバックする。
  """
  try:
    x, y = _element_center(driver, element)
    if move_steps is None:
      move_steps = random.randint(8, 18)  # 軌跡の細かさもランダム

    # 始点: 直前のカーソル位置。無ければ画面内の適当な位置から。
    if _last_cursor["x"] is None:
      vw = driver.execute_script("return window.innerWidth;") or 390
      vh = driver.execute_script("return window.innerHeight;") or 844
      start_x = random.uniform(vw * 0.15, vw * 0.85)
      start_y = random.uniform(vh * 0.15, vh * 0.85)
    else:
      start_x, start_y = _last_cursor["x"], _last_cursor["y"]

    # 制御点を始点〜終点の左右にずらし、わずかに弧を描く軌跡にする
    dx, dy = x - start_x, y - start_y
    dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
    # 弧の深さ。距離が近いと弧が浅くなり直線的になるので下限を厚めに取る。
    # （同じ要素を連打するときは移動距離がほぼ 0 になるため、下限が効く）
    bow = max(random.uniform(45, 110), random.uniform(0.15, 0.35) * dist)
    side = random.choice((1, -1))
    # 進行方向に対する法線方向へ制御点をずらす
    nx, ny = -dy / dist, dx / dist
    c1x = start_x + dx * random.uniform(0.2, 0.4) + nx * bow * side
    c1y = start_y + dy * random.uniform(0.2, 0.4) + ny * bow * side
    c2x = start_x + dx * random.uniform(0.6, 0.8) + nx * bow * side * 0.5
    c2y = start_y + dy * random.uniform(0.6, 0.8) + ny * bow * side * 0.5

    for i in range(1, move_steps + 1):
      t = i / move_steps
      # ease-in-out（動き出しと止まり際が遅い、人の手の動き）
      te = 3 * t * t - 2 * t * t * t
      px = _bezier_point(start_x, c1x, c2x, x, te)
      py = _bezier_point(start_y, c1y, c2y, y, te)
      # 手ぶれ（終点に近いほど小さくなるが、最後まで多少は残る）
      jitter = (0.25 + 0.75 * (1 - te)) * random.uniform(0, 3.5)
      px += random.uniform(-jitter, jitter)
      py += random.uniform(-jitter, jitter)
      # 移動間隔もランダム。中盤は速く、終盤は減速する
      base = 0.012 + 0.05 * te          # 終盤ほど長めに止まる
      gap = random.uniform(base * 0.5, base * 1.8)
      # 送信の待ち時間を移動間隔そのものに充てる（応答は待たない）
      _fire_mouse_move(driver, px, py, wait=gap)
      # ときどき途中で止まる（何かを見た/迷った）
      if random.random() < 0.08:
        time.sleep(random.uniform(0.08, 0.45))

    # 狙いを定める間（押す直前の一拍）
    time.sleep(random.uniform(0.08, 0.45))
    for ev in ("mousePressed", "mouseReleased"):
      driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": ev,
        "x": x, "y": y,
        "button": "left",
        "clickCount": 1,
      })
      if ev == "mousePressed":
        time.sleep(random.uniform(0.05, 0.16))  # 押してから離すまで
    _last_cursor["x"], _last_cursor["y"] = x, y
    # 押した後の一拍（人はクリック直後すぐ次の操作をしない）
    time.sleep(random.uniform(0.1, 0.5))
    return True
  except Exception as e:
    print(f"[human_click] CDP クリック失敗({type(e).__name__}) → 通常クリックにフォールバック")
    try:
      element.click()
      return True
    except ElementClickInterceptedException:
      driver.execute_script("arguments[0].click();", element)
      return True


def human_type(driver, element, text, clear=True):
  """CDP で「定型文を貼り付ける」操作としてテキストを入力する。

  人間も定型文はコピペで一瞬で貼るため、1文字ずつ打つ必要はない。
  Input.insertText は貼り付けと同じ経路で、beforeinput / input が
  いずれも isTrusted:true で発火する（9222 で実測確認済み）。

  重要: 手動の dispatchEvent(new Event('input')) を足してはいけない。
  手動 dispatch は isTrusted:false になり、Bot 判定の材料になる（実測で確認済み）。
  value への直接代入はイベントが一切発生しないため、最後のフォールバックでのみ使う。
  """
  if text is None:
    text = ""
  text = str(text)
  try:
    human_click(driver, element)  # まずフォーカスを当てる（実クリック）
    # 貼り付ける前の一拍（入力欄を選んでから貼るまでの間）
    time.sleep(random.uniform(0.2, 0.6))
    if clear:
      # 全選択 → 上書き。insertText は選択範囲を置き換えるので、
      # 選択状態にしておけば既存テキストはそのまま消える。
      driver.execute_script(
        "arguments[0].focus();"
        "if (arguments[0].setSelectionRange) {"
        "  arguments[0].setSelectionRange(0, (arguments[0].value || '').length);"
        "}", element)
      time.sleep(random.uniform(0.05, 0.15))
      if not text:
        # 空にするだけなら Backspace 一発（選択範囲が消える）
        driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
          "type": "keyDown", "key": "Backspace", "code": "Backspace",
          "windowsVirtualKeyCode": 8, "nativeVirtualKeyCode": 8})
        driver.execute_cdp_cmd("Input.dispatchKeyEvent", {
          "type": "keyUp", "key": "Backspace", "code": "Backspace",
          "windowsVirtualKeyCode": 8, "nativeVirtualKeyCode": 8})
        time.sleep(random.uniform(0.05, 0.15))
        if driver.execute_script("return arguments[0].value || '';", element):
          driver.execute_script(
            "arguments[0].value='';"
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", element)
        return True
    if text:
      # 貼り付け（選択範囲があれば置き換わる）
      driver.execute_cdp_cmd("Input.insertText", {"text": text})
      # 貼った内容をざっと確認する間
      time.sleep(random.uniform(0.3, 0.9))
    return True
  except Exception as e:
    print(f"[human_type] CDP 入力失敗({type(e).__name__}) → フォールバック")
    try:
      if clear:
        element.clear()
      element.send_keys(text)
      return True
    except Exception:
      driver.execute_script("arguments[0].value = arguments[1];", element, text)
      driver.execute_script(
        "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));", element)
      return True
