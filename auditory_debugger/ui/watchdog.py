import time
import threading
from auditory_debugger import play

_last_tick = time.time()
_last_ui_tick = time.time()

registered_widgets = {}


# =========================
# HEARTBEAT
# =========================
def register_tick():
    global _last_tick
    _last_tick = time.time()


def register_ui_tick():
    global _last_ui_tick
    _last_ui_tick = time.time()


# =========================
# INTERNAL ALERT
# =========================
def _report_lost(reason="WIDGET_LOST", wid=None):

    if wid is not None:
        registered_widgets.pop(wid, None)

    play(reason)
    print(f"❌ WATCHDOG ALERT: {reason}")


# =========================
# WIDGET REGISTRATION + HOOKS
# =========================
def register_widget(widget):

    wid = id(widget)
    registered_widgets[wid] = widget

    # -------- DESTROY HOOK --------
    original_destroy = widget.destroy

    def wrapped_destroy():

        _report_lost("WIDGET_LOST", wid)

        return original_destroy()

    widget.destroy = wrapped_destroy

    # -------- CONFIG HOOK --------
    original_config = getattr(widget, "config", None)

    if original_config:

        def wrapped_config(*args, **kwargs):

            try:
                return original_config(*args, **kwargs)

            except Exception:

                _report_lost("WIDGET_LOST", wid)
                raise

        widget.config = wrapped_config

    # -------- CANVAS itemconfig HOOK --------
    original_itemconfig = getattr(widget, "itemconfig", None)

    if original_itemconfig:

        def wrapped_itemconfig(*args, **kwargs):

            try:
                return original_itemconfig(*args, **kwargs)

            except Exception:

                _report_lost("WIDGET_LOST", wid)
                raise

        widget.itemconfig = wrapped_itemconfig


# =========================
# FALLBACK CHECK
# =========================
def check_widgets():

    lost = []

    for wid, w in list(registered_widgets.items()):

        try:
            if not w.winfo_exists():
                lost.append(wid)

        except Exception:
            lost.append(wid)

    for wid in lost:
        _report_lost("WIDGET_LOST", wid)


# =========================
# WATCHDOG LOOP
# =========================
def start_watchdog():

    def loop():

        global _last_tick, _last_ui_tick

        while True:

            time.sleep(0.5)

            # UI freeze detection
            if time.time() - _last_ui_tick > 2:
                play("UI_FREEZE")
                print("⚠️ UI FREEZE DETECTED")
                _last_ui_tick = time.time()

            # general freeze detection
            if time.time() - _last_tick > 2:
                play("UI_FREEZE")
                print("⚠️ MAIN LOOP FREEZE DETECTED")
                _last_tick = time.time()

            check_widgets()

    threading.Thread(target=loop, daemon=True).start()