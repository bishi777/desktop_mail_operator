"""
6時間進捗報告を、ポート（= debug_drivers プロセス）をまたいで1通にまとめる。

debug_drivers_ph_ch_fm.py はポートごとに別プロセスで動くため、各プロセスが
自分の分だけを送るとポートの数だけメールが届く。そこで各プロセスは締めの時刻に
自分の集計を共有フォルダへ書き出すだけにし、稼働中の全ポートの報告が揃った時点
（または締め切りを過ぎた時点）で、1プロセスだけが全ポート分をまとめて送る。

共有フォルダ（logs/progress_report/<kind>/）:
  heartbeats/<port>.json            稼働中の印。キャラ処理のたびに更新する
  slots/<YYYYmmdd_HH>/port_<port>.json  そのポートの締め報告
  slots/<YYYYmmdd_HH>/claim         送信権。O_EXCL で作れた1プロセスだけが送る
  slots/<YYYYmmdd_HH>/failed_<n>    送信失敗の記録（再送の間隔と回数の判定に使う）
  slots/<YYYYmmdd_HH>/done.json     送信済みの印と、本文に含めたポートの一覧
  slots/<YYYYmmdd_HH>/late_sent_<port>  締め後に届いた報告を個別に送った印

ファイルで共有するので、まとまるのは同じPCで動くポート同士だけ。
"""
import json
import os
import shutil
import time
from datetime import datetime, date, timedelta
from pathlib import Path

from widget import func

# 最後のキャラ処理からこの時間を過ぎたポートは「停止中」とみなし、報告を待たない
HEARTBEAT_TTL = timedelta(minutes=60)
# 締め時刻からこの時間を過ぎたら、揃っていなくても届いた分だけで送る
SLOT_DEADLINE = timedelta(minutes=50)
# 送信に失敗したとき、次に再送するまでの間隔と最大試行回数
RETRY_INTERVAL = timedelta(minutes=5)
MAX_SEND_ATTEMPTS = 3
# 送信権を持ったまま止まった（ウィンドウを閉じた等）とみなすまでの時間
STALE_CLAIM = timedelta(minutes=15)
# これより古い締めフォルダは削除する
KEEP_SLOTS = timedelta(days=3)

METRIC_KEYS = ["fst", "rf", "check_first", "check_second", "gmail_condition", "check_more"]
_TS_FMT = "%Y-%m-%d %H:%M:%S"
_SLOT_FMT = "%Y%m%d_%H"
_LOG = "[進捗報告]"


def _ts(dt):
  return dt.strftime(_TS_FMT) if dt else None


def _parse_ts(s):
  if not s:
    return None
  try:
    return datetime.strptime(s, _TS_FMT)
  except (TypeError, ValueError):
    return None


def _to_jsonable(v):
  if isinstance(v, datetime):
    return v.strftime(_TS_FMT)
  if isinstance(v, date):
    return v.strftime("%Y-%m-%d")
  return v


def _to_int(v):
  try:
    return int(v)
  except (TypeError, ValueError):
    return 0


def _port_sort_key(p):
  return (0, int(p), p) if p.isdigit() else (1, 0, p)


def _write_json_atomic(path, data):
  """一時ファイルに書いてから置き換える（読み手に書きかけを見せない）。"""
  tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
  with open(tmp, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)
  for attempt in range(5):
    try:
      os.replace(tmp, path)
      return
    except PermissionError:
      # Windows は他プロセスが開いている最中のファイルを置き換えられないので少し待つ
      if attempt == 4:
        try:
          os.remove(tmp)
        except OSError:
          pass
        raise
      time.sleep(0.2)


def _read_json(path):
  try:
    with open(path, encoding="utf-8") as f:
      return json.load(f)
  except (OSError, ValueError):
    return None


class ProgressAggregator:
  def __init__(self, kind, port, title, base_dir=None):
    """
    kind : 共有フォルダの区分（例: "pcmax"）。同じ kind のプロセス同士でまとめる
    port : このプロセスのデバッグポート（None なら "noport"）
    title: メール件名の先頭（例: "PCMAX 6時間の進捗報告"）
    """
    self.port = str(port) if port is not None else "noport"
    self.title = title
    root = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent / "logs" / "progress_report"
    self.base = root / kind
    self.hb_dir = self.base / "heartbeats"
    self.slots_dir = self.base / "slots"
    # 締めの準備ができた（send_flug が True になった）時刻。締めたら None に戻る。
    # この時刻より後の締めにだけ、このポートの報告を待つ。
    self.armed_at = None
    self._last_cleanup = None

  # ------------------------------------------------------------------
  # プロセス側から呼ぶもの
  # ------------------------------------------------------------------
  def heartbeat(self, now, armed):
    """キャラ処理のたびに呼ぶ。armed には呼び出し時点の send_flug を渡す。"""
    if not armed:
      self.armed_at = None
    elif self.armed_at is None:
      self.armed_at = now
    try:
      self.hb_dir.mkdir(parents=True, exist_ok=True)
      _write_json_atomic(self.hb_dir / f"{self.port}.json", {
        "port": self.port,
        "pid": os.getpid(),
        "updated_at": _ts(now),
        "armed_at": _ts(self.armed_at),
      })
    except Exception as e:
      print(f"{_LOG} heartbeat の書き込みに失敗: {type(e).__name__}: {e}")

  def close_period(self, report_dict, start_time, now, mail_info):
    """
    締めの時刻に呼ぶ。自分の集計を共有フォルダへ書き出し、全ポート分が揃っていれば
    まとめて送る。書き出せなかったときは従来どおり自分の分だけを送る。
    同じ締めの中で何度呼んでも、報告ファイルが上書きされるだけで重複しない。
    """
    slot_start = now.replace(minute=0, second=0, microsecond=0)
    slot_dir = self.slots_dir / slot_start.strftime(_SLOT_FMT)
    payload = {
      "port": self.port,
      "start_time": _ts(start_time),
      "closed_at": _ts(now),
      "report": {
        name: {k: _to_jsonable(v) for k, v in (vals.items() if isinstance(vals, dict) else [("fst", vals)])}
        for name, vals in (report_dict or {}).items()
      },
    }
    try:
      slot_dir.mkdir(parents=True, exist_ok=True)
      _write_json_atomic(slot_dir / f"port_{self.port}.json", payload)
      print(f"{_LOG} port {self.port} の締め報告を書き出しました（{slot_dir.name}）")
    except Exception as e:
      print(f"{_LOG} 共有フォルダに書き出せないため、このポート分だけ送ります: {type(e).__name__}: {e}")
      self._send_single(payload, now, mail_info, label="")
      return
    self.heartbeat(now, armed=False)
    self.flush(mail_info, now)

  def flush(self, mail_info, now=None):
    """揃った（または締め切りを過ぎた）締めがあれば送る。何度呼んでもよい。"""
    now = now or datetime.now()
    if not self.slots_dir.is_dir():
      return
    self._cleanup(now)
    try:
      slot_dirs = sorted(p for p in self.slots_dir.iterdir() if p.is_dir())
    except OSError as e:
      print(f"{_LOG} 締めフォルダを読めません: {e}")
      return
    for slot_dir in slot_dirs:
      try:
        slot_start = datetime.strptime(slot_dir.name, _SLOT_FMT)
      except ValueError:
        continue
      try:
        if (slot_dir / "done.json").exists():
          self._send_late_if_needed(slot_dir, now, mail_info)
        else:
          self._try_send_slot(slot_dir, slot_start, now, mail_info)
      except Exception as e:
        print(f"{_LOG} {slot_dir.name} の処理でエラー: {type(e).__name__}: {e}")

  # ------------------------------------------------------------------
  # 内部処理
  # ------------------------------------------------------------------
  def _load_submissions(self, slot_dir):
    subs = {}
    for p in slot_dir.glob("port_*.json"):
      d = _read_json(p)
      if d is not None:
        subs[str(d.get("port") or p.stem[len("port_"):])] = d
    return subs

  def _expected_ports(self, slot_start, now):
    """この締めで報告を待つべきポート（稼働中で、締め時刻より前に準備ができていたもの）。"""
    ports = set()
    if not self.hb_dir.is_dir():
      return ports
    for hb in self.hb_dir.glob("*.json"):
      d = _read_json(hb)
      if not d:
        continue
      updated = _parse_ts(d.get("updated_at"))
      armed = _parse_ts(d.get("armed_at"))
      if updated is None or now - updated > HEARTBEAT_TTL:
        continue  # 停止中
      if armed is None or armed >= slot_start:
        continue  # 締め時刻の後に起動・締め済みなど、この回の報告は出さない
      ports.add(str(d.get("port") or hb.stem))
    return ports

  def _try_send_slot(self, slot_dir, slot_start, now, mail_info):
    subs = self._load_submissions(slot_dir)
    if not subs:
      return
    expected = self._expected_ports(slot_start, now)
    missing = expected - set(subs)
    if missing and now < slot_start + SLOT_DEADLINE:
      return  # まだ揃っていない

    claim = slot_dir / "claim"
    if claim.exists():
      # 送信中。ただし長く残っていれば、送信中に止まったとみなして失敗扱いにする
      try:
        age = now - datetime.fromtimestamp(claim.stat().st_mtime)
      except OSError:
        return
      if age < STALE_CLAIM:
        return
      self._mark_failed(slot_dir)

    failed = list(slot_dir.glob("failed_*"))
    if len(failed) >= MAX_SEND_ATTEMPTS:
      print(f"{_LOG} {slot_dir.name} は {len(failed)} 回送信に失敗したため諦めます")
      _write_json_atomic(slot_dir / "done.json", {
        "sent_by": None, "sent_at": None, "gave_up": True,
        "included": sorted(subs, key=_port_sort_key),
      })
      return
    if failed:
      last_fail = max(datetime.fromtimestamp(p.stat().st_mtime) for p in failed)
      if now - last_fail < RETRY_INTERVAL:
        return

    try:
      fd = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
      return  # 他のポートが先に送信権を取った
    os.write(fd, f"port={self.port} pid={os.getpid()} at={_ts(now)}".encode("utf-8"))
    os.close(fd)

    sent = False
    try:
      # 送信権を取るまでの間に届いた報告も含めるため読み直す
      subs = self._load_submissions(slot_dir)
      missing = expected - set(subs)
      subject, body = self._build_mail(subs, missing, now)
      print(f"{_LOG} {slot_dir.name} を送信します（ポート: {', '.join(sorted(subs, key=_port_sort_key))}）")
      sent = func.send_mail(body, mail_info, subject)
      if sent:
        # claim は消さずに残す（消すと他のプロセスが同じ締めを再送できてしまう）
        _write_json_atomic(slot_dir / "done.json", {
          "sent_by": self.port,
          "sent_at": _ts(datetime.now()),
          "included": sorted(subs, key=_port_sort_key),
          "missing": sorted(missing, key=_port_sort_key),
        })
    finally:
      if not sent:
        # 送信失敗・Ctrl+C など。送信権を手放して、後で誰かが再送できるようにする
        self._mark_failed(slot_dir)

  def _mark_failed(self, slot_dir):
    n = len(list(slot_dir.glob("failed_*"))) + 1
    try:
      os.replace(slot_dir / "claim", slot_dir / f"failed_{n}")
    except OSError:
      pass

  def _send_late_if_needed(self, slot_dir, now, mail_info):
    """送信済みの締めに、自分の報告が含まれていなければ個別に送る（自分の分だけ扱う）。"""
    own = slot_dir / f"port_{self.port}.json"
    marker = slot_dir / f"late_sent_{self.port}"
    if not own.exists() or marker.exists():
      return
    done = _read_json(slot_dir / "done.json")
    if done is None:
      return  # 読めないときは次回に回す（誤って追加分を送らないように）
    if self.port in done.get("included", []):
      return
    sub = _read_json(own)
    if not sub:
      return
    print(f"{_LOG} {slot_dir.name} の送信後に届いた port {self.port} の報告を個別に送ります")
    # 送れなくても印を付ける（1分おきに再送を繰り返さないため）
    marker.touch()
    self._send_single(sub, now, mail_info, label=f"（追加分 port{self.port}）")

  def _build_mail(self, subs, missing, now):
    merged = {}
    starts = []
    for sub in subs.values():
      st = _parse_ts(sub.get("start_time"))
      if st:
        starts.append(st)
      for name, v in (sub.get("report") or {}).items():
        m = merged.setdefault(name, dict({k: 0 for k in METRIC_KEYS}, check_date=None))
        for k in METRIC_KEYS:
          m[k] += _to_int(v.get(k))
        cd = v.get("check_date")
        if cd and (m["check_date"] is None or str(cd) > str(m["check_date"])):
          m["check_date"] = cd
    lines = [
      func.format_progress_mail(merged, now),
      f"📡 集計ポート: {', '.join(sorted(subs, key=_port_sort_key))}",
    ]
    if missing:
      lines.append(f"⚠️ 未報告ポート: {', '.join(sorted(missing, key=_port_sort_key))}（締め切りまでに報告なし）")
    start = min(starts) if starts else now
    subject = f"{self.title}  開始時間：{_ts(start)}"
    return subject, "\n".join(lines)

  def _send_single(self, sub, now, mail_info, label):
    start = _parse_ts(sub.get("start_time")) or now
    body = func.format_progress_mail(sub.get("report") or {}, now)
    body += f"\n📡 集計ポート: {self.port}"
    return func.send_mail(body, mail_info, f"{self.title}{label}  開始時間：{_ts(start)}")

  def _cleanup(self, now):
    if self._last_cleanup and now - self._last_cleanup < timedelta(hours=1):
      return
    self._last_cleanup = now
    try:
      for d in self.slots_dir.iterdir():
        try:
          slot_start = datetime.strptime(d.name, _SLOT_FMT)
        except ValueError:
          continue
        if now - slot_start > KEEP_SLOTS:
          shutil.rmtree(d, ignore_errors=True)
    except OSError:
      pass
