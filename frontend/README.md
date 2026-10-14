# 前端目录说明

前端项目使用 Vue 3 和 Vite。日常查看或修改前端时，可以先从下面几个文件开始：

```text
frontend/
├── index.html              # 网页入口
├── package.json            # 前端依赖和启动命令
└── src/
    ├── main.js              # 创建 Vue 应用、注册控件和加载全局样式
    ├── App.vue              # 登录、学习总览、课表、问答和管理页面
    ├── api/
    │   └── client.js         # 后端请求、登录令牌和错误提示
    └── styles/
        └── main.css          # 所有页面共用的布局、颜色和字号
```

## 常见修改位置

- 修改页面内容或按钮行为：打开 `src/App.vue`，页面区域和主要逻辑都有中文说明。
- 修改页面外观、间距或字体：打开 `src/styles/main.css`，按中文分区注释查找样式。
- 修改前后端请求设置：打开 `src/api/client.js`。
- 注册全局控件或样式：打开 `src/main.js`。

## 启动前端

在 `frontend` 目录运行：

```powershell
npm run dev
```

需要验证正式构建时运行：

```powershell
npm run build
```
