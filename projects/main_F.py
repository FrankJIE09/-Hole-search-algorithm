
import time
from projects.Control import URControl as UR
import threading
from projects.calibration import calibration


def test():
    FT_test = UR()
    chart_thread = threading.Thread(target=FT_test.get_ft_chart, daemon=False)
    # UR().get_ft_chart()
    try:
        chart_thread.start()
        time.sleep(5)
        move_test_thread = threading.Thread(target=FT_test.move_test())
        move_test_thread.start()
    except Exception:
        print("Error: 无法启动线程")
    while move_test_thread.isAlive() == 1:
        time.sleep(1)
        continue
    print("over")


if __name__ == '__main__':
    FT_ = UR()
    chart_thread = threading.Thread(target=FT_.get_ft_chart, daemon=True)
    logic_thread = threading.Thread(target=FT_.logic)

    # UR().get_ft_chart()
    try:
        chart_thread.start()
        time.sleep(1)
        logic_thread.start()
    except Exception:
        print("Error: 无法启动线程")
    while logic_thread.isAlive() == 1:
        time.sleep(1)
        continue
    print("over")
    # test()
    # cali = calibration()
    # cali.cali1(UR)
