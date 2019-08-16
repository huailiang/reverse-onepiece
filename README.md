对端游《航海王-燃烧之血》的破解：

主要是端游的端游资源的提取， 分别为网格mesh和纹理texture的获取.

环境：

```
python27
pillow (PIL)
```

command PIL with pip:
```
pip install pillow
```


steps:

step1.  解压.cpk 

使用CPK File Builder对cpk解压， 你将得到三种文件 .npk .npki .npkv

.npk  是各种资源的索引
.npki 是mesh的buffer
.npkv 是raw texture buffer

<br><img src='img/CPK.png'><br>


step2.  使用hex分析二进制文件 确认mesh中的vertiex&face的地址和数量

<br><img src='img/hex.jpg'><br>


step3. 使用step2的参数输入到hex2obj中， 提取mesh

<br><img src='img/h2o.png'><br>


上面所用到的工具都可以在工程中的tool.zip中得到。