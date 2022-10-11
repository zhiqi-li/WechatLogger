# log_config = dict(
#     interval=10,
#     hooks=[
#         dict(type='WechatLoggerHook'), # use this hook in your log_config
#         dict(type='TextLoggerHook'),
#         dict(type='TensorboardLoggerHook')
#     ])
from typing import Dict
import numpy as np
import os.path as osp
from mmcv.runner.dist_utils import master_only
from mmcv.runner.hooks import HOOKS
from mmcv.runner.hooks.logger.base import LoggerHook
from urllib import request, parse
import json
from urllib.error import HTTPError, URLError
import socket

@HOOKS.register_module()
class WechatLoggerHook(LoggerHook):
    """Class to log metrics to Wechat. Get your latest training results immediately!

    Args:
        interval (int): Logging interval (every k iterations).
            Default 10.
        ignore_last (bool): Ignore the log of last iterations in each epoch
            if less than `interval`.
            Default: True.
        reset_flag (bool): Whether to clear the output buffer after logging.
            Default: False.
        by_epoch (bool): Whether EpochBasedRunner is used.
            Default: True.
        allowed_subkeys: No need to send all results to your phone. Catch the point!
        miao_code: Get your own code from https://www.showdoc.com.cn/miaotixing/9175237605891603
    """

    def __init__(self,
                 interval: int = 10,
                 ignore_last: bool = True,
                 reset_flag: bool = False,
                 commit: bool = True,
                 by_epoch: bool = True,
                 allowed_subkeys = ['NDS', 'mAP'], # remove some keys based on subkeys.
                 miao_code='xxxx'): # get your onw miao code from https://www.showdoc.com.cn/miaotixing/9175237605891603
        
        super().__init__(interval, ignore_last, reset_flag, by_epoch)
        self.miao_code = miao_code
        self.allowed_subkeys = allowed_subkeys
        self.notification = True

    @master_only
    def before_run(self, runner) -> None:
        super().before_run(runner)

    @master_only
    def get_table_text(self, runner, tags):
        row_lists = []
        row_lists.append([runner.meta['exp_name'], ''])
        if self.by_epoch:
            row_lists.append(['Epoch', runner.epoch])
        for key in tags.keys():
            for allowed_subkey in self.allowed_subkeys:
                if allowed_subkey in key:
                    row_lists.append([key, tags[key]])

        table_txt = ''
        for each_row in row_lists:
            table_txt += '{key}:  {value}\n'.format(key=each_row[0], value=str(each_row[1]))
        return table_txt

    @master_only
    def log(self, runner) -> None:
        if not self.notification: return

        mode=self.get_mode(runner)
        tags = self.get_loggable_tags(runner)
        text = None

        if mode == 'train':
            if np.isnan(tags['train/loss']) or np.isinf(tags['train/loss']):
                text = runner.meta['exp_name'] + 'got NaN/INF loss'
                runner.logger.info('got NaN/INF loss value, we will not send any notification to your phone later')
                self.notification = False
        elif mode == 'val':   
            text =  self.get_table_text(runner, tags)
        else:
            assert False, 'what is the running status?'

        self._send(runner, text)

    @master_only
    def _send(self, runner, text) -> None:
        if text is None: return 
        
        page=None

        try:
            page = request.urlopen("http://miaotixing.com/trigger?" + parse.urlencode({"id":self.miao_code, "text":text, "type":"json"}), timeout=5)
        except HTTPError as error:
            runner.logger.info('Data not retrieved because %s\nURL: %s', error, url)
        except URLError as error:
            if isinstance(error.reason, socket.timeout):
                runner.logger.info('MiaoTiXing: socket timed out - URL %s', url)
            else:
                runner.logger.info('MiaoTiXing: some other error happened ')
        else:
            runner.logger.info('MiaoTiXing: Access successful.')
        
        if page is None: return
        result = page.read()
        jsonObj = json.loads(result)
        
        if (jsonObj["code"] == 0):
            runner.logger.info("发送信息到喵提醒成功")
        else:
            runner.logger.info("发送信息到喵提醒失败，错误代码：" + str(jsonObj["code"]) + "，描述：" + jsonObj["msg"])


    @master_only
    def after_run(self, runner) -> None:
        text = runner.meta['exp_name'] + ' Done!!!'
        self._send(runner, text)
        pass
