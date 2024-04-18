![arch](ARCHITECTURE.png)

> [!NOTE]
> 项目仅仅满足个人学习交流，不保证任何有效性。

## 特性
- 无需浏览器（只需本地 Flash Player Standalone）
- 无需账号（也可以玩造梦西游等需要账号的游戏）
- 自动嗅探下载游戏

## 使用说明
- 初始化游戏
    ```shell
    py -3 main.py init <url>
    ```
- 启动游戏
    ```shell
    py -3 main.py run
    ```

## 构建

0. 首先确保已正确安装 Python3, Java, Apache Flex, Adobe Flash Player Standalone。
    - **需要 playerglobal.swc 为 32.0 版本**

1. 下载 [FFDec_lib](https://github.com/jindrapetrik/jpexs-decompiler/tree/master/libsrc/ffdec_lib)，并将 jar 文件放入 `swfutil/libs` 文件夹。

2. 构建 `swfutil.jar`
    ```shell
    cd swfutil
    mvn package
    ```


3. 安装 Python 依赖
    ```shell
    pip install -r requirements.txt
    ```

4. 安装 Playwright Chromium
    ```shell
    playwright install chromium
    ```

5. 参照 `.env.example` 创建 `.env` 文件，填写相关信息。

## 其他
细节参考[这篇博文](https://blog.itsmygo.tech/posts/play-an-4399-flash-game-offline/)。

## 协议
除 `external` 文件夹下的文件外，其余文件均采用 [AGPL-3.0 协议](LICENSE) 进行许可。
