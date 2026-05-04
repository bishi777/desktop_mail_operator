"""ハッピーメールAndroidネイティブアプリ自動化モジュール.

Appium UiAutomator2 driver で `jp.co.i_bec.suteki_happy` を操作する。
"""
import os
import random
import re
import subprocess
import tempfile
import time
import traceback
import unicodedata
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
# AreaSelectExpandableActivity 用 (居住地 都道府県選択)
ID_AREA_PARENT_ROW = f"{APP_PACKAGE}:id/listrow_area_select_parent_row"
ID_AREA_PARENT_TITLE = f"{APP_PACKAGE}:id/listrow_area_select_parent_tv_title"
ID_AREA_PARENT_CHECK = f"{APP_PACKAGE}:id/listrow_area_select_parent_check"
# 足あと (FootmarkActivity)
ID_FOOTMARK_BTN_RECEIVE = f"{APP_PACKAGE}:id/footmark_btn_receive"
ID_FOOTMARK_BTN_SELF = f"{APP_PACKAGE}:id/footmark_btn_self"
ID_FOOTMARK_RV = f"{APP_PACKAGE}:id/footmark_receive_rv"
ID_FOOTMARK_COUNT_TODAY = f"{APP_PACKAGE}:id/footmark_receive_tv_count_today"

# タイプリスト (typelist タブ)
ID_TYPELIST_BTN_RECEIVE = f"{APP_PACKAGE}:id/fragment_typelist_btn_receive"
ID_TYPELIST_BTN_SELF = f"{APP_PACKAGE}:id/fragment_typelist_btn_self"
ID_TYPELIST_BTN_MUTUAL_LOVE = f"{APP_PACKAGE}:id/fragment_typelist_btn_mutual_love"
ID_TYPELIST_HEADER = f"{APP_PACKAGE}:id/fragment_typelist_header"
ID_BTN_SEND_TYPE = f"{APP_PACKAGE}:id/btn_send_type"  # 「タイプを返す」ボタン
ID_LAYOUT_EMPTY_STATE = f"{APP_PACKAGE}:id/layout_empty_state"  # 「まだ〜していません」空状態

# ユーザー詳細 (OtherProfileActivity) のアクションフッター
ID_BTN_SEND_MSG = f"{APP_PACKAGE}:id/btn_send_msg"
ID_BTN_TYPE = f"{APP_PACKAGE}:id/btn_type"

# 初回メッセージ画面マーカー
ID_FRAME_FIRST_MESSAGE = f"{APP_PACKAGE}:id/frame_first_message"

# プロフィール本文 (PRコメント / 自己紹介)
ID_TXT_COMMENT = f"{APP_PACKAGE}:id/txt_comment"

# マイページのメニュー位置 (3x4 グリッド): プロフィール / お知らせ / 最新情報 /
# 通話募集 / 足あと / マイリスト / 無視 / ヘルプ / カップルレポート / 各種設定 / ログアウト / (空)
FOOTPRINT_GRID_INDEX = 4

# プロフィール NG ワード (検出時 見ちゃいや登録)
PROFILE_NG_WORDS = ("通報", "業者", "金銭", "条件")

# 足あと処理の対象年齢 (txt_age に含まれる文字列で判定)
FOOTPRINT_AGE_PATTERNS = ("20代", "18~19")

# BottomSheet (外見/仕事・学歴/ライフスタイル 等) 用
ID_BOTTOMSHEET = f"{APP_PACKAGE}:id/design_bottom_sheet"
ID_BOTTOMSHEET_CANCEL = f"{APP_PACKAGE}:id/btn_cancel"
ID_VIEW_TAG = f"{APP_PACKAGE}:id/view_tag"
ID_VIEW_TAG_ROW = f"{APP_PACKAGE}:id/view_tag_row"
ID_TXT_TAG_NAME = f"{APP_PACKAGE}:id/txt_tag_name"
ID_TXT_TITLE = f"{APP_PACKAGE}:id/txt_title"

# 送信バブル判定: 右端がこの比率以上なら自分の送信とみなす
SENT_BUBBLE_RIGHT_RATIO = 0.88

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# BAN / 警告画面の検出に使うテキストパターン (page_source 文字列上で部分一致)
# widget/happymail.catch_warning_screen の web 版判定文言を Android 用に流用 + 拡張。
# 誤検知を避けるため通常UI に出ない強い文言だけを並べる。
BAN_TEXT_PATTERNS = (
  "ご利用いただけません",
  "ご利用いただけなく",
  "アカウントが停止",
  "アカウントを停止",
  "アカウント停止",
  "規約違反",
  "利用規約違反",
  "登録は利用できません",
  "違反のご報告",
  "強制ログアウト",
  "ログインできません",
  "ログインできなく",
  "退会処理",
  "退会済み",
  "ご利用停止",
  "サービス停止",
)

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


def human_sleep(min_sec=1.0, max_sec=3.0):
  """人間的なランダム待機（正規分布寄り）。

  widget/happymail.py の同名関数のAndroid版（依存切り出し）。
  """
  mean = (min_sec + max_sec) / 2
  std = (max_sec - min_sec) / 4
  t = max(min_sec, min(max_sec, random.gauss(mean, std)))
  time.sleep(t)


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
# 足跡返し
# =============================================================================

def _open_footprint_list(driver):
  """マイページ → 足あとグリッドをタップして 足あと一覧画面に遷移する。"""
  # マッチング成立モーダル等の強制モーダルを先に処理
  _dismiss_matching_modal(driver)
  dismiss_popups(driver)
  open_mypage_tab(driver)
  human_sleep(1.0, 2.0)
  grid_buttons = driver.find_elements(AppiumBy.ID, ID_MYPAGE_GRID_BUTTON)
  if len(grid_buttons) <= FOOTPRINT_GRID_INDEX:
    raise RuntimeError(
      f"マイページのグリッドメニュー数が不足: {len(grid_buttons)} (期待 >= {FOOTPRINT_GRID_INDEX + 1})"
    )
  try:
    grid_buttons[FOOTPRINT_GRID_INDEX].click()
  except WebDriverException:
    udid = _udid(driver)
    bnds = grid_buttons[FOOTPRINT_GRID_INDEX].get_attribute("bounds") or ""
    _adb_tap_bounds(udid, bnds)
  time.sleep(2.5)
  dismiss_popups(driver)
  if not driver.find_elements(AppiumBy.ID, ID_FOOTMARK_BTN_RECEIVE):
    raise RuntimeError("足あと画面遷移に失敗 (footmark_btn_receive 不在)")


def _back_to_footprint_list(driver, max_tries=6):
  """back キー連打で 足あと一覧画面に戻る。"""
  for _ in range(max_tries):
    if driver.find_elements(AppiumBy.ID, ID_FOOTMARK_BTN_RECEIVE):
      return True
    try:
      driver.press_keycode(4)
    except WebDriverException:
      pass
    time.sleep(1.2)
    dismiss_popups(driver)
  return bool(driver.find_elements(AppiumBy.ID, ID_FOOTMARK_BTN_RECEIVE))


def _profile_has_ng_words(driver):
  """ユーザー詳細画面の txt_comment 群を結合して NG ワード判定する。"""
  try:
    comments = driver.find_elements(AppiumBy.ID, ID_TXT_COMMENT)
  except WebDriverException:
    return False
  full = " ".join((c.text or "") for c in comments)
  norm = full.replace(" ", "").replace("\n", "")
  return any(ng in norm for ng in PROFILE_NG_WORDS)


def _register_micha_iya_from_user_detail(driver):
  """ユーザー詳細画面から見ちゃいや登録する。

  前提: btn_ellipses_menu が画面にある (OtherProfileActivity)。
  呼び出し後の画面状態は不定 (登録ダイアログ閉じ後)。
  呼び出し側で `_back_to_footprint_list` 等で目的画面に戻すこと。
  """
  udid = _udid(driver)
  ells = driver.find_elements(AppiumBy.ID, ID_BTN_ELLIPSES_MENU)
  if not ells:
    print("  [micha_iya:detail] btn_ellipses_menu 不在")
    return False
  try:
    ells[0].click()
  except WebDriverException as e:
    print(f"  [micha_iya:detail] その他ボタン click 失敗: {e}")
    return False
  time.sleep(2)
  mi = _find_in_dump(driver, text="見ちゃいや登録")
  if not mi:
    print("  [micha_iya:detail] 見ちゃいや登録メニュー不在")
    try: driver.press_keycode(4)
    except WebDriverException: pass
    return False
  if not _adb_tap_bounds(udid, mi.get("bounds", "")):
    print("  [micha_iya:detail] 見ちゃいや登録 adb tap 失敗")
    return False
  time.sleep(2.5)
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
    print("  [micha_iya:detail] 登録ボタン不在")
    return False
  try:
    reg_btn.click()
  except WebDriverException as e:
    print(f"  [micha_iya:detail] 登録 click 失敗: {e}")
    return False
  time.sleep(2)
  end = time.time() + 8
  yes_btn = None
  while time.time() < end:
    yes = driver.find_elements(AppiumBy.ID, ID_YESNO_YES)
    if yes:
      yes_btn = yes[0]
      break
    time.sleep(0.4)
  if yes_btn is None:
    print("  [micha_iya:detail] OKダイアログ不在")
    return False
  try:
    yes_btn.click()
  except WebDriverException as e:
    print(f"  [micha_iya:detail] OK click 失敗: {e}")
    return False
  time.sleep(2)
  print("  [micha_iya:detail] 登録完了")
  return True


def _scroll_footprint_list(driver):
  """足あと一覧を上方向にスワイプ (= リストを下にスクロール) してより古い足あとを表示。"""
  udid = _udid(driver)
  if not udid:
    return
  subprocess.run(
    ["adb", "-s", udid, "shell", "input", "swipe", "540", "1700", "540", "700", "500"],
    check=False,
  )
  time.sleep(1.5)


def _return_footprint_only(driver, chara_data, send_cnt=1):
  """足跡返し本体: 足あと一覧から条件に合う最初のユーザーに 1 通送る。

  公開 API は `return_footpoint` (タイプ返し / マッチング返し / 足跡返し をオーケストレート)。
  この関数はそのうちの「足跡返し」担当。

  Args:
    driver: Appium driver
    chara_data: dict (`name`, `return_foot_message`, `chara_image`)
    send_cnt: この呼び出しで送る最大件数

  Returns:
    実際に送信できた件数 (0 以上の整数)。失敗時 0。
  """
  name = chara_data.get("name", "")
  return_foot_message = chara_data.get("return_foot_message", "") or ""
  chara_image = chara_data.get("chara_image", "") or ""

  if not return_foot_message:
    print(f"[{name}] return_foot_message が空のため return_foot スキップ")
    return 0

  try:
    _open_footprint_list(driver)
  except Exception as e:
    print(f"[{name}] 足あと画面に遷移できず: {e}")
    return 0

  sent_count = 0
  processed_names = set()
  attempts = 0
  scroll_no_progress = 0
  MAX_ATTEMPTS = 50
  MAX_SCROLL_NO_PROGRESS = 3

  while sent_count < send_cnt and attempts < MAX_ATTEMPTS:
    attempts += 1
    rows = driver.find_elements(AppiumBy.ID, ID_FRAME_SWIPE)
    if not rows:
      print(f"[{name}] 足あとリストが空")
      break

    target_row = None
    target_user_name = None
    target_user_age = None
    for row in rows:
      try:
        name_els = row.find_elements(AppiumBy.ID, ID_TXT_NAME)
        age_els = row.find_elements(AppiumBy.ID, ID_TXT_AGE)
        if not name_els or not age_els:
          continue
        u_name = (name_els[0].text or "").strip()
        u_age = (age_els[0].text or "").strip()
      except (NoSuchElementException, StaleElementReferenceException, WebDriverException):
        continue
      if not u_name or u_name in processed_names:
        continue
      if not any(p in u_age for p in FOOTPRINT_AGE_PATTERNS):
        processed_names.add(u_name)
        continue
      target_row = row
      target_user_name = u_name
      target_user_age = u_age
      break

    if target_row is None:
      scroll_no_progress += 1
      if scroll_no_progress > MAX_SCROLL_NO_PROGRESS:
        print(f"[{name}] スクロールしても候補なし → 終了")
        break
      print(f"[{name}] 表示中の足あとに候補なし → 下にスクロール")
      _scroll_footprint_list(driver)
      continue
    scroll_no_progress = 0

    print(f"[{name}] 足あと候補: {target_user_name} ({target_user_age})")
    processed_names.add(target_user_name)

    try:
      target_row.click()
    except (StaleElementReferenceException, WebDriverException) as e:
      print(f"  [{name}] 行クリック失敗: {e}")
      continue
    time.sleep(2.5)
    dismiss_popups(driver)

    if _profile_has_ng_words(driver):
      print(f"  [{name}] {target_user_name}: NGワード検出 → 見ちゃいや登録")
      try:
        _register_micha_iya_from_user_detail(driver)
      except Exception:
        print(traceback.format_exc())
      _back_to_footprint_list(driver)
      continue

    send_btns = driver.find_elements(AppiumBy.ID, ID_BTN_SEND_MSG)
    if not send_btns:
      print(f"  [{name}] {target_user_name}: btn_send_msg 不在 → スキップ")
      _back_to_footprint_list(driver)
      continue
    try:
      send_btns[0].click()
    except (StaleElementReferenceException, WebDriverException) as e:
      print(f"  [{name}] btn_send_msg click 失敗: {e}")
      _back_to_footprint_list(driver)
      continue
    time.sleep(2.5)
    dismiss_popups(driver)

    if not driver.find_elements(AppiumBy.ID, ID_FRAME_FIRST_MESSAGE):
      print(f"  [{name}] {target_user_name}: 既存スレッドあり → スキップ")
      _back_to_footprint_list(driver)
      continue

    if not driver.find_elements(AppiumBy.ID, ID_EDIT_INPUT):
      print(f"  [{name}] {target_user_name}: edit_text_message_input 不在 → スキップ")
      _back_to_footprint_list(driver)
      continue

    text = return_foot_message.format(name=target_user_name)
    try:
      ok = _send_text_message(driver, text)
    except WebDriverException:
      raise
    except Exception:
      print(traceback.format_exc())
      ok = False

    if not ok:
      print(f"  [{name}] {target_user_name}: 送信エコー未確認 → スキップ扱い")
      _back_to_footprint_list(driver)
      continue

    sent_count += 1
    print(f"  [{name}] {target_user_name}: 送信OK ({sent_count}/{send_cnt})")

    if chara_image:
      try:
        send_image(driver, chara_image)
      except Exception:
        print(f"  [{name}] {target_user_name}: 画像送信失敗")
        print(traceback.format_exc())

    _back_to_footprint_list(driver)
    human_sleep(1.5, 3.5)

  return sent_count


# =============================================================================
# タイプ返し / マッチング返し (typelist タブ)
# =============================================================================

def _open_typelist_tab(driver):
  """typelist タブに遷移する。"""
  # マッチング成立モーダル等の強制モーダルを先に処理
  _dismiss_matching_modal(driver)
  dismiss_popups(driver)
  if not driver.find_elements(AppiumBy.ID, ID_TYPELIST_TAB):
    _ensure_main_tab(driver)
  if not driver.find_elements(AppiumBy.ID, ID_TYPELIST_TAB):
    raise RuntimeError("typelist タブが見つからない (メインタブに居ない)")
  driver.find_element(AppiumBy.ID, ID_TYPELIST_TAB).click()
  time.sleep(2)
  dismiss_popups(driver)
  # フィルタタブ群のいずれかが見えるまで待つ
  end = time.time() + 5
  while time.time() < end:
    if driver.find_elements(AppiumBy.ID, ID_TYPELIST_BTN_RECEIVE):
      return True
    time.sleep(0.5)
  return False


def _select_typelist_filter(driver, filter_id):
  """typelist 内のフィルタタブ (相手から/自分から/マッチング) を1つ選択する。"""
  els = driver.find_elements(AppiumBy.ID, filter_id)
  if not els:
    return False
  try:
    els[0].click()
  except WebDriverException:
    udid = _udid(driver)
    bnds = els[0].get_attribute("bounds") or ""
    if not _adb_tap_bounds(udid, bnds):
      return False
  time.sleep(2)
  dismiss_popups(driver)
  return True


def _back_to_typelist(driver, max_tries=6):
  """back キー連打で typelist タブ画面 (3つのフィルタタブが見える状態) に戻る。"""
  for _ in range(max_tries):
    if driver.find_elements(AppiumBy.ID, ID_TYPELIST_BTN_RECEIVE):
      return True
    try:
      driver.press_keycode(4)
    except WebDriverException:
      pass
    time.sleep(1.2)
    dismiss_popups(driver)
  return bool(driver.find_elements(AppiumBy.ID, ID_TYPELIST_BTN_RECEIVE))


def _confirm_yes_dialog(driver, timeout=4):
  """common_yesnodialog_tv_yes が出ていれば押す。出なければスルー。"""
  end = time.time() + timeout
  while time.time() < end:
    yes = driver.find_elements(AppiumBy.ID, ID_YESNO_YES)
    if yes:
      try:
        yes[0].click()
        time.sleep(1.5)
        return True
      except WebDriverException:
        pass
    time.sleep(0.4)
  return False


def _dismiss_matching_modal(driver):
  """マッチング成立モーダル ('Best matching ... マッチングしました') を閉じる試み。

  タイプ返しで両片想い成立時に出るオーバーレイモーダル。back キーや一般的な
  dismiss_popups では閉じない強制モーダル。
  **アプリの強制終了 (`am force-stop` / `terminate_app`) は使わない方針**のため、
  以下の手段でアプリ内から正規に閉じる:
    1. `閉じる` / `Close` 等の content-desc を持つ要素を Appium で探してタップ
    2. clickable=true の右上 ImageView を bounds で抽出してタップ
    3. 失敗時はログ出力のみ (上位の判断に委ねる)

  Returns:
    True: 閉じることに成功 / False: 閉じられなかった or モーダルなし
  """
  try:
    src = driver.page_source
  except WebDriverException:
    return False
  if "マッチングしました" not in src and "Best matching" not in src:
    return False

  print("  [matching_modal] 'マッチングしました' モーダルを検出 → 閉じる試み")
  udid = _udid(driver)

  # ── 試行 1: content-desc で × を探して click ──
  for query in (
    '//*[@content-desc="閉じる"]',
    '//*[@content-desc="Close"]',
    '//*[@content-desc="close"]',
    '//*[@content-desc="×"]',
  ):
    try:
      els = driver.find_elements(AppiumBy.XPATH, query)
    except WebDriverException:
      els = []
    for el in els:
      try:
        if el.is_displayed():
          el.click()
          time.sleep(1.5)
          new_src = driver.page_source
          if "マッチングしました" not in new_src:
            print("  [matching_modal] content-desc で閉じた")
            return True
      except (StaleElementReferenceException, WebDriverException):
        continue

  # ── 試行 2: 右上にある clickable な ImageView の bounds をタップ ──
  try:
    candidates = driver.find_elements(
      AppiumBy.XPATH,
      '//android.widget.ImageView[@clickable="true"]',
    )
  except WebDriverException:
    candidates = []
  for el in candidates:
    try:
      bounds = el.get_attribute("bounds") or ""
      parsed = _parse_bounds(bounds)
      if not parsed:
        continue
      x1, y1, x2, y2 = parsed
      # 「右上の小さいアイコン」: x_max が画面右側、y が上半分、サイズ小さめ
      if x2 > 900 and y1 < 1000 and (x2 - x1) < 250 and (y2 - y1) < 250:
        if udid:
          cx = (x1 + x2) // 2
          cy = (y1 + y2) // 2
          print(f"  [matching_modal] 右上 ImageView adb tap ({cx},{cy}) bounds={bounds}")
          subprocess.run(
            ["adb", "-s", udid, "shell", "input", "tap", str(cx), str(cy)],
            check=False,
          )
          time.sleep(1.5)
          try:
            new_src = driver.page_source
            if "マッチングしました" not in new_src:
              print("  [matching_modal] 右上 ImageView で閉じた")
              return True
          except WebDriverException:
            pass
    except (StaleElementReferenceException, WebDriverException):
      continue

  print("  [matching_modal] 自動で閉じられず — ユーザー手動対応推奨。今回の周は中断扱い。")
  return False


def _return_type_only(driver, chara_data, send_cnt=1):
  """タイプ返し: typelist タブ → 相手から → 現在カードに btn_send_type をタップ。

  メッセージ送信ではなく「タイプを返す」アクションのみ (ワンタップ)。
  年齢が 20代 / 18-19 でない場合はスキップ (誤送信回避)。

  Returns:
    タイプ送信できた件数 (0 or send_cnt)。
  """
  name = chara_data.get("name", "")
  try:
    if not _open_typelist_tab(driver):
      print(f"[{name}] type: typelist タブに遷移失敗")
      return 0
  except RuntimeError as e:
    print(f"[{name}] type: {e}")
    return 0
  if not _select_typelist_filter(driver, ID_TYPELIST_BTN_RECEIVE):
    print(f"[{name}] type: 相手から フィルタ選択失敗")
    return 0

  sent = 0
  attempts = 0
  while sent < send_cnt and attempts < 20:
    attempts += 1
    if driver.find_elements(AppiumBy.ID, ID_LAYOUT_EMPTY_STATE):
      print(f"[{name}] type: 受信タイプなし (empty)")
      break

    age_els = driver.find_elements(AppiumBy.ID, ID_TXT_AGE)
    if age_els:
      user_age = (age_els[0].text or "").strip()
      if not any(p in user_age for p in FOOTPRINT_AGE_PATTERNS):
        print(f"[{name}] type: 対象外年齢 ({user_age!r}) → 中止")
        break

    name_els = driver.find_elements(AppiumBy.ID, ID_TXT_NAME)
    user_name = (name_els[0].text or "").strip() if name_els else "(unknown)"

    send_type_btns = driver.find_elements(AppiumBy.ID, ID_BTN_SEND_TYPE)
    if not send_type_btns:
      print(f"[{name}] type: btn_send_type 不在 → 中止")
      break
    try:
      send_type_btns[0].click()
    except WebDriverException as e:
      print(f"[{name}] type: btn_send_type click 失敗: {e}")
      break
    time.sleep(2)
    # 確認ダイアログがあれば yes
    _confirm_yes_dialog(driver, timeout=4)
    dismiss_popups(driver)
    # マッチング成立モーダル ('Best matching') が出る可能性あり (両片想い時)。閉じる試み
    _dismiss_matching_modal(driver)
    sent += 1
    print(f"  [{name}] type: タイプ返し OK ({user_name}) {sent}/{send_cnt}")
    human_sleep(1.5, 3.0)

  return sent


def _return_matching_only(driver, chara_data, send_cnt=1):
  """マッチング返し: typelist タブ → マッチング → リスト先頭の20代ユーザーへ初回メッセージ。

  メッセージは fst_message (元 widget/happymail.return_matching と同じ)。
  既存スレッドありユーザーはスキップ。NG ワード検出で見ちゃいや登録。

  Returns:
    送信できた件数 (0 or 1)。
  """
  name = chara_data.get("name", "")
  fst_message = chara_data.get("fst_message", "") or ""
  chara_image = chara_data.get("chara_image", "") or ""
  if not fst_message:
    print(f"[{name}] matching: fst_message が空のためスキップ")
    return 0

  try:
    if not _open_typelist_tab(driver):
      print(f"[{name}] matching: typelist タブ遷移失敗")
      return 0
  except RuntimeError as e:
    print(f"[{name}] matching: {e}")
    return 0
  if not _select_typelist_filter(driver, ID_TYPELIST_BTN_MUTUAL_LOVE):
    print(f"[{name}] matching: マッチング フィルタ選択失敗")
    return 0

  # 空状態
  if driver.find_elements(AppiumBy.ID, ID_LAYOUT_EMPTY_STATE):
    print(f"[{name}] matching: マッチングなし (empty)")
    return 0

  # リスト行を取得
  rows = driver.find_elements(AppiumBy.ID, ID_FRAME_SWIPE)
  if not rows:
    print(f"[{name}] matching: frame_swipe 行不在")
    return 0

  # 最初の20代ユーザーを選ぶ
  target_row = None
  target_user_name = None
  target_user_age = None
  for row in rows:
    try:
      name_els = row.find_elements(AppiumBy.ID, ID_TXT_NAME)
      age_els = row.find_elements(AppiumBy.ID, ID_TXT_AGE)
      if not name_els or not age_els:
        continue
      u_name = (name_els[0].text or "").strip()
      u_age = (age_els[0].text or "").strip()
    except (NoSuchElementException, StaleElementReferenceException, WebDriverException):
      continue
    if not u_name:
      continue
    if not any(p in u_age for p in FOOTPRINT_AGE_PATTERNS):
      continue
    target_row = row
    target_user_name = u_name
    target_user_age = u_age
    break

  if target_row is None:
    print(f"[{name}] matching: 候補ユーザーなし (全て対象外年齢)")
    return 0

  print(f"[{name}] matching: 候補 {target_user_name} ({target_user_age})")

  try:
    target_row.click()
  except (StaleElementReferenceException, WebDriverException) as e:
    print(f"  [{name}] 行クリック失敗: {e}")
    return 0
  time.sleep(2.5)
  dismiss_popups(driver)

  if _profile_has_ng_words(driver):
    print(f"  [{name}] {target_user_name}: NGワード検出 → 見ちゃいや登録")
    try:
      _register_micha_iya_from_user_detail(driver)
    except Exception:
      print(traceback.format_exc())
    _back_to_typelist(driver)
    return 0

  send_btns = driver.find_elements(AppiumBy.ID, ID_BTN_SEND_MSG)
  if not send_btns:
    print(f"  [{name}] {target_user_name}: btn_send_msg 不在")
    _back_to_typelist(driver)
    return 0
  try:
    send_btns[0].click()
  except (StaleElementReferenceException, WebDriverException) as e:
    print(f"  [{name}] btn_send_msg click 失敗: {e}")
    _back_to_typelist(driver)
    return 0
  time.sleep(2.5)
  dismiss_popups(driver)

  if not driver.find_elements(AppiumBy.ID, ID_FRAME_FIRST_MESSAGE):
    print(f"  [{name}] {target_user_name}: 既存スレッドあり → スキップ")
    _back_to_typelist(driver)
    return 0

  if not driver.find_elements(AppiumBy.ID, ID_EDIT_INPUT):
    print(f"  [{name}] {target_user_name}: 入力欄不在 → スキップ")
    _back_to_typelist(driver)
    return 0

  text = fst_message.format(name=target_user_name)
  try:
    ok = _send_text_message(driver, text)
  except WebDriverException:
    raise
  except Exception:
    print(traceback.format_exc())
    ok = False

  if not ok:
    print(f"  [{name}] {target_user_name}: 送信エコー未確認")
    _back_to_typelist(driver)
    return 0

  print(f"  [{name}] {target_user_name}: マッチング返し 送信OK")
  if chara_image:
    try:
      send_image(driver, chara_image)
    except Exception:
      print(traceback.format_exc())

  _back_to_typelist(driver)
  return 1


# =============================================================================
# 能動アクションのオーケストレーター
# =============================================================================

def return_footpoint(driver, chara_data, send_cnt=1):
  """タイプ返し → マッチング返し → 足跡返し の順で実行する。

  実行ルール:
    1. **タイプ返し**: 常に実行 (タップのみで「通」ではないので戻り値カウントには含めない)
    2. **マッチング返し**: 試行。1 件送れたら以降スキップ
    3. **足跡返し**: マッチング返しが 0 件のときだけ実行

  1ループ1通制約により、能動送信 (マッチング返し or 足跡返し) は最大 1 件。
  h_app_drivers_android.py から呼ばれる公開 API。

  Args:
    driver: Appium driver
    chara_data: dict (`name`, `return_foot_message`, `fst_message`, `chara_image` 等)
    send_cnt: マッチング返し / 足跡返し の最大件数 (推奨 1)

  Returns:
    daily_limit に加算する件数 (= マッチング返し + 足跡返し の送信数)。
    タイプ返しは含まれない。
  """
  name = chara_data.get("name", "")

  # 1) タイプ返し (常に実行・カウント対象外)
  try:
    type_sent = _return_type_only(driver, chara_data, send_cnt=1) or 0
    if type_sent > 0:
      print(f"[{name}] return_footpoint type 完了 +{type_sent} (カウント対象外)")
    else:
      print(f"[{name}] return_footpoint type: 0 件")
  except WebDriverException:
    raise
  except Exception:
    print(f"[{name}] type: 例外")
    print(traceback.format_exc())

  # 2) マッチング返し (1 件成功で能動送信ノルマ消化、足跡返しスキップ)
  try:
    matching_sent = _return_matching_only(driver, chara_data, send_cnt=send_cnt) or 0
  except WebDriverException:
    raise
  except Exception:
    print(f"[{name}] matching: 例外")
    print(traceback.format_exc())
    matching_sent = 0

  if matching_sent > 0:
    print(f"[{name}] return_footpoint matching 成功 +{matching_sent} → 足跡返しスキップ")
    return matching_sent

  # 3) 足跡返し (マッチング返しが 0 件のときのみ)
  print(f"[{name}] return_footpoint matching 0 件 → 足跡返しへフォールバック")
  try:
    foot_sent = _return_footprint_only(driver, chara_data, send_cnt=send_cnt) or 0
  except WebDriverException:
    raise
  except Exception:
    print(f"[{name}] footprint: 例外")
    print(traceback.format_exc())
    foot_sent = 0

  if foot_sent > 0:
    print(f"[{name}] return_footpoint footprint 成功 +{foot_sent}")
  else:
    print(f"[{name}] return_footpoint footprint: 0 件 (能動送信なしの周)")
  return foot_sent


# =============================================================================
# BAN / 警告画面検出
# =============================================================================

def detect_ban_screen(driver):
  """画面が BAN / 利用停止 / 強制ログアウト 等の状態かを検出する。

  page_source を取得して BAN_TEXT_PATTERNS のいずれかが含まれているかチェックする。
  誤検知を避けるため、通常 UI に出ない強い文言のみを対象としている。

  Returns:
    検出時はマッチした文言 (str)、正常時は None。
  """
  try:
    src = driver.page_source
  except WebDriverException:
    return None
  except Exception:
    return None
  for pattern in BAN_TEXT_PATTERNS:
    if pattern in src:
      return pattern
  return None


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


def _ensure_my_profile(driver, max_back=8):
  """現在の画面が MyProfile になるまで戻るキーを連打。
  失敗時 (max_back に達しても戻らない) は False。
  選択肢ピッカーや子 Activity に取り残されている場合の復帰用。
  """
  for _ in range(max_back):
    if driver.find_elements(AppiumBy.ID, ID_MY_PROFILE_SCROLL):
      return True
    _back_one(driver)
  return bool(driver.find_elements(AppiumBy.ID, ID_MY_PROFILE_SCROLL))


def _normalize(s):
  """半角/全角・互換文字の差を吸収するための NFKC 正規化。"""
  if not s:
    return ""
  return unicodedata.normalize("NFKC", str(s)).strip()


def _wait_for_bottomsheet(driver, timeout=5):
  end = time.time() + timeout
  while time.time() < end:
    if driver.find_elements(AppiumBy.ID, ID_BOTTOMSHEET):
      return True
    time.sleep(0.3)
  return False


def _close_bottomsheet(driver):
  """BottomSheet をシート外領域タップで閉じる。

  btn_cancel (✕) も back キーも変更を確定保存しないケースがあるため、
  シートの上の透明領域 (modal scrim) をタップして dismiss する。
  modal=true の BottomSheet ではこれが標準的な閉じ方。
  """
  udid = _udid(driver)
  # シートの bnd は概ね [0,556][1080,2270]。それより上の y=200 付近をタップ。
  subprocess.run(
    ["adb", "-s", udid, "shell", "input", "tap", "540", "200"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
  )
  time.sleep(1.5)
  # それでも閉じなければ back キー fallback
  if driver.find_elements(AppiumBy.ID, ID_BOTTOMSHEET):
    _back_one(driver)
    time.sleep(1.0)


# 「未指定」を意味する値 (該当セクションの選択を解除する)
_UNSET_VALUES = {"指定しない", "指定なし", "ナイショ"}


def _bottomsheet_section_state(driver, section):
  """シート内の section の (sec_top, sec_next_top, rows[(row_el, tag_text, selected)]) を返す。
  section が見えなければ (None, None, [])。
  """
  try:
    root = ET.fromstring(driver.page_source)
  except (ET.ParseError, WebDriverException):
    return None, None, []
  section_titles = []
  for el in root.iter():
    if el.attrib.get("resource-id", "").endswith(":id/txt_title") and el.attrib.get("text"):
      b = _parse_bounds(el.attrib.get("bounds", ""))
      if b:
        section_titles.append((el.attrib["text"], b[1]))
  section_titles.sort(key=lambda x: x[1])
  sec_top = None
  sec_next_top = None
  for i, (t, y) in enumerate(section_titles):
    if t == section:
      sec_top = y
      if i + 1 < len(section_titles):
        sec_next_top = section_titles[i + 1][1]
      break
  if sec_top is None:
    return None, None, []
  rows = []
  for el in root.iter():
    if not el.attrib.get("resource-id", "").endswith(":id/view_tag_row"):
      continue
    b = _parse_bounds(el.attrib.get("bounds", ""))
    if not b:
      continue
    if b[1] < sec_top:
      continue
    if sec_next_top is not None and b[1] >= sec_next_top:
      continue
    tag_text = ""
    for child in el.iter():
      if child.attrib.get("resource-id", "").endswith(":id/txt_tag_name"):
        tag_text = child.attrib.get("text", "") or ""
        break
    rows.append((el, tag_text, el.attrib.get("selected") == "true"))
  return sec_top, sec_next_top, rows


def _tap_row(driver, row_el):
  """row_el (view_tag_row) を adb tap で押下。"""
  udid = _udid(driver)
  b = _parse_bounds(row_el.attrib.get("bounds", ""))
  if not b:
    return False
  cx = (b[0] + b[2]) // 2
  cy = (b[1] + b[3]) // 2
  subprocess.run(
    ["adb", "-s", udid, "shell", "input", "tap", str(cx), str(cy)],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
  )
  return True


def _select_bottomsheet_section(driver, section, value, max_scroll=10, unset_target=None):
  """BottomSheet が開いている前提で、section 内の value タグを設定する。

  - value が UNSET (指定しない/ナイショ) なら:
    * unset_target (現在 MyProfile に表示されている値) が与えられていれば、その行を
      タップして解除する。
    * unset_target が無い場合は selected="true" の行を解除タップ (selected が信頼
      できない端末では何も起きない可能性あり)。
  - 通常の値なら該当行を選択する。
  - selected 属性は実機では即時更新されないため "変更なし" 判定はせず、毎回タップする。
  - section の末端まで見えているのに値が無い場合は即諦める。
  """
  norm_value = _normalize(value)
  is_unset = value in _UNSET_VALUES
  norm_unset_target = _normalize(unset_target or "")
  udid = _udid(driver)
  for attempt in range(max_scroll):
    sec_top, sec_next_top, rows = _bottomsheet_section_state(driver, section)
    if sec_top is not None:
      if is_unset:
        # 1) unset_target が指定されていればその行をタップ (現在選択値の解除)
        if norm_unset_target:
          target = next((r for r in rows if _normalize(r[1]) == norm_unset_target), None)
          if target is not None:
            row_el, txt, _ = target
            if _tap_row(driver, row_el):
              time.sleep(1.5)
              print(f"  [sheet:{section}] 解除: {txt}")
              return True
            return False
          if sec_next_top is not None:
            # セクション内に該当無し
            print(f"  [sheet:{section}] 解除対象「{unset_target}」がセクション内に無し")
            return False
        else:
          # 2) selected ベース fallback (アプリが selected を更新する場合のみ機能)
          sel_row = next((r for r in rows if r[2]), None)
          if sel_row is None:
            print(f"  [sheet:{section}] 変更なし (未指定)")
            return True
          row_el, sel_text, _ = sel_row
          if _tap_row(driver, row_el):
            time.sleep(1.5)
            print(f"  [sheet:{section}] 解除: {sel_text}")
            return True
          return False
      else:
        # 通常の値
        target = next((r for r in rows if _normalize(r[1]) == norm_value), None)
        if target is not None:
          row_el, _, _ = target
          if _tap_row(driver, row_el):
            time.sleep(1.5)
            print(f"  [sheet:{section}] 設定: {value}")
            return True
          return False
        if sec_next_top is not None:
          print(f"  [sheet:{section}] 「{value}」がセクション内に存在しません")
          return False

    # 下にスクロール
    subprocess.run(
      ["adb", "-s", udid, "shell", "input", "swipe", "540", "1800", "540", "900", "300"],
      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(0.6)

  print(f"  [sheet:{section}] 「{value}」が見つかりません")
  return False


def _read_my_profile_value(driver, label):
  """MyProfile 上の label 行の表示値 (txt_value/txt_comment) を読む。
  見つからない / 値ロード前なら "" を返す。"""
  try:
    root = ET.fromstring(driver.page_source)
  except (ET.ParseError, WebDriverException):
    return ""
  for el in root.iter():
    if (el.attrib.get("text", "") or "") != label:
      continue
    rid = el.attrib.get("resource-id", "") or ""
    if not (rid.endswith(":id/txt_title") or rid.endswith(":id/txt_header")):
      continue
    bnd = el.attrib.get("bounds", "")
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bnd)
    if not m:
      continue
    ly1 = int(m.group(2)); ly2 = int(m.group(4))
    val = ""
    best_dy = None
    for vel in root.iter():
      vrid = vel.attrib.get("resource-id", "") or ""
      if not (vrid.endswith(":id/txt_value") or vrid.endswith(":id/txt_comment")):
        continue
      vbnd = vel.attrib.get("bounds", "") or ""
      vm = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", vbnd)
      if not vm:
        continue
      vy1 = int(vm.group(2))
      if abs(vy1 - ly1) < 60:
        val = vel.attrib.get("text", "") or val
        return val
      if vy1 >= ly2 - 5:
        dy = vy1 - ly2
        if dy < 250 and (best_dy is None or dy < best_dy):
          val = vel.attrib.get("text", "") or val
          best_dy = dy
    return val
  return ""


def _value_matches(actual, expected):
  """expected が "指定しない/ナイショ" の場合は actual が未設定 (空 / タップして設定) なら一致。"""
  if expected in _UNSET_VALUES:
    return actual in ("", "タップして設定", "指定しない", "ナイショ")
  return _normalize(actual) == _normalize(expected)


def _process_bottomsheet_field(driver, label, value, skip_check=False):
  """1セクションをシートで開き、値タップして閉じる。1回の試行のみ。
  反映確認は呼び出し側で別途実施する。

  skip_check=True なら "変更なし" 判定をスキップして即シート開く
  (呼び出し時点で未反映が確定している場合、誤判定を避けるため)。

  value が UNSET 値 (指定しない 等) のときは、シート開く前に MyProfile 上の現在値を
  読み取り、それを解除対象として _select_bottomsheet_section に渡す
  (selected 属性が信頼できない端末で確実に解除するため)。
  """
  if not _ensure_my_profile(driver):
    print(f"  [sheet:{label}] MyProfile に復帰できず")
    return False
  _scroll_my_profile_top(driver, max_swipes=8)

  is_unset = value in _UNSET_VALUES
  current_my_profile = ""
  if is_unset or not skip_check:
    # ラベルが見えるまでスクロールして現在値を読む
    current_my_profile = _scroll_to_value_for_label(driver, label) or ""

  if not skip_check and not is_unset:
    if _value_matches(current_my_profile, value):
      print(f"  [sheet:{label}] 変更なし ({current_my_profile})")
      return True
  if is_unset and current_my_profile in ("", "タップして設定", "指定しない", "ナイショ"):
    print(f"  [sheet:{label}] 変更なし (未指定)")
    return True

  _scroll_my_profile_top(driver, max_swipes=8)
  if not _scroll_to_label_and_tap(driver, label):
    print(f"  [sheet:{label}] 行が見つかりません")
    return False
  time.sleep(2)
  if not _wait_for_bottomsheet(driver, timeout=5):
    print(f"  [sheet:{label}] BottomSheet が開かなかった")
    _ensure_my_profile(driver)
    return False
  _select_bottomsheet_section(driver, label, value, unset_target=current_my_profile if is_unset else None)
  time.sleep(0.5)
  _close_bottomsheet(driver)
  time.sleep(1)
  _ensure_my_profile(driver)
  time.sleep(0.5)
  return True


def _scroll_to_value_for_label(driver, label, max_scroll=15):
  """MyProfile をスクロールしながらラベル行を探し、その表示値 (txt_value/txt_comment)
  を返す。見つからなければ None。"""
  udid = _udid(driver)
  for _ in range(max_scroll):
    val = _read_my_profile_value(driver, label)
    if val is not None and val != "":
      return val
    # ラベル自体を見つけたが値が空かもしれない — そういう場合は val == "" で抜けない
    # ラベルが page_source に存在するか確認
    try:
      root = ET.fromstring(driver.page_source)
    except (ET.ParseError, WebDriverException):
      time.sleep(0.4); continue
    label_seen = any(
      (el.attrib.get("text", "") or "") == label
      and (el.attrib.get("resource-id", "") or "").endswith((":id/txt_title", ":id/txt_header"))
      for el in root.iter()
    )
    if label_seen:
      return val if val is not None else ""
    subprocess.run(
      ["adb", "-s", udid, "shell", "input", "swipe", "540", "1700", "540", "500", "400"],
      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(0.8)
  return None


def _process_bottomsheet_group(driver, open_label, sections, chara_data):
  """各セクションを 1 シート 1 セクションで処理 (1回試行)。"""
  for section_label, key in sections:
    val = chara_data.get(key)
    if not val:
      continue
    _process_bottomsheet_field(driver, section_label, val)
    time.sleep(0.3)
  return True


def _select_list_field(driver, label, value, expected_header=None):
  """ProfItemSelectActivity 形式 (単一選択リスト) のフィールドを設定する。

  Args:
    driver: Appium driver
    label: MyProfile 上のラベル (例: "血液型")
    value: 設定したい値 (例: "Ａ型")
    expected_header: ヘッダータイトルが label と異なる場合に指定 (例: 詳細エリア → "市区町村選択")
  """
  if not value:
    return False
  if not _ensure_my_profile(driver):
    print(f"  [select:{label}] MyProfile に復帰できず")
    return False
  _scroll_my_profile_top(driver, max_swipes=8)
  if not _scroll_to_label_and_tap(driver, label):
    print(f"  [select:{label}] 行が見つかりません")
    return False
  time.sleep(2)

  # ProfItemSelectActivity に到達したか確認 (ヘッダータイトルがラベルと一致)
  hdr_target = expected_header or label
  end = time.time() + 8
  ok = False
  current_title = ""
  while time.time() < end:
    titles = driver.find_elements(AppiumBy.ID, ID_TXT_HEADER_TITLE)
    if titles:
      current_title = titles[0].text or ""
      if current_title == hdr_target:
        ok = True
        break
    time.sleep(0.5)
  if not ok:
    print(f"  [select:{label}] セレクタ画面に到達せず (現ヘッダー={current_title!r})")
    _ensure_my_profile(driver)
    return False

  udid = _udid(driver)
  norm_value = _normalize(value)
  # まずリスト先頭まで戻す (画面ロード時のスクロール位置に依存させない)
  for _ in range(8):
    subprocess.run(
      ["adb", "-s", udid, "shell", "input", "swipe", "540", "500", "540", "1900", "300"],
      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(0.4)
  found = False
  for _ in range(40):
    rows = driver.find_elements(AppiumBy.ID, ID_PROFITEMSELECT_ROW)
    target_row = None
    for r in rows:
      titles = r.find_elements(AppiumBy.ID, ID_PROFITEMSELECT_TITLE)
      if not titles:
        continue
      if _normalize(titles[0].text or "") == norm_value:
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
          _ensure_my_profile(driver)
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
    _ensure_my_profile(driver)
    return False

  # MyProfile に戻る (タップで自動遷移しない場合は手動 back)
  end = time.time() + 4
  while time.time() < end:
    if driver.find_elements(AppiumBy.ID, ID_MY_PROFILE_SCROLL):
      return True
    time.sleep(0.5)
  _ensure_my_profile(driver)
  return True


def _select_prefecture(driver, prefecture):
  """居住地行をタップして AreaSelectExpandableActivity を開き、prefecture 行をタップ→
  back キーで MyProfile に戻る (これで 居住地 が確定する)。

  既に同じ都道府県が選択済み (parent_check checked=true) なら何もしない。
  """
  if not prefecture:
    return False
  if not _ensure_my_profile(driver):
    print(f"  [residence:居住地] MyProfile に復帰できず")
    return False
  _scroll_my_profile_top(driver, max_swipes=8)
  if not _scroll_to_label_and_tap(driver, "居住地"):
    print(f"  [residence:居住地] 行が見つかりません")
    return False
  time.sleep(2)

  end = time.time() + 8
  ok = False
  while time.time() < end:
    titles = driver.find_elements(AppiumBy.ID, ID_TXT_HEADER_TITLE)
    if titles and (titles[0].text or "") == "居住地":
      ok = True
      break
    time.sleep(0.5)
  if not ok:
    print(f"  [residence:居住地] AreaSelect 画面に到達せず")
    _ensure_my_profile(driver)
    return False

  udid = _udid(driver)
  norm_pref = _normalize(prefecture)
  found = False
  already = False
  for _ in range(20):
    rows = driver.find_elements(AppiumBy.ID, ID_AREA_PARENT_ROW)
    target = None
    for r in rows:
      ts = r.find_elements(AppiumBy.ID, ID_AREA_PARENT_TITLE)
      if not ts: continue
      if _normalize(ts[0].text or "") != norm_pref: continue
      target = r
      checks = r.find_elements(AppiumBy.ID, ID_AREA_PARENT_CHECK)
      if checks and checks[0].get_attribute("checked") == "true":
        already = True
      break
    if target is not None:
      if already:
        print(f"  [residence:居住地] 変更なし ({prefecture})")
      else:
        bnd = target.get_attribute("bounds") or ""
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bnd)
        if not m:
          print(f"  [residence:居住地] bounds 解析失敗: {bnd}")
          _back_one(driver); _ensure_my_profile(driver)
          return False
        cx = (int(m.group(1)) + int(m.group(3))) // 2
        cy = (int(m.group(2)) + int(m.group(4))) // 2
        subprocess.run(
          ["adb", "-s", udid, "shell", "input", "tap", str(cx), str(cy)],
          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(1.2)
        print(f"  [residence:居住地] 設定: {prefecture}")
      found = True
      break
    subprocess.run(
      ["adb", "-s", udid, "shell", "input", "swipe", "540", "1700", "540", "800", "300"],
      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(0.7)

  if not found:
    print(f"  [residence:居住地] 「{prefecture}」が見つかりません")
    _back_one(driver); _ensure_my_profile(driver)
    return False

  # back で確定
  _back_one(driver)
  time.sleep(1.2)
  _ensure_my_profile(driver)
  return True


# MyProfile ラベル ↔ chara_data キー マッピング (ProfItemSelectActivity 単一選択型)。
PROFILE_LIST_FIELDS = [
  ("年齢", "age"),
  ("出身地", "birth_place"),
  ("血液型", "blood_type"),
  ("星座", "constellation"),
]

# BottomSheet グループ。各エントリで MyProfile のラベルをタップ → 1セクションのみ
# 設定 → シート閉じる → 次へ。シート内で複数セクション操作するとアプリ側の保存が
# 不安定になるので、必ず1シート1セクションで完結させる。
PROFILE_BOTTOMSHEET_GROUPS = [
  ("身長", [("身長", "height")]),
  ("スタイル", [("スタイル", "style")]),
  ("ルックス", [("ルックス", "looks")]),
  ("職業", [("職業", "job")]),
  ("学歴", [("学歴", "education")]),
  ("休日", [("休日", "holiday")]),
  ("子ども", [("子ども", "having_children")]),
  ("タバコ", [("タバコ", "smoking")]),
  ("お酒", [("お酒", "sake")]),
  ("クルマ", [("クルマ", "car_ownership")]),
  ("同居人", [("同居人", "roommate")]),
  ("兄弟姉妹", [("兄弟姉妹", "brothers_and_sisters")]),
  ("出会うまでの希望", [("出会うまでの希望", "until_we_met")]),
  ("初回デート費用", [("初回デート費用", "date_expenses")]),
]


# プロフィール検証用 ラベル ↔ chara_data キー
PROFILE_VERIFY_LABELS = [
  ("身長", "height"),
  ("スタイル", "style"),
  ("ルックス", "looks"),
  ("職業", "job"),
  ("学歴", "education"),
  ("休日", "holiday"),
  ("子ども", "having_children"),
  ("タバコ", "smoking"),
  ("お酒", "sake"),
  ("クルマ", "car_ownership"),
  ("同居人", "roommate"),
  ("兄弟姉妹", "brothers_and_sisters"),
  ("出会うまでの希望", "until_we_met"),
  ("初回デート費用", "date_expenses"),
  ("居住地", "activity_area"),
  ("詳細エリア", "detail_activity_area"),
  ("年齢", "age"),
  ("出身地", "birth_place"),
  ("血液型", "blood_type"),
  ("星座", "constellation"),
]


def _read_all_my_profile_values(driver):
  """MyProfile を開いてスクロールしながら PROFILE_VERIFY_LABELS の値を全部読む。"""
  values = {}
  _ensure_main_tab(driver)
  if not _open_my_profile(driver):
    return values
  _scroll_my_profile_top(driver, max_swipes=12)
  time.sleep(0.5)
  remaining = {l for l, _ in PROFILE_VERIFY_LABELS}
  udid = _udid(driver)
  for _ in range(20):
    try:
      root = ET.fromstring(driver.page_source)
    except (ET.ParseError, WebDriverException):
      time.sleep(0.5)
      continue
    for label in list(remaining):
      val = _parse_value_for(root, label)
      if val is not None:
        values[label] = val
        remaining.discard(label)
    if not remaining:
      break
    subprocess.run(
      ["adb", "-s", udid, "shell", "input", "swipe", "540", "1700", "540", "500", "400"],
      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    time.sleep(1.0)
  return values


def _parse_value_for(root, label):
  """ET ツリーから label 行の表示値を返す (見つからなければ None)。"""
  for el in root.iter():
    if (el.attrib.get("text", "") or "") != label:
      continue
    rid = el.attrib.get("resource-id", "") or ""
    if not (rid.endswith(":id/txt_title") or rid.endswith(":id/txt_header")):
      continue
    bnd = el.attrib.get("bounds", "")
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bnd)
    if not m:
      continue
    ly1 = int(m.group(2))
    ly2 = int(m.group(4))
    val = ""
    best_dy = None
    for vel in root.iter():
      vrid = vel.attrib.get("resource-id", "") or ""
      if not (vrid.endswith(":id/txt_value") or vrid.endswith(":id/txt_comment")):
        continue
      vbnd = vel.attrib.get("bounds", "") or ""
      vm = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", vbnd)
      if not vm:
        continue
      vy1 = int(vm.group(2))
      if abs(vy1 - ly1) < 60:
        val = vel.attrib.get("text", "") or val
        return val
      if vy1 >= ly2 - 5:
        dy = vy1 - ly2
        if dy < 250 and (best_dy is None or dy < best_dy):
          val = vel.attrib.get("text", "") or val
          best_dy = dy
    return val
  return None


def verify_profile(driver, chara_data):
  """MyProfile から全 PROFILE_VERIFY_LABELS の値を読み、chara_data と比較。
  返り値: 不一致の (label, expected, actual) リスト。"""
  observed = _read_all_my_profile_values(driver)
  diffs = []
  for label, key in PROFILE_VERIFY_LABELS:
    expected = chara_data.get(key)
    if not expected:
      continue
    actual = observed.get(label, "")
    if expected in _UNSET_VALUES:
      ok = actual in ("", "タップして設定", "指定しない", "ナイショ")
    else:
      ok = _normalize(actual) == _normalize(expected)
    if not ok:
      diffs.append((label, expected, actual))
  return diffs


def re_registration_partial(chara_data, driver, missing_labels):
  """missing_labels に含まれるラベルだけ再処理する (クラッシュ復旧後の差分実行用)。"""
  name = chara_data.get("name", "")
  print(f"--- [re_registration_partial:{name}] start (targets={sorted(missing_labels)}) ---")
  dismiss_popups(driver)
  if not _open_my_profile(driver):
    return False
  dismiss_popups(driver)
  _scroll_my_profile_top(driver, max_swipes=10)
  time.sleep(1)

  if "居住地" in missing_labels:
    pref = chara_data.get("activity_area")
    if pref:
      _select_prefecture(driver, pref)
      time.sleep(0.8)

  if "詳細エリア" in missing_labels:
    city = chara_data.get("detail_activity_area")
    if city:
      _select_list_field(driver, "詳細エリア", city, expected_header="市区町村選択")
      time.sleep(0.8)

  for label, key in PROFILE_LIST_FIELDS:
    if label not in missing_labels:
      continue
    val = chara_data.get(key)
    if not val:
      continue
    _select_list_field(driver, label, val)
    time.sleep(0.8)

  for open_label, sections in PROFILE_BOTTOMSHEET_GROUPS:
    if not any(s in missing_labels for s, _ in sections):
      continue
    for section_label, key in sections:
      if section_label not in missing_labels:
        continue
      val = chara_data.get(key)
      if not val:
        continue
      _process_bottomsheet_field(driver, section_label, val, skip_check=True)
      time.sleep(0.3)

  _back_one(driver)
  _ensure_main_tab(driver)
  print(f"--- [re_registration_partial:{name}] done ---")
  return True


def re_registration(chara_data, driver):
  """ハッピーメール Android アプリのプロフィールを chara_data で再登録する。

  端末が対象アカウントでログイン済みであることを前提とする。
  対応フィールド:
    - テキスト型: ニックネーム / PRコメント / 自己紹介
    - 単一選択型 (ProfItemSelectActivity): PROFILE_LIST_FIELDS
    - BottomSheet 型: PROFILE_BOTTOMSHEET_GROUPS
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

  # 居住地 (都道府県) — AreaSelectExpandableActivity 経由で確定
  pref = chara_data.get("activity_area")
  if pref:
    _select_prefecture(driver, pref)
    time.sleep(0.8)

  # 詳細エリア (市区町村) — header='市区町村選択' の ProfItemSelect 形式
  city = chara_data.get("detail_activity_area")
  if city:
    _select_list_field(driver, "詳細エリア", city, expected_header="市区町村選択")
    time.sleep(0.8)

  # ProfItemSelectActivity 型フィールド
  for label, key in PROFILE_LIST_FIELDS:
    val = chara_data.get(key)
    if not val:
      continue
    _select_list_field(driver, label, val)
    time.sleep(0.8)

  # BottomSheet グループ
  for open_label, sections in PROFILE_BOTTOMSHEET_GROUPS:
    if not any(chara_data.get(k) for _, k in sections):
      continue
    _process_bottomsheet_group(driver, open_label, sections, chara_data)
    time.sleep(0.8)

  # MyProfile へ戻ってメインタブまで戻す
  _back_one(driver)
  _ensure_main_tab(driver)
  print(f"--- [re_registration:{name}] done ---")
  return True
