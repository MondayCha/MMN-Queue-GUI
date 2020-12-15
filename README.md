Python + DearPyGui 实现的M-M-N队列模型仿真，初始化时建立事件对象类Event，存储事件序号、对应窗口、事件类型、事件开始时间、事件结束时间，并为事件配置比较和输出方法。

当从GUI的仿真按钮确认开始仿真后，按照事件处理流程，所用到的主要函数如下：

a)   初始化，根据平均到达时间生成随机的用户到达间隔时间，将这些未来事件放入事件序列。

b)   对运行过程进行仿真，这里直接模拟了M/M/n模型，具体实现如下：

c)   仿真结束后将结果输出到日志和GUI上。图像绘制按照固定时间步长推进方法，以每分钟为间隔刷新图像。绘制了当前排队人数的折线图，同时刷新当前时间、平均等待时间、平均等待客户数、平均服务器利用率等值。

对应GUI效果图：
![image](https://github.com/MondayCha/MMN-Queue-GUI/blob/master/README.assets/Snipaste_2020-11-04_15-37-38.png)

视频演示地址：

- 知乎：https://www.zhihu.com/zvideo/1307375212308856832

- 哔哩哔哩：https://www.bilibili.com/video/BV1cz4y1y7nW
