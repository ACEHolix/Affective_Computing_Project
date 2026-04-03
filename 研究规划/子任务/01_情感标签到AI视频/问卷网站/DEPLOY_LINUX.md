# Linux 部署与运维留痕

日期：2026-04-01

## 当前已部署实例

当前问卷网站已经部署到以下 Linux 机器并可访问：

- 主机：`100.81.1.116`
- 用户：`tuoxiaoying`
- 访问地址：
  - `http://100.81.1.116`
  - `http://100.81.1.116/survey`
  - `http://100.81.1.116/admin`
  - `http://100.81.1.116:3000`
  - `http://100.81.1.116:3000/survey`

当前远端部署目录：

- `/home/tuoxiaoying/deploy/subtask01-survey`

当前用户级服务名：

- `subtask01-survey.service`

当前 nginx 已配置反向代理：

- `80` 端口 -> `127.0.0.1:3000`

提交结果保存目录：

- `/home/tuoxiaoying/deploy/subtask01-survey/data/submissions/`

## 一、首次部署步骤

### 1. 本地同步代码到远端

```bash
rsync -av --delete \
  --exclude node_modules \
  --exclude .next \
  --exclude data/submissions \
  '/Users/tuoxiaoying/Documents/Work/Repostories/Affective_Computing_Review/研究规划/子任务/01_情感标签到AI视频/问卷网站/' \
  'tuoxiaoying@100.81.1.116:~/deploy/subtask01-survey/'
```

### 2. 在远端安装依赖并构建

说明：

- 远端 `node` 和 `npm` 由 `nvm` 管理
- 当前使用的 Node 路径是：
  - `/home/tuoxiaoying/.nvm/versions/node/v24.12.0/bin`

执行命令：

```bash
ssh -tt tuoxiaoying@100.81.1.116 '
  export PATH=/home/tuoxiaoying/.nvm/versions/node/v24.12.0/bin:$PATH &&
  cd ~/deploy/subtask01-survey &&
  npm install &&
  npm run build
'
```

### 3. 创建用户级 systemd 服务

服务文件路径：

- `~/.config/systemd/user/subtask01-survey.service`

服务内容：

```ini
[Unit]
Description=Subtask01 Survey Site
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/tuoxiaoying/deploy/subtask01-survey
Environment=NODE_ENV=production
Environment=PORT=3000
Environment=PATH=/home/tuoxiaoying/.nvm/versions/node/v24.12.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/home/tuoxiaoying/.nvm/versions/node/v24.12.0/bin/npm run start
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

### 4. 启用并启动服务

```bash
ssh -tt tuoxiaoying@100.81.1.116 '
  mkdir -p ~/.config/systemd/user ~/deploy/subtask01-survey/data/submissions &&
  systemctl --user daemon-reload &&
  systemctl --user enable subtask01-survey &&
  systemctl --user start subtask01-survey
'
```

## 二、日常运维命令

### 查看服务状态

```bash
ssh tuoxiaoying@100.81.1.116 'systemctl --user status subtask01-survey --no-pager'
```

### 查看 nginx 状态

```bash
ssh tuoxiaoying@100.81.1.116 'sudo systemctl status nginx --no-pager'
```

### 重启服务

```bash
ssh tuoxiaoying@100.81.1.116 'systemctl --user restart subtask01-survey'
```

### 停止服务

```bash
ssh tuoxiaoying@100.81.1.116 'systemctl --user stop subtask01-survey'
```

### 查看实时日志

```bash
ssh -tt tuoxiaoying@100.81.1.116 'journalctl --user -u subtask01-survey -f'
```

## 三、更新部署步骤

如果本地代码有修改，推荐按下面顺序更新：

### 1. 重新同步代码

```bash
rsync -av --delete \
  --exclude node_modules \
  --exclude .next \
  --exclude data/submissions \
  '/Users/tuoxiaoying/Documents/Work/Repostories/Affective_Computing_Review/研究规划/子任务/01_情感标签到AI视频/问卷网站/' \
  'tuoxiaoying@100.81.1.116:~/deploy/subtask01-survey/'
```

### 2. 远端重新安装依赖、重新构建、重启服务

```bash
ssh -tt tuoxiaoying@100.81.1.116 '
  export PATH=/home/tuoxiaoying/.nvm/versions/node/v24.12.0/bin:$PATH &&
  cd ~/deploy/subtask01-survey &&
  npm install &&
  npm run build &&
  systemctl --user restart subtask01-survey
'
```

## 四、健康检查

### 检查首页是否可访问

```bash
curl -I http://100.81.1.116
```

```bash
curl -I http://100.81.1.116:3000
```

### 检查问卷页是否可访问

```bash
curl -I http://100.81.1.116/survey
```

```bash
curl -I http://100.81.1.116:3000/survey
```

### 检查管理员页是否可访问

```bash
curl -I http://100.81.1.116/admin
```

### 检查转换接口是否可用

```bash
ssh tuoxiaoying@100.81.1.116 "curl -s http://127.0.0.1:3000/api/transform \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{\"answers\":{\"preferred_scene_types\":[\"seaside\"],\"preferred_narrative_themes\":[\"reunion\"],\"preferred_visual_styles\":[\"cinematic\"],\"preferred_color_lighting\":[\"warm\"],\"preferred_audio_elements\":[\"piano\"],\"self_relevant_scenes\":[\"home\"],\"high_intensity_themes\":[\"companionship\"],\"autobiographical_cues\":[\"rain_sound\"],\"emotion_induction_mode\":\"build_up\",\"negative_phase_preference\":\"low_arousal_negative\",\"max_emotion_intensity\":4}}'"
```

## 五、提交结果保存位置

用户提交问卷后，服务端会自动把完整数据写到：

- `/home/tuoxiaoying/deploy/subtask01-survey/data/submissions/`

其中包含：

- 原始答卷 `answers`
- 转换后的 `profile`
- `generationInputs`
- `promptPackage`

### 查看提交结果

```bash
ssh tuoxiaoying@100.81.1.116 'ls -lah ~/deploy/subtask01-survey/data/submissions'
```

### 下载提交结果到本地

```bash
rsync -av 'tuoxiaoying@100.81.1.116:~/deploy/subtask01-survey/data/submissions/' \
  '/Users/tuoxiaoying/Downloads/subtask01-submissions/'
```

## 六、当前远端环境信息

当前远端 Node 和 npm 版本：

- `node`: `v24.12.0`
- `npm`: `11.6.2`

当前路径：

- `node`: `/home/tuoxiaoying/.nvm/versions/node/v24.12.0/bin/node`
- `npm`: `/home/tuoxiaoying/.nvm/versions/node/v24.12.0/bin/npm`

## 七、常见问题

### 1. 远端提示 `npm: command not found`

原因：

- 非交互 shell 没有加载 `nvm`

解决方法：

- 在 SSH 命令前显式设置：

```bash
export PATH=/home/tuoxiaoying/.nvm/versions/node/v24.12.0/bin:$PATH
```

### 2. `/api/submit` 写文件失败

检查：

- `~/deploy/subtask01-survey/data/submissions/` 是否存在
- 当前用户是否有写权限

修复：

```bash
ssh tuoxiaoying@100.81.1.116 'mkdir -p ~/deploy/subtask01-survey/data/submissions'
```

### 3. 改完代码访问还是旧页面

可能原因：

- 没有重新 `build`
- 没有重启服务

标准修复：

```bash
ssh -tt tuoxiaoying@100.81.1.116 '
  export PATH=/home/tuoxiaoying/.nvm/versions/node/v24.12.0/bin:$PATH &&
  cd ~/deploy/subtask01-survey &&
  npm run build &&
  systemctl --user restart subtask01-survey
'
```

## 八、下一步可选增强

当前部署已经满足持续运行。

后续可继续做：

1. 配置域名
2. 为管理员页增加访问控制
3. 增加管理员页面中的筛选、搜索、导出
4. 把 `data/submissions` 改成数据库
