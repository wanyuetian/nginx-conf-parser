# introduction
解析nginx配置文件，获取主配置，server配置和upstream配置等相关信息及其关联
# prepare

Python >= 3.9

```
pip install -r requirement.txt
```

# examples

```
main, servers, upstreams = parser("./nginx.conf", "./conf.d/")
```
