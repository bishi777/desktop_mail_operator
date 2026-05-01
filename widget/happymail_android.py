"""ハッピーメールAndroidネイティブアプリ自動化モジュール.

Appium UiAutomator2 driver で `jp.co.i_bec.suteki_happy` を操作する。
"""
import os
import re
import subprocess
import tempfile
import time
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import io

import requests
from PIL import Image
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import (
  NoSuchElementException,
  StaleElementReferenceException,
  WebDriverException,
)

from widget import func


APP_PACKAGE = "jp.co.i_bec.suteki_happy"

ID_MESSAGE_TAB = f"{APP_PACKAGE}:id/maintab_footer_frame_message"
ID_MYPAGE_TAB = f"{APP_PACKAGE}:id/maintab_footer_frame_mypage"
ID_SEARCH_TAB = f"{APP_PACKAGE}:id/maintab_footer_frame_search"
ID_BOARD_TAB = f"{APP_PACKAGE}:id/maintab_footer_frame_board"
ID_TYPELIST_TAB = f"{APP_PACKAGE}:id/maintab_footer_frame_typelist"

ID_MESSAGE_BADGE = f"{APP_PACKAGE}:id/maintab_footer_badge_message"
ID_BADGE_COUNT = f"{APP_PACKAGE}:id/common_badge_tv_count"
ID_BADGE_COUNT_OVER = f"{APP_PACKAGE}:id/common_badge_tv_count_hundred_over"

# メッセージタブ内
ID_MSG_BTN_ALL = f"{APP_PACKAGE}:id/maintab_message_btn_all"
ID_MSG_BTN_UNREAD = f"{APP_PACKAGE}:id/maintab_message_btn_unread"
ID_MSG_BTN_UNREPLY = f"{APP_PACKAGE}:id/maintab_message_btn_unreply"
ID_MSG_BTN_REPLY = f"{APP_PACKAGE}:id/maintab_message_btn_reply"
ID_MSG_BTN_SAVED = f"{APP_PACKAGE}:id/maintab_message_btn_saved"
ID_MSG_RV = f"{APP_PACKAGE}:id/maintab_message_rv_message"

# メッセージリスト行
ID_FRAME_SWIPE = f"{APP_PACKAGE}:id/frame_swipe"
ID_TXT_NAME = f"{APP_PACKAGE}:id/txt_name"
ID_TXT_AGE = f"{APP_PACKAGE}:id/txt_age"
ID_TXT_RESIDENCE = f"{APP_PACKAGE}:id/txt_residence"
ID_TXT_MESSAGE = f"{APP_PACKAGE}:id/txt_message"
ID_TXT_POST_TIME = f"{APP_PACKAGE}:id/txt_post_time"

# スレッド詳細
ID_TXT_HEADER_TITLE = f"{APP_PACKAGE}:id/txt_header_title"
ID_HEADER_BACK = f"{APP_PACKAGE}:id/frame_header_back_btn"
ID_HEADER_RIGHT_BTN_1 = f"{APP_PACKAGE}:id/header_right_btn_1"
ID_EDIT_INPUT = f"{APP_PACKAGE}:id/edit_text_message_input"
ID_BTN_SEND = f"{APP_PACKAGE}:id/btn_message_send"
ID_BTN_MENU_SWITCH = f"{APP_PACKAGE}:id/btn_menu_switch"
ID_BTN_GALLERY = f"{APP_PACKAGE}:id/btn_gallery"
ID_TXT_VIA_FROM = f"{APP_PACKAGE}:id/txt_via_from"
ID_TXT_VIA_LINK = f"{APP_PACKAGE}:id/txt_via_link"
ID_LOADING_LOCK = f"{APP_PACKAGE}:id/activity_default_loading_lock"

# 画像トリム画面
ID_FRAGMENT_PHOTO_TRIM_IV = f"{APP_PACKAGE}:id/fragment_photo_trim_iv_size"

# ユーザー詳細・見ちゃいや
ID_BTN_ELLIPSES_MENU = f"{APP_PACKAGE}:id/btn_ellipses_menu"
ID_MENU_ROW_FRAME = f"{APP_PACKAGE}:id/listrow_common_menudialog_frombottom_frame"
ID_MENU_ROW_TITLE = f"{APP_PACKAGE}:id/listrow_common_menudialog_frombottom_tv_title"
ID_BLOCK_REGISTER_BTN = f"{APP_PACKAGE}:id/cutsom_pressble_button_btn"
ID_BLOCK_REGISTER_TITLE = f"{APP_PACKAGE}:id/cutsom_pressble_button_tv_title"
ID_BLOCK_TV_NAME = f"{APP_PACKAGE}:id/fragment_block_tv_name"
ID_YESNO_YES = f"{APP_PACKAGE}:id/common_yesnodialog_tv_yes"
ID_YESNO_NO = f"{APP_PACKAGE}:id/common_yesnodialog_tv_no"

# DocumentsUI 画像ピッカー
ID_DOCUMENTSUI_ITEM = "com.google.android.documentsui:id/item_root"

# マイページ・プロフィール編集
ID_MYPAGE_GRID_BUTTON = f"{APP_PACKAGE}:id/griditem_mypage_menu_button"
ID_PROFILE_TEXTEDIT_ET = f"{APP_PACKAGE}:id/fragment_common_textedit_et"
ID_PROFILE_TEXTEDIT_COUNT = f"{APP_PACKAGE}:id/fragment_common_textedit_tv_count"
# ProfItemSelectActivity 用
ID_PROFITEMSELECT_ROW = f"{APP_PACKAGE}:id/listrow_profileedit_normal_row"
ID_PROFITEMSELECT_TITLE = f"{APP_PACKAGE}:id/listrow_profileedit_normal_tv_title"
ID_PROFITEMSELECT_CHECK = f"{APP_PACKAGE}:id/listrow_profileedit_normal_check"
ID_PROFITEMSELECT_LIST = f"{APP_PACKAGE}:id/list"
ID_MY_PROFILE_SCROLL = f"{APP_PACKAGE}:id/my_profile_item_scroll"

# 送信バブル判定: 右端がこの比率以上なら自分の送信とみなす
SENT_BUBBLE_RIGHT_RATIO = 0.88

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# ポップアップ閉じるボタン候補（テキストベース）
_DISMISS_TEXTS = [
  "閉じる",
  "あとで",
  "後で",
  "今はしない",
  "許可しない",
  "次へ",
  "スキップ",
  "とじる",
]
# NOTE: 「キャンセル」「OK」は送信取消ダイアログ・見ちゃいや確認等の意味のある選択肢に
# マッチしてしまうので _DISMISS_TEXTS には入れない。

# 既知のポップアップ閉じるresource-id
_DISMISS_IDS = [
  f"{APP_PACKAGE}:id/io_repro_android_message_close_button",  # Repro SDK in-app message
  f"{APP_PACKAGE}:id/common_age_verification_dialog_btn_yes",  # 18歳以上確認（初回のみ）
  "android:id/button2",  # システムダイアログのキャンセル(ネガティブ)
]
# NOTE: btn_cross / btn_cancel（送信取消ダイアログの✕・キャンセル）は誤発火しやすく、
# 閉じる→誤タップで再発のループを生むので _DISMISS_IDS には入れない。
# 送信取消ダイアログは back キーで閉じる。


def dismiss_popups(driver, max_loops=3, verbose=False):
  """既知のポップアップ・モーダルを閉じる。

  - resource-id ベースの既知ボタンをクリック
  - text ベースで「閉じる」「あとで」などをクリック
  - 何も閉じられなかったら抜ける
  - max_loops 回まで繰り返し（重なった時用）
  """
  for loop in range(max_loops):
    closed = False

    for rid in _DISMISS_IDS:
      try:
        els = driver.find_elements(AppiumBy.ID, rid)
      except WebDriverException:
        els = []
      for el in els:
        try:
          if el.is_displayed() and el.is_enabled():
            el.click()
            if verbose:
              print(f"  [dismiss_popups] clicked id={rid}")
            time.sleep(0.6)
            closed = True
            break
        except (StaleElementReferenceException, WebDriverException):
          continue
      if closed:
        break

    if closed:
      continue

    for txt in _DISMISS_TEXTS:
      try:
        els = driver.find_elements(
          AppiumBy.XPATH,
          f'//*[@text="{txt}" or @content-desc="{txt}"]',
        )
      except WebDriverException:
        els = []
      for el in els:
        try:
          if el.is_displayed() and el.is_enabled():
            el.click()
            if verbose:
              print(f"  [dismiss_popups] clicked text={txt}")
            time.sleep(0.6)
            closed = True
            break
        except (StaleElementReferenceException, WebDriverException):
          continue
      if closed:
        break

    if not closed:
      break


def _badge_count(driver):
  """メッセージタブの未読バッジ数を返す。バッジ無しなら 0。"""
  try:
    badge = driver.find_element(AppiumBy.ID, ID_MESSAGE_BADGE)
  except NoSuchElementException:
    return 0
  for rid in (ID_BADGE_COUNT, ID_BADGE_COUNT_OVER):
    try:
      els = badge.find_elements(AppiumBy.ID, rid)
    except WebDriverException:
      els = []
    for el in els:
      txt = (el.text or "").strip().replace("+", "")
      if txt.isdigit():
        return int(txt)
      if txt:
        return 999
  return 0


def has_new_message(driver):
  """新着メールがあるか（メッセージタブにバッジが付いているか）."""
  return _badge_count(driver) > 0


def _ensure_main_tab(driver, max_back=8):
  """メイン下タブが見えるまで back キーで戻す。"""
  for _ in range(max_back):
    if driver.find_elements(AppiumBy.ID, ID_MESSAGE_TAB):
      return True
    try:
      driver.press_keycode(4)
    except WebDriverException:
      pass
    time.sleep(1)
    dismiss_popups(driver)
  return bool(driver.find_elements(AppiumBy.ID, ID_MESSAGE_TAB))


def open_message_tab(driver):
  """メッセージタブを開く。"""
  dismiss_popups(driver)
  if not driver.find_elements(AppiumBy.ID, ID_MESSAGE_TAB):
    _ensure_main_tab(driver)
  driver.find_element(AppiumBy.ID, ID_MESSAGE_TAB).click()
  time.sleep(2)
  dismiss_popups(driver)


def open_mypage_tab(driver):
  """マイページタブを開く。"""
  dismiss_popups(driver)
  driver.find_element(AppiumBy.ID, ID_MYPAGE_TAB).click()
  time.sleep(2)
  dismiss_popups(driver)


def _parse_bounds(s):
  m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", s or "")
  if not m:
    return None
  return tuple(int(x) for x in m.groups())


def _screen_width(driver):
  try:
    return int(driver.get_window_size().get("width") or 1080)
  except Exception:
    return 1080


def _is_sent_bubble(bounds_str, screen_width):
  b = _parse_bounds(bounds_str)
  if not b:
    return False
  return b[2] > screen_width * SENT_BUBBLE_RIGHT_RATIO


def _get_message_bubbles(driver):
  """スレッド詳細画面から送受信バブルを取得して返す。

  返り値: list of {"text": str, "is_sent": bool, "bounds": str}
  画面に出ている順（≒時系列）。
  """
  bubbles = []
  width = _screen_width(driver)
  els = driver.find_elements(AppiumBy.ID, ID_TXT_MESSAGE)
  for el in els:
    try:
      bounds = el.get_attribute("bounds") or ""
      text = el.text or ""
    except (StaleElementReferenceException, WebDriverException):
      continue
    bubbles.append({
      "text": text,
      "is_sent": _is_sent_bubble(bounds, width),
      "bounds": bounds,
    })
  return bubbles


def _get_via_info_texts(driver):
  """スレッド詳細画面のすべての txt_via_from テキストを返す。「募集から送信」検出用。"""
  out = []
  for el in driver.find_elements(AppiumBy.ID, ID_TXT_VIA_FROM):
    try:
      out.append(el.text or "")
    except (StaleElementReferenceException, WebDriverException):
      pass
  return out


def _wait_for_send_echo(driver, expected_text, timeout=15):
  """送信したテキストが自分の送信バブルに反映されるまで待機。"""
  expected_clean = func.normalize_text(expected_text)
  end = time.time() + timeout
  while time.time() < end:
    for b in _get_message_bubbles(driver):
      if b["is_sent"] and func.normalize_text(b["text"]) == expected_clean:
        return True
    time.sleep(1)
  return False


def _send_text_message(driver, text):
  """テキストを入力欄に流し込んで送信し、送信バブル反映を待つ。"""
  edit = driver.find_element(AppiumBy.ID, ID_EDIT_INPUT)
  edit.click()
  time.sleep(0.5)
  try:
    edit.clear()
  except WebDriverException:
    pass
  edit.send_keys(text)
  time.sleep(0.6)
  driver.find_element(AppiumBy.ID, ID_BTN_SEND).click()
  time.sleep(1.5)
  dismiss_popups(driver)
  return _wait_for_send_echo(driver, text, timeout=15)


def _udid(driver):
  """driverのcapabilitiesからUDIDを抽出。"""
  try:
    caps = driver.capabilities or {}
    return caps.get("udid") or caps.get("deviceUDID") or caps.get("appium:udid")
  except Exception:
    return None


def _adb_tap_bounds(udid, bounds):
  """adb input tap で bounds の中央を直接タップする。
  btn_gallery のように Selenium .click() が効かない要素用。
  """
  b = _parse_bounds(bounds)
  if not b or not udid:
    return False
  cx = (b[0] + b[2]) // 2
  cy = (b[1] + b[3]) // 2
  subprocess.run(
    ["adb", "-s", udid, "shell", "input", "tap", str(cx), str(cy)],
    check=False,
  )
  return True


def _wait_loading_cleared(driver, timeout=15):
  """activity_default_loading_lock が消えるまで待つ。"""
  end = time.time() + timeout
  while time.time() < end:
    try:
      if not driver.find_elements(AppiumBy.ID, ID_LOADING_LOCK):
        return True
    except WebDriverException:
      pass
    time.sleep(0.5)
  return False


def _find_in_dump(driver, *, text=None, rid_suffix=None):
  """page_source を XML パースして条件一致の最初の要素 attrib を返す。
  text は一部一致でもOK、rid_suffix は resource-id の末尾一致。
  非clickableなTextViewにも text= は当たる（タップは bounds 経由で行う）。
  """
  try:
    src = driver.page_source
  except WebDriverException:
    return None
  try:
    root = ET.fromstring(src)
  except ET.ParseError:
    return None
  for el in root.iter():
    if text is not None:
      hay = (el.attrib.get("text", "") or "") + (el.attrib.get("content-desc", "") or "")
      if text not in hay:
        continue
    if rid_suffix is not None:
      if not (el.attrib.get("resource-id", "") or "").endswith(rid_suffix):
        continue
    return el.attrib
  return None


def _pick_image_by_filename(driver, basename):
  """DocumentsUI ピッカーで preview_icon の content-desc が「ファイル <basename> をプレビューする」
  となっている item_root を Selenium .click() で選択する。
  見つかれば True、見つからなければ False。
  """
  try:
    src = driver.page_source
    root = ET.fromstring(src)
  except (WebDriverException, ET.ParseError):
    return False

  target_idx = None
  items_found = []
  for el in root.iter():
    rid = el.attrib.get("resource-id", "") or ""
    if rid == ID_DOCUMENTSUI_ITEM:
      items_found.append(el)
      desc = ""
      for sub in el.iter():
        d = sub.attrib.get("content-desc", "") or ""
        if "ファイル" in d and "プレビュー" in d:
          desc = d
          break
      if basename in desc:
        target_idx = len(items_found) - 1
        break

  if target_idx is None:
    return False

  driver_items = driver.find_elements(AppiumBy.ID, ID_DOCUMENTSUI_ITEM)
  if target_idx >= len(driver_items):
    return False
  try:
    driver_items[target_idx].click()
    return True
  except WebDriverException:
    return False


def _push_image_to_device(driver, image_url):
  """mail_img(URL) をダウンロード→PNG として /sdcard/Pictures/happy_send_<ts>.png に push→media scan。
  DocumentsUI ピッカー (内部ストレージ→画像フィルタ) で確実に表示されるよう
  既存の happy_send_*.png 系列に合わせる。
  失敗時は None。
  """
  udid = _udid(driver)
  if not udid:
    print("  [send_image] udid取得失敗")
    return None
  try:
    resp = requests.get(image_url, timeout=20)
    resp.raise_for_status()
  except Exception as e:
    print(f"  [send_image] 画像DL失敗 {image_url}: {e}")
    return None

  # PNG として保存
  try:
    img = Image.open(io.BytesIO(resp.content))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()
  except Exception as e:
    print(f"  [send_image] PNG変換失敗: {e}")
    return None

  ts = int(time.time())
  fname = f"happy_send_{ts}.png"
  local_path = os.path.join(tempfile.gettempdir(), fname)
  with open(local_path, "wb") as f:
    f.write(png_bytes)

  remote_path = f"/sdcard/Pictures/{fname}"
  try:
    subprocess.run(["adb", "-s", udid, "push", local_path, remote_path], check=True)
    subprocess.run(
      ["adb", "-s", udid, "shell", "am", "broadcast", "-a",
       "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
       "-d", f"file://{remote_path}"],
      check=False,
    )
  except Exception as e:
    print(f"  [send_image] adb push 失敗: {e}")
    return None
  finally:
    try:
      os.remove(local_path)
    except OSError:
      pass

  # MediaStore 反映待ち (Android 11+ でも broadcast は通常成功する)
  end = time.time() + 15
  while time.time() < end:
    try:
      out = subprocess.check_output(
        ["adb", "-s", udid, "shell", "content", "query",
         "--uri", "content://media/external_primary/images/media",
         "--projection", "_display_name",
         "--where", f"\"_display_name='{fname}'\""],
        stderr=subprocess.DEVNULL, timeout=5,
      ).decode()
      if fname in out:
        break
    except Exception:
      pass
    time.sleep(1)
  return remote_path


def send_image(driver, mail_img):
  """スレッド詳細画面から画像を1枚送信する。

  前提: edit_text_message_input が画面にある（スレッド詳細）。
  フロー:
    1. mail_img URL から DL → PNG として /sdcard/Pictures/happy_send_<ts>.png に push
    2. btn_gallery を adb tap (Selenium .click() は効かない)
    3. ボトムシート「ライブラリから選ぶ」を adb tap
    4. DocumentsUI: ハンバーガー → 端末モデル → 「画像」フィルタ
    5. push したファイル名と一致する item_root を Selenium .click()
    6. トリム画面で header_right_btn_1 (決定) を Selenium .click()
    7. スレッド詳細に戻ってくるまで待つ
  返り値: True=成功 False=失敗
  """
  if not mail_img:
    return False

  remote_path = _push_image_to_device(driver, mail_img)
  if not remote_path:
    return False

  udid = _udid(driver)

  # 1) btn_gallery: Selenium / mobile:clickGesture が効かないので adb input tap 一択
  galleries = driver.find_elements(AppiumBy.ID, ID_BTN_GALLERY)
  if not galleries:
    print("  [send_image] btn_gallery 不在")
    return False
  gallery_bounds = galleries[0].get_attribute("bounds") or ""
  if not _adb_tap_bounds(udid, gallery_bounds):
    print("  [send_image] btn_gallery adb tap 失敗")
    return False
  time.sleep(2.5)

  # 2) 「ライブラリから選ぶ」 — TextView (clickable=false) なのでテキスト座標を adb tap
  lib = _find_in_dump(driver, text="ライブラリから選ぶ")
  if not lib:
    print("  [send_image] 「ライブラリから選ぶ」が見つからず")
    driver.press_keycode(4)
    return False
  if not _adb_tap_bounds(udid, lib.get("bounds", "")):
    print("  [send_image] 「ライブラリから選ぶ」 adb tap 失敗")
    return False
  time.sleep(4)

  # 3) DocumentsUI ピッカー — ハンバーガー→画像→Camera→ファイル名 でナビ
  basename = os.path.basename(remote_path)

  # ピッカーが表示されるまで待つ
  picker_end = time.time() + 10
  while time.time() < picker_end:
    if driver.find_elements(AppiumBy.ID, ID_DOCUMENTSUI_ITEM):
      break
    time.sleep(0.5)

  # ハンバーガー (左上の「ルートを表示する」)
  burger = _find_in_dump(driver, text="ルートを表示する")
  if not burger or not burger.get("bounds"):
    print("  [send_image] ハンバーガーボタン不在")
    driver.press_keycode(4); driver.press_keycode(4)
    return False
  _adb_tap_bounds(udid, burger.get("bounds", ""))
  time.sleep(2)

  # ドロワーで端末モデル（内部ストレージ）をクリック
  try:
    model = subprocess.check_output(
      ["adb", "-s", udid, "shell", "getprop", "ro.product.model"],
      timeout=5,
    ).decode().strip()
  except Exception:
    model = ""
  if not model:
    print("  [send_image] 端末モデル取得失敗")
    return False

  try:
    storage = driver.find_elements(
      AppiumBy.ANDROID_UIAUTOMATOR,
      f'new UiSelector().resourceId("android:id/title").text("{model}")',
    )
    if not storage:
      print(f"  [send_image] ドロワーに {model} エントリ無し")
      driver.press_keycode(4); driver.press_keycode(4)
      return False
    storage[0].click()
  except WebDriverException as e:
    print(f"  [send_image] 端末ストレージ click 失敗: {e}")
    return False
  time.sleep(3)

  # 「画像」フィルタチップをクリック
  img_filter = _find_in_dump(driver, text="画像")
  if not img_filter or img_filter.get("clickable") != "true":
    print("  [send_image] 「画像」フィルタ不在")
    driver.press_keycode(4); driver.press_keycode(4); driver.press_keycode(4)
    return False
  _adb_tap_bounds(udid, img_filter.get("bounds", ""))
  time.sleep(4)  # リロード待ち

  # 一覧から push したファイルを選択 (反映遅延に備えて数秒リトライ)
  picked = False
  retry_end = time.time() + 12
  while time.time() < retry_end:
    if _pick_image_by_filename(driver, basename):
      picked = True
      break
    time.sleep(1.5)
  if not picked:
    print(f"  [send_image] push したファイル {basename} が画像一覧で見つからず")
    driver.press_keycode(4); driver.press_keycode(4); driver.press_keycode(4)
    return False
  time.sleep(3)

  # 4) PhotoTrimActivity が立ち上がるまで待ち、header_right_btn_1 (決定) を click
  trim_end = time.time() + 20
  rights = []
  while time.time() < trim_end:
    try:
      act = driver.current_activity or ""
    except WebDriverException:
      act = ""
    if "PhotoTrim" in act or driver.find_elements(AppiumBy.ID, ID_FRAGMENT_PHOTO_TRIM_IV):
      rights = driver.find_elements(AppiumBy.ID, ID_HEADER_RIGHT_BTN_1)
      if rights:
        break
    time.sleep(0.5)
  if not rights:
    print("  [send_image] 決定ボタン(header_right_btn_1)が見つからず")
    driver.press_keycode(4)
    driver.press_keycode(4)
    return False
  try:
    rights[0].click()
  except WebDriverException as e:
    print(f"  [send_image] 決定ボタン click 失敗: {e}")
    return False

  # 5) スレッド詳細(edit_text_message_input)が戻るまで待つ
  end = time.time() + 15
  while time.time() < end:
    if driver.find_elements(AppiumBy.ID, ID_EDIT_INPUT):
      time.sleep(1.5)
      dismiss_popups(driver)
      print("  [send_image] 画像送信完了")
      return True
    time.sleep(0.5)
  print("  [send_image] スレッドに戻らず — 状態不明")
  return False


def register_micha_iya(driver):
  """スレッド詳細画面から相手を「見ちゃいや」登録する。

  前提: edit_text_message_input が画面にある（スレッド詳細）。
  フロー:
    1. txt_via_link (○○さんのプロフィール) を adb tap → OtherProfileActivity
    2. ローディング解除待ち
    3. btn_ellipses_menu を Selenium .click() → ボトムシートメニュー
    4. 「見ちゃいや登録」テキスト座標を adb tap → BlockUserActivity
    5. cutsom_pressble_button_btn (登録) を Selenium .click()
    6. スレッド詳細に戻るまで back キーで戻す
  返り値: True=登録ボタン押下まで完了 False=途中失敗
  """
  udid = _udid(driver)

  # 1) プロフィール遷移（txt_via_link が無いケースは img_thumbnail フォールバック）
  via_links = driver.find_elements(AppiumBy.ID, ID_TXT_VIA_LINK)
  nav_done = False
  if via_links:
    bnds = via_links[0].get_attribute("bounds") or ""
    if _adb_tap_bounds(udid, bnds):
      time.sleep(2.5)
      _wait_loading_cleared(driver, 10)
      if not driver.find_elements(AppiumBy.ID, ID_EDIT_INPUT):
        nav_done = True
  if not nav_done:
    thumbs = driver.find_elements(AppiumBy.ID, f"{APP_PACKAGE}:id/img_thumbnail")
    if thumbs:
      bnds = thumbs[0].get_attribute("bounds") or ""
      if _adb_tap_bounds(udid, bnds):
        time.sleep(2.5)
        _wait_loading_cleared(driver, 10)
        if not driver.find_elements(AppiumBy.ID, ID_EDIT_INPUT):
          nav_done = True
  if not nav_done:
    print("  [micha_iya] ユーザー詳細に遷移できず")
    return False

  # 2) その他メニュー
  ells = driver.find_elements(AppiumBy.ID, ID_BTN_ELLIPSES_MENU)
  if not ells:
    print("  [micha_iya] btn_ellipses_menu 不在")
    _back_to_thread_detail(driver)
    return False
  try:
    ells[0].click()
  except WebDriverException as e:
    print(f"  [micha_iya] その他ボタン click 失敗: {e}")
    _back_to_thread_detail(driver)
    return False
  time.sleep(2)
  # NOTE: ここで dismiss_popups は呼ばない（メニュー内「キャンセル」を誤タップする）

  # 3) 「見ちゃいや登録」 — TextView (clickable=false) なので bounds で adb tap
  mi = _find_in_dump(driver, text="見ちゃいや登録")
  if not mi:
    print("  [micha_iya] 見ちゃいや登録メニュー不在")
    driver.press_keycode(4)
    _back_to_thread_detail(driver)
    return False
  if not _adb_tap_bounds(udid, mi.get("bounds", "")):
    print("  [micha_iya] 見ちゃいや登録 adb tap 失敗")
    _back_to_thread_detail(driver)
    return False
  time.sleep(2.5)

  # 4) 登録ページ — 「登録」ボタン押下
  end = time.time() + 8
  reg_btn = None
  while time.time() < end:
    if driver.find_elements(AppiumBy.ID, ID_BLOCK_TV_NAME):
      btns = driver.find_elements(AppiumBy.ID, ID_BLOCK_REGISTER_BTN)
      if btns:
        reg_btn = btns[0]
        break
    time.sleep(0.5)
  if reg_btn is None:
    print("  [micha_iya] 登録ボタン不在")
    _back_to_thread_detail(driver)
    return False
  try:
    reg_btn.click()
  except WebDriverException as e:
    print(f"  [micha_iya] 登録ボタン click 失敗: {e}")
    _back_to_thread_detail(driver)
    return False
  time.sleep(2)

  # 5) 確認ダイアログ「OK」 — dismiss_popups は誤って「キャンセル」を押すので使わない
  end = time.time() + 8
  yes_btn = None
  while time.time() < end:
    yes = driver.find_elements(AppiumBy.ID, ID_YESNO_YES)
    if yes:
      yes_btn = yes[0]
      break
    time.sleep(0.4)
  if yes_btn is None:
    print("  [micha_iya] 確認ダイアログのOKボタン不在")
    _back_to_thread_detail(driver)
    return False
  try:
    yes_btn.click()
  except WebDriverException as e:
    print(f"  [micha_iya] OK click 失敗: {e}")
    _back_to_thread_detail(driver)
    return False
  time.sleep(2)
  print("  [micha_iya] 登録完了")
  _back_to_thread_detail(driver)
  return True


def _back_to_thread_detail(driver, max_tries=6):
  """back キー連打でスレッド詳細(edit_text_message_input がある画面)に戻る。"""
  for _ in range(max_tries):
    if driver.find_elements(AppiumBy.ID, ID_EDIT_INPUT):
      return True
    try:
      driver.press_keycode(4)
    except WebDriverException:
      pass
    time.sleep(1.2)
    dismiss_popups(driver)
  return bool(driver.find_elements(AppiumBy.ID, ID_EDIT_INPUT))


def _back_to_message_list(driver):
  """スレッド詳細から戻るキー or ヘッダー戻るボタンでメッセージ一覧へ。"""
  try:
    backs = driver.find_elements(AppiumBy.ID, ID_HEADER_BACK)
    if backs:
      backs[0].click()
    else:
      driver.press_keycode(4)
  except WebDriverException:
    try:
      driver.press_keycode(4)
    except WebDriverException:
      pass
  time.sleep(2)
  dismiss_popups(driver)


def _select_unread_filter(driver):
  """メッセージ画面で「未読」タブを選択する。"""
  els = driver.find_elements(AppiumBy.ID, ID_MSG_BTN_UNREAD)
  if not els:
    return False
  els[0].click()
  time.sleep(1.5)
  dismiss_popups(driver)
  return True


def check_mail(
  name,
  driver,
  login_id,
  password,
  fst_message,
  second_message,
  post_return_message,
  conditions_message,
  confirmation_mail,
  mail_img,
  gmail_address,
  gmail_password,
  return_check_cnt=10,
  chara_prompt=None,
):
  """ハッピーメールAndroid版 新着メール処理.

  既存 widget.happymail.multidrivers_checkmail のAndroidネイティブ移植。
  - 未読バッジが無ければ即 return None
  - 未読タブで新着スレッドを順に処理
  - 自分送信通数で fst / second / 通知のみ を分岐
  - 受信本文にメアドが含まれていたら外部Gmailで条件分送信
  - return_list（既存と同形式の文字列リスト）を返す。空なら None
  TODO: BAN画面検出 は未実装。
  """
  return_list = []

  open_message_tab(driver)
  if not has_new_message(driver):
    print(f"[{name}] 新着メールなし — スキップ")
    return None

  if not _select_unread_filter(driver):
    print(f"[{name}] 未読タブ要素が見つからず処理中断")
    return None

  loop_cnt = 0
  while loop_cnt < return_check_cnt:
    rows = driver.find_elements(AppiumBy.ID, ID_FRAME_SWIPE)
    if not rows:
      print(f"[{name}] 未読スレッド残り0")
      break

    first_row = rows[0]

    post_time_text = ""
    try:
      pts = first_row.find_elements(AppiumBy.ID, ID_TXT_POST_TIME)
      if pts:
        post_time_text = pts[0].text or ""
    except (StaleElementReferenceException, WebDriverException):
      pass

    now = datetime.now()
    arrival = func.parse_arrival_datetime(post_time_text, now)
    if arrival is None:
      four_min_passed = True
    else:
      four_min_passed = (now - arrival) >= timedelta(minutes=4)

    if not four_min_passed:
      print(f"[{name}] 4分未経過のためループ終了 (post_time={post_time_text})")
      break

    try:
      first_row.click()
    except (StaleElementReferenceException, WebDriverException) as e:
      print(f"[{name}] 行クリック失敗: {e}")
      break
    time.sleep(3)
    dismiss_popups(driver)

    title_els = driver.find_elements(AppiumBy.ID, ID_TXT_HEADER_TITLE)
    user_name = (title_els[0].text if title_els else "").strip() or "(不明)"

    bubbles = _get_message_bubbles(driver)
    sent_bubbles = [b for b in bubbles if b["is_sent"]]
    received_bubbles = [b for b in bubbles if not b["is_sent"]]
    send_me_length = len(sent_bubbles)
    last_received = received_bubbles[-1]["text"] if received_bubbles else ""
    via_info_text = " ".join(_get_via_info_texts(driver))
    via_post_board = "募集から送信" in via_info_text

    print(f"[{name}] {user_name}: sent={send_me_length} via={via_info_text!r}")

    email_list = EMAIL_PATTERN.findall(last_received)

    handled = False
    if email_list:
      handled = True
      if "icloud.com" in last_received:
        icloud_text = (
          "メール送ったんですけど、ブロックされちゃって届かないので"
          "こちらのアドレスにお名前添えて送ってもらえますか？\n" + (gmail_address or "")
        )
        try:
          _send_text_message(driver, icloud_text)
        except Exception as e:
          print(f"[{name}] iCloud返信失敗: {e}")
          traceback.print_exc()
      else:
        for user_address in email_list:
          user_address = func.normalize_text(user_address)
          try:
            func.send_conditional(
              user_name, user_address, gmail_address, gmail_password,
              conditions_message, "ハッピーメール",
            )
            print(f"  [{name}] {user_name} -> {user_address} 条件分送信")
          except Exception as e:
            print(f"  [{name}] アドレス内1stメール送信失敗 {user_address}: {e}")
            traceback.print_exc()
            try:
              func.send_error(name, f"アドレス内1stメールの送信に失敗\n{user_address}\n{gmail_address}\n{traceback.format_exc()}")
            except Exception:
              pass
        if confirmation_mail:
          try:
            _send_text_message(driver, confirmation_mail)
          except Exception as e:
            print(f"[{name}] 確認メッセージ送信失敗: {e}")
      try:
        register_micha_iya(driver)
      except Exception as e:
        print(f"[{name}] 見ちゃいや登録失敗: {e}")
        traceback.print_exc()

    if not handled:
      if send_me_length == 0:
        send_text = fst_message.format(name=user_name) if fst_message else ""
        if via_post_board and post_return_message:
          send_text = post_return_message.format(name=user_name)
        if send_text:
          try:
            _send_text_message(driver, send_text)
          except Exception as e:
            print(f"[{name}] FST送信失敗: {e}")
            traceback.print_exc()
        if mail_img:
          try:
            send_image(driver, mail_img)
          except Exception as e:
            print(f"[{name}] 画像送信失敗: {e}")
            traceback.print_exc()
      elif send_me_length == 1:
        if via_post_board:
          ret = f"{name}happymail,{login_id}:{password}\n{user_name}「{last_received}」"
          return_list.append(ret)
        else:
          send_text = second_message.format(name=user_name) if second_message else ""
          if send_text:
            try:
              _send_text_message(driver, send_text)
            except Exception as e:
              print(f"[{name}] second送信失敗: {e}")
              traceback.print_exc()
      else:
        ret = f"{name}happymail,{login_id}:{password}\n{user_name}「{last_received}」"
        return_list.append(ret)
        try:
          register_micha_iya(driver)
        except Exception as e:
          print(f"[{name}] 見ちゃいや登録失敗: {e}")
          traceback.print_exc()

    _back_to_message_list(driver)
    _select_unread_filter(driver)
    loop_cnt += 1

  return return_list if return_list else None


# =============================================================================
# プロフィール編集
# =============================================================================

def _open_my_profile(driver):
  """マイページ → 「プロフィール」グリッドをタップ → MyProfileActivity を開く。"""
  # 残存画面を確実に閉じる（ProfileEditActivity 等）
  for _ in range(10):
    if driver.find_elements(AppiumBy.ID, ID_MYPAGE_TAB):
      break
    try: driver.press_keycode(4)
    except WebDriverException: pass
    time.sleep(0.7)
    dismiss_popups(driver)
  _ensure_main_tab(driver)
  open_mypage_tab(driver)
  time.sleep(1.5)
  buttons = driver.find_elements(AppiumBy.ID, ID_MYPAGE_GRID_BUTTON)
  if not buttons:
    print("  [re_registration] マイページのグリッドが見つかりません")
    return False
  # 一番左上 (y最小, x最小) のボタンが「プロフィール」
  first = None
  best_key = None
  for b in buttons:
    bnd = _parse_bounds(b.get_attribute("bounds") or "")
    if not bnd: continue
    x1, y1, _, _ = bnd
    key = (y1, x1)
    if best_key is None or key < best_key:
      best_key = key; first = b
  if first is None:
    print("  [re_registration] プロフィールボタン特定不可")
    return False
  first.click()
  end = time.time() + 12
  while time.time() < end:
    if driver.find_elements(AppiumBy.ID, f"{APP_PACKAGE}:id/my_profile_item_scroll"):
      time.sleep(1)
      return True
    time.sleep(0.7)
  return False


def _scroll_my_profile_top(driver, max_swipes=15):
  """MyProfile のスクロールビューをトップまで戻す。"""
  udid = _udid(driver)
  for _ in range(max_swipes):
    subprocess.run(
      ["adb", "-s", udid, "shell", "input", "swipe", "540", "500", "540", "1900", "300"],
      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(0.6)


def _find_tap_target_for_label(driver, label):
  """ラベル行のタップ座標を返す。

  - row 形式 (txt_title): ラベル TextView 自身の clickable 祖先を返す。
  - section 形式 (txt_header): ラベル直下の txt_value/txt_comment を起点に
    その clickable 祖先を返す（section ラベル自体はクリック不可）。
  """
  try:
    root = ET.fromstring(driver.page_source)
  except Exception:
    return None
  parent_map = {c: p for p in root.iter() for c in p}
  # 優先度: txt_title / txt_header を優先、なければ最初のヒット
  label_el = None
  for el in root.iter():
    if el.attrib.get("class") != "android.widget.TextView":
      continue
    if el.attrib.get("text", "") != label:
      continue
    rid = el.attrib.get("resource-id", "")
    if rid.endswith(":id/txt_title") or rid.endswith(":id/txt_header"):
      label_el = el
      break
    if label_el is None:
      label_el = el
  if label_el is None:
    return None

  def _climb_clickable(start):
    cur = start
    for _ in range(12):
      parent = parent_map.get(cur)
      if parent is None:
        break
      if parent.attrib.get("clickable") == "true":
        b = _parse_bounds(parent.attrib.get("bounds", ""))
        if b:
          return b
      cur = parent
    return None

  rid = label_el.attrib.get("resource-id", "")
  if rid.endswith(":id/txt_header"):
    label_b = _parse_bounds(label_el.attrib.get("bounds", ""))
    if not label_b:
      return None
    ly2 = label_b[3]
    target_el = None
    best_dy = None
    for el in root.iter():
      r = el.attrib.get("resource-id", "")
      if not (r.endswith(":id/txt_value") or r.endswith(":id/txt_comment")):
        continue
      b = _parse_bounds(el.attrib.get("bounds", ""))
      if not b:
        continue
      if b[1] < ly2 - 5:
        continue
      dy = b[1] - ly2
      if dy > 250:
        continue
      if best_dy is None or dy < best_dy:
        target_el = el
        best_dy = dy
    if target_el is not None:
      clickable_b = _climb_clickable(target_el)
      if clickable_b:
        return clickable_b
      return _parse_bounds(target_el.attrib.get("bounds", ""))
    return label_b

  # row 形式 (txt_title) もしくは不明
  clickable_b = _climb_clickable(label_el)
  if clickable_b:
    return clickable_b
  return _parse_bounds(label_el.attrib.get("bounds", ""))


def _scroll_to_label_and_tap(driver, label, max_swipes=20):
  """ラベル行を見つけてタップ。見つからなければスクロールして再探索。"""
  udid = _udid(driver)
  for _ in range(max_swipes):
    target = _find_tap_target_for_label(driver, label)
    if target:
      x1, y1, x2, y2 = target
      cx = (x1 + x2) // 2; cy = (y1 + y2) // 2
      print(f"  [tap:{label}] target=[{x1},{y1}][{x2},{y2}] cx={cx} cy={cy}")
      subprocess.run(
        ["adb", "-s", udid, "shell", "input", "tap", str(cx), str(cy)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
      )
      return True
    subprocess.run(
      ["adb", "-s", udid, "shell", "input", "swipe", "540", "1700", "540", "500", "400"],
      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(1.2)
  return False


def _edit_text_field(driver, label, value, expected_header=None):
  """MyProfile からラベル行をタップし、表示された ProfileEditActivity の
  テキスト入力で value をセット → 保存 → 戻る。

  expected_header: ヘッダーが期待値と一致しなければスキップ。
  """
  if not value:
    return False
  # 毎回トップに戻してから探す（前回編集後のスクロール位置に依存しないため）
  _scroll_my_profile_top(driver, max_swipes=8)
  if not _scroll_to_label_and_tap(driver, label):
    print(f"  [edit_text:{label}] 行が見つかりません")
    return False
  time.sleep(2)

  # ヘッダー確認
  hdr = expected_header or label
  end = time.time() + 8
  ok = False
  while time.time() < end:
    titles = driver.find_elements(AppiumBy.ID, ID_TXT_HEADER_TITLE)
    if titles and (titles[0].text or "") == hdr:
      ok = True
      break
    time.sleep(0.5)
  if not ok:
    print(f"  [edit_text:{label}] エディタ画面に到達せず")
    _back_one(driver)
    return False

  # 入力欄
  ets = driver.find_elements(AppiumBy.ID, ID_PROFILE_TEXTEDIT_ET)
  if not ets:
    print(f"  [edit_text:{label}] 入力欄が見つかりません")
    _back_one(driver)
    return False
  et = ets[0]
  current = et.get_attribute("text") or ""
  if current == value:
    print(f"  [edit_text:{label}] 変更なし ({value})")
    _back_one(driver)
    return True
  try:
    et.click()
    time.sleep(0.5)
    et.clear()
    time.sleep(0.5)
    et.send_keys(value)
    time.sleep(0.8)
  except WebDriverException as e:
    print(f"  [edit_text:{label}] 入力失敗: {e}")
    _back_one(driver)
    return False

  # 保存/審査ボタン
  save_btns = driver.find_elements(AppiumBy.ID, ID_HEADER_RIGHT_BTN_1)
  if not save_btns:
    print(f"  [edit_text:{label}] 保存ボタンが見つかりません")
    _back_one(driver)
    return False
  try:
    save_btns[0].click()
  except WebDriverException as e:
    print(f"  [edit_text:{label}] 保存タップ失敗: {e}")
    _back_one(driver)
    return False
  time.sleep(2)

  # 自己紹介などは「審査確認」ダイアログが出る → 「提出する」をタップ
  end = time.time() + 5
  while time.time() < end:
    yes = driver.find_elements(AppiumBy.ID, ID_YESNO_YES)
    if yes:
      try:
        yes[0].click()
        print(f"  [edit_text:{label}] 審査確認 → 提出")
      except WebDriverException:
        pass
      break
    time.sleep(0.5)
  time.sleep(2)

  # エディタがまだ残っているなら戻る
  if driver.find_elements(AppiumBy.ID, ID_PROFILE_TEXTEDIT_ET):
    _back_one(driver)
  print(f"  [edit_text:{label}] 設定: {value}")
  return True


def _back_one(driver):
  """ヘッダーの戻るボタン or back キーで1つ戻す。"""
  backs = driver.find_elements(AppiumBy.ID, ID_HEADER_BACK)
  if backs:
    try:
      backs[0].click()
      time.sleep(1.2)
      return
    except WebDriverException:
      pass
  try:
    driver.press_keycode(4)
  except WebDriverException:
    pass
  time.sleep(1.2)


def _select_list_field(driver, label, value):
  """ProfItemSelectActivity 形式 (単一選択リスト) のフィールドを設定する。

  Args:
    driver: Appium driver
    label: MyProfile 上のラベル (例: "血液型")
    value: 設定したい値 (例: "Ａ型")
  """
  if not value:
    return False
  _scroll_my_profile_top(driver, max_swipes=8)
  if not _scroll_to_label_and_tap(driver, label):
    print(f"  [select:{label}] 行が見つかりません")
    return False
  time.sleep(2)

  # ProfItemSelectActivity に到達したか確認 (ヘッダータイトルがラベルと一致)
  end = time.time() + 8
  ok = False
  while time.time() < end:
    titles = driver.find_elements(AppiumBy.ID, ID_TXT_HEADER_TITLE)
    if titles and (titles[0].text or "") == label:
      ok = True
      break
    time.sleep(0.5)
  if not ok:
    print(f"  [select:{label}] セレクタ画面に到達せず")
    _back_one(driver)
    return False

  udid = _udid(driver)
  found = False
  for _ in range(20):
    rows = driver.find_elements(AppiumBy.ID, ID_PROFITEMSELECT_ROW)
    target_row = None
    for r in rows:
      titles = r.find_elements(AppiumBy.ID, ID_PROFITEMSELECT_TITLE)
      if not titles:
        continue
      if (titles[0].text or "") == value:
        target_row = r
        break
    if target_row is not None:
      # 既に選択済みなら何もしない（CheckBox の checked 属性で判定）
      checks = target_row.find_elements(AppiumBy.ID, ID_PROFITEMSELECT_CHECK)
      already = False
      if checks:
        already = (checks[0].get_attribute("checked") == "true")
      if already:
        print(f"  [select:{label}] 変更なし ({value})")
      else:
        try:
          target_row.click()
          time.sleep(1)
          print(f"  [select:{label}] 設定: {value}")
        except WebDriverException as e:
          print(f"  [select:{label}] 選択タップ失敗: {e}")
          _back_one(driver)
          return False
      found = True
      break
    # スクロールして探す
    subprocess.run(
      ["adb", "-s", udid, "shell", "input", "swipe", "540", "1700", "540", "800", "300"],
      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(0.7)

  if not found:
    print(f"  [select:{label}] 選択肢「{value}」が見つかりません")
    _back_one(driver)
    return False

  # MyProfile に戻る (タップで自動遷移しない場合は手動 back)
  end = time.time() + 4
  while time.time() < end:
    if driver.find_elements(AppiumBy.ID, ID_MY_PROFILE_SCROLL):
      return True
    time.sleep(0.5)
  if driver.find_elements(AppiumBy.ID, ID_PROFITEMSELECT_LIST):
    _back_one(driver)
  return True


def re_registration(chara_data, driver):
  """ハッピーメール Android アプリのプロフィールを chara_data で再登録する。

  端末が対象アカウントでログイン済みであることを前提とする。

  v1 実装範囲:
    - ニックネーム (chara_data["name"])
    - PRコメント (chara_data.get("pr_comment"))
    - 自己紹介 (chara_data.get("self_promotion"))

  他のフィールド（リスト選択型・タグ型）は今後拡張。
  """
  name = chara_data.get("name", "")
  print(f"--- [re_registration:{name}] start ---")
  dismiss_popups(driver)
  if not _open_my_profile(driver):
    print(f"--- [re_registration:{name}] MyProfile に遷移できず ---")
    return False
  dismiss_popups(driver)
  _scroll_my_profile_top(driver, max_swipes=10)
  time.sleep(1)

  # ニックネーム
  _edit_text_field(driver, "ニックネーム", name)
  time.sleep(1)

  # PRコメント
  pr = chara_data.get("pr_comment")
  if pr:
    _edit_text_field(driver, "PRコメント", pr)
    time.sleep(1)

  # 自己紹介
  intro = chara_data.get("self_promotion") or chara_data.get("self_introduction")
  if intro:
    _edit_text_field(driver, "自己紹介", intro)
    time.sleep(1)

  # 血液型 (リスト選択型 - パターン確認用)
  blood = chara_data.get("blood_type")
  if blood:
    _select_list_field(driver, "血液型", blood)
    time.sleep(1)

  # MyProfile へ戻ってメインタブまで戻す
  _back_one(driver)
  _ensure_main_tab(driver)
  print(f"--- [re_registration:{name}] done ---")
  return True
