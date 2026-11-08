# VP 预演：当前结构与操作

所有新增关卡和资产均放在 `/Game/Developers/CLY` 下。

## 关卡职责

| 关卡 | 内容 |
| --- | --- |
| `Levels/VP_Main` | 摄影棚主关卡、封闭棚体、四盏棚内矩形灯、黄色实景前景方块 `VP_Studio_ForegroundCube` |
| `Levels/VP_Ndisplay` | 摄影棚环屏 `BJ_nDisplayConfig`、供操控的 `CineCameraActor` |
| `Levels/VP_TestContent` | 后台虚拟内容、红绿蓝测试方块、内容地面、完整环境灯光、`VP_ContentRenderOrigin` 和编辑视角 `VP_Content_EditView` |

`VP_Main` 加载两个子关卡。当前是同一 UE World 内的空间隔离方案，不是两个独立进程，也不是两个完全隔离的 World。太阳、天空光、SkyAtmosphere、雾、云和天空球现在全部归属于 `VP_TestContent`，因此单独打开内容地图也有同一套环境照明。天空等仍具有 World 全局作用域；棚内靠封闭墙体和顶棚遮挡外部环境，并使用局部灯照明。

## 两套照明

- 内容太阳和内容网格使用 Lighting Channel 1；棚内网格、实景和四盏局部矩形灯使用 Channel 0。通道用于区分直接光照，不代表全局天空和所有间接光完全隔离。
- 四盏 `VP_Studio_Overhead_01` 至 `04` 为可移动矩形灯，当前每盏 1000 lm，仅照亮棚内附近区域。
- 棚体为四面墙和顶棚，沿用舞台地面。棚体和摄影机、实景一起被排除在 nDisplay 内容渲染之外。
- 内容地图单独打开和作为子关卡加载时使用同一组灯光资产与参数。动态云、天空光更新和渲染历史可能造成短暂画面差异，不保证不同时间截取的画面逐像素相同。

## 画面如何送到环屏

1. 内容区域通过空 Actor `VP_ContentRoot` 统一沿世界 X 轴平移 100000 cm（1 km），与摄影棚分开。内容关卡的 15 个对象均附加到该根节点，子对象使用不含 1 km 偏移的相对坐标，原有世界位置保持不变。内容原点 `VP_ContentRenderOrigin` 复制了舞台的屏幕投影配置，自己的屏幕预览关闭。
2. 摄影棚环屏上的 `DisplayClusterPreviewShare` 组件使用 `Pull Actor`，来源指定为 `VP_ContentRenderOrigin`。环屏预览据此使用内容区域的渲染原点和配置生成画面。
3. 同一组件的 ICVFX 摄影机同步使用 `Push Actor`：将摄影棚 `CAM1` 实际引用的 `CineCameraActor` 的相对位置、旋转、Filmback 和焦距同步到内容区域的 `CAM1`。同步按两套原点的相对变换计算。
4. 近、中、远的内容方块分别为红、绿、蓝。它们和内容地面设置了 15000 cm（150 m）的距离剔除：棚内观察时看不到远处实体，内容摄影机在附近渲染时能看到它们。后续新增内容也要检查距离剔除或遮挡，不能只依靠放进子关卡实现可见性隔离。

## 摄影棚里的实景与摄影机

- 黄色 `VP_Studio_ForegroundCube` 是实景美术，实际放在摄影棚内；红绿蓝方块是虚拟内容，只通过环屏呈现。
- 实景方块和 `CineCameraActor` 已加入两套 nDisplay 配置的 `Stage Settings > Content Hidden from Entire Cluster`（Hide List）。这会同时排除内外视锥中的这些物体，不会全局隐藏它们。
- 摄影机新增 `VP_CameraBody` 和 `VP_CameraLens` 两个可渲染组件，因此在运行时也有可见的简易外形。这两个组件属于原来的 `CineCameraActor`，会跟随它移动，并设置为摄影机自身视点不可见。
- 两套 `CAM1` 的 `Camera Settings > Border > Enable` 均已关闭；内视锥仍然工作，只是不再显示调试红框。

## 如何操作

1. 打开 `VP_Main`。在 Outliner 搜索并选中 `CineCameraActor`，修改它的 Transform、焦距等；不要直接操控后台内容原点或后台 `CAM1`。
2. 编辑摄影棚实景时，把 `VP_Main` 设为当前关卡。新增实景物体后，将其加入两套 nDisplay 配置的整簇隐藏列表，避免被渲染到屏幕。
3. 可以直接打开 `VP_TestContent` 编辑虚拟场景：在 Outliner 选择 `VP_Content_EditView`，按 F 定位，或右键 Pilot 进入它的视角。它仅供编辑，不会驱动棚内摄影机。也可以在主地图把 `VP_TestContent` 设为当前关卡，选择一个 `VPTest_` 方块按 F 到达内容区域。
4. 在内容原点附近布置新内容，并将新增对象保存在 `VP_TestContent`、附加到 `VP_ContentRoot` 下，以相对坐标布置。新增内容网格的 Lighting Channels 使用 Channel 1，Max Draw Distance 建议先沿用 15000 cm，并确认不是 Never Distance Cull。整体平移只需修改根节点 Location；当前根组件为 Static，用于编辑器调整，保持旋转为 0、缩放为 1。若单独编辑时临时将根节点 X 改为 0，返回主地图预演前恢复为 100000 cm。这是 Actor 层级方案，不是子关卡整体变换。
5. `G` 切换编辑器游戏视图。它会隐藏编辑器图标和 UE 自带的摄影机代理模型；新增的可渲染机身不依赖这些图标。

概念上，LED 屏输出只包含后台虚拟内容；棚内摄影机看到的构图则可以同时包含黄色实景前景和 LED 屏上的虚拟内容。

## 已验证与尚未完成

已在模拟运行中验证：后台内容画面正常显示、摄影机相对位置和焦距同步、摄影机机身运行时可见、实景方块被整簇隐藏列表排除、红框关闭。

另以独立的无界面 UE 检查进程打开了 `VP_TestContent`，验证仅加载该地图、六个环境 Actor 完整存在、未加载摄影棚 Actor。结果见 `Validation/standalone-content-result.json`。该检查验证独立加载和资源归属，不是离线画面渲染测试。检查进程还报告了项目既有的 GameFeatureData 资产扫描配置错误，因此命令行退出码为 1；内容地图的检查脚本本身通过。

头显内的实际显示、VR 手柄抓取摄影机和镜头控制尚未实现或验证。
