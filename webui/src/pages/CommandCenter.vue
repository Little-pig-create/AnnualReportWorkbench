<template>
  <section class="console-page">
    <header class="console-head surface">
      <div class="console-head__copy">
        <p class="section-kicker">任务面板</p>
        <h2>任务控制台</h2>
        <p>运行中实时展示阶段进度、年份统计图表与日志，同时尽量避免影响 PDF 下载和文本提取速度。</p>
      </div>

      <div class="console-head__actions">
        <button
          :class="['action', 'action--links', { 'action--active': activeRunMode === 'links', 'action--active-main': activeRunMode === 'links' }]"
          title="抓取公告入口"
          @click="start('links')"
          :disabled="taskStore.isBusy"
        >
          <span class="action__icon"><Link2 :size="16" /></span>
          <span class="action__content">
            <span class="action__label">仅抓链接</span>
            <span class="action__hint">抓取公告入口</span>
          </span>
        </button>
        <button
          :class="['action', 'action--pdf', { 'action--active': activeRunMode === 'pdf', 'action--active-main': activeRunMode === 'pdf' }]"
          title="批量下载 PDF 文件"
          @click="start('pdf')"
          :disabled="taskStore.isBusy"
        >
          <span class="action__icon"><Download :size="16" /></span>
          <span class="action__content">
            <span class="action__label">仅下 PDF</span>
            <span class="action__hint">批量下载文件</span>
          </span>
        </button>
        <button
          :class="['action', 'action--extract', { 'action--active': activeRunMode === 'extract', 'action--active-main': activeRunMode === 'extract' }]"
          title="提取正文内容"
          @click="start('extract')"
          :disabled="taskStore.isBusy"
        >
          <span class="action__icon"><FileText :size="16" /></span>
          <span class="action__content">
            <span class="action__label">仅提文本</span>
            <span class="action__hint">提取正文内容</span>
          </span>
        </button>
        <button
          :class="['action', 'action--pipeline', { 'action--active': activeRunMode === 'pipeline', 'action--active-main': activeRunMode === 'pipeline' }]"
          title="执行完整流程"
          @click="start('pipeline')"
          :disabled="taskStore.isBusy"
        >
          <span class="action__icon"><Play :size="16" /></span>
          <span class="action__content">
            <span class="action__label">执行全流程</span>
            <span class="action__hint">链接 / 下载 / 提取</span>
          </span>
        </button>
        <button
          :class="['action', 'action--pause', { 'action--active': actionControlsHighlighted, 'action--active-control': actionControlsHighlighted }]"
          :title="taskStore.isResumable ? '从当前进度恢复任务' : '临时暂停当前处理'"
          @click="togglePause"
          :disabled="!taskStore.isPausable && !taskStore.isResumable"
        >
          <span class="action__icon">
            <component :is="taskStore.isResumable ? Play : Pause" :size="16" />
          </span>
          <span class="action__content">
            <span class="action__label">{{ taskStore.isResumable ? "继续任务" : "暂停任务" }}</span>
            <span class="action__hint">{{ taskStore.isResumable ? "从当前进度恢复" : "临时停止处理" }}</span>
          </span>
        </button>
        <button
          :class="['action', 'action--terminate', { 'action--active': actionControlsHighlighted, 'action--active-control': actionControlsHighlighted }]"
          title="结束当前运行"
          @click="terminateRun"
          :disabled="!taskStore.isBusy"
        >
          <span class="action__icon"><Square :size="15" /></span>
          <span class="action__content">
            <span class="action__label">终止任务</span>
            <span class="action__hint">结束当前运行</span>
          </span>
        </button>
      </div>
    </header>

    <div class="console-grid">
      <section class="surface overview-stack">
        <div class="focus-panel">
          <div class="focus-panel__gauge">
            <div class="gauge-card">
              <BaseChart :option="progressGaugeOption" />
            </div>
          </div>

          <div class="focus-panel__meta">
              <article>
                <small>运行模式</small>
                <strong>{{ modeLabel }}</strong>
              </article>
              <article>
                <small>进度口径</small>
                <strong>{{ progressLogicLabel }}</strong>
              </article>
            <article>
              <small>开始时间</small>
              <strong>{{ formatDateTime(taskStore.run.startedAt, "等待任务启动") }}</strong>
            </article>
            <article>
              <small>输出目录</small>
              <strong>{{ outputDirLabel }}</strong>
            </article>
          </div>
        </div>

        <section class="overview-stack__logs">
          <header class="section-header">
            <div>
              <p class="section-kicker">日志</p>
              <h3>最近日志</h3>
            </div>
            <button class="mini-link" @click="appStore.setPage('logs')">打开日志中心</button>
          </header>
          <LogConsole :items="taskStore.recentLogs" />
        </section>
      </section>

      <section class="surface status-wall">
        <header class="section-header">
          <div>
            <p class="section-kicker">阶段</p>
            <h3>阶段状态</h3>
          </div>
          <span class="mono">{{ runStatusText }}</span>
        </header>
        <div class="stage-stack">
          <StageCard :stage="taskStore.stages.links" />
          <StageCard :stage="taskStore.stages.pdf" />
          <StageCard :stage="taskStore.stages.extract" />
        </div>
      </section>
    </div>

    <section class="surface live-strip">
      <header class="section-header">
        <div>
          <p class="section-kicker">实时抓取</p>
          <h3>公告链接抓取实时进度</h3>
        </div>
        <span class="mono">{{ liveCrawlLabel }}</span>
      </header>

      <div class="live-layout">
        <article class="live-chart-card">
          <BaseChart :option="liveYearOption" />
        </article>

        <div class="live-grid">
          <article class="live-card live-card--accent">
            <small>当前年份</small>
            <strong>{{ taskStore.liveCrawl?.currentYear ?? "-" }}</strong>
            <span>{{ yearStepLabel }}</span>
          </article>

          <article class="live-card">
            <small>当前区间</small>
            <strong>{{ taskStore.liveCrawl?.currentWindow || "-" }}</strong>
            <span>{{ windowStepLabel }}</span>
          </article>

          <article class="live-card">
            <small>公告数量</small>
            <strong>{{ resolvedLiveTotal }}</strong>
            <span>运行中按当前任务实时结果展示</span>
          </article>

          <article class="live-card">
            <small>当前年份数量</small>
            <strong>{{ currentYearCount }}</strong>
            <span>当前年份累计数量</span>
          </article>
        </div>
      </div>
    </section>

    <div v-if="taskStore.hasVisualizationData" class="metrics-grid">
      <article class="surface chart-card chart-card--pdf">
        <header class="section-header section-header--chart">
          <div>
            <p class="section-kicker">PDF</p>
            <h3>PDF 下载实时进度</h3>
          </div>
          <div class="chart-header-right">
            <div class="view-switch">
              <button :class="{ active: pdfView === 'stacked' }" @click="pdfView = 'stacked'">堆叠柱状</button>
              <button :class="{ active: pdfView === 'trend' }" @click="pdfView = 'trend'">趋势曲线</button>
            </div>
            <div class="chart-header-meta">
              <span class="speed-badge speed-badge--pdf">{{ pdfSpeedLabel }}</span>
              <span class="chart-caption">{{ pdfView === "stacked" ? "按年份分布 · 堆叠统计" : "按年份趋势 · 完成量与目标量" }}</span>
            </div>
          </div>
        </header>
        <div class="summary-grid">
          <article class="summary-card summary-card--strong">
            <small>总量</small>
            <strong>{{ pdfSummary.total }}</strong>
            <span>本阶段目标总数</span>
          </article>
          <article class="summary-card">
            <small>已完成</small>
            <strong>{{ pdfSummary.completed }}</strong>
            <span>{{ pdfSummary.percentText }}</span>
          </article>
          <article class="summary-card">
            <small>当前高亮年份</small>
            <strong>{{ pdfSummary.activeYearText }}</strong>
            <span>{{ pdfSummary.activeYearSubtext }}</span>
          </article>
          <article class="summary-card">
            <small>失败 / 跳过</small>
            <strong>{{ pdfSummary.failedSkipped }}</strong>
            <span>异常与跳过合计</span>
          </article>
        </div>
        <div class="chart-card__viewport">
          <BaseChart :option="pdfOption" />
        </div>
      </article>

      <article class="surface chart-card chart-card--extract">
        <header class="section-header section-header--chart">
          <div>
            <p class="section-kicker">提取</p>
            <h3>文本提取实时进度</h3>
          </div>
          <div class="chart-header-right">
            <div class="view-switch">
              <button :class="{ active: extractView === 'stacked' }" @click="extractView = 'stacked'">堆叠柱状</button>
              <button :class="{ active: extractView === 'trend' }" @click="extractView = 'trend'">趋势曲线</button>
            </div>
            <div class="chart-header-meta">
              <span class="speed-badge speed-badge--extract">{{ extractSpeedLabel }}</span>
              <span class="chart-caption">{{ extractView === "stacked" ? "按年份分布 · 堆叠统计" : "按年份趋势 · 完成量与目标量" }}</span>
            </div>
          </div>
        </header>
        <div class="summary-grid">
          <article class="summary-card summary-card--strong">
            <small>总量</small>
            <strong>{{ extractSummary.total }}</strong>
            <span>本阶段目标总数</span>
          </article>
          <article class="summary-card">
            <small>已完成</small>
            <strong>{{ extractSummary.completed }}</strong>
            <span>{{ extractSummary.percentText }}</span>
          </article>
          <article class="summary-card">
            <small>当前高亮年份</small>
            <strong>{{ extractSummary.activeYearText }}</strong>
            <span>{{ extractSummary.activeYearSubtext }}</span>
          </article>
          <article class="summary-card">
            <small>失败数量</small>
            <strong>{{ extractSummary.failed }}</strong>
            <span>提取异常总数</span>
          </article>
        </div>
        <div class="chart-card__viewport">
          <BaseChart :option="extractOption" />
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { Download, FileText, Link2, Pause, Play, Square } from "@lucide/vue";
import { computed, onBeforeUnmount, ref, watch } from "vue";
import BaseChart from "@/components/BaseChart.vue";
import LogConsole from "@/components/LogConsole.vue";
import StageCard from "@/components/StageCard.vue";
import { formatDateTime } from "@/services/datetime";
import { getErrorMessage } from "@/services/errors";
import { useAppStore } from "@/stores/app";
import { useSettingsStore } from "@/stores/settings";
import { useTaskStore } from "@/stores/task";
import type { RunMode } from "@/services/types";

const taskStore = useTaskStore();
const appStore = useAppStore();
const settingsStore = useSettingsStore();
const displayedProgress = ref(0);
const pdfView = ref<"stacked" | "trend">("stacked");
const extractView = ref<"stacked" | "trend">("stacked");
let animationFrameId = 0;

function formatFixed(value: number, digits = 2) {
  return Number(value || 0).toFixed(digits);
}

function formatPercent(value: number) {
  return `${formatFixed(value * 100)}%`;
}

const progressPercentText = computed(() => formatPercent(displayedProgress.value));
const chartPalette = computed(() => (
  appStore.themeMode === "midnight"
    ? {
        gaugeTrack: "#243244",
        gaugePrimary: "#60a5fa",
        gaugeAxis: "#8ca3bd",
        gaugeDetail: "#e5eef9",
        teal: "#2dd4bf",
        tealLight: "#67e8f9",
        blue: "#60a5fa",
        blueLight: "#93c5fd",
        red: "#fb7185",
        redLight: "#fda4af",
        orange: "#f59e0b",
        orangeLight: "#fdba74",
        grid: "rgba(148, 163, 184, 0.14)",
        axis: "#8ca3bd",
        text: "#dbeafe",
        tooltipBg: "rgba(8, 13, 23, 0.96)",
        tooltipBorder: "rgba(96, 165, 250, 0.18)",
        tooltipShadow: "0 18px 42px rgba(2, 6, 23, 0.52)",
        axisLine: "rgba(148, 163, 184, 0.28)",
        axisPointer: "rgba(148, 163, 184, 0.08)",
        linePointBorder: "#08111c",
        liveShadow: "rgba(45, 212, 191, 0.24)",
        neutralTop: "#64748b",
        neutralBottom: "#94a3b8",
      }
    : {
        gaugeTrack: "#e5e7eb",
        gaugePrimary: "#597ef7",
        gaugeAxis: "#6b7280",
        gaugeDetail: "#374151",
        teal: "#15847a",
        tealLight: "#3fb7ab",
        blue: "#3c6df0",
        blueLight: "#6b93ff",
        red: "#ef4444",
        redLight: "#fb7185",
        orange: "#f59e0b",
        orangeLight: "#fbbf24",
        grid: "rgba(148, 163, 184, 0.18)",
        axis: "#64748b",
        text: "#334155",
        tooltipBg: "rgba(255, 255, 255, 0.96)",
        tooltipBorder: "rgba(148, 163, 184, 0.2)",
        tooltipShadow: "0 16px 40px rgba(15, 23, 42, 0.14)",
        axisLine: "rgba(148, 163, 184, 0.35)",
        axisPointer: "rgba(15, 23, 42, 0.04)",
        linePointBorder: "#ffffff",
        liveShadow: "rgba(21, 132, 122, 0.18)",
        neutralTop: "#c5d2e6",
        neutralBottom: "#94a3b8",
      }
));

const progressGaugeOption = computed(() => {
  const palette = chartPalette.value;
  return {
  backgroundColor: "transparent",
  tooltip: {
    formatter: "{a} <br/>{b} : {c}%",
  },
  series: [
    {
      name: "Progress",
      type: "gauge",
      min: 0,
      max: 100,
      startAngle: 225,
      endAngle: -45,
      progress: {
        show: true,
        width: 9,
        roundCap: false,
      },
      axisLine: {
        lineStyle: {
          width: 9,
          color: [[1, palette.gaugeTrack]],
        },
      },
      radius: "78%",
      center: ["50%", "54%"],
      pointer: {
        show: true,
        length: "42%",
        width: 4,
        itemStyle: {
          color: palette.gaugePrimary,
        },
      },
      anchor: {
        show: false,
      },
      itemStyle: {
        color: palette.gaugePrimary,
      },
      axisTick: {
        show: true,
        splitNumber: 5,
        distance: -10,
        length: 6,
        lineStyle: {
          color: palette.gaugeAxis,
          width: 1,
        },
      },
      splitLine: {
        show: true,
        distance: -12,
        length: 12,
        lineStyle: {
          color: palette.gaugeAxis,
          width: 1.6,
        },
      },
      axisLabel: {
        distance: -28,
        color: palette.gaugeAxis,
        fontSize: 12,
        fontWeight: 500,
      },
      title: {
        show: true,
        offsetCenter: [0, "38%"],
        fontSize: 14,
        fontWeight: 500,
        color: palette.gaugeAxis,
      },
      detail: {
        valueAnimation: true,
        offsetCenter: [0, "66%"],
        fontSize: 26,
        fontWeight: 700,
        color: palette.gaugeDetail,
        formatter: (value: number) => `${formatFixed(value)}%`,
      },
      data: [
        {
          value: Number(formatFixed(displayedProgress.value * 100)),
          name: "进度",
        },
      ],
    },
  ],
  };
});

function gradientColor(top: string, bottom: string) {
  return {
    type: "linear",
    x: 0,
    y: 0,
    x2: 0,
    y2: 1,
    colorStops: [
      { offset: 0, color: top },
      { offset: 1, color: bottom },
    ],
  };
}

function makeTooltipFormatter(mode: "live" | "pdf" | "extract") {
  const palette = chartPalette.value;
  return (params: any[]) => {
    const items = Array.isArray(params) ? params : [params];
    if (!items.length) return "";
    const title = items[0]?.axisValueLabel || items[0]?.name || "";
    const lines = items
      .filter((item) => Number(item?.value || 0) > 0 || mode === "live")
      .map((item) => {
        const marker = `<span style="display:inline-block;width:10px;height:10px;border-radius:999px;background:${item.color};margin-right:8px;"></span>`;
        return `${marker}${item.seriesName}：<b>${Number(item.value || 0)}</b>`;
      });
    return `
      <div style="min-width:160px">
        <div style="margin-bottom:8px;font-weight:700;color:${palette.text};">${title}</div>
        ${lines.join("<br/>")}
      </div>
    `;
  };
}

function baseBarOption(categories: string[]) {
  const palette = chartPalette.value;
  return {
    backgroundColor: "transparent",
    animationDurationUpdate: 240,
    animationEasingUpdate: "cubicOut",
    legend: {
      bottom: 0,
      itemWidth: 14,
      itemHeight: 14,
      icon: "roundRect",
      textStyle: {
        color: palette.axis,
        fontSize: 13,
        fontWeight: 600,
      },
    },
    grid: {
      left: 26,
      right: 10,
      top: 26,
      bottom: 52,
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: categories,
      axisLabel: {
        color: palette.axis,
        fontSize: 12,
        margin: 12,
      },
      axisLine: {
        lineStyle: {
          color: palette.axisLine,
        },
      },
      axisTick: {
        show: false,
      },
    },
    yAxis: {
      type: "value",
      axisLabel: {
        color: palette.axis,
        fontSize: 12,
        margin: 12,
      },
      axisLine: {
        show: false,
      },
      axisTick: {
        show: false,
      },
      splitLine: {
        lineStyle: {
          color: palette.grid,
          type: "dashed",
        },
      },
    },
  };
}

function findActiveBucket(buckets: any[]) {
  return buckets.find((item: any) => item?.active) || null;
}

function compactValueLabel(position: "inside" | "insideTop" | "top" = "insideTop") {
  const palette = chartPalette.value;
  return {
    show: true,
    position,
    color: position === "top" ? palette.text : palette.linePointBorder,
    fontSize: 11,
    fontWeight: 700,
    distance: 6,
    formatter: ({ value }: any) => (Number(value || 0) > 0 ? String(value) : ""),
  };
}

function filterBucketsByConfiguredYears<T extends { year?: number | string }>(buckets: T[]) {
  const startYear = Number(
    settingsStore.data?.workspace.startYear ?? taskStore.visualizationIndex?.meta?.startYear ?? NaN,
  );
  const endYear = Number(
    settingsStore.data?.workspace.endYear ?? taskStore.visualizationIndex?.meta?.endYear ?? NaN,
  );
  if (!Number.isFinite(startYear) || !Number.isFinite(endYear) || startYear > endYear) {
    return buckets;
  }
  return buckets.filter((item) => {
    const year = Number(item?.year);
    return Number.isFinite(year) && year >= startYear && year <= endYear;
  });
}

async function start(mode: RunMode) {
  const modeText = {
    links: "公告链接抓取",
    pdf: "PDF 下载",
    extract: "文本提取",
    pipeline: "完整流程",
  }[mode];
  appStore.showAlert(`已提交${modeText}任务，正在启动...`, "info", "任务通知");
  try {
    await taskStore.startRun(mode);
    appStore.showAlert(`${modeText}任务已启动`, "success", "任务通知");
  } catch (error) {
    appStore.showAlert(getErrorMessage(error, "启动任务失败"), "error");
  }
}

async function togglePause() {
  try {
    if (taskStore.isResumable) {
      await taskStore.resumeRun();
      appStore.showAlert("任务已继续", "success");
      return;
    }
    if (taskStore.isPausable) {
      await taskStore.pauseRun();
      appStore.showAlert("任务已暂停", "info");
    }
  } catch (error) {
    appStore.showAlert(getErrorMessage(error, "操作失败"), "error");
  }
}

async function terminateRun() {
  try {
    await taskStore.cancelRun();
    appStore.showAlert("任务终止中", "info");
  } catch (error) {
    appStore.showAlert(getErrorMessage(error, "终止任务失败"), "error");
  }
}

const runStatusText = computed(() => ({
  idle: "空闲",
  running: "运行中",
  paused: "已暂停",
  completed: "已完成",
  failed: "失败",
  cancelling: "终止中",
  cancelled: "已终止",
}[taskStore.run.status]));

const activeRunMode = computed<RunMode | null>(() => (
  ["running", "paused", "cancelling"].includes(taskStore.run.status)
    ? taskStore.run.mode || null
    : null
));

const actionControlsHighlighted = computed(() => (
  taskStore.run.status === "running" || taskStore.run.status === "paused"
));

const modeLabel = computed(() => ({
  links: "公告链接抓取",
  pdf: "PDF 下载",
  extract: "文本提取",
  pipeline: "完整流程",
  null: "尚未启动",
}[String(taskStore.run.mode)]));

const progressLogicLabel = computed(() => {
  if (!taskStore.run.mode) return "等待任务启动";
  if (taskStore.run.mode === "pipeline") {
    return "按当前执行阶段计算";
  }
  return "按当前单任务计算";
});

const outputDirLabel = computed(() => {
  const outputs = taskStore.run.outputs || {};
  if (taskStore.run.mode === "extract") return outputs.textOutputDir || "-";
  if (taskStore.run.mode === "pipeline") return outputs.textOutputDir || outputs.annualReportDir || "-";
  return outputs.annualReportDir || "-";
});

const resolvedLiveYearBuckets = computed(() => filterBucketsByConfiguredYears(taskStore.liveYearBuckets || []));
const resolvedLiveTotal = computed(() =>
  resolvedLiveYearBuckets.value.reduce((sum: number, item: any) => sum + Number(item.count || item.total || 0), 0),
);
const livePdfBuckets = computed(() => filterBucketsByConfiguredYears(taskStore.livePdf?.yearBuckets || []));
const liveExtractBuckets = computed(() => filterBucketsByConfiguredYears(taskStore.liveExtract?.yearBuckets || []));

const liveCrawlLabel = computed(() => {
  if (taskStore.run.status === "paused") return "任务已暂停";
  if (taskStore.run.currentStage !== "links" && taskStore.run.status !== "completed") {
    return "链接阶段空闲";
  }
  if (!taskStore.liveCrawl) return "等待实时数据";
  return formatPercent(Number(taskStore.liveCrawl.overallPercent || 0));
});

const yearStepLabel = computed(() => {
  if (!taskStore.liveCrawl) return "等待实时数据";
  return `第 ${taskStore.liveCrawl.currentYearIndex || 0} / ${taskStore.liveCrawl.yearTotal || 0} 年`;
});

const windowStepLabel = computed(() => {
  if (!taskStore.liveCrawl) return "等待区间信息";
  return `${taskStore.liveCrawl.rangeCurrent || 0} / ${taskStore.liveCrawl.rangeTotal || 0}`;
});

const currentYearCount = computed(() => {
  const currentYear = taskStore.liveCrawl?.currentYear;
  if (!currentYear) return 0;
  const bucket = resolvedLiveYearBuckets.value.find((item: any) => Number(item.year) === Number(currentYear));
  return Number(bucket?.count || 0);
});

const pdfSpeedLabel = computed(() => {
  const speed = Number(taskStore.livePdf?.speedPerMinute || 0);
  const eta = Number(taskStore.livePdf?.etaSeconds || 0);
  const speedText = speed > 0 ? `${formatFixed(speed)} 份/分钟` : "速度统计中";
  const etaText = eta > 0 ? `，预计剩余 ${formatFixed(eta)} 秒` : "";
  return `${speedText}${etaText}`;
});

const extractSpeedLabel = computed(() => {
  const speed = Number(taskStore.liveExtract?.speedPerMinute || 0);
  const eta = Number(taskStore.liveExtract?.etaSeconds || 0);
  const speedText = speed > 0 ? `${formatFixed(speed)} 份/分钟` : "速度统计中";
  const etaText = eta > 0 ? `，预计剩余 ${formatFixed(eta)} 秒` : "";
  return `${speedText}${etaText}`;
});

const pdfSummary = computed(() => {
  const buckets = livePdfBuckets.value;
  const active = findActiveBucket(buckets);
  const total = buckets.reduce((sum: number, item: any) => sum + Number(item.total || 0), 0);
  const completed = buckets.reduce((sum: number, item: any) => sum + Number(item.completed || 0), 0);
  const failed = buckets.reduce((sum: number, item: any) => sum + Number(item.failed || 0), 0);
  const skipped = buckets.reduce((sum: number, item: any) => sum + Number(item.skipped || 0), 0);
  const percent = total > 0 ? (completed / total) * 100 : 0;
  return {
    total,
    completed,
    failedSkipped: `${failed + skipped}`,
    percentText: total > 0 ? `${formatFixed(percent)}% 已完成` : "等待数据",
    activeYearText: active ? String(active.year) : "-",
    activeYearSubtext: active ? `该年已完成 ${active.completed || 0} / ${active.total || 0}` : "暂无高亮年份",
  };
});

const extractSummary = computed(() => {
  const buckets = liveExtractBuckets.value;
  const active = findActiveBucket(buckets);
  const total = buckets.reduce((sum: number, item: any) => sum + Number(item.total || 0), 0);
  const completed = buckets.reduce((sum: number, item: any) => sum + Number(item.completed || 0), 0);
  const failed = buckets.reduce((sum: number, item: any) => sum + Number(item.failed || 0), 0);
  const percent = total > 0 ? (completed / total) * 100 : 0;
  return {
    total,
    completed,
    failed,
    percentText: total > 0 ? `${formatFixed(percent)}% 已完成` : "等待数据",
    activeYearText: active ? String(active.year) : "-",
    activeYearSubtext: active ? `该年已完成 ${active.completed || 0} / ${active.total || 0}` : "暂无高亮年份",
  };
});

const liveYearOption = computed(() => {
  const palette = chartPalette.value;
  const categories = resolvedLiveYearBuckets.value.map((item: any) => String(item.year));
  return {
    ...baseBarOption(categories),
    tooltip: {
      trigger: "axis",
      backgroundColor: palette.tooltipBg,
      borderColor: palette.tooltipBorder,
      borderWidth: 1,
      textStyle: { color: palette.text },
      extraCssText: `box-shadow: ${palette.tooltipShadow}; border-radius: var(--radius-md);`,
      formatter: makeTooltipFormatter("live"),
    },
    legend: { show: false },
    series: [{
      name: "公告数",
      type: "bar",
      barWidth: 28,
      showBackground: true,
      backgroundStyle: {
        color: "rgba(148, 163, 184, 0.08)",
        borderRadius: [14, 14, 0, 0],
      },
      label: {
        show: true,
        position: "top",
        color: palette.text,
        fontSize: 12,
        fontWeight: 700,
        formatter: ({ value }: any) => (Number(value || 0) > 0 ? String(value) : ""),
      },
      itemStyle: {
        borderRadius: [14, 14, 4, 4],
        shadowBlur: 18,
        shadowColor: palette.liveShadow,
      },
      data: resolvedLiveYearBuckets.value.map((item: any) => ({
        value: Number(item.count || 0),
        itemStyle: {
          color: item.active
            ? gradientColor("#1f9d8f", "#0f766e")
            : item.status === "completed"
              ? gradientColor("#4f7ef7", "#2d5bdb")
              : gradientColor(palette.neutralTop, palette.neutralBottom),
        },
      })),
    }],
  };
});

const pdfOption = computed(() => {
  const palette = chartPalette.value;
  const categories = livePdfBuckets.value.map((item: any) => String(item.year));
  const activeYear = findActiveBucket(livePdfBuckets.value)?.year;
  const completedLine = livePdfBuckets.value.map((item: any) => Number(item.completed || 0));
  const totalLine = livePdfBuckets.value.map((item: any) => Number(item.total || 0));

  if (pdfView.value === "trend") {
    return {
      ...baseBarOption(categories),
      tooltip: {
        trigger: "axis",
        backgroundColor: palette.tooltipBg,
        borderColor: palette.tooltipBorder,
        borderWidth: 1,
        textStyle: { color: palette.text },
        extraCssText: `box-shadow: ${palette.tooltipShadow}; border-radius: var(--radius-md);`,
        formatter: makeTooltipFormatter("pdf"),
      },
      series: [
        {
          name: "目标量",
          type: "line",
          smooth: true,
          symbol: "circle",
          symbolSize: 7,
          lineStyle: { width: 2, type: "dashed", color: palette.blue },
          itemStyle: { color: palette.blue },
          data: totalLine,
        },
        {
          name: "已完成",
          type: "line",
          smooth: true,
          symbol: "circle",
          symbolSize: 9,
          areaStyle: {
            color: gradientColor("rgba(63,183,171,0.28)", "rgba(63,183,171,0.02)"),
          },
          lineStyle: { width: 3, color: palette.teal },
          itemStyle: { color: palette.teal, borderColor: palette.linePointBorder, borderWidth: 2 },
          data: completedLine.map((value, index) => ({
            value,
            itemStyle: Number(categories[index]) === Number(activeYear) ? {
              shadowBlur: 18,
              shadowColor: "rgba(21,132,122,0.35)",
            } : undefined,
          })),
        },
      ],
    };
  }

  return {
      ...baseBarOption(categories),
      tooltip: {
        trigger: "axis",
      axisPointer: { type: "shadow", shadowStyle: { color: palette.axisPointer } },
      backgroundColor: palette.tooltipBg,
      borderColor: palette.tooltipBorder,
      borderWidth: 1,
      textStyle: { color: palette.text },
      extraCssText: `box-shadow: ${palette.tooltipShadow}; border-radius: var(--radius-md);`,
      formatter: makeTooltipFormatter("pdf"),
    },
    series: [
      {
        name: "已完成（下载+已存在）",
        type: "bar",
        stack: "pdf",
        barWidth: 24,
        itemStyle: {
          color: gradientColor(palette.tealLight, palette.teal),
          borderRadius: [10, 10, 0, 0],
        },
        data: livePdfBuckets.value.map((item: any) => ({
          value: Number(item.downloaded || 0) + Number(item.exists || 0),
          itemStyle: Number(item.year) === Number(activeYear) ? {
            borderColor: palette.linePointBorder,
            borderWidth: 2,
            shadowBlur: 24,
            shadowColor: "rgba(21, 132, 122, 0.28)",
          } : undefined,
        })),
      },
      {
        name: "失败",
        type: "bar",
        stack: "pdf",
        itemStyle: {
          color: gradientColor(palette.redLight, palette.red),
        },
        data: livePdfBuckets.value.map((item: any) => ({
          value: Number(item.failed || 0),
          itemStyle: Number(item.year) === Number(activeYear) ? {
            borderColor: palette.linePointBorder,
            borderWidth: 2,
          } : undefined,
        })),
      },
      {
        name: "跳过",
        type: "bar",
        stack: "pdf",
        label: {
          ...compactValueLabel("top"),
          formatter: (_: any) => "",
        },
        itemStyle: {
          color: gradientColor(palette.orangeLight, palette.orange),
          borderRadius: [10, 10, 0, 0],
        },
        data: livePdfBuckets.value.map((item: any) => ({
          value: Number(item.skipped || 0),
          label: {
            ...compactValueLabel("top"),
            formatter: () => {
              const total = Number(item.downloaded || 0) + Number(item.exists || 0) + Number(item.failed || 0) + Number(item.skipped || 0);
              return total > 0 ? String(total) : "";
            },
          },
          itemStyle: Number(item.year) === Number(activeYear) ? {
            borderColor: palette.linePointBorder,
            borderWidth: 2,
            shadowBlur: 20,
            shadowColor: "rgba(245, 158, 11, 0.25)",
          } : undefined,
        })),
      },
    ],
  };
});

const extractOption = computed(() => {
  const palette = chartPalette.value;
  const categories = liveExtractBuckets.value.map((item: any) => String(item.year));
  const activeYear = findActiveBucket(liveExtractBuckets.value)?.year;
  const completedLine = liveExtractBuckets.value.map((item: any) => Number(item.completed || 0));
  const totalLine = liveExtractBuckets.value.map((item: any) => Number(item.total || 0));

  if (extractView.value === "trend") {
    return {
      ...baseBarOption(categories),
      tooltip: {
        trigger: "axis",
        backgroundColor: palette.tooltipBg,
        borderColor: palette.tooltipBorder,
        borderWidth: 1,
        textStyle: { color: palette.text },
        extraCssText: `box-shadow: ${palette.tooltipShadow}; border-radius: var(--radius-md);`,
        formatter: makeTooltipFormatter("extract"),
      },
      series: [
        {
          name: "目标量",
          type: "line",
          smooth: true,
          symbol: "circle",
          symbolSize: 7,
          lineStyle: { width: 2, type: "dashed", color: palette.blue },
          itemStyle: { color: palette.blue },
          data: totalLine,
        },
        {
          name: "已完成",
          type: "line",
          smooth: true,
          symbol: "circle",
          symbolSize: 9,
          areaStyle: {
            color: gradientColor("rgba(58,155,214,0.24)", "rgba(58,155,214,0.02)"),
          },
          lineStyle: { width: 3, color: "#155e75" },
          itemStyle: { color: "#155e75", borderColor: palette.linePointBorder, borderWidth: 2 },
          data: completedLine.map((value, index) => ({
            value,
            itemStyle: Number(categories[index]) === Number(activeYear) ? {
              shadowBlur: 18,
              shadowColor: "rgba(21,94,117,0.32)",
            } : undefined,
          })),
        },
      ],
    };
  }

  return {
      ...baseBarOption(categories),
      tooltip: {
        trigger: "axis",
      axisPointer: { type: "shadow", shadowStyle: { color: palette.axisPointer } },
      backgroundColor: palette.tooltipBg,
      borderColor: palette.tooltipBorder,
      borderWidth: 1,
      textStyle: { color: palette.text },
      extraCssText: `box-shadow: ${palette.tooltipShadow}; border-radius: var(--radius-md);`,
      formatter: makeTooltipFormatter("extract"),
    },
    series: [
      {
        name: "已完成（提取+已存在）",
        type: "bar",
        stack: "extract",
        barWidth: 24,
        itemStyle: {
          color: gradientColor("#3a9bd6", "#155e75"),
          borderRadius: [10, 10, 0, 0],
        },
        data: liveExtractBuckets.value.map((item: any) => ({
          value: Number(item.extracted || 0) + Number(item.exists || 0),
          itemStyle: Number(item.year) === Number(activeYear) ? {
            borderColor: palette.linePointBorder,
            borderWidth: 2,
            shadowBlur: 24,
            shadowColor: "rgba(21, 94, 117, 0.26)",
          } : undefined,
        })),
      },
      {
        name: "失败",
        type: "bar",
        stack: "extract",
        label: {
          ...compactValueLabel("top"),
          formatter: (_: any) => "",
        },
        itemStyle: {
          color: gradientColor(palette.redLight, palette.red),
          borderRadius: [10, 10, 0, 0],
        },
        data: liveExtractBuckets.value.map((item: any) => ({
          value: Number(item.failed || 0),
          label: {
            ...compactValueLabel("top"),
            formatter: () => {
              const total = Number(item.extracted || 0) + Number(item.exists || 0) + Number(item.failed || 0);
              return total > 0 ? String(total) : "";
            },
          },
          itemStyle: Number(item.year) === Number(activeYear) ? {
            borderColor: palette.linePointBorder,
            borderWidth: 2,
            shadowBlur: 20,
            shadowColor: "rgba(239, 68, 68, 0.22)",
          } : undefined,
        })),
      },
    ],
  };
});

watch(
  () => taskStore.currentTaskProgress,
  (target) => {
    const start = displayedProgress.value;
    const end = target;
    const startedAt = performance.now();
    const duration = 180;
    cancelAnimationFrame(animationFrameId);
    const tick = (now: number) => {
      const elapsed = Math.min((now - startedAt) / duration, 1);
      const eased = 1 - Math.pow(1 - elapsed, 3);
      displayedProgress.value = start + (end - start) * eased;
      if (elapsed < 1) animationFrameId = requestAnimationFrame(tick);
    };
    animationFrameId = requestAnimationFrame(tick);
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  cancelAnimationFrame(animationFrameId);
  taskStore.stopIncrementalPolling();
});
</script>

<style scoped>
.console-page {
  --command-log-panel-height: clamp(360px, 41vh, 460px);
  --console-gauge-height: clamp(252px, 29vh, 286px);
  --console-metric-card-height: clamp(112px, 13vh, 124px);
  --console-chart-height: clamp(272px, 32vh, 320px);
  display: grid;
  gap: 16px;
}
.console-head { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 16px; }
.console-head__copy { display: grid; align-content: center; min-width: 0; }
.console-head__copy h2 { margin: 6px 0 10px; font-size: var(--type-page-title); line-height: 1.12; }
.console-head__copy p:last-child { margin: 0; max-width: 680px; color: var(--muted); line-height: 1.6; font-size: var(--type-body); }
.console-head__actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  align-content: start;
}
.action {
  --action-surface: linear-gradient(135deg, #6a96ff 0%, #6170ef 100%);
  --action-surface-active: linear-gradient(135deg, #5e86ef 0%, #5462da 100%);
  --action-shadow: rgba(97, 112, 239, 0.24);
  --action-shadow-strong: rgba(97, 112, 239, 0.34);
  --action-label-color: #ffffff;
  --action-icon-bg: rgba(255, 255, 255, 0.18);
  --action-icon-color: #ffffff;
  position: relative;
  overflow: hidden;
  isolation: isolate;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 56px;
  padding: 0 20px;
  border: 0;
  border-radius: 20px;
  background: var(--action-surface);
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 0.01em;
  white-space: nowrap;
  cursor: pointer;
  color: var(--action-label-color);
  box-shadow: 0 12px 24px var(--action-shadow);
  transition:
    box-shadow 0.18s cubic-bezier(0.22, 1, 0.36, 1),
    background 0.2s ease,
    filter 0.18s ease,
    opacity 0.18s ease;
}
.action__icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 32px;
  border-radius: 999px;
  background: var(--action-icon-bg);
  color: var(--action-icon-color);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.16);
  transition: background 0.18s ease, box-shadow 0.18s ease, color 0.18s ease;
}
.action__icon :deep(svg) {
  display: block;
  width: 16px;
  height: 16px;
  stroke-width: 2.25;
  vector-effect: non-scaling-stroke;
  shape-rendering: geometricPrecision;
}
.action__content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-width: 0;
  padding-inline: 40px;
}
.action__label {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1;
  color: var(--action-label-color);
  text-align: center;
}
.action__hint {
  display: none;
}
.action::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.18), rgba(255, 255, 255, 0) 58%);
  opacity: 0.6;
  pointer-events: none;
  transition: opacity 0.18s ease;
}
.action::after {
  content: "";
  position: absolute;
  inset: 1px;
  border-radius: inherit;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.18);
  pointer-events: none;
  opacity: 0.92;
  transition: box-shadow 0.18s ease, opacity 0.18s ease;
}
.action--links {
  --action-surface: linear-gradient(135deg, #6794ff 0%, #6471f0 100%);
  --action-surface-active: linear-gradient(135deg, #587fe8 0%, #5461d7 100%);
  --action-shadow: rgba(100, 113, 240, 0.24);
  --action-shadow-strong: rgba(100, 113, 240, 0.38);
}
.action--pdf {
  --action-surface: linear-gradient(135deg, #3da8ee 0%, #2f7fe0 100%);
  --action-surface-active: linear-gradient(135deg, #2f94da 0%, #286ecf 100%);
  --action-shadow: rgba(47, 127, 224, 0.24);
  --action-shadow-strong: rgba(47, 127, 224, 0.38);
}
.action--extract {
  --action-surface: linear-gradient(135deg, #2fc0b0 0%, #239a8c 100%);
  --action-surface-active: linear-gradient(135deg, #28ac9e 0%, #1d8478 100%);
  --action-shadow: rgba(35, 154, 140, 0.24);
  --action-shadow-strong: rgba(35, 154, 140, 0.38);
}
.action--pipeline {
  --action-surface: linear-gradient(135deg, #28b755 0%, #23c764 100%);
  --action-surface-active: linear-gradient(135deg, #20a84c 0%, #1eb35a 100%);
  --action-shadow: rgba(35, 199, 100, 0.24);
  --action-shadow-strong: rgba(35, 199, 100, 0.38);
}
.action--pause {
  --action-surface: linear-gradient(135deg, #8b7ef1 0%, #6e62dc 100%);
  --action-surface-active: linear-gradient(135deg, #7d70e4 0%, #6256ca 100%);
  --action-shadow: rgba(110, 98, 220, 0.24);
  --action-shadow-strong: rgba(110, 98, 220, 0.38);
}
.action--terminate {
  --action-surface: linear-gradient(135deg, #e68181 0%, #cf5e5e 100%);
  --action-surface-active: linear-gradient(135deg, #d97070 0%, #bf5252 100%);
  --action-shadow: rgba(207, 94, 94, 0.24);
  --action-shadow-strong: rgba(207, 94, 94, 0.38);
}
.action.action--active,
.action.action--active:disabled {
  background: var(--action-surface-active);
  box-shadow: 0 14px 30px var(--action-shadow-strong);
  filter: saturate(1.08) brightness(1.03);
}
.action.action--active::before,
.action.action--active:disabled::before {
  opacity: 0.72;
}
.action.action--active::after,
.action.action--active:disabled::after {
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.24),
    inset 0 0 0 2px rgba(255, 255, 255, 0.08);
}
.action.action--active .action__icon,
.action.action--active:disabled .action__icon {
  background: rgba(255, 255, 255, 0.22);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.22);
}
.action.action--active .action__label,
.action.action--active:disabled .action__label {
  color: var(--action-label-color);
}
.action.action--active:disabled {
  cursor: not-allowed;
  filter: none;
}
.action.action--active-main,
.action.action--active-main:disabled {
  box-shadow:
    0 18px 36px var(--action-shadow-strong),
    0 0 0 1px rgba(255, 255, 255, 0.08);
  filter: saturate(1.12) brightness(1.06);
}
.action.action--active-main::before,
.action.action--active-main:disabled::before {
  opacity: 0.76;
}
.action.action--active-main::after,
.action.action--active-main:disabled::after {
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.28),
    inset 0 0 0 2px rgba(255, 255, 255, 0.1);
}
.action.action--active-main .action__icon,
.action.action--active-main:disabled .action__icon {
  background: rgba(255, 255, 255, 0.24);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.26);
}
.action.action--active-control,
.action.action--active-control:disabled {
  box-shadow: 0 15px 32px var(--action-shadow-strong);
  filter: saturate(1.06) brightness(1.04);
}
.action:hover:not(:disabled) {
  box-shadow: 0 14px 28px var(--action-shadow);
  filter: saturate(1.02);
}
.action:hover:not(:disabled)::before {
  opacity: 0.68;
}
.action:active:not(:disabled) {
  box-shadow: 0 8px 18px var(--action-shadow);
  filter: brightness(0.98);
}
.action:disabled:not(.action--active) {
  --action-label-color: rgba(255, 255, 255, 0.74);
  --action-icon-color: rgba(255, 255, 255, 0.8);
  --action-icon-bg: rgba(255, 255, 255, 0.12);
  cursor: not-allowed;
  filter: grayscale(0.08) saturate(0.72);
  background: linear-gradient(135deg, #b2bdcf 0%, #99a8bb 100%);
  box-shadow: none;
}
.action:disabled:not(.action--active)::before {
  opacity: 0.46;
}
.action:disabled:not(.action--active)::after {
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.14);
}
.action:disabled:not(.action--active) .action__icon {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12);
}
body[data-theme="midnight"] .action {
  box-shadow:
    0 16px 28px rgba(2, 6, 23, 0.22),
    0 8px 20px var(--action-shadow);
}
body[data-theme="midnight"] .action__icon {
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.14),
    0 4px 10px rgba(2, 6, 23, 0.12);
}
body[data-theme="midnight"] .action__icon :deep(svg) {
  opacity: 1;
  filter: none;
}
body[data-theme="midnight"] .action::before {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.14), rgba(255, 255, 255, 0) 60%);
}
body[data-theme="midnight"] .action.action--active,
body[data-theme="midnight"] .action.action--active:disabled {
  box-shadow:
    0 18px 34px rgba(2, 6, 23, 0.28),
    0 10px 26px var(--action-shadow-strong);
}
body[data-theme="midnight"] .action.action--active-main,
body[data-theme="midnight"] .action.action--active-main:disabled {
  box-shadow:
    0 22px 40px rgba(2, 6, 23, 0.34),
    0 12px 30px var(--action-shadow-strong);
  filter: saturate(1.08) brightness(1.03);
}
body[data-theme="midnight"] .action.action--active-main .action__icon,
body[data-theme="midnight"] .action.action--active-main:disabled .action__icon {
  box-shadow:
    0 8px 18px rgba(2, 6, 23, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.24);
}
body[data-theme="midnight"] .action.action--active-control,
body[data-theme="midnight"] .action.action--active-control:disabled {
  box-shadow:
    0 18px 34px rgba(2, 6, 23, 0.28),
    0 10px 26px var(--action-shadow-strong);
  filter: saturate(1.04) brightness(1.02);
}
body[data-theme="midnight"] .action.action--active::before,
body[data-theme="midnight"] .action.action--active:disabled::before {
  opacity: 0.68;
}
body[data-theme="midnight"] .action.action--active::after,
body[data-theme="midnight"] .action.action--active:disabled::after {
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.22),
    inset 0 0 0 2px rgba(255, 255, 255, 0.08);
}
body[data-theme="midnight"] .action.action--active .action__icon,
body[data-theme="midnight"] .action.action--active:disabled .action__icon {
  box-shadow:
    0 8px 16px rgba(2, 6, 23, 0.16),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}
body[data-theme="midnight"] .action:hover:not(:disabled) {
  box-shadow:
    0 18px 32px rgba(2, 6, 23, 0.24),
    0 10px 24px var(--action-shadow);
}
body[data-theme="midnight"] .action:active:not(:disabled) {
  box-shadow:
    0 10px 20px rgba(2, 6, 23, 0.22),
    0 6px 16px var(--action-shadow);
}
body[data-theme="midnight"] .action:disabled:not(.action--active) {
  background: linear-gradient(135deg, #617185 0%, #536172 100%);
  box-shadow: none;
}
body[data-theme="midnight"] .action:disabled:not(.action--active) .action__icon {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.console-grid { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 16px; align-items: stretch; }
.overview-stack { display: flex; flex-direction: column; justify-content: flex-start; gap: 16px; height: 100%; }
.overview-stack__logs { display: grid; grid-template-rows: auto minmax(0, 1fr); gap: 12px; height: var(--command-log-panel-height); min-height: var(--command-log-panel-height); max-height: var(--command-log-panel-height); min-width: 0; flex: none; }
.overview-stack__logs :deep(.console) { height: 100%; min-height: 100%; max-height: 100%; }
.focus-panel { display: grid; grid-template-columns: 1fr; gap: 14px; align-items: start; flex: 1; min-height: 0; }
.focus-panel__gauge { display: grid; place-items: center; width: 100%; padding-top: 12px; }
.gauge-card { width: 100%; max-width: 440px; padding-top: 0; }
.gauge-card :deep(.chart) { min-height: var(--console-gauge-height); height: var(--console-gauge-height); }
.focus-panel__meta { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; align-content: start; }
.focus-panel__meta article,.live-card { display: flex; flex-direction: column; justify-content: flex-start; min-height: var(--console-metric-card-height); padding: 12px 14px; border-radius: var(--radius-lg); background: var(--panel-alt); box-sizing: border-box; }
.focus-panel__meta small,.live-card small { display: block; color: var(--muted); margin-bottom: 10px; }
.focus-panel__meta strong,.live-card strong { display: block; line-height: 1.4; }
.live-card span { display: block; margin-top: 8px; color: var(--muted); font-size: var(--type-body-small); line-height: 1.45; }
.live-card--accent { background: var(--accent-panel-soft); }
.section-header--chart { margin-bottom: 10px; }
.chart-header-right { display: grid; justify-items: end; gap: 10px; }
.chart-header-meta { display: grid; justify-items: end; gap: 8px; }
.view-switch { display: inline-flex; gap: 6px; padding: 5px; border-radius: var(--radius-pill); background: var(--field-bg-soft); border: 1px solid var(--line); }
.view-switch button { border: 0; min-height: var(--control-height-sm); padding: 0 14px; border-radius: var(--radius-pill); background: transparent; color: var(--muted); font-size: var(--type-body); font-weight: 700; cursor: pointer; transition: all .18s ease; }
.view-switch button.active { background: var(--accent-panel-soft); color: var(--brand); box-shadow: inset 0 0 0 1px rgba(15,118,110,0.12); }
.speed-badge { display: inline-flex; align-items: center; min-height: var(--control-height-sm); padding: 0 14px; border-radius: var(--radius-pill); font-size: var(--type-pill); font-weight: 700; letter-spacing: 0.01em; }
.speed-badge--pdf { background: var(--accent-panel-soft); color: var(--brand-strong); }
.speed-badge--extract { background: var(--accent-panel-soft-alt); color: var(--text-soft); }
.chart-caption { color: var(--muted); font-size: var(--type-body-small); }
.summary-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin: 2px 0 4px; }
.summary-card { position: relative; overflow: hidden; min-height: var(--card-min-height-md); padding: 12px 14px; border-radius: var(--radius-md); border: 1px solid var(--line); background: var(--surface-card-strong-soft); }
.summary-card::after { content: ""; position: absolute; inset: 0; background: var(--surface-card-highlight-strong); pointer-events: none; }
.summary-card small { display: block; margin-bottom: 8px; color: var(--muted); }
.summary-card strong { display: block; font-size: var(--type-metric); line-height: 1.1; color: var(--text); }
.summary-card span { display: block; margin-top: 6px; color: var(--muted); font-size: var(--type-caption); line-height: 1.4; }
.summary-card--strong { background: var(--accent-panel-soft); border-color: rgba(125, 211, 252, 0.32); }
.mono { font-family: Consolas, "Courier New", monospace; color: var(--muted); }
.stage-stack { display: grid; gap: 12px; align-content: start; }
.status-wall,.live-strip { display: grid; gap: 12px; }
.status-wall { height: 100%; align-content: start; }
.live-layout { display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(0, 0.9fr); gap: 12px; }
.live-chart-card,.chart-card { position: relative; overflow: hidden; }
.live-chart-card::before,.chart-card::before { content: ""; position: absolute; inset: 0; background: var(--surface-card-highlight); pointer-events: none; }
.live-chart-card { border-radius: var(--radius-xl); background: var(--surface-card-strong-soft); padding: 6px 10px 2px; border: 1px solid var(--line); }
.chart-card { display: grid; grid-template-rows: auto auto minmax(0, 1fr); border: 1px solid var(--line); background: var(--surface-card-strong); box-shadow: 0 18px 44px rgba(15, 23, 42, 0.06); }
.chart-card--pdf { background-image: radial-gradient(circle at top right, rgba(59,130,246,0.08), transparent 34%), var(--surface-card-strong); }
.chart-card--extract { background-image: radial-gradient(circle at top right, rgba(21,132,122,0.08), transparent 34%), var(--surface-card-strong); }
.chart-card__viewport { min-height: var(--console-chart-height); }
.chart-card__viewport :deep(.chart) { min-height: var(--console-chart-height); height: var(--console-chart-height); }
.live-chart-card,.chart-card,.status-wall,.live-strip,.overview-stack { min-width: 0; }
.live-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; grid-auto-rows: minmax(var(--console-metric-card-height), auto); }
.metrics-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.mini-link { border: 0; background: var(--control-tint-bg); color: var(--control-tint-text); border-radius: var(--radius-pill); padding: 10px 14px; cursor: pointer; }
@media (max-width: 1320px) {
  .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .live-layout { grid-template-columns: 1fr; }
  .chart-header-right,.chart-header-meta { justify-items: start; }
}
@media (max-width: 1180px) {
  .console-head,.console-grid,.metrics-grid,.live-layout,.focus-panel,.focus-panel__meta,.live-grid,.summary-grid { grid-template-columns: 1fr; }
  .console-page {
    --command-log-panel-height: clamp(320px, 38vh, 400px);
    --console-gauge-height: clamp(208px, 24vh, 228px);
    --console-metric-card-height: clamp(106px, 12vh, 118px);
    --console-chart-height: clamp(248px, 30vh, 280px);
  }
  .overview-stack__logs { height: var(--command-log-panel-height); min-height: var(--command-log-panel-height); max-height: var(--command-log-panel-height); }
  .gauge-card { max-width: 100%; }
  .chart-header-right,.chart-header-meta { justify-items: start; }
}
@media (max-width: 1320px) {
  .action { min-height: 52px; padding-inline: 18px; }
  .action__content { padding-inline: 36px; }
}
</style>


