# CheckSH
简介说明：
    改程序耗时较长，要解析上百万个页面(很多404特殊页面)；还有很多需要优化的地方
    单纯测试的话无需修改，如果要完全跑一遍请修改return True if len_a < 100 else False
    -->return True if len_a != len_b else False

V1.0（test版）:
    1、递归爬取m.sohu.com的域名下所有页面上的的url，输出到日志
    2、检测url 的可达性

V2.0:
    1、输出到数据库中，初始化一次，定期做更新
