# DeepSeek API 文档介绍_deepseek api文档-CSDN博客

原文链接: https://blog.csdn.net/qq_38027465/article/details/145519538

# DeepSeek API 文档介绍

原创
已于 2025-02-10 13:24:09 修改
·
7.3k 阅读

·
![](images/0b22a680d8caf61b3fc4d6ce595a5a36.png)
![](images/5e06ae5b64a61915c89019db36be22b5.png)

14

·
![](images/169ac251df55845562af7f2f9151a130.png)
![](images/4a1192b08a5588d2ac0f778efad9e13f.png)

25
·

CC 4.0 BY-SA版权

版权声明：本文为博主原创文章，遵循 [CC 4.0 BY-SA](http://creativecommons.org/licenses/by-sa/4.0/) 版权协议，转载请附上原文出处链接和本声明。

文章标签：

[#ai](https://so.csdn.net/so/search/s.do?q=ai&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#AI编程](https://so.csdn.net/so/search/s.do?q=AI%E7%BC%96%E7%A8%8B&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)
[#人工智能](https://so.csdn.net/so/search/s.do?q=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)

于 2025-02-08 17:41:42 首次发布

Seed-Coder-8B-Base一键部署

Seed-Coder是一个功能强大、透明、参数高效的 8B 级开源代码模型系列，包括基础变体、指导变体和推理变体，由字节团队开源

*DeepSeek API 文档*\*，涵盖 API 的基本信息、请求参数、响应格式和示例代码

---

### **DeepSeek API 文档**

DeepSeek API 提供了强大的自然语言处理和代码生成能力，适用于多种场景。以下是 API 的使用说明。

---

#### **1. API 基本信息**

* **API 地址**：`https://api.deepseek.com/v1/generate`
* **请求方法**：`POST`
* **认证方式**：Bearer Token
* **Content-Type**：`application/json`

---

#### **2. 请求参数**

##### **Headers**

| 参数名 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| `Authorization` | String | 是 | Bearer Token，格式：`Bearer {api_key}` |
| `Content-Type` | String | 是 | 固定值：`application/json` |

##### **Body**

| 参数名 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| `prompt` | String | 是 | 输入的提示文本 |
| `max_tokens` | Int | 否 | 生成内容的最大长度（默认 100） |
| `temperature` | Float | 否 | 生成内容的随机性（默认 0.7） |
| `top_p` | Float | 否 | 生成内容的多样性（默认 1.0） |

---

#### **3. 响应格式**

##### **成功响应**

```

{
  "id": "cmpl-1234567890",
  "object": "text_completion",
  "created": 1677654321,
  "model": "deepseek-v1",
  "choices": [
    {
      "text": "生成的文本内容",
      "index": 0,
      "logprobs": null,
      "finish_reason": "length"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}

```

##### **字段说明**

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| `id` | String | 请求的唯一标识符 |
| `object` | String | 对象类型（固定值：`text_completion`） |
| `created` | Int | 请求时间戳 |
| `model` | String | 使用的模型名称 |
| `choices` | Array | 生成的内容列表 |
| `choices[].text` | String | 生成的文本内容 |
| `choices[].index` | Int | 内容索引 |
| `usage` | Object | Token 使用情况 |
| `usage.prompt_tokens` | Int | 提示文本的 Token 数量 |
| `usage.completion_tokens` | Int | 生成内容的 Token 数量 |
| `usage.total_tokens` | Int | 总 Token 数量 |

##### **错误响应**

```

{
  "error": {
    "message": "错误信息",
    "type": "invalid_request_error",
    "code": 400
  }
}

```

---

#### **4. 示例代码**

##### **Python 示例**

```

import requests

api_key = "your_deepseek_api_key"
url = "https://api.deepseek.com/v1/generate"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "prompt": "生成一段关于春天的诗歌",
    "max_tokens": 50
}
response = requests.post(url, headers=headers, json=data)
print(response.json())

```

##### **cURL 示例**

```

curl -X POST "https://api.deepseek.com/v1/generate" \
     -H "Authorization: Bearer your_deepseek_api_key" \
     -H "Content-Type: application/json" \
     -d '{
           "prompt": "生成一段关于春天的诗歌",
           "max_tokens": 50
         }'

```

---

#### **5. 常见问题**

##### **Q1：如何获取 API Key？**

* 访问 DeepSeek 官网，注册账号并生成 API Key。

##### **Q2：如何提高生成内容的质量？**

* 调整 `temperature` 和 `top_p` 参数，控制生成内容的随机性和多样性。
* 提供更详细的 `prompt`，明确生成内容的主题和格式。

##### **Q3：API 调用频率有限制吗？**

* 免费用户通常有每分钟和每月的调用限制，具体限制请参考官网文档。

---

#### **6. 参考链接**

* [DeepSeek 官方文档](https://www.deepseek.com/docs)
* [API 认证指南](https://www.deepseek.com/docs/authentication)

（请大家先关注我,后续还会更新!!!）

您可能感兴趣的与本文相关的镜像

![Seed-Coder-8B-Base](images/bcd9c990d4e0f6e17e6e485c4790d34e.jpg)

Seed-Coder-8B-Base

文本生成

Seed-Coder

Seed-Coder是一个功能强大、透明、参数高效的 8B 级开源代码模型系列，包括基础变体、指导变体和推理变体，由字节团队开源

一键部署运行

![](images/3499c7f767d8069c132c42c5e958af67.png)

确定要放弃本次机会？

福利倒计时

*:*

*:*

![](images/241bad06794cb671d2a282c127a3c99e.png)
立减 ¥

普通VIP年卡可用

[立即使用](https://mall.csdn.net/vip)

[![](images/43503723b615e906143dcec5f2376ac3.jpg)

kang\_deepsk](https://blog.csdn.net/qq_38027465)

[关注](javascript:;)
关注

* ![](images/7ae65a949cf422c16a3786a91cf99bf5.png)
  ![](images/864d5cb763134ab76db2e859d86c6ac9.png)
  ![](images/0242911ea5c167952ccce45d91294727.png)

  14

  点赞
* ![](images/0b4303d154e4a79a407e76e4701501e5.png)
  ![](images/eeee8107f3b2f57f85820f2decdaec0b.png)

  踩
* [![](images/79bdf29087a3087d00590dc03d3fb1b5.png)
  ![](images/7fd742a4babd71a5a9496b1b4bd992d0.png)
  ![](images/4674569fc86e4bbaace341fb5a9fec58.png)

  25](javascript:;)

  收藏

  觉得还不错?
  一键收藏
  ![](images/b6f228a33563ff279d1935a8d841e241.png)
* ![](images/b2e686a877c19770edb75ee87b4459a0.png)
  知道了

  [![](images/96a8575800e94aded08b5299cc1f98de.png)

  0](#commentBox)

  评论
* [![](images/d2fcbdc90dda726c2bfd8148bb28973b.png)
  分享](javascript:;)

  复制链接

  分享到 QQ

  分享到新浪微博

  ![](images/4c875eeaf69ccf68dbb37cf3137e1884.png)扫一扫
* ![](images/3f6c9dae656a10d2abaa9b2f08bffd89.png)

  ![](images/6e27cb0a51e039d131e7e6af5c4b931c.png)
  举报

  ![](images/6e27cb0a51e039d131e7e6af5c4b931c.png)
  举报

![]()

[*DeepSeek*提示库（官方*文档*）](https://blog.csdn.net/weixin_47061482/article/details/145909890)

[一个喜欢诗和远方的程序媛](https://blog.csdn.net/weixin_47061482)

02-27
![](images/c435921c498fd8cf48f9f07527be548a.png)
2743

[专注于提示词和训练技巧本身，才才能让*DeepSeek*更好的帮助我们](https://blog.csdn.net/weixin_47061482/article/details/145909890)

参与评论
您还未登录，请先
登录
后发表或查看评论

[三、连接*DeepSeek* *API*，开启数据交互](https://zxcopyang.blog.csdn.net/article/details/145693815)

[weixin\_39169967的博客](https://blog.csdn.net/weixin_39169967)

02-17
![](images/c435921c498fd8cf48f9f07527be548a.png)
1668

[*API*（Application Programming Interface，应用程序*编程*接口）是一种允许不同软件应用程序之间进行通信和数据交换的机制。通过*API*，我们可以调用其他软件系统提供的功能和服务，而无需了解其内部实现细节。在文生视频项目中，*DeepSeek*提供了一系列*API*，我们可以使用这些*API*将文本描述发送给*DeepSeek*，然后获取*DeepSeek*根据文本生成的图像、视频等内容。](https://zxcopyang.blog.csdn.net/article/details/145693815)

[用C++调用*DeepSeek* *API*？保姆级教程来了（附完整代码）](https://devpress.csdn.net/v1/article/detail/156237534)

[weixin\_46564301的博客](https://blog.csdn.net/weixin_46564301)

12-24
![](images/c435921c498fd8cf48f9f07527be548a.png)
991

[在*AI*大模型*API*调用的主流示例中，curl、Python、Node.js是最常见的三种方式。但对于习惯用C++开发的同学来说，如何快速对接大模型*API*呢？](https://devpress.csdn.net/v1/article/detail/156237534)

[如何通过*Deepseek*的*API*进行开发和使用(适合开发者和小白的学习使用教程)](https://h0xsecdebug.blog.csdn.net/article/details/145481907)

[记录开发和安全学习过程中的点点滴滴](https://blog.csdn.net/weixin_72543266)

02-06
![](images/c435921c498fd8cf48f9f07527be548a.png)
4008

[最近在休息的时候也是一直会刷到关于*deepseek*,简单使用了一下,发现这个*AI*和以往使用过的有很大的不同,起码在我看来有了人性,今天突然发现官方开放了*API*,赶紧来玩一下,通过*deepseek*今后可以极大的提高开发工具的效率.](https://h0xsecdebug.blog.csdn.net/article/details/145481907)

[ollama本地部署的*deepseek*解析接口*文档*，结合Python生成pytest+yml的框架用例](https://tester-with-python.blog.csdn.net/article/details/145532374)

[weixin\_44872675的博客](https://blog.csdn.net/weixin_44872675)

02-09
![](images/c435921c498fd8cf48f9f07527be548a.png)
2617

[在接口测试中，测试工程师通常需要根据开发提供的接口*文档*手动编写测试用例。这种方式不仅耗时，还容易遗漏边界场景。通过。](https://tester-with-python.blog.csdn.net/article/details/145532374)

[*DeepSeek* *API**文档*解读（对话模块）](https://devpress.csdn.net/v1/article/detail/145438941)

[2302\_82179879的博客](https://blog.csdn.net/2302_82179879)

02-04
![](images/c435921c498fd8cf48f9f07527be548a.png)
2485

[对话补全。](https://devpress.csdn.net/v1/article/detail/145438941)

[*DeepSeek* *API**文档*：创建对话补全的指南](https://blog.csdn.net/m0_59328104/article/details/138587442)

[m0\_59328104的博客](https://blog.csdn.net/m0_59328104)

05-08
![](images/c435921c498fd8cf48f9f07527be548a.png)
1万+

[*DeepSeek*的*API*允许开发者通过*编程*方式与*DeepSeek*的MoE模型进行交互，实现自定义的对话生成和补全。这为构建聊天机器人、虚拟助手或其他需要自然语言处理的应用提供了极大的灵活性。通过*DeepSeek*的*API**文档*，开发者可以快速掌握如何利用*DeepSeek*平台的强大功能来创建智能对话补全。无论是构建聊天机器人还是集成到更复杂的系统中，*DeepSeek* *API*都提供了必要的工具和灵活性。要开始使用*DeepSeek* *API*，可以访问*DeepSeek* *API**文档*获取更多详细信息和指南。](https://blog.csdn.net/m0_59328104/article/details/138587442)

精选资源
[*DeepSeek* *API* 调用指南：从注册到流式输出完整流程](https://download.csdn.net/download/qq_51917985/90342595)

02-06

[内容概要：本文*介绍*了*DeepSeek* *API*的详细调用方式。首先阐述了如何在*DeepSeek*官网注册账户并获取*API* Key，随后讲述了环境准备以及安装必要的工具包，紧接着提供了利用Open*AI* SDK或直接发送HTTP请求的具体Python代码...](https://download.csdn.net/download/qq_51917985/90342595)

精选资源
[*DeepSeek* *API* 调用教程：从获取*API* Key到流式消息输出](https://download.csdn.net/download/weixin_43196388/90345836)

02-06

[内容概要：本文*介绍*了如何获取 *DeepSeek* *API* 密钥，并使用 *Api*fox 进行 *API* 调用与调试的具体步骤。首先需要访问 *DeepSeek* 官网注册账号以获取 *api*\_key 和一些免费的 token 额度；接着通过创建新的 *API* Key 并正确...](https://download.csdn.net/download/weixin_43196388/90345836)

精选资源
[如何修复 *DeepSeek* *API* 错误 401 身份验证失败.pdf](https://download.csdn.net/download/calvin189s/90400579)

02-18

[在进行修复过程中，重要的是保持*API*密钥的安全性，定期更新过期的令牌，并随时参考最新的*API**文档*和官方指南。 最后，用户在使用*DeepSeek* *API*时，应保持对*API*密钥和账户的高度重视，避免因管理不当导致的权限问题。...](https://download.csdn.net/download/calvin189s/90400579)

精选资源
[调用*DeepSeek* *API* 增强版纯前端实现方案，支持文件上传和内容解析功能](https://download.csdn.net/download/qq_31982109/90418974)

02-23

[而调用*DeepSeek* *API*可以是实现这一功能的有效手段之一。通过纯前端技术实现，不仅可以提升用户体验，还可以简化后端服务的负担。下面将详细探讨如何在前端实现文件上传和内容解析的功能，并调用*DeepSeek* *API*以增强...](https://download.csdn.net/download/qq_31982109/90418974)

精选资源
[*DeepSeek* *API* 的 Python 客户端](https://download.csdn.net/download/hefeng_aspnet/90460069)

03-06

[*文档*中详细*介绍*了每个 *API* 的使用方法、参数说明以及返回值，而示例代码则展示了如何在实际的项目中应用这些 *API*。这不仅为初学者提供了学习的捷径，也为经验丰富的开发者节省了查阅和测试的时间。 值得注意的是，...](https://download.csdn.net/download/hefeng_aspnet/90460069)

[*Deepseek*提示库（官方*文档*）](https://devpress.csdn.net/v1/article/detail/145491194)

[star\_nwe的博客](https://blog.csdn.net/star_nwe)

02-07
![](images/c435921c498fd8cf48f9f07527be548a.png)
4592

[*Deepseek*官方给出了提示库*文档*：https://*api*-docs.*deepseek*.com/zh-cn/prompt-library/下面举几个例子：文案大纲生成器：根据用户提供的主题，来生成文案大纲。](https://devpress.csdn.net/v1/article/detail/145491194)

[*DeepSeek* *API* 客户端使用*文档*](https://devpress.csdn.net/v1/article/detail/146191002)

[大白菜代码的博客](https://blog.csdn.net/hzether)

03-11
![](images/c435921c498fd8cf48f9f07527be548a.png)
2143

[deep.py是一个用于与 *DeepSeek* *API* 交互的 Python 客户端封装。它提供了简单易用的接口，支持对话历史管理、日志记录等功能，使得与 *DeepSeek* *API* 的交互更加便捷和可靠。](https://devpress.csdn.net/v1/article/detail/146191002)

[*Deepseek*官网接口*文档*](https://blog.csdn.net/weixin_39682092/article/details/145709228)

[风一样](https://blog.csdn.net/weixin_39682092)

02-18
![](images/c435921c498fd8cf48f9f07527be548a.png)
1793

[参数应包含一个字典，其中包含 safetensors 模型的文件，包括文件名和每个文件的 SHA256 摘要。在调用此 *API* 之前，请使用 [/*api*/blobs/:digest](#推送一个 blob) 将每个文件推送到服务器。在调用此 *API* 之前，请使用 [/*api*/blobs/:digest](#推送一个 blob) 将 GGUF 文件推送到服务器。取消的拉取操作将从上次中断的地方继续，多次调用将共享相同的下载进度。此示例设置了所有可用选项，但您可以单独设置其中任何一个，并省略您不想覆盖的选项。](https://blog.csdn.net/weixin_39682092/article/details/145709228)

[*deepseek*实战教程-第四篇开放平台接口*文档*使用](https://global-fairy-top.blog.csdn.net/article/details/146483534)

[极客栈](https://blog.csdn.net/jiao_zg)

03-24
![](images/c435921c498fd8cf48f9f07527be548a.png)
3435

[通过上面的*介绍*，我们就基本掌握了*deepseek*提供的基础的开发*api*功能，我们可以通过学习掌握这些*api*接口，来在自己的项目中调用所需接口，完成我们自己的业务功能，实现和我们的项目的嵌入。当然这是程序员的工作，并不是没有*编程*基础的人做的事情，希望我们能够尽快掌握并进入大模型的业务开发中，实现工作效率和业务效率的双重提升通过本章我们已经可以完成*deepseek*的应用开发了。](https://global-fairy-top.blog.csdn.net/article/details/146483534)

[*DeepSeek* *API* 对接*文档**介绍*](https://devpress.csdn.net/v1/article/detail/146133158)

[行思理的博客](https://blog.csdn.net/xzp19841203xzp)

03-09
![](images/c435921c498fd8cf48f9f07527be548a.png)
2417

[*DeepSeek* *API* 对接*文档*主要接口为对话补全*DeepSeek* *API* 使用与 Open*AI* 兼容的 *API* 格式，通过修改配置，您可以使用 Open*AI* SDK 来访问 *DeepSeek* *API*，或使用与 Open*AI* *API* 兼容的软件。base\_urlv1在创建 *API* key 之后，你可以使用以下样例脚本的来访问 *DeepSeek* *API*。样例为非流式输出，您可以将 stream 设置为 true 来使用流式输出。不同语言的sdk看右边红框部分。](https://devpress.csdn.net/v1/article/detail/146133158)

[*DeepSeek*使用*文档*](https://devpress.csdn.net/v1/article/detail/146021333)

[顾茗轩的博客](https://blog.csdn.net/2404_87426459)

03-04
![](images/c435921c498fd8cf48f9f07527be548a.png)
2503

[*DeepSeek* 是一款由深度求索(*DeepSeek* Inc.)开发的智能工具，支持自然语言处理、数据分析、代码生成等多种*AI*能力。本*文档*将指导您如何快速使用其核心功能。](https://devpress.csdn.net/v1/article/detail/146021333)

[【常见语言大模型*API*调用】第一篇：深度求索--*deepseek*

热门推荐](https://devpress.csdn.net/v1/article/detail/143112086)

[qq\_45584615的博客](https://blog.csdn.net/qq_45584615)

10-21
![](images/c435921c498fd8cf48f9f07527be548a.png)
5万+

[*DeepSeek*大模型*api*调用，python](https://devpress.csdn.net/v1/article/detail/143112086)

[*deepseek* *api**文档*的安装教程

最新发布](https://wenku.csdn.net/answer/7jmn9ca0mz)

02-05

[### *DeepSeek* *API* *文档*安装教程 ...为了更好地理解和运用该*API*接口，在实际编码前阅读完整的 [*DeepSeek* *API**文档*](https://example.com/*deepseek*/docs)[^2] 尤为重要。这其中包括但不限于认证机制、请求格式说明等内容。](https://wenku.csdn.net/answer/7jmn9ca0mz)