# VPRehearsal

用于 LED 背景虚拟拍摄的多人协作预演工程。

## 多人协作具体操作规范

本项目以 `main` 作为团队集成分支。各成员在自己的分支上工作，将改动推送到个人分支后，通过 Pull Request（PR）申请合并到 `main`。以下用个人分支 `sza`、个人资源目录 `Content/SZA/` 举例，请替换为自己的姓名缩写。

### 1. 建立个人工作文件夹，共享内容统一管理

在 UE 内容浏览器中创建自己的工作文件夹，个人新增的模型、材质、蓝图、关卡、镜头序列等资源，优先放在 `Content/姓名缩写/` 下。

共享模块按照团队约定的统一目录和负责人管理。引擎缓存、插件、项目配置继续保留在工程规定的位置：`Config/` 用于共享项目设置，`Plugins/` 用于插件；`Saved/`、`Intermediate/`、`DerivedDataCache/` 等缓存由忽略规则排除。不要将这些目录整体搬入个人资源文件夹。

### 2. 修改他人资源前，先复制到个人工作文件夹

使用其他成员制作的资源时，如果需要做个人版本的修改，应先在 UE 内容浏览器中复制一份到自己的工作文件夹，再修改副本。复制后检查相关依赖和引用，确认自己的关卡或蓝图使用的是预期版本。

共享模块、项目配置、插件源码或确需统一修改的原始资源，应先与负责人沟通，再按约定修改和提交，避免各自维护互不兼容的共享版本。

### 3. 每天开始工作前，先同步主分支并更新个人远程分支

在 GitHub Desktop 中按以下顺序操作：

1. 保存资源，将已有改动提交到自己的分支，确认工作区干净，然后关闭 UE。
2. 切换到 `main`，执行 **Fetch origin**；如有更新，再执行 **Pull origin**，让本地主分支与远程同步。
3. 切回个人分支，例如 `sza`。如果该分支的远程有更新，先拉取。首次协作时，从最新 `main` 创建自己的分支，并通过 **Publish branch** 发布。
4. 保持当前分支为个人分支，在 **Current Branch** 下选择 **Choose a branch to merge into sza**，选中 `main`，执行 **Merge main into sza**。注意合并方向是 **`main` → 个人分支**。
5. 如果出现冲突，先与涉及的成员确认并解决，再完成合并；地图、蓝图等二进制资源的冲突由相关成员共同确认保留版本。
6. 按需执行 `git lfs pull`，确认资源完整；通过 **Push origin** 将合并后的个人分支更新到远程，再打开 UE 开始工作。

只在个人分支点击 **Pull origin**，更新的是个人分支，不会自动将 `main` 合并进来。GitHub Desktop 的操作说明见 [同步与合并分支](https://docs.github.com/en/desktop/working-with-your-remote-repository-on-github-or-github-enterprise/syncing-your-branch-in-github-desktop)。

### 4. 每天工作结束后，再同步主分支并提交 PR

1. 在 UE 中保存当天的资源修改，关闭 UE，检查改动列表并将改动提交到个人分支。
2. 再次执行上面的主分支拉取、合并到个人分支和 LFS 补下载流程，解决当天新增的冲突。
3. 打开 UE 检查相关关卡、资源和插件能否正常使用；如有后续修正，保存并提交，再通过 **Push origin** 上传个人分支，等待 Git 和 LFS 上传完成。
4. 在 GitHub Desktop 中点击 **Preview Pull Request / Create Pull Request**，或在 GitHub 仓库页面创建 PR。确认 **base 为 `main`，compare 为自己的分支**，即 **个人分支 → `main`**。
5. 在 PR 中说明本次完成的工作、主要资源路径、是否修改共享配置或插件，以及在 UE 中的验证结果；涉及画面效果时附上截图，交由相关负责人检查后合并。

当天工作尚未完成时，可提交 Draft PR 并说明进度和待完成项。如果个人分支已有尚未合并的 PR，继续向该分支推送即可更新原 PR，无需重复创建。操作说明见 [通过 GitHub Desktop 创建 PR](https://docs.github.com/en/desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request-from-github-desktop)。

## 协作者必读：Git LFS

本仓库通过 Git LFS 管理 UE 资源、音视频、图片、模型和插件二进制文件。Git 仓库保存这些文件的指针，完整内容由 LFS 下载到本地；**拉取工程后，先确认 LFS 文件下载完成，再打开 UE。**

当前工程使用 **Windows x64、Unreal Engine 5.8.3**，随工程提供的 VibeUE 5.0 DLL 对应该引擎构建（BuildId：`55116800`）。协作者应使用相同引擎版本和兼容构建；其他平台或不兼容构建需要重新编译插件。

### 1. 首次获取工程

推荐使用 GitHub Desktop 登录有仓库访问权限的账号，然后通过 **Clone repository** 克隆工程。GitHub Desktop 已内置 Git LFS；如果出现 **Initialize Git LFS** 提示，选择初始化。详见 [GitHub Desktop 的 LFS 说明](https://docs.github.com/en/desktop/configuring-and-customizing-github-desktop/about-git-large-file-storage-and-github-desktop)。

使用命令行的协作者需先安装 Git 和 [Git LFS](https://git-lfs.com/)，再运行：

```powershell
git lfs version
git lfs install
```

随后克隆仓库。在本地工程根目录（`VPRehearsal.uproject` 所在目录）打开终端，执行：

```powershell
git lfs install
git lfs pull
git lfs ls-files
```

- `git lfs install` 配置 LFS 过滤器和当前仓库所需的钩子，新电脑或新克隆的仓库应确认已初始化。
- `git lfs pull` 下载当前检出分支需要的 LFS 对象，并将完整内容写入工作目录；它不会代替普通 Git 拉取，也不会切换分支。详见 [Git LFS pull 文档](https://github.com/git-lfs/git-lfs/blob/main/docs/man/git-lfs-pull.adoc)。
- `git lfs ls-files` 列出受 LFS 管理的文件。路径前的 `*` 表示工作目录中已有完整文件，`-` 表示仍是指针；下载完成后，工程资源和插件 DLL 应显示为 `*`。

确认地图、资源和插件文件下载完成后，再打开 `VPRehearsal.uproject`。首次启动会生成本机缓存、编译着色器，需要等待。

### 2. 日常更新与提交

1. 按上面的“多人协作具体操作规范”同步 `main` 和个人分支；拉取、切换分支前先关闭 UE，避免覆盖编辑器正在使用的资源或 DLL。
2. 合并或切换分支后，确认该分支的 LFS 内容已下载。需要补下载时，在工程根目录运行 `git lfs pull`。
3. 文件同步完成后打开 UE 开始工作。普通更新通常会自动下载 LFS 文件，无需重复执行 `git lfs track`。
4. 编辑完成后保存资源，检查 GitHub Desktop 的改动列表，再向个人分支执行 **Commit** 和 **Push origin**。确认 Git 和 LFS 文件上传成功，按上面的流程提交或更新 PR；PR 合并后，其他成员再通过同步 `main` 获取共享改动。

提交前需要检查大文件状态时，可以运行：

```powershell
git lfs status
git lfs ls-files
```

### 3. 本仓库的同步范围

| 内容 | 处理方式 |
| --- | --- |
| `.uasset`、`.umap` 及资源附带的二进制数据 | 通过 LFS 同步 |
| 图片、模型、音视频等素材 | 已配置的文件类型通过 LFS 同步 |
| 插件 DLL 和其他已配置的二进制依赖 | 通过 LFS 同步 |
| `.uproject`、`Config/`、插件源码与配置 | 按普通 Git 文件同步 |
| `Saved/`、`Intermediate/`、`DerivedDataCache/`、调试符号 | 由忽略规则排除，在各成员电脑本地生成 |

具体文件类型以仓库根目录的 [.gitattributes](.gitattributes) 为准。新增尚未覆盖的大文件格式时，应先与维护者确认并更新该文件，再提交相应素材。

项目设置应保存在 `Config/` 下的共享配置中；只写入 `Saved/Config/` 的本机设置不会同步。如果某项设置需要团队共用，应将其写入合适的 `Config/Default*.ini`，并随改动提交。

VibeUE 已作为普通插件目录随工程提供，包括源码、内容、DLL 和 `UnrealEditor.modules`，无需额外初始化 Git 子模块。保留仓库现有的 [.gitignore](.gitignore)、`.gitattributes` 和插件内的忽略规则，避免替换为会排除插件运行文件的通用模板。

### 4. 常见问题

**拉取后资源缺失、地图打不开，或 VibeUE 提示缺少 DLL**

先关闭 UE，在工程根目录运行：

```powershell
git lfs install
git lfs pull
git lfs ls-files
```

如果本应是二进制的文件只有几百字节，内容以 `version https://git-lfs.github.com/spec/v1` 开头，说明拿到的是 LFS 指针，需要下载完整内容。DLL 已完整下载但仍提示版本不匹配时，检查 UE 版本及构建是否与随工程提供的插件一致。

**下载提示权限错误、404、配额不足或对象不存在**

确认 GitHub 登录账号有仓库访问权限，并保留错误信息联系维护者。上传者需要确认对应 LFS 对象已成功上传；存储或流量额度问题需要仓库维护者处理。

**两个人修改了同一张地图、同一个蓝图或序列**

LFS 负责大文件存储，不会自动合并 UE 二进制资源。开始修改同一资源前先协调负责人，尽量按独立关卡、资源和镜头序列分工；出现冲突时由相关成员确认保留的版本。

