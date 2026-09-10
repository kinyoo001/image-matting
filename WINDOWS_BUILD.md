# Windows 版打包与使用说明

macOS 上不能直接产出 Windows 的 exe，所以用 GitHub 的云电脑自动打包，
打出来的就是开箱即用的绿色版（解压双击即用）。

## 一、准备工作（只需做一次）

1. 在 GitHub 上 Fork 本仓库（右上角 Fork），或新建空仓库把代码推上去。
   注意：不要直接往 `pangxiaobin/image-matting` 推，你没有权限。
2. 确认 `backend/hub_model/briaai/` 没有被提交（它在 `.gitignore` 里，
   云端打包时会重新下载模型）。

## 二、打包（每次发版点一次）

1. 打开你自己仓库的 **Actions** 页面。
2. 左侧选 **Build Windows**，点 **Run workflow**。
3. 等约 10~20 分钟，跑完后在页面底部 **Artifacts** 下载
   `XiaoYing-Matting-win-x64.zip`。
4. 如果打了 tag 再 push（例如 `v0.2.7`），会自动再发一个
   **Release**，zip 会挂在 Release 下面，方便分发。

## 三、在 Windows 上运行

1. 解压 zip，进 `小颖AI抠图` 文件夹，双击 `ImageMatting.exe`。
2. 首次启动如果提示缺 WebView2，去装一下
   [Edge WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/)（Win10/11 一般自带）。
3. 包里已内置 RMBG-1.4 模型（168MB），断网也能抠图。
   RMBG-2.0 体积太大没打进包，在设置里切换后会提示下载（需要 HF token）。

## 四、打印功能说明

- Windows 版支持打印：结果页点「打印」，走系统打印，
  份数/纸张等在 Windows 打印对话框里确认。
- macOS / Linux 版走 CUPS，可在程序内直接指定份数、纸张、方向。
