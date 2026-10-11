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


def human_click(driver, element, move_steps=None):
  """CDP で実際のマウス操作を再現してクリックする。

  mouseMoved を複数回（軌跡）→ mousePressed → mouseReleased の順に送るので
  isTrusted:true かつ先行イベント付きになり、JS クリックの痕跡が残らない。
  CDP が使えない場合は通常クリック → JS クリックの順にフォールバックする。
  """
  try:
    x, y = _element_center(driver, element)
    # mouseMoved はホバー処理やレイアウト再計算の完了を待つため、
    # ページによっては1回に数秒かかる（9222 で実測: 1回あたり最大5秒）。
    # 先行イベントは1回あれば isTrusted:true と「移動してから押した」痕跡が残るので、
    # 既定では1回だけ送る。軌跡を増やしたい場合のみ move_steps を指定する。
    if move_steps is None:
      move_steps = 1
    start_x = x + random.uniform(-120, 120)
    start_y = y + random.uniform(-120, 120)
    for i in range(1, move_steps + 1):
      t = i / move_steps
      # ease-out 気味に（人は対象に近づくほど減速する）
      t = 1 - (1 - t) ** 2
      driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseMoved",
        "x": start_x + (x - start_x) * t,
        "y": start_y + (y - start_y) * t,
        "button": "none",
      })
      if move_steps > 1:
        time.sleep(random.uniform(0.01, 0.05))
    time.sleep(random.uniform(0.05, 0.18))  # 狙いを定める間
    for ev in ("mousePressed", "mouseReleased"):
      driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": ev,
        "x": x, "y": y,
        "button": "left",
        "clickCount": 1,
      })
      if ev == "mousePressed":
        time.sleep(random.uniform(0.04, 0.12))  # 押してから離すまで
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
