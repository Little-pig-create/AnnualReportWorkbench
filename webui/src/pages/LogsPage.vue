<template>
  <section class="logs-page editor-page">
    <header class="logs-head editor-head surface">
      <div class="logs-copy editor-copy">
        <p class="section-kicker">日志</p>
        <h2>运行日志中心</h2>
        <p>按级别和阶段快速筛选，方便在任务执行时直接定位问题。</p>
      </div>
    </header>

    <section class="surface logs-tools">
      <div class="filters">
        <label class="filter-field">
          <span>级别</span>
          <ElSelect v-model="levelFilter" class="control-select--el" popper-class="app-select-popper">
            <ElOption value="ALL" label="全部级别" />
            <ElOption value="INFO" label="信息" />
            <ElOption value="WARN" label="警告" />
            <ElOption value="ERROR" label="错误" />
            <ElOption value="DEBUG" label="调试" />
          </ElSelect>
        </label>

        <label class="filter-field">
          <span>阶段</span>
          <ElSelect v-model="stageFilter" class="control-select--el" popper-class="app-select-popper">
            <ElOption value="ALL" label="全部阶段" />
            <ElOption value="system" label="系统" />
            <ElOption value="links" label="链接" />
            <ElOption value="pdf" label="PDF" />
            <ElOption value="extract" label="提取" />
          </ElSelect>
        </label>
      </div>

      <div class="logs-tools__summary">
        <article class="summary-pill summary-pill--strong">
          <small>当前结果</small>
          <strong>{{ filteredLogs.length }}</strong>
          <span>条日志</span>
        </article>

        <article class="summary-pill">
          <small>筛选状态</small>
          <strong>{{ filterHeadline }}</strong>
          <span>{{ filterSubline }}</span>
        </article>
      </div>
    </section>

    <section class="surface logs-panel">
      <LogConsole :items="filteredLogs" class="logs-console" />
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { ElOption, ElSelect } from "element-plus/es/components/select/index";
import LogConsole from "@/components/LogConsole.vue";
import { useTaskStore } from "@/stores/task";

const taskStore = useTaskStore();
const levelFilter = ref("ALL");
const stageFilter = ref("ALL");

const levelLabels: Record<string, string> = {
  ALL: "全部级别",
  INFO: "信息",
  WARN: "警告",
  ERROR: "错误",
  DEBUG: "调试",
};

const stageLabels: Record<string, string> = {
  ALL: "全部阶段",
  system: "系统",
  links: "链接",
  pdf: "PDF",
  extract: "提取",
};

const filteredLogs = computed(() =>
  taskStore.logs.filter((item) => {
    const levelOk = levelFilter.value === "ALL" || item.level === levelFilter.value;
    const stageOk = stageFilter.value === "ALL" || item.stage === stageFilter.value;
    return levelOk && stageOk;
  }),
);

const filterHeadline = computed(() => {
  if (levelFilter.value === "ALL" && stageFilter.value === "ALL") return "全部日志";
  return `${levelLabels[levelFilter.value]} / ${stageLabels[stageFilter.value]}`;
});

const filterSubline = computed(() => `总计 ${taskStore.logs.length} 条`);
</script>

<style scoped>
.logs-page {
  --logs-console-height: clamp(320px, calc(100vh - 260px), 620px);
  display: grid;
  gap: 12px;
}

.logs-tools {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) auto;
  gap: 12px;
  align-items: stretch;
  padding: 14px 16px;
}

.filters {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.filter-field {
  display: grid;
  gap: 7px;
  min-width: 0;
}

.filter-field span {
  color: var(--muted);
  font-size: var(--type-body-small);
}

.logs-tools__summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 10px;
}

.summary-pill {
  display: grid;
  gap: 2px;
  min-width: 120px;
  padding: 10px 12px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  background: var(--surface-muted);
  align-content: start;
}

.summary-pill small {
  color: var(--muted);
  font-size: var(--type-caption);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.summary-pill--strong {
  border-color: var(--line-strong);
  background: var(--accent-panel-soft);
}

.summary-pill strong {
  font-size: var(--type-metric);
  line-height: 1.05;
}

.summary-pill span {
  color: var(--muted);
  font-size: var(--type-body-small);
  line-height: 1.35;
}

.logs-panel {
  display: grid;
  padding: 14px;
}

.logs-console {
  width: 100%;
}

.logs-console:deep(.console) {
  height: var(--logs-console-height);
  min-height: var(--logs-console-height);
  max-height: var(--logs-console-height);
}

@media (max-width: 1180px) {
  .logs-tools,
  .filters,
  .logs-tools__summary {
    grid-template-columns: 1fr;
  }

  .summary-pill {
    min-width: 0;
  }

  .logs-page {
    --logs-console-height: clamp(300px, calc(100vh - 300px), 460px);
  }
}
</style>
