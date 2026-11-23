# 重建触发：IPC namespace 初始化修复

- 日期：2026-11-23
- 本文件仅用于触发 `build-sagit-droidspaces-22.2`（该 workflow 的 push 触发路径为
  `.github/workflows/build-sagit.yml`、`config/**`、`scripts/**`）。
- 代入的改动不在本仓库，而在内核 fork：
  **andyfriday105/android_kernel_xiaomi_msm8998 @ droidspaces-22.2**
  commit `c6924f19`（`ipc/namespace.c`）。

## 修复内容

`create_ipc_ns()` 里 `ns->user_ns = get_user_ns(user_ns);` 原本在 `mq_init_ns(ns)`
之后才执行。但 `mq_init_ns() -> mqueue_mount() -> mount_ns()` 会把 `ns->user_ns`
传给 `sget_userns()/alloc_super()`，后者调用 `get_user_ns(user_ns)`。`ns` 来自
`kmalloc()`（未初始化），于是每次 `clone()/unshare(CLONE_NEWIPC)` 都把野指针交给
`atomic_inc(&user_ns->count)`：

```
PC is at sget_userns+0xfc
Kernel panic - not syncing: Fatal exception
```

现象：开机约 25 秒重启（Droidspaces 自启容器时 unshare）、打开 Firefox 重启。

修复：把赋值移到 `mq_init_ns()` 之前（与上游 4.19 一致），并在失败路径补
`put_user_ns()`。

## 产物

构建成功后在本次 run 的 Artifacts 中取：

- `boot-sagit-droidspaces.img`（用官方 20261106 boot.img 重打包的 ramdisk + 新内核）
- `Image.gz-dtb`
- `.config` / `System.map` / `build.log` / `kernel-commit.txt`
