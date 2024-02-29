# 数据标注平台

优化LLM的可视化数据标注平台，标注员可自主上传源数据文件并下载标注后的文件

共包含[`single`](screenshot/single.pdf)，[`triple`](screenshot/triple.pdf)两种界面

`single`：根据设定筛选符合条件的session，对单个session进行修改、评论、分档

`triple`：同时展示相同query下的三组不同的模型输出，可以对各项进行修改，对整体评论、分档

### 各文件夹用途

`rawdata`：存放标注员上传的原始表格

`excels`：程序运行期使用的表格

`download`：生成的标注后返回给标注员的表格

### 启动方式

进入`./single`或`./triple`文件夹下，使用如下命令启动：

```bash
nohup python app.py > nohup.log 2>&1 &
```

然后通过主机IP和对应端口即可访问，默认端口：single(8788)，triple(8789)
