<template>
  <div
    class="workbench-shell"
    :data-sidebar-mode="appStore.sidebarMode"
    :data-sidebar-phase="sidebarMotionPhase"
  >
    <aside class="sidebar surface">
      <div class="sidebar__top">
        <div class="brand-block">
          <div class="brand-block__icon">
            <img :src="sidebarLogoUrl" alt="AR" class="brand-block__logo" />
          </div>
          <p class="brand-block__eyebrow">ANNUAL REPORT WORKBENCH</p>
          <h1 class="brand-block__title">年报工作台</h1>
        </div>
      </div>

      <div class="sidebar__nav">
        <section v-for="group in navGroups" :key="group.key" class="nav-group">
          <p class="nav-group__title">{{ group.title }}</p>
          <button
            v-for="item in group.items"
            :key="item.key"
            class="nav-item"
            :class="{ active: appStore.currentPage === item.key }"
            type="button"
            :title="item.label"
            @click="appStore.setPage(item.key)"
          >
            <span class="nav-item__icon">
              <component :is="item.icon" :size="18" />
            </span>
            <span class="nav-item__copy">
              <strong>{{ item.label }}</strong>
            </span>
          </button>
        </section>
      </div>

      <div class="sidebar__bottom">
        <button
          class="nav-item nav-item--utility nav-item--theme"
          :class="{ 'is-switching': appStore.themeTransitioning }"
          type="button"
          :title="themeToggleTitle"
          :aria-busy="appStore.themeTransitioning ? 'true' : 'false'"
          @click="toggleTheme($event)"
        >
          <span class="nav-item__icon nav-item__icon--theme">
            <component :is="appStore.themeMode === 'sunrise' ? MoonStar : Sunrise" :size="18" />
          </span>
          <span class="nav-item__copy">
            <strong>{{ themeToggleLabel }}</strong>
          </span>
        </button>

        <button
          class="nav-item nav-item--utility nav-item--collapse"
          type="button"
          :aria-label="isSidebarExpanded ? '折叠侧边栏' : '展开侧边栏'"
          @click="appStore.toggleSidebar()"
        >
          <span class="nav-item__icon nav-item__icon--collapse">
            <component :is="isSidebarExpanded ? PanelLeftClose : PanelLeftOpen" :size="18" />
          </span>
          <span class="nav-item__copy">
            <strong>折叠侧边栏</strong>
          </span>
        </button>
      </div>
    </aside>

    <div ref="mainPanelRef" class="main-panel" @scroll="handleMainPanelScroll">
      <section
        class="progress-header surface"
        :data-state="taskStore.run.status"
        :data-condensed="shouldCondenseProgress ? 'true' : 'false'"
      >
        <div class="progress-header__top">
          <div class="progress-headline">
            <span class="progress-badge" :data-state="taskStore.run.status">{{ runStatusText }}</span>
            <div class="progress-headline__copy">
              <h2>{{ progressHeadline }}</h2>
              <span>{{ currentStageText }} · {{ progressSubline }}</span>
            </div>
          </div>

          <div class="progress-sidefacts">
            <article>
              <small>运行模式</small>
              <strong>{{ runModeText }}</strong>
            </article>
            <article>
              <small>开始时间</small>
              <strong>{{ formatDateTime(taskStore.run.startedAt, "等待任务启动") }}</strong>
            </article>
            <article>
              <small>已运行</small>
              <strong>{{ elapsedText }}</strong>
            </article>
          </div>
        </div>

        <div class="progress-hero">
          <div class="progress-hero__summary">
            <div class="progress-hero__value">{{ progressPercentText }}</div>
            <div class="progress-hero__caption">总进度</div>
          </div>

          <div class="progress-hero__track">
            <div class="energy-track">
              <div class="energy-track__fill" :style="{ '--progress-fill-scale': progressFillScale.toFixed(4) }">
                <span class="energy-track__glow"></span>
              </div>
            </div>
            <div class="progress-hero__meta">
              <span>{{ runModeText }}</span>
              <span>{{ progressMetricText }}</span>
            </div>
          </div>
        </div>

        <div class="stage-progress-strip">
          <article
            v-for="item in stageProgressCards"
            :key="item.key"
            class="stage-progress-card"
            :class="{ active: item.isCurrent }"
            :data-stage="item.key"
          >
            <div class="stage-progress-card__header">
              <strong>{{ item.label }}</strong>
              <span>{{ item.percentText }}</span>
            </div>
            <div class="stage-progress-card__track">
              <div class="stage-progress-card__fill" :style="{ width: item.percentText }"></div>
            </div>
            <div class="stage-progress-card__footer">
              <span>{{ item.hint }}</span>
              <span>{{ item.metric }}</span>
            </div>
          </article>
        </div>
      </section>

      <main class="content-frame">
        <Transition name="page-swap" mode="out-in">
          <div class="page-swap-shell" :key="appStore.currentPage">
            <component :is="currentPage" />
          </div>
        </Transition>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import {
  FileScan,
  FileText,
  FolderOpen,
  Gauge,
  History,
  Info,
  Link,
  MoonStar,
  PanelLeftClose,
  PanelLeftOpen,
  Sunrise,
  Terminal,
} from "@lucide/vue";
import sidebarLogoUrl from "@/assets/annual_report_spider.png";
import { bridge } from "@/services/bridge";
import { formatDateTime, formatDuration, formatElapsed } from "@/services/datetime";
import { getErrorMessage } from "@/services/errors";
import { mountDesktopEventBus } from "@/services/eventBus";
import { useAppStore } from "@/stores/app";
import { useHistoryStore } from "@/stores/history";
import { useSettingsStore } from "@/stores/settings";
import { useTaskStore } from "@/stores/task";
import type { PageKey, StageName, StageState } from "@/services/types";

const appStore = useAppStore();
const historyStore = useHistoryStore();
const settingsStore = useSettingsStore();
const taskStore = useTaskStore();

const nowTick = ref(Date.now());
const mainPanelRef = ref<HTMLElement | null>(null);
const isProgressCondensed = ref(false);
const sidebarMotionPhase = ref<"idle" | "collapsing" | "expanding">("idle");
const PROGRESS_CONDENSE_SCROLL_TOP = 96;
const PROGRESS_EXPAND_SCROLL_TOP = 12;
const PROGRESS_CONDENSE_LOCK_MS = 420;
const SIDEBAR_MOTION_SETTLE_MS = 320;
let elapsedTimer: number | null = null;
let sidebarResizeFrame: number | null = null;
let sidebarResizeTimers: number[] = [];
let sidebarMotionTimer: number | null = null;
let progressScrollFrame: number | null = null;
let progressCondenseLockUntil = 0;
let progressLastScrollTop = 0;

const pageMap = {
  command: defineAsyncComponent(() => import("@/pages/CommandCenter.vue")),
  workspace: defineAsyncComponent(() => import("@/pages/WorkspacePage.vue")),
  links: defineAsyncComponent(() => import("@/pages/LinksConfigPage.vue")),
  pdf: defineAsyncComponent(() => import("@/pages/PdfConfigPage.vue")),
  extract: defineAsyncComponent(() => import("@/pages/ExtractConfigPage.vue")),
  logs: defineAsyncComponent(() => import("@/pages/LogsPage.vue")),
  history: defineAsyncComponent(() => import("@/pages/HistoryPage.vue")),
  about: defineAsyncComponent(() => import("@/pages/AboutPage.vue")),
};

const navGroups = [
  {
    key: "core",
    title: "核心工作",
    items: [
      { key: "command" as PageKey, label: "任务总览", icon: Gauge },
      { key: "workspace" as PageKey, label: "工作区", icon: FolderOpen },
    ],
  },
  {
    key: "config",
    title: "阶段配置",
    items: [
      { key: "links" as PageKey, label: "链接配置", icon: Link },
      { key: "pdf" as PageKey, label: "PDF 配置", icon: FileText },
      { key: "extract" as PageKey, label: "提取配置", icon: FileScan },
    ],
  },
  {
    key: "system",
    title: "记录与系统",
    items: [
      { key: "logs" as PageKey, label: "日志中心", icon: Terminal },
      { key: "history" as PageKey, label: "历史任务", icon: History },
      { key: "about" as PageKey, label: "关于软件", icon: Info },
    ],
  },
];

const stageMeta: Record<StageName, { label: string }> = {
  links: { label: "链接抓取" },
  pdf: { label: "PDF 下载" },
  extract: { label: "文本提取" },
};

function formatPercent(value: number) {
  const percent = Math.min(100, Math.max(0, Number(value || 0) * 100));
  if (percent === 0 || percent === 100) return `${Math.round(percent)}%`;
  if (percent >= 10) return `${percent.toFixed(1)}%`;
  return `${percent.toFixed(2)}%`;
}

function stageMetric(stage: StageState) {
  const current = Number(stage.progress?.current || 0);
  const total = Number(stage.progress?.total || 0);
  if (total > 0) {
    return `${Math.min(current, total)}/${total}`;
  }
  return formatPercent(Number(stage.progress?.percent || 0));
}

function stageHint(stage: StageState) {
  if (stage.hint) return stage.hint;
  return {
    pending: "等待执行",
    running: "执行中",
    completed: "已完成",
    failed: "执行失败",
    cancelled: "已终止",
  }[stage.status];
}

const currentPage = computed(() => pageMap[appStore.currentPage]);
const isSidebarExpanded = computed(() => appStore.sidebarMode === "expanded");
const hasTerminalProgressState = computed(() => ["completed", "failed", "cancelled"].includes(taskStore.run.status));
const shouldCondenseProgress = computed(() => {
  if (taskStore.run.status === "idle") return false;
  if (hasTerminalProgressState.value) return true;
  if (!isProgressCondensed.value) return false;
  return ["running", "paused", "cancelling"].includes(taskStore.run.status);
});

const runStatusText = computed(
  () =>
    ({
      idle: "空闲",
      running: "运行中",
      paused: "已暂停",
      completed: "已完成",
      failed: "失败",
      cancelling: "终止中",
      cancelled: "已终止",
    })[taskStore.run.status],
);

const activeStage = computed(() => {
  const currentStage = taskStore.run.currentStage;
  return currentStage ? taskStore.stages[currentStage] : null;
});

const currentStageText = computed(() => {
  const currentStage = taskStore.run.currentStage;
  if (currentStage) {
    return `当前阶段：${stageMeta[currentStage].label}`;
  }
  if (taskStore.run.status === "paused") return "当前阶段：任务暂停中";
  if (taskStore.run.status === "completed") return "当前阶段：全部完成";
  if (taskStore.run.status === "failed") return "当前阶段：执行失败";
  if (taskStore.run.status === "cancelled") return "当前阶段：任务已终止";
  return "当前阶段：等待开始";
});

const runModeText = computed(
  () =>
    ({
      links: "仅抓链接",
      pdf: "仅下载 PDF",
      extract: "仅提取文本",
      pipeline: "完整流程",
      null: "未启动",
    })[String(taskStore.run.mode)],
);

const elapsedText = computed(() => {
  if (!taskStore.run.startedAt) return "00:00";
  if (taskStore.run.finishedAt) {
    return formatDuration(taskStore.run.startedAt, taskStore.run.finishedAt, "00:00");
  }
  return formatElapsed(taskStore.run.startedAt, "00:00");
});

const progressFraction = computed(() => Number(taskStore.currentTaskProgress || 0));
const progressFillScale = computed(() => Math.min(1, Math.max(0, progressFraction.value)));
const progressPercentText = computed(() => formatPercent(progressFraction.value));

const progressHeadline = computed(() => {
  if (taskStore.run.status === "running") return "任务正在执行";
  if (taskStore.run.status === "paused") return "任务已暂停";
  if (taskStore.run.status === "completed") return "任务执行完成";
  if (taskStore.run.status === "failed") return "任务执行失败";
  if (taskStore.run.status === "cancelling") return "正在终止任务";
  if (taskStore.run.status === "cancelled") return "任务已终止";
  return "准备开始新任务";
});

const progressSubline = computed(() => {
  if (taskStore.run.status === "idle") return "配置完成后即可启动。";
  if (taskStore.run.error) return taskStore.run.error;
  return activeStage.value?.hint || "等待阶段信息更新。";
});

const progressMetricText = computed(() => {
  const stage = activeStage.value;
  if (!stage) return "暂无进度";
  return stageMetric(stage);
});

const stageProgressCards = computed(() =>
  (Object.values(taskStore.stages) as StageState[]).map((stage) => ({
    key: stage.name,
    label: stageMeta[stage.name].label,
    percentText: formatPercent(Number(stage.progress?.percent || 0)),
    hint: stageHint(stage),
    metric: stageMetric(stage),
    isCurrent: taskStore.run.currentStage === stage.name,
  })),
);

const themeToggleLabel = computed(() => (appStore.themeMode === "sunrise" ? "切换深夜" : "切换日出"));
const themeToggleTitle = computed(() => (appStore.themeMode === "sunrise" ? "切换到深夜模式" : "切换到日出模式"));

function toggleTheme(event: MouseEvent) {
  const sourceElement = event.currentTarget instanceof HTMLElement ? event.currentTarget : null;
  appStore.setTheme(appStore.themeMode === "sunrise" ? "midnight" : "sunrise", sourceElement);
}

function syncProgressCondensedState() {
  const top = mainPanelRef.value?.scrollTop || 0;
  const now = typeof performance !== "undefined" ? performance.now() : Date.now();
  const previousTop = progressLastScrollTop;
  const scrollingDown = top > previousTop + 2;
  const scrollingUp = top < previousTop - 2;
  progressLastScrollTop = top;

  const status = taskStore.run.status;
  if (status === "idle") {
    isProgressCondensed.value = false;
    progressCondenseLockUntil = 0;
    return;
  }
  if (hasTerminalProgressState.value) {
    isProgressCondensed.value = true;
    progressCondenseLockUntil = now + PROGRESS_CONDENSE_LOCK_MS;
    return;
  }
  if (now < progressCondenseLockUntil) return;

  const shouldCondenseNow = top >= PROGRESS_CONDENSE_SCROLL_TOP && scrollingDown;
  const shouldExpandNow = top <= PROGRESS_EXPAND_SCROLL_TOP && scrollingUp;

  if (!isProgressCondensed.value && shouldCondenseNow) {
    isProgressCondensed.value = true;
    progressCondenseLockUntil = now + PROGRESS_CONDENSE_LOCK_MS;
    return;
  }

  if (isProgressCondensed.value && shouldExpandNow) {
    isProgressCondensed.value = false;
    progressCondenseLockUntil = now + PROGRESS_CONDENSE_LOCK_MS;
    return;
  }
}

function handleMainPanelScroll() {
  if (progressScrollFrame !== null || typeof window === "undefined") return;
  progressScrollFrame = window.requestAnimationFrame(() => {
    syncProgressCondensedState();
    progressScrollFrame = null;
  });
}

function emitLayoutResize() {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new Event("resize"));
}

function clearSidebarResizeTasks() {
  if (sidebarResizeFrame !== null) {
    window.cancelAnimationFrame(sidebarResizeFrame);
    sidebarResizeFrame = null;
  }
  if (sidebarResizeTimers.length) {
    sidebarResizeTimers.forEach((timer) => window.clearTimeout(timer));
    sidebarResizeTimers = [];
  }
}

function clearSidebarMotionTask() {
  if (sidebarMotionTimer !== null) {
    window.clearTimeout(sidebarMotionTimer);
    sidebarMotionTimer = null;
  }
}

function startSidebarMotionPhase(mode: "expanded" | "collapsed") {
  if (typeof window === "undefined") return;
  clearSidebarMotionTask();
  sidebarMotionPhase.value = mode === "collapsed" ? "collapsing" : "expanding";
  sidebarMotionTimer = window.setTimeout(() => {
    sidebarMotionPhase.value = "idle";
    sidebarMotionTimer = null;
  }, SIDEBAR_MOTION_SETTLE_MS);
}

function scheduleSidebarResize() {
  if (typeof window === "undefined") return;
  clearSidebarResizeTasks();
  nextTick(() => {
    emitLayoutResize();
    sidebarResizeFrame = window.requestAnimationFrame(() => {
      emitLayoutResize();
      sidebarResizeFrame = null;
    });
    sidebarResizeTimers = [460].map((delay) =>
      window.setTimeout(() => {
        emitLayoutResize();
      }, delay),
    );
  });
}

watch(
  () => [taskStore.run.startedAt, taskStore.run.finishedAt] as const,
  ([startedAt, finishedAt]) => {
    if (elapsedTimer !== null) {
      window.clearInterval(elapsedTimer);
      elapsedTimer = null;
    }
    if (startedAt && !finishedAt) {
      elapsedTimer = window.setInterval(() => {
        nowTick.value = Date.now();
      }, 1000);
    } else {
      nowTick.value = Date.now();
    }
  },
  { immediate: true },
);

watch(
  () => taskStore.run.status,
  (status) => {
    if (["running", "paused", "cancelling"].includes(status)) {
      historyStore.startAutoRefresh();
      return;
    }
    historyStore.stopAutoRefresh();
    historyStore.load().catch(() => {});
  },
  { immediate: true },
);

watch(
  () => appStore.sidebarMode,
  (mode) => {
    startSidebarMotionPhase(mode);
    scheduleSidebarResize();
  },
);

watch(
  () => taskStore.run.status,
  (status, previousStatus) => {
    const enteringActiveRun = ["running", "paused", "cancelling"].includes(status)
      && !["running", "paused", "cancelling"].includes(String(previousStatus || ""));
    if (enteringActiveRun) {
      const top = mainPanelRef.value?.scrollTop || 0;
      progressLastScrollTop = top;
      if (top <= PROGRESS_EXPAND_SCROLL_TOP) {
        isProgressCondensed.value = false;
        progressCondenseLockUntil = 0;
      }
    }
    syncProgressCondensedState();
  },
  { immediate: true },
);

onMounted(async () => {
  appStore.hydrateUiPrefs();
  taskStore.loadNotificationPrefs();

  const originalHandleEvent = taskStore.handleEvent.bind(taskStore);
  taskStore.handleEvent = ((event: any) => {
    if (event?.event === "app.close_requested") {
      void appStore.showConfirm({
        title: "确认关闭当前窗口",
        message: ["running", "paused", "cancelling"].includes(String(event?.data?.status || "idle"))
          ? "检测到当前仍有任务正在运行或暂停。关闭窗口后，已完成进度会保留，但当前执行步骤会被中断。"
          : "当前没有正在执行的任务，确认后将直接关闭窗口。",
        type: "warning",
        confirmText: "确认关闭",
        cancelText: "取消",
      }).then(async () => {
        try {
          await bridge.confirmCloseWindow();
        } catch (error) {
          appStore.showAlert(getErrorMessage(error, "关闭窗口失败"), "error");
        }
      }).catch(() => {
        bridge.cancelCloseWindowRequest().catch(() => {});
      });
      return;
    }
    originalHandleEvent(event);
  }) as typeof taskStore.handleEvent;

  try {
    await bridge.waitUntilReady();
    mountDesktopEventBus(taskStore);
    await Promise.all([
      appStore.loadAbout().catch(() => {}),
      settingsStore.load().catch((error) => {
        appStore.showAlert(getErrorMessage(error, "配置加载失败"), "error");
      }),
      taskStore.hydrateActiveRun().catch((error) => {
        appStore.showAlert(getErrorMessage(error, "任务状态加载失败"), "error");
      }),
      taskStore.loadVisualizationIndex().catch(() => {}),
      historyStore.load().catch((error) => {
        appStore.showAlert(getErrorMessage(error, "历史记录加载失败"), "error");
      }),
      appStore.autoCheckUpdate().catch(() => {}),
    ]);
    appStore.bridgeReady = true;
    await nextTick();
    progressLastScrollTop = mainPanelRef.value?.scrollTop || 0;
    syncProgressCondensedState();
  } catch (error) {
    appStore.bridgeReady = false;
    appStore.showAlert(getErrorMessage(error, "桥接初始化失败"), "error");
  }
});

onBeforeUnmount(() => {
  historyStore.stopAutoRefresh();
  clearSidebarResizeTasks();
  clearSidebarMotionTask();
  if (progressScrollFrame !== null) {
    window.cancelAnimationFrame(progressScrollFrame);
    progressScrollFrame = null;
  }
  progressCondenseLockUntil = 0;
  if (elapsedTimer !== null) {
    window.clearInterval(elapsedTimer);
    elapsedTimer = null;
  }
});
</script>
