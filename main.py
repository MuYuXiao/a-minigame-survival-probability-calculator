#**coding:utf-8**
import random
import sys
from tqdm import tqdm
import concurrent.futures   
import time
from prettytable import PrettyTable
from pyecharts.charts import Line
from pyecharts import options as opts

def simluation(m,n,times):
    count = 0
    for i in tqdm(range(times),desc=f'Thread {m}',position=m):
        dead = False
        for j in range(n-m):
            if random.random() <= m/n:
                dead = True
                break
        if dead:
            count+=1
    return (m,1-count/times)

def cal(n,real_results):
    for i in range(1,n):
        j = n-i
        real_results[i]=(j/n)**j

def plot_result(results,real_results):
    kys = sorted(list(results.keys()))
    y1 = [results[i]*100 for i in kys]
    y2 = [real_results[i]*100 for i in kys]
    x = [str(i) for i in kys]
    line_chart = (
        Line()
        .add_xaxis(x)
        .add_yaxis("result",y1,is_smooth=True)
        .add_yaxis("real_result",y2,is_smooth=True)
        .set_global_opts(
        title_opts=opts.TitleOpts(title="结果")
        )
    )
    line_chart.render("result.html")

def plot_error(results,real_results):
    kys = sorted(list(results.keys()))
    y1 = [results[i] for i in kys]
    y2 = [real_results[i] for i in kys]
    x = [str(i) for i in kys]
    line_chart = (
        Line()
        .add_xaxis(x)
        .add_yaxis("result",[abs(y1[x]-y2[x]) for x in range(len(x))],is_smooth=True)
        .set_global_opts(
        title_opts=opts.TitleOpts(title="误差")
        )
    )
    line_chart.render("error.html")

def main():
    n = 10 #轮盘赌手枪的可容纳子弹数
    times = 1000000 #模拟次数
    results = {} #模拟的概率结果
    real_results = {} #计算概率结果
    cal(n,real_results) # 计算真实概率
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
        threads = []
        for i in range(n-1):
            threads.append(executor.submit(simluation,i+1,n,times,))
        for future in concurrent.futures.as_completed(threads):  # 并发执行
            results[future.result()[0]] = future.result()[1]
        executor.shutdown()
    print('-----------------------------------------------------------------------------')
    table = PrettyTable(['Bullets','simulation','cal','error']) #建立结果表
    round_num = 5
    for i in range(1,n):
        table.add_row([i,round(results[i],round_num),round(real_results[i],round_num),f'{abs(results[i]-real_results[i]):.2e}'])
    print(table)
    plot_result(results,real_results) #画结果图
    plot_error(results,real_results)    #画误差图

if __name__ == '__main__':
    main()
