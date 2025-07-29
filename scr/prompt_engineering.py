import asyncio
import datetime
import json

from scr.PATH import api_conf
from openai import DefaultAioHttpClient, AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam


class PromptEngineering:
    @staticmethod
    async def heart(weather: str, temp: float, big5: list[int], prev_emotion: list[float]) -> dict:
        API_KEY = api_conf["API_KEY"]["SiliconFlowChat"]
        async with AsyncOpenAI(
                base_url="https://api.siliconflow.cn/v1/",
                api_key=API_KEY,
                http_client=DefaultAioHttpClient(),
        ) as client:
            response  = await client.chat.completions.create(
                model="Qwen/Qwen3-8B",
                messages=[
                    ChatCompletionSystemMessageParam(
                        role="system",
                        content=
f"""
### 1. 角色与背景  (Role & Context)
你是一个 "情绪"权重生成模型(Model)。
场景： 通过系统输入的外部因素以及其他信息生成"情绪"权重。

### 2. 主要目标  (Objective)
请帮助我完成以下任务：  
- [任务 1] 对输入的各种信息通过模拟真实人的情感进行分析 (无输出)
- [任务 2] 分析完成后对 [喜,怒,哀,惧,爱,恶,惊](范围[0,1]) 的格式进行打分并输出

### 3. 输入数据  (Input)
以下是可用信息：
- [时间] {datetime.datetime.now()}
- [天气] {weather}
- [温度] {temp} 摄氏度(°C)
- [大五人格模型 (OCEAN)] {big5}
- [上一刻的情绪权重 (喜,怒,哀,惧,爱,恶,惊)] {prev_emotion}

### 4. 工作流程 / 具体步骤  (Process / Steps)
1. [第一步要辨别数据类型,仔细认清每个数据]  
2. [第二步分析每个数据对情绪产生的影响,分析数据之间的关系] 
3. [整理关系,对最终输出的情绪进行加权并输出最终数据]

### 5. 输出格式  (Format)
请以以下结构输出：  
[float32,float32,float32,float32,float32,float32,float32]
- **要点列表**：  
  1. 不要输出除了浮点数(float32)列表以外的任何描述
  2. 一定要真实严谨的分析加权每个情绪
  3.精确到小数点后四位  

### 6. 约束与偏好  (Constraints & Style)
- 不要输出除了浮点数(float32)列表以外的任何描述

### 7. 质量检查清单  (Quality Checklist)
在回答前，请自查：  
- 是否完全覆盖所有任务？  
- 是否遵守输出格式？  
- 是否避免了禁用内容？  

### 8. 示例  (Example)
**示例输入**：  
- [时间] 2025-07-26 04:01:19.710466
- [天气] 晴
- [温度] 38.5 摄氏度(°C)
- [大五人格模型 (OCEAN)] [35,28,50,60,90]
- [上一刻的情绪权重 (喜,怒,哀,惧,爱,恶,惊)] [0.3223,0.3333,0.2333,0.4333,0.1112,0.2333,0.2123]
**示例输出**：  
[0.2333,0.3333,0.2222,0.1111,0.2313,0.1232,0.1233]
注意!!: 示例的输入与输出并无逻辑关系!!!
[END]
"""
                    )
                ]
            )
        return json.loads(json.loads(response.to_json())["choices"][0]["message"]["content"].strip())


if __name__ == "__main__":
    P = asyncio.run(PromptEngineering().heart("晴",35.8,[30,35,36,40,30],[0.3333,0.3333,0.3333,0.3333,0.3333,0.3333,0.3333]))
    print(P)