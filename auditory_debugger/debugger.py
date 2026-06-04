import sys
import time
import os
import linecache
import weakref

try:
    import pretty_errors
except ImportError:
    pretty_errors = None

from sound_bank import (
    ERROR_SOUNDS,
    EVENT_SOUNDS,
    DYNAMIC_SOUNDS
)

# =========================
# 🔊 SOUND ENGINE
# =========================
try:
    import winsound

    def tone(freq, duration):
        winsound.Beep(freq, duration)

    def play(event, value=0):

        if isinstance(event, type) and issubclass(event, Exception):

            sequence = ERROR_SOUNDS.get(
                event,
                [(500,400),(300,400)]
            )

        else:

            if event in DYNAMIC_SOUNDS:
                sequence = DYNAMIC_SOUNDS[event](value)

            else:
                sequence = EVENT_SOUNDS.get(event)

        if not sequence:
            return

        for freq, duration in sequence:
            tone(freq, duration)

except ImportError:

    def play(event, value=0):
        sys.stdout.write("\a")
        sys.stdout.flush()


# =========================
# 🌐 GLOBAL ERROR MODE
# =========================

FORCE_AUDIO_ERRORS = True

# =========================
# EXCEPTION DEDUPLICATION
# =========================

_PLAYED_EXCEPTIONS = weakref.WeakKeyDictionary()


def _mark_exception_seen(exc_value):

    try:

        if exc_value in _PLAYED_EXCEPTIONS:
            return False

        _PLAYED_EXCEPTIONS[exc_value] = True
        return True

    except TypeError:

        # fallback: some exceptions may not support weak refs
        try:
            if getattr(exc_value, "_auditory_seen", False):
                return False

            exc_value._auditory_seen = True
            return True

        except Exception:
            return True


def enable_global_audio_errors(mode="STOP_ON_ERROR"):

    def handler(exc_type, exc_value, tb):
        if not _mark_exception_seen(exc_value):
            return

        play(exc_type)

        time.sleep(0.4)

        if mode == "STOP_ON_ERROR":
            sys.__excepthook__(exc_type, exc_value, tb)
            print("\n🛑 AUDITORY DEBUG SESSION STOPPED\n")
            os._exit(1)

        elif mode == "CONTINUOUS_MODE":
            print("\n⚠️ ERROR DETECTED (CONTINUING)\n")
            sys.__excepthook__(exc_type, exc_value, tb)

    sys.excepthook = handler


# =========================
# 🧠 SAFE WRAPPER
# =========================

def safe(func=None, *, raise_error=False):
    if func is None:
        return lambda f: safe(f, raise_error=raise_error)

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except Exception as e:
            sys.excepthook(type(e), e, e.__traceback__)
            time.sleep(0.2)

            if raise_error:
                raise

            return None

    return wrapper


# =========================
# 🧠 FUNCTION DECORATOR
# =========================

class AuditoryDebugger:
    def __init__(self, slow_threshold=0.5):
        self.depth = 0
        self.slow_threshold = slow_threshold

    def watch(self):
        def decorator(func):
            def wrapper(*args, **kwargs):

                self.depth += 1
                play("enter", self.depth)

                start = time.perf_counter()

                try:
                    result = func(*args, **kwargs)

                except Exception as e:
                    # use the same deduplicated excepthook
                    sys.excepthook(type(e), e, e.__traceback__)
                    time.sleep(0.2)
                    self.depth -= 1
                    raise

                duration = time.perf_counter() - start

                if duration > self.slow_threshold:
                    play("slow")

                play("exit")
                self.depth -= 1

                return result

            return wrapper
        return decorator


_debugger = AuditoryDebugger()

def watch(func):
    return _debugger.watch()(func)


# =========================
# 🎬 AUTO TRACE
# =========================

def auto_start(delay=0.1, slow_threshold=0.8, mode="STOP_ON_ERROR"):

    enable_global_audio_errors(mode=mode)

    caller_frame = sys._getframe(1)
    main_file = os.path.abspath(caller_frame.f_globals.get("__file__", ""))

    printed_lines = set()
    call_stack = []

    def slow_print(text):
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write("\n")
        sys.stdout.flush()

    def tracer(frame, event, arg):
        if frame.f_code.co_name == "watchdog":
            return tracer

        filename = os.path.abspath(frame.f_code.co_filename)

        if filename != main_file:
            return tracer

        lineno = frame.f_lineno
        line = linecache.getline(main_file, lineno)

        if not line:
            return tracer

        line = line.rstrip("\n")
        stripped = line.strip()

        if event == "call":
            call_stack.append(frame.f_code.co_name)
            play("enter", len(call_stack))

        elif event == "return":
            if call_stack:
                call_stack.pop()
            play("exit")

        elif event == "exception":
            pass

        elif event == "line":

            if lineno not in printed_lines and stripped:
                printed_lines.add(lineno)
                
                if not stripped.startswith("print("):
                    slow_print(f"{lineno:>4}: {line}")

            if stripped.startswith("for ") or stripped.startswith("while "):
                play("burst")

            if "sleep(" in stripped:
                play("slow")

        return tracer

    sys.settrace(tracer)
    return tracer