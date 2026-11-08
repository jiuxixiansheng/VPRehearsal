# VP 预演操作说明

更新日期：2026-11-08

本文记录项目当前已搭建的方案与操作方法。打开项目使用本目录中的 `VPRehearsal.uproject`，日常预演打开 `/Game/Developers/CLY/Levels/VP_Main`。

## 1. 当前方案

目前使用 **一个 UE 进程、一个 World、主关卡加载两个子关卡**。虚拟内容在远处渲染，画面通过 nDisplay 的预览共享组件显示到摄影棚环屏上。

| 关卡 | 用途 | 主要对象 |
| --- | --- | --- |
| `VP_Main` | 摄影棚主关卡 | 棚体、棚内灯、黄色实景前景方块 |
| `VP_Ndisplay` | 摄影棚设备子关卡 | 环屏 `BJ_nDisplayConfig`、操控用的 `CineCameraActor` |
| `VP_TestContent` | 虚拟内容子关卡 | 红绿蓝方块、内容地面、环境照明、`VP_ContentRenderOrigin` |

以上地图均在 `/Game/Developers/CLY/Levels/` 中。新增 UE 资产统一放在 `/Game/Developers/CLY/` 下；本文按要求放在项目根目录，便于查阅。

**当前的空间隔离仍然保留**：`VP_TestContent` 中的 15 个内容对象已统一挂在空 Actor `VP_ContentRoot` 下。根节点 Location 为 `(100000, 0, 0)` cm，统一承担 1 km 偏移；子对象使用相对坐标，例如近景左方块 X 为 `1200`，内容渲染原点 X 为 `-290`。世界位置保持不变。这里使用 Actor 父子层级，不是子关卡整体变换。

在 Outliner 选择 `VP_ContentRoot`，修改它的 Location 即可统一移动内容、照明和渲染原点。当前根组件为 Static，适合编辑器内调整；运行时动态移动不在此次实现范围内。建议只调整平移，保持旋转为 0、缩放为 1。

`VP_TestContent` 仍会出现在主地图的 Levels 列表中。这套方案没有创建第二个独立 World，也没有编写新的原生插件。完全分离 World 的改造已按要求搁置。

## 2. 打开摄影棚与操控摄影机

1. 打开 `VP_Main`，等待两个子关卡和环屏预览加载。
2. 在 Outliner 中搜索 `CineCameraActor`，选中摄影棚里的原始电影摄影机。
3. 使用移动、旋转工具调整机位，或在 Details 中修改 Transform。
4. 在摄影机组件中调整 `Current Focal Length` 等镜头参数。
5. 如需从摄影机视角查看构图，可右键该 Actor，使用 Pilot／驾驶功能；结束后退出驾驶。

操控对象是摄影棚中的 `CineCameraActor`。后台的 `VP_ContentRenderOrigin` 和它的内部 `CAM1` 用于内容渲染，不作为日常机位操作对象。

摄影机已增加简易机身与镜头网格，属于原始摄影机 Actor，会随它移动。按 `G` 切换游戏视图时，UE 自带的编辑器摄影机图标可能消失，新增的可渲染机身仍可显示；从摄影机自身视角观察时，机身会隐藏。

如果自由透视视口发生倾斜，先退出 Pilot，并检查当前视角的 Roll。自由视口的倾斜与电影摄影机 Actor 的旋转是两件事，不要为了修正编辑视角而误改实际拍摄机位。

## 3. 环屏上的内容从哪里来

当前使用 UE 自带的 `DisplayClusterPreviewShare`，主要设置如下：

| 对象／设置 | 当前配置 | 作用 |
| --- | --- | --- |
| 摄影棚环屏的预览共享组件 | `Pull Actor` | 从后台 nDisplay 内容原点取得渲染配置和场景来源 |
| `Source NDisplay Actor` | `VP_ContentRenderOrigin` | 指向内容区域的 nDisplay 根 Actor |
| ICVFX 摄影机同步 | `Push Actor` | 将摄影棚摄影机状态推送给内容区域摄影机 |
| 摄影棚 `CAM1` 的外部摄影机引用 | 原始 `CineCameraActor` | 以摄影棚摄影机作为内视锥的操作来源 |

后台原点复制了原来的屏幕投影配置，并关闭自己的屏幕预览。摄影棚环屏使用后台内容区域生成的画面进行预览。

摄影机同步依据两套 nDisplay 根节点的相对变换计算：摄影棚里的机位变化会映射到后台内容区域，同时同步旋转、Filmback 和焦距。因此两套摄影机即使相隔约 1 km，也能保持对应的拍摄关系。

两套 `CAM1` 的 `Camera Settings > Border > Enable` 都已关闭。内视锥继续工作，只是不显示红色调试边框。

## 4. 编辑虚拟内容场景

可以直接单独打开 `VP_TestContent` 搭建虚拟场景。

1. 打开 `/Game/Developers/CLY/Levels/VP_TestContent`。
2. 在 Outliner 中选择 `VP_Content_EditView`，按 `F` 定位，或右键 Pilot 进入编辑视角。
3. 在现有测试方块和内容原点附近搭景。新对象要保存在 `VP_TestContent` 中，并在 Outliner 中挂到 `VP_ContentRoot` 下，再按相对坐标布置；新建对象不会自动成为根节点的子对象。世界空间中的内容仍在约 1 km 外，子对象的相对坐标已经不含这段偏移。
4. 新增内容网格使用 `Lighting Channel 1`，关闭默认的 Channel 0，以沿用现有内容直接光照分组。
5. 参考现有测试网格设置 `Desired Max Draw Distance = 15000 cm`，并关闭 `Never Distance Cull`；保存后返回 `VP_Main` 检查屏幕与摄影棚视角。

也可以在 `VP_Main` 中打开 Levels 面板，将 `VP_TestContent` 设为当前关卡，再选择现有内容方块按 `F` 到达内容区域。新增 Actor 前确认当前关卡，避免把虚拟内容误存到摄影棚关卡。

红、绿、蓝方块分别用于测试近、中、远景的透视、视差和机位同步，不代表摄影棚中的实景美术。`VP_Content_EditView` 仅用于编辑定位，不会驱动摄影棚电影摄影机。

**距离剔除需要逐个检查新增网格**：新 Actor 不会自动继承现有方块的设置。当前方案也不能保证大型地形、天空和所有类型的对象都通过相同设置隔离；新增这些内容后要在摄影棚视角检查。

## 5. 添加摄影棚实景美术

黄色方块 `VP_Studio_ForegroundCube` 是已放置的实景前景示例。它应当出现在摄影棚里，并能与屏幕内容一起进入电影摄影机的构图，但不应成为屏幕画面的一部分。

新增实景时：

1. 在 `VP_Main` 中将 `VP_Main` 设为当前关卡。
2. 在摄影棚内部放置实景 Actor。
3. 实景网格使用 `Lighting Channel 0`，沿用棚内灯光分组。
4. 分别检查摄影棚 `BJ_nDisplayConfig` 和后台 `VP_ContentRenderOrigin`，把新增实景 Actor 加入各自配置的 `Stage Settings > Content Hidden from Entire Cluster` 隐藏列表。
5. 保存相关关卡，检查实景在摄影棚可见、在 LED 屏的内外视锥内容中不可见。

这里的隐藏列表只用于排除 nDisplay 内容渲染。不要用 Actor 的全局隐藏代替，否则摄影棚里也会看不到实景。

现有摄影机、实景方块和棚体已加入相关排除列表。新增实景不会自动进入列表，需要手动维护。

## 6. 单独打开内容地图时的照明

`VP_TestContent` 自己保存了太阳、天空光、SkyAtmosphere、雾、云和天空球。单独打开它时，这些 Actor 仍然存在；回到 `VP_Main` 加载它时，也使用同一套灯光资产和参数。

摄影棚使用封闭墙体、顶棚和四盏局部矩形灯，每盏当前为 1000 lm。棚内物体和灯使用 Channel 0，内容太阳与内容网格使用 Channel 1。

Lighting Channels 用于区分受支持的直接光照，并不隔离全部天空、雾和间接光。两部分仍处在同一个 World，环境效果仍可能互相影响。动态天空更新、曝光与渲染历史也可能造成预览差异，因此“一致预览”指保留同一组环境与灯光配置，不保证画面逐像素一致。

## 7. 保存与检查

- 操作摄影机后，保存它所在的 `VP_Ndisplay`。
- 修改棚体、棚灯或实景后，保存 `VP_Main`。
- 修改虚拟内容、环境灯或后台原点后，保存 `VP_TestContent`。
- 修改 `VP_ContentRoot` 后，也保存 `VP_TestContent`。如果单独编辑时临时把根节点 X 改为 0，返回主地图预演前应恢复为 100000 cm，避免内容与摄影棚重叠。
- 修改跨关卡引用或 nDisplay 隐藏列表后，保存涉及的关卡。
- 不要把后台原点移回摄影棚附近，也不要直接删除内容子关卡引用，否则会破坏当前空间隔离或画面来源。

完成修改后，建议检查：环屏有画面；移动摄影棚摄影机后屏幕透视跟随变化；调整焦距后内视锥跟随变化；实景前景在摄影棚可见且不进入屏幕内容；红色调试边框保持关闭。

## 8. 当前完成范围

此前已在编辑器模拟中验证：后台内容显示到环屏、摄影机相对位置与焦距同步、摄影机机身运行时可见、测试实景被屏幕渲染排除，以及内视锥红框关闭。

内容地图也做过独立加载检查，确认环境 Actor 属于内容地图，且未加载摄影棚 Actor。该检查不是独立地图的画面一致性渲染测试。

**VR 头显内的实际显示、手柄抓取摄影机和镜头控制尚未实现或验证。** 当前文档描述的是已有场景与编辑器预演操作，不代表完整 VR 交互已经完成。

更详细的原有实现记录位于 `Content/Developers/CLY/VPPrevis/README.md`，相关验证记录位于同目录的 `Validation/`。
