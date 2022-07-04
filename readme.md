# 瓜大自动疫情填报程序

## 必须依赖

1. 谷歌浏览器
2. 谷歌驱动 (版本要与浏览器匹配)
3. selenium

## 配置文件

```json
{
    // 学号
    "username": , 
    // 密码
    "password": "",
    // in的内容为[学校 | 西安市内 | 国内]
    // 所在地址，暂不支持国外
    // 填写要求 XX省，XX市，XX区/县
    // 校内不需要填省市区，市内不需要填省市
    "address": {
        "in": "", 
        "province": "",
        "city": "",
        "district": ""
    },
	// 填报后邮件通知
    "email": {
        "enable": true,
        // 发送通知邮件的邮箱，请自备，密码为自行获取对应协议的令牌，不是油箱密码
        "sender": {
            "username":"",
            "password":""
        },
        // 接受者邮箱账号
        "receivers": [
            ""
        ]
    }
}
```

