<template>
  <section class="editor-page" v-if="settings">
    <header class="editor-head surface">
      <div class="editor-copy">
        <p class="section-kicker">工作区</p>
        <h2>路径与年份范围</h2>
        <p>集中配置项目路径、输出目录和抓取年份范围，适合在批量运行前做一次快速检查。</p>
      </div>
      <button class="save-button" @click="saveWorkspace()" :disabled="settingsStore.saving">
        {{ settingsStore.saving ? "保存中..." : "保存工作区" }}
      </button>
    </header>

    <div class="config-grid">
      <section class="surface editor-card core-card">
        <header class="section-header">
          <div>
            <p class="section-kicker">路径</p>
            <h3>核心目录</h3>
          </div>
        </header>

        <div class="form-grid">
          <PathField
            label="项目根目录"
            v-model="settings.workspace.projectRoot"
            openable
            selectable
            @open="open(settings.workspace.projectRoot)"
            @select="pickDirectory('projectRoot')"
            @update:model-value="setProjectRoot"
            @blur="syncProjectRootDefaultsOnBlur"
          />
          <PathField
            label="年报输出目录"
            v-model="settings.workspace.annualReportDir"
            openable
            selectable
            @open="openResolved(settings.workspace.annualReportDir)"
            @select="pickDirectory('annualReportDir')"
            @update:model-value="settingsStore.touch()"
          />
          <PathField
            label="文本输出目录"
            v-model="settings.workspace.textOutputDir"
            openable
            selectable
            @open="openResolved(settings.workspace.textOutputDir)"
            @select="pickDirectory('textOutputDir')"
            @update:model-value="settingsStore.touch()"
          />
          <PathField
            label="状态目录"
            v-model="settings.workspace.stateDir"
            openable
            selectable
            @open="openResolved(settings.workspace.stateDir)"
            @select="pickDirectory('stateDir')"
            @update:model-value="settingsStore.touch()"
          />
        </div>
      </section>

      <section class="surface side-panel">
        <section class="editor-card range-card">
          <header class="section-header side-panel__header">
            <div>
              <p class="section-kicker">年份范围</p>
              <h3>抓取窗口</h3>
            </div>
          </header>

          <div class="range-grid">
            <label class="field">
              <span>开始年份</span>
              <input type="number" v-model.number="settings.workspace.startYear" @input="settingsStore.touch()" />
            </label>
            <label class="field">
              <span>结束年份</span>
              <input type="number" v-model.number="settings.workspace.endYear" @input="settingsStore.touch()" />
            </label>
          </div>

          <div class="range-band">
            <div class="range-band__line"></div>
            <div class="range-band__marker">
              <strong>{{ settings.workspace.startYear }}</strong>
              <span>开始</span>
            </div>
            <div class="range-band__marker">
              <strong>{{ settings.workspace.endYear }}</strong>
              <span>结束</span>
            </div>
          </div>
        </section>

        <section class="editor-card notify-card">
          <header class="section-header side-panel__header">
            <div>
              <p class="section-kicker">通知</p>
              <h3>任务完成提醒</h3>
            </div>
          </header>

          <div class="notify-stack">
            <label class="notify-item">
              <input
                type="checkbox"
                :checked="taskStore.notificationPrefs.desktopEnabled"
                @change="toggleDesktopNotify(($event.target as HTMLInputElement).checked)"
              />
              <div>
                <strong>系统通知</strong>
                <p>任务完成、失败或终止时弹出系统消息。</p>
              </div>
            </label>

            <label class="notify-item">
              <input
                type="checkbox"
                :checked="taskStore.notificationPrefs.soundEnabled"
                @change="toggleSoundNotify(($event.target as HTMLInputElement).checked)"
              />
              <div>
                <strong>提示音</strong>
                <p>任务结束时播放提示音，可与系统通知分开控制。</p>
              </div>
            </label>
          </div>

          <div class="notify-foot">
            <p class="notify-status">通知权限：{{ notifyPermissionText }}</p>
            <div class="notify-actions">
              <button class="ghost-button" @click="testSound">测试提示音</button>
            </div>
          </div>
        </section>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import PathField from "@/components/PathField.vue";
import { bridge } from "@/services/bridge";
import { getErrorMessage } from "@/services/errors";
import { useAppStore } from "@/stores/app";
import { useSettingsStore } from "@/stores/settings";
import { useTaskStore } from "@/stores/task";

const appStore = useAppStore();
const settingsStore = useSettingsStore();
const taskStore = useTaskStore();
const settings = computed(() => settingsStore.data);

const notifyPermissionText = computed(() => ({
  granted: "已授权",
  denied: "已拒绝",
  default: "未请求",
  unsupported: "当前环境不支持",
}[taskStore.notificationPrefs.permission]));

function open(path: string) {
  bridge.openPath(path);
}

function toWindowsPath(path: string) {
  return path.replace(/\//g, "\\").replace(/\\{2,}/g, "\\").trim();
}

function joinWindowsPath(root: string, child: string) {
  const normalizedRoot = toWindowsPath(root).replace(/[\\\/]+$/, "");
  if (!normalizedRoot) return child;
  return `${normalizedRoot}\\${child}`;
}

function applyProjectRootDefaults(projectRoot: string, options?: { announce?: boolean }) {
  if (!settings.value) return;
  const normalizedRoot = toWindowsPath(projectRoot);
  settings.value.workspace.projectRoot = normalizedRoot;
  settings.value.workspace.annualReportDir = joinWindowsPath(normalizedRoot, "annual_reports");
  settings.value.workspace.textOutputDir = joinWindowsPath(normalizedRoot, "txt_extract");
  settings.value.workspace.stateDir = normalizedRoot;
  settingsStore.touch();
  if (options?.announce && normalizedRoot) {
    appStore.showAlert("已按项目根目录自动填充年报目录、文本目录和状态目录。", "info", "工作区联动");
  }
}

function setProjectRoot(value: string) {
  if (!settings.value) return;
  settings.value.workspace.projectRoot = toWindowsPath(value);
  settingsStore.touch();
}

function syncProjectRootDefaultsOnBlur() {
  if (!settings.value) return;
  applyProjectRootDefaults(settings.value.workspace.projectRoot);
}

function resolvePath(raw: string) {
  const value = (raw || "").trim();
  if (!settings.value) return value;
  if (!value) return settings.value.workspace.projectRoot;
  if (/^[a-zA-Z]:[\\/]/.test(value) || value.startsWith("\\\\") || value.startsWith("/")) {
    return value;
  }
  return `${settings.value.workspace.projectRoot}/${value}`.replace(/\\/g, "/");
}

function openResolved(path: string) {
  bridge.openPath(resolvePath(path));
}

async function pickDirectory(field: "projectRoot" | "annualReportDir" | "textOutputDir" | "stateDir") {
  if (!settings.value) return;
  const current = settings.value.workspace[field];
  const selected = await bridge.selectDirectory(resolvePath(current));
  if (!selected.path) return;
  if (field === "projectRoot") {
    applyProjectRootDefaults(selected.path, { announce: true });
    return;
  }
  settings.value.workspace[field] = selected.path;
  settingsStore.touch();
}

async function saveWorkspace() {
  if (!settings.value) return;
  await settingsStore.save();
  if (taskStore.isBusy) {
    appStore.showAlert("工作区已保存。当前任务运行中，首页图表会在任务结束后自动刷新。", "warning", "工作区切换");
    return;
  }
  try {
    await taskStore.reloadVisualizationForSettings(settings.value);
    appStore.showAlert("首页图表已切换为当前工作区对应的数据。", "success", "工作区切换");
  } catch (error) {
    appStore.showAlert(getErrorMessage(error, "刷新首页图表失败"), "warning");
  }
}

async function toggleDesktopNotify(enabled: boolean) {
  try {
    await taskStore.updateNotificationPrefs({ desktopEnabled: enabled });
    if (enabled && taskStore.notificationPrefs.desktopEnabled) {
      appStore.showAlert("系统通知已开启。", "success");
      return;
    }
    if (enabled && !taskStore.notificationPrefs.desktopEnabled) {
      appStore.showAlert("系统通知未开启：请先授权通知权限。", "warning");
      return;
    }
    appStore.showAlert("系统通知已关闭。", "info");
  } catch (error) {
    appStore.showAlert(getErrorMessage(error, "更新系统通知设置失败"), "error");
  }
}

async function toggleSoundNotify(enabled: boolean) {
  try {
    await taskStore.updateNotificationPrefs({ soundEnabled: enabled });
    appStore.showAlert(enabled ? "提示音已开启。" : "提示音已关闭。", "info");
  } catch (error) {
    appStore.showAlert(getErrorMessage(error, "更新提示音设置失败"), "error");
  }
}

function testSound() {
  taskStore.playCompletionSound();
}
</script>

<style scoped>
.editor-page { --config-grid-columns: minmax(0, 1.18fr) minmax(280px, 0.82fr); }
.editor-card { display: grid; gap: 12px; }
.form-grid { display: grid; gap: 12px; margin-top: -8px; }
.core-card { gap: 6px; align-content: start; }
.core-card .section-header { margin-bottom: -6px; }
.core-card .form-grid { margin-top: 0; }
.side-panel { display: grid; gap: 14px; align-content: start; padding: 16px 18px; }
.side-panel__header { margin-bottom: -2px; }
.range-card {
  padding: 16px 18px;
  border-radius: var(--radius-2xl);
  border: 1px solid var(--line-strong);
  background: linear-gradient(180deg, var(--surface-strong), var(--surface-muted));
  box-shadow: inset 0 0 0 1px var(--surface-outline);
}
.range-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.range-band { position: relative; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; padding-top: 16px; }
.range-band__line { position: absolute; top: 0; left: 0; right: 0; height: var(--track-height-sm); border-radius: var(--radius-pill); background: linear-gradient(90deg, #1d4ed8, #0f766e); }
.range-band__marker {
  padding: 12px 14px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  background: var(--field-bg-soft);
}
.range-band__marker strong { display: block; font-size: var(--type-metric-md); margin-bottom: 2px; }
.range-band__marker span { color: var(--muted); letter-spacing: 0.16em; font-size: var(--type-caption); }
.notify-card {
  align-content: start;
  gap: 10px;
  padding: 14px 16px;
  border-radius: var(--radius-2xl);
  border: 1px solid var(--line);
  background: var(--surface-muted);
}
.notify-stack { display: grid; gap: 10px; }
.notify-item { display: grid; grid-template-columns: 18px 1fr; gap: 10px; align-items: start; padding: 12px 14px; border-radius: var(--radius-lg); border: 1px solid var(--line); background: var(--field-bg-soft); }
.notify-item input { margin-top: 3px; }
.notify-item strong { display: block; margin-bottom: 3px; font-size: var(--type-strong); }
.notify-item p { margin: 0; color: var(--muted); font-size: var(--type-body-small); line-height: 1.5; }
.notify-foot { display: flex; justify-content: space-between; gap: 12px; align-items: center; flex-wrap: wrap; }
.notify-status { margin: 0; color: var(--muted); font-size: var(--type-body-small); }
.notify-actions { display: flex; }

.side-panel :deep(.section-header h3) {
  font-size: var(--type-section-title);
}

.side-panel .range-card + .notify-card {
  margin-top: 2px;
}

@media (max-width: 1180px) {
  .range-grid {
    grid-template-columns: 1fr;
  }

  .notify-foot {
    align-items: flex-start;
  }
}
</style>
