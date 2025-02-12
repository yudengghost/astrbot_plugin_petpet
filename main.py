from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.all import *
import json
import aiohttp
import os
import random
from astrbot.core.utils.t2i.network_strategy import NetworkRenderStrategy
import ssl

@register("考公", "yudengghost", "帮助考公人随时背书的插件(?)", "1.0.0", "https://github.com/yudengghost/astrbot_plugin_public_servant")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.network_strategy = NetworkRenderStrategy()

    @filter.command_group("考公")
    def 考公(self):
        pass

    @考公.command("help")
    async def help(self, event: AstrMessageEvent):
        msg = """/考公 help --> 获取帮助\n
/考公 每日晨读 --> 获取每日晨读\n
/考公 60s --> 获取每日60秒读懂世界要闻\n
/考公 高频成语 --> 随机获取一个高频成语\n"""
        yield event.plain_result(msg)

    @考公.command("每日晨读")
    async def daily_reading(self, event: AstrMessageEvent):
        try:
            # 获取每日文章
            async with aiohttp.ClientSession() as session:
                async with session.post("https://saduck.top/api/article/getArticleByDay") as resp:
                    if resp.status != 200:
                        yield event.plain_result("获取文章失败，请稍后再试")
                        return
                    
                    article_data = await resp.json()
                    if not article_data.get("result"):
                        yield event.plain_result("获取文章失败，请稍后再试")
                        return
                    
                    article = article_data["result"]
                    
                    # 构建 Markdown 内容
                    content = f"""# {article['title']}

{article['content']}

> 来源: {article['source']}"""

                    try:
                        # 使用 NetworkRenderStrategy 渲染内容为图片
                        image_path = await self.network_strategy.render(content)
                        
                        # 发送图片
                        yield event.image_result(image_path)
                        
                        # 删除临时图片文件
                        if os.path.exists(image_path):
                            os.remove(image_path)
                    except Exception as e:
                        logger.error(f"渲染或发送图片失败: {str(e)}")
                        if 'image_path' in locals() and os.path.exists(image_path):
                            os.remove(image_path)
                        raise
                    
        except Exception as e:
            logger.error(f"获取每日晨读失败: {str(e)}")
            yield event.plain_result("获取文章失败，请稍后再试")

    @考公.command("60s")
    async def sixty_seconds(self, event: AstrMessageEvent):
        """获取每日60秒读懂世界要闻"""
        try:
            # 创建 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get("https://api.03c3.cn/api/zb") as resp:
                    if resp.status != 200:
                        yield event.plain_result("获取60秒读懂世界失败，请稍后再试")
                        return
                    
                    # 获取二进制图片数据
                    image_data = await resp.read()
                    if not image_data:
                        yield event.plain_result("获取60秒读懂世界失败，请稍后再试")
                        return
                    
                    # 保存临时文件
                    temp_path = os.path.join(os.path.dirname(__file__), "temp_60s.jpg")
                    with open(temp_path, "wb") as f:
                        f.write(image_data)
                    
                    try:
                        # 发送图片
                        yield event.image_result(temp_path)
                    finally:
                        # 删除临时文件
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    
        except Exception as e:
            logger.error(f"获取60秒读懂世界失败: {str(e)}")
            yield event.plain_result("获取60秒读懂世界失败，请稍后再试")

    @考公.command("高频成语")
    async def highword(self, event: AstrMessageEvent):
        """随机获取一个高频成语"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://saduck.top/api/word/getHWord", json={}) as resp:
                    if resp.status != 200:
                        yield event.plain_result("获取高频成语失败，请稍后再试")
                        return
                    
                    data = await resp.json()
                    if not data.get("result"):
                        yield event.plain_result("获取高频成语失败，请稍后再试")
                        return
                    
                    # 获取成语列表长度
                    total = len(data["result"])
                    
                    # 生成随机索引
                    idx = random.randrange(total)
                    
                    # 获取随机成语
                    word = data["result"][idx]
                    
                    # 构建返回消息
                    content = f"""# 今日高频成语：{word['wordContent']}

拼音：{word['pinyin']}

释义：{word['explanation']}

出处：{word['derivation']}

例句：{word['example']}

近义词：{word['similar']}

反义词：{word['opposite']}"""

                    try:
                        # 使用 NetworkRenderStrategy 渲染内容为图片
                        image_path = await self.network_strategy.render(content)
                        
                        # 发送图片
                        yield event.image_result(image_path)
                        
                        # 删除临时图片文件
                        if os.path.exists(image_path):
                            os.remove(image_path)
                    except Exception as e:
                        logger.error(f"渲染或发送图片失败: {str(e)}")
                        if 'image_path' in locals() and os.path.exists(image_path):
                            os.remove(image_path)
                        raise
                    
        except Exception as e:
            logger.error(f"获取高频成语失败: {str(e)}")
            yield event.plain_result("获取高频成语失败，请稍后再试")
