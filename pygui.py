import queue
import time
from enum import Enum

import numpy
from dearpygui.core import *
from dearpygui.simple import *

averageArrivalTime = 0
averageServeTime = 0
customerNumber = 0
maxQueueLength = 0
windowNumber = 1
outAverageWaitCustomer = 0
outAverageWaitTime = 0
outServerUsingRate = 0

servedCustomerNumber = 0
totalWaitTime = 0

simulateTime = 0
lastEventTime = 0
waitQueueAverageSum = 0

logOutput = True
stopWhenFull = True
canPlot = False

windowIsEmptyAt = []
windowServeTimeAt = []
windowLastBeginTimeAt = []
plotDataList = []
eventList = queue.PriorityQueue()
waitEventQueue = queue.Queue()

add_additional_font('./static/font/sarasa-fixed-cl-regular.ttf', 22, glyph_ranges='chinese_simplified_common')


class PlotData(object):
    def __init__(self, time, averageWaitCustomer, averageWaitTime, serverUsingRate, currentWait):
        self.time = time
        self.averageWaitCustomer = averageWaitCustomer
        self.averageWaitTime = averageWaitTime
        self.serverUsingRate = serverUsingRate
        self.currentWait = currentWait


class EventType(Enum):
    ADD = 1
    SER = 2
    END = 3


class Event:
    def __init__(self, proCustomer, proWindow, proType, proBegin, proEnd):
        self.itemId = proCustomer
        self.window = proWindow
        self.type = proType
        self.beginTime = proBegin
        self.endTime = proEnd

    # PriorityQueue的对比
    def __lt__(self, other):
        if self.beginTime == other.beginTime:
            return self.itemId < other.itemId
        else:
            return self.endTime < other.endTime

    def to_log_info(self):
        if logOutput:
            if self.type == EventType.ADD:
                log_info("顾客" + str(self.itemId) + "在第" + str(round(self.beginTime, 2)) + "分钟到达")
            if self.type == EventType.SER:
                log_info(
                    "顾客" + str(self.itemId) + "在第" + str(round(self.endTime, 2)) + "分钟接受窗口" + str(
                        self.window + 1) + "的服务")
            if self.type == EventType.END:
                log_info("顾客" + str(self.itemId) + "在第" + str(round(self.endTime, 2)) + "分钟离开")


def clear_global_var():
    global averageArrivalTime, averageServeTime, customerNumber, maxQueueLength, windowNumber, servedCustomerNumber, \
        totalWaitTime, simulateTime, lastEventTime, waitQueueAverageSum, logOutput, windowIsEmptyAt, \
        windowServeTimeAt, windowLastBeginTimeAt, eventList, waitEventQueue, outAverageWaitTime, outServerUsingRate, \
        outAverageWaitCustomer, canPlot, plotDataList
    canPlot = False
    outAverageWaitCustomer = 0
    outAverageWaitTime = 0
    outServerUsingRate = 0
    servedCustomerNumber = 0
    totalWaitTime = 0
    simulateTime = 0
    lastEventTime = 0
    waitQueueAverageSum = 0
    windowIsEmptyAt = []
    windowServeTimeAt = []
    windowLastBeginTimeAt = []
    plotDataList = []
    eventList = queue.PriorityQueue()
    waitEventQueue = queue.Queue()


def initial():
    # 清空上次仿真结果
    clear_global_var()
    # 初始化窗口列表
    for i in range(windowNumber):
        windowIsEmptyAt.append(True)
        windowServeTimeAt.append(0)
        windowLastBeginTimeAt.append(0)
    rand_time = 0
    rand_id = 1
    # 根据平均到达时间生成随机的用户到达间隔时间
    for i in range(customerNumber):
        inter_arrival_time = numpy.random.exponential(averageArrivalTime)
        rand_time += inter_arrival_time
        # 将这些未来事件放入事件序列
        eventList.put(Event(rand_id, -1, EventType.ADD, rand_time, rand_time))
        rand_id += 1


def get_empty_window():
    for i in range(windowNumber):
        if windowIsEmptyAt[i]:
            return i
    return -1


def update_result():
    global outAverageWaitTime, outServerUsingRate, outAverageWaitCustomer
    outAverageWaitCustomer = waitQueueAverageSum / simulateTime
    if servedCustomerNumber != 0:
        outAverageWaitTime = totalWaitTime / servedCustomerNumber
    if windowNumber != 0:
        using_rate_at = []
        tmp_rate = 0
        for i in range(windowNumber):
            using_rate_at.append(windowServeTimeAt[i] / simulateTime)
            tmp_rate += using_rate_at[i]
        outServerUsingRate = tmp_rate / windowNumber
    plotDataList.append(PlotData(simulateTime, outAverageWaitCustomer, outAverageWaitTime, outServerUsingRate,
                                 waitEventQueue.qsize()))


def simulate():
    global simulateTime, lastEventTime, waitQueueAverageSum, totalWaitTime, servedCustomerNumber, canPlot
    canPlot = False
    add_data("frame_count", 0)
    add_data("plot_data", [])
    clear_plot("当前排队人数")
    while not eventList.empty():
        current_event = eventList.get()
        lastEventTime = simulateTime
        simulateTime = current_event.endTime
        waitQueueAverageSum += waitEventQueue.qsize() * (simulateTime - lastEventTime)
        tmp_customer_id = current_event.itemId
        tmp_customer_begin_time = current_event.beginTime
        current_event.to_log_info()
        if current_event.type == EventType.ADD:
            tmp_window = get_empty_window()
            if tmp_window != -1:
                eventList.put(Event(tmp_customer_id, tmp_window, EventType.SER, tmp_customer_begin_time, simulateTime))
            else:
                if waitEventQueue.qsize() == maxQueueLength:
                    if stopWhenFull:
                        log_warning("达到排队最大人数！仿真中断")
                        return
                    else:
                        log_warning("顾客" + str(tmp_customer_id) + "放弃排队")
                else:
                    waitEventQueue.put(current_event)
        elif current_event.type == EventType.SER:
            tmp_window = current_event.window
            windowIsEmptyAt[tmp_window] = False
            windowLastBeginTimeAt[tmp_window] = simulateTime
            tmp_serve_time = numpy.random.exponential(averageServeTime)
            eventList.put(Event(tmp_customer_id, tmp_window, EventType.END, tmp_customer_begin_time,
                                simulateTime + tmp_serve_time))
        else:
            tmp_window = current_event.window
            totalWaitTime += (simulateTime - tmp_customer_begin_time)
            servedCustomerNumber += 1
            windowServeTimeAt[tmp_window] += (simulateTime - windowLastBeginTimeAt[tmp_window])
            if waitEventQueue.empty():
                windowIsEmptyAt[tmp_window] = True
            else:
                tmp_event = waitEventQueue.get()
                eventList.put(
                    Event(tmp_event.itemId, tmp_window, EventType.SER, tmp_event.beginTime, simulateTime))
        update_result()
    log_warning("仿真成功")
    if logOutput:
        log_info(">>>> 总仿真时间：" + str(round(simulateTime, 2)) + "分钟")
        log_info(">>>> 平均等待客户：" + str(round(outAverageWaitCustomer)))
        log_info(">>>> 平均等待时间：" + str(round(outAverageWaitTime, 2)))
        log_info(">>>> 服务器利用率：" + str(round(outServerUsingRate * 100, 2)) + " %")
        if windowNumber > 1:
            for i in range(windowNumber):
                log_info(
                    "窗口" + str(i + 1) + "的利用率为" + str(round((windowServeTimeAt[i] / simulateTime) * 100, 2)) + " %")
    canPlot = True


def save_callback(sender, data):
    global averageArrivalTime, averageServeTime, customerNumber, maxQueueLength, windowNumber
    averageArrivalTime = get_value("平均到达时间##1")
    averageServeTime = get_value("平均服务时间##2")
    customerNumber = get_value("顾客来访数目##3")
    maxQueueLength = get_value("队列最大长度##4")
    windowNumber = get_value("运行窗口数目##5")
    if customerNumber < 0 or maxQueueLength < 0:
        log_error("顾客数目或队列最大长度应该大于0！")
        set_value("顾客来访数目##3", 0)
        set_value("队列最大长度##4", 0)
    else:
        if logOutput:
            log_info(">>>> 平均到达时间: " + str(round(averageArrivalTime, 2)))
            log_info(">>>> 平均服务时间: " + str(round(averageServeTime, 2)))
            log_info(">>>> 顾客来访数目: " + str(customerNumber))
            log_info(">>>> 队列最大长度: " + str(maxQueueLength))
            log_info(">>>> 运行窗口数目: " + str(windowNumber))
        initial()
        simulate()


def output_choice(sender, data):
    global logOutput
    logOutput = get_value("输出运行日志")
    # print(logOutput)


def stop_choice(sender, data):
    global stopWhenFull
    stopWhenFull = get_value("达到最大排队人数时结束仿真")


def plot_callback(sender, data):
    plot_data = get_data("plot_data")
    frame_count = get_data("frame_count")
    if canPlot and len(plot_data) <= simulateTime:
        frame_count += 1
        add_data("frame_count", frame_count)
        y_content = 0
        for i in range(len(plotDataList)):
            if frame_count > plotDataList[i].time:
                y_content = plotDataList[i].currentWait
                set_value("当前仿真时间", str(frame_count) + " 分钟")
                set_value("平均等待客户", str(round(plotDataList[i].averageWaitCustomer)) + " 人")
                set_value("平均等待时间", str(round(plotDataList[i].averageWaitTime, 2)) + " 分钟")
                set_value("服务器利用率", str(round(plotDataList[i].serverUsingRate * 100, 2)) + " %")
        # print(y_content)
        plot_data.append([frame_count, y_content])
        add_data("plot_data", plot_data)
        clear_plot("当前排队人数")
        add_line_series("当前排队人数", "排队人数", plot_data, weight=2)
    time.sleep(0.02)


# show_documentation()
# show_debug()
# show_about()
# show_metrics()
show_logger()
set_log_level(0)

# 编程实现队列模型（M/M/1)的仿真程序
# 输入参数：平均到达时间，平均服务时间，顾客来访数目，队列最大长度
# 输出参数：队列中平均等待客户数；平均等待时间；服务器利用率


with window("BUAA 18373580 队列模型仿真程序", width=400, height=780, x_pos=800, y_pos=50):
    add_tab_bar("Simulation")
    add_tab("M/M/N队列模型")
    add_spacing(count=1)
    add_slider_float("平均到达时间##1", default_value=0.1, min_value=0.0,
                     max_value=60, format='%.2f 分钟')  # Average Arrival Time
    add_slider_float("平均服务时间##2", default_value=1, min_value=0.0,
                     max_value=60, format='%.2f 分钟')  # Average Serve Time
    add_input_int("顾客来访数目##3", default_value=400)  # Customer Number
    add_input_int("队列最大长度##4", default_value=50)  # Max Queue Length
    add_input_int("运行窗口数目##5", default_value=7)  # Max Queue Length
    add_checkbox("输出运行详情", callback=output_choice, default_value=True)
    add_checkbox("达到最大排队人数时结束仿真", callback=stop_choice, default_value=True)
    add_spacing(count=1)
    add_button("Simulate 仿真##5", callback=save_callback, width=386)
    add_spacing(count=1)
    add_plot("当前排队人数", width=380, height=300)
    add_data("plot_data", [])
    add_data("frame_count", 0)
    set_render_callback(plot_callback)
    # 输出参数：队列中平均等待客户数；平均等待时间；服务器利用率
    add_input_text("当前仿真时间")
    add_input_text("平均等待客户")
    add_input_text("平均等待时间")
    add_input_text("服务器利用率")
    set_value("当前仿真时间", "00.00 分钟")
    set_value("平均等待客户", "0 人")
    set_value("平均等待时间", "00.00 分钟")
    set_value("服务器利用率", "00.00 %")
    end()
    add_tab("About")
    end()

# draw_line("Drawing_1", [10, 10], [100, 100], [255, 0, 0, 255], 1)
# draw_text("Drawing_1", [16, 16], "Origin", color=[250, 250, 250, 255], size=15)
# draw_arrow("Drawing_1", [50, 70], [100, 65], [0, 200, 255], 1, 10)
#
# set_drawing_origin("Drawing_1", 150, 150)  # simple
# set_drawing_scale("Drawing_1", 2, 2)  # simple
# set_drawing_size("Drawing_1", 400, 500)  # simple

if __name__ == '__main__':
    start_dearpygui()
