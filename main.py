from auditory_debugger import auto_start, safe
import time
auto_start(mode="CONTINUOUS_MODE")

print("START")

# =========================
# TEST 1
# =========================
@safe
def test1():
    return 3 / 0

print("TEST 1")
test1()

# =========================
# TEST 2
# =========================
@safe
def test2():
    return int("ciao")

print("TEST 2")
test2()

# =========================
# TEST 3
# =========================
@safe
def test3():
    return [1, 2][5]

print("TEST 3")
test3()

# =========================
# TEST 4
# =========================
@safe
def test4():
    return {"a": 1}["b"]

print("TEST 4")
test4()

# =========================
# TEST 5
# =========================
@safe
def test5():
    return "a" + 1

print("TEST 5")
test5()

# =========================
# TEST 6
# =========================
@safe
def test6():
    return (123).append(1)

print("TEST 6")
test6()

# =========================
# TEST 7
# =========================
@safe
def test7():
    return undefined_variable

print("TEST 7")
test7()

# =========================
# TEST 8
# =========================
@safe
def test8_compute():
    total = 0

    for i in range(5):
        total += i

    return total

print("TEST 8")
test8_compute()

# =========================
# TEST 9
# =========================
@safe
def test9_slow():
    time.sleep(1.2)

print("TEST 9")
test9_slow()

# =========================
# TEST 10
# =========================
@safe
def test10():
    return int("331")

print("TEST 10")
test10()

print("END")