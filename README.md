# 小米 6（sagit）DroidSpaces 内核 — LineageOS 22.2（Android 15）

适用：**小米 6（sagit）** · **LineageOS 22.2** · Linux **4.4.302**（非 GKI）。

本仓库用 **GitHub Actions 云编译** 带 DroidSpaces 支持的内核：

- **内核基线**：`lineage-22.2` 分支自带的 `arch/arm64/configs/sagit_defconfig`（官方 ROM 用的配置）
- **追加选项**：`config/additions.config`（DroidSpaces 必需项 + sagit DTB 名）
- **补丁**：`patches/02-cgroup-file-prefix-4.4.patch`（DroidSpaces non-GKI；4.4.302 **没有** `net/netfilter/xt_qtaguid.c`，故不打 01 补丁）
- **工具链**：Proton clang 13 + `aarch64-linux-gnu` binutils（`LLVM=1 LLVM_IAS=1`）

## 云编译

push 到 `main`，或手动 `Actions → build-sagit-droidspaces-22.2 → Run workflow`。

单次 run 的 **Artifacts**（保留 14 天）：

| 文件 | 说明 |
| --- | --- |
| `Image.gz-dtb` | 内核 + DTB，可自行打包 |
| `boot-sagit-droidspaces.img` | 用官方 22.2 `boot.img` 重打包的 fastboot 直刷镜像（若官方镜像可下载） |
| `.config` / `System.map` / `build.log` / `kernel-commit.txt` | 调试用 |

> Actions 上只编**内核**（整包 ROM 需要 ≥64GB RAM/400GB 磁盘，Actions 跑不动）。需要整包 ROM 请在本地按 LineageOS wiki 构建，并用 `apply_to_lineage_tree.sh` 把同一套改动打进内核树。

## 刷入（自行确认已解锁并备份）

```bash
fastboot flash boot boot-sagit-droidspaces.img
fastboot reboot
```

或用 `Image.gz-dtb` + 官方 `boot.img` 自行重打包后刷入。

## root（必须）

DroidSpaces 必须 root。用 **Magisk**（v27+；Android 15 建议最新稳定版）对镜像「安装 → 选择并修补一个文件」再刷入。
> KernelSU / SukiSU 需要 Linux 4.14+，sagit 的 4.4.302 不满足，故本内核不集成。

## 安装 DroidSpaces

1. 安装 DroidSpaces APK → 授予 root；
2. 按提示安装 backend，重启；
3. `Settings → Requirements → Check Requirements` 全过后再建容器。

## 说明

- 内核版本 `4.4.302-perf`；启用 PID/UTS/IPC/NET/USER 命名空间、SYSVIPC、seccomp、cgroup v1（memcg/cfs/pids）、devtmpfs、overlayfs、veth/bridge/nf_tables/NAT/macvlan；关闭 `ANDROID_PARANOID_NETWORK`。
- 刷机有风险，自行承担。

## 资源

- LineageOS 下载：<https://download.lineageos.org/devices/sagit>
- LOS 22.2 ROM/boot/recovery（mirrorbits）：<https://mirrorbits.lineageos.org/full/sagit/>
- 内核源码：<https://github.com/LineageOS/android_kernel_xiaomi_msm8998>（`lineage-22.2`）
- Magisk：<https://github.com/topjohnwu/Magisk/releases/latest>
- DroidSpaces：<https://github.com/ravindu644/Droidspaces-OSS>
- LineageOS 安装教程：<https://wiki.lineageos.org/devices/sagit/install>
