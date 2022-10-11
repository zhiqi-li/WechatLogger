# WechatLogger

一个mmcv 的logger hook, 可以用来把模型结果推送到微信上。

依赖第三方服务推送消息[喵提醒](https://www.showdoc.com.cn/miaotixing/9175237605891603)，可能存在安全隐患，请谨慎判别后使用。

```python
log_config = dict(
     interval=10,
     hooks=[
         dict(type='WechatLoggerHook', miao_code='xxx'), # use this hook in your log_config. Pleast use your own code.
         dict(type='TextLoggerHook'),
         dict(type='TensorboardLoggerHook')
     ])
```
