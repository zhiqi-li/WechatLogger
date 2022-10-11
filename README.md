# WechatLogger

一个mmcv 的logger hook, 可以用来把模型结果推送到微信上。

依赖第三方服务推送消息，可能存在安全隐患，请谨慎判别后使用。

```
log_config = dict(
     interval=10,
     hooks=[
         dict(type='WechatLoggerHook'), # use this hook in your log_config
         dict(type='TextLoggerHook'),
         dict(type='TensorboardLoggerHook')
     ])
```
