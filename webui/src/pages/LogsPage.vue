<template>
  <section class="logs-page">
    <header class="logs-head">
      <div class="logs-copy">
        <p class="section-kicker">日志</p>
        <h2>运行日志中心</h2>
        <p>按级别和阶段快速筛选，方便在任务执行时直接定位问题。</p>
      </div>

      <div class="logs-tools">
        <div class="filters">
          <select v-model="levelFilter">
            <option value="ALL">全部级别</option>
            <option value="INFO">信息</option>
            <option value="WARN">警告</option>
            <option value="ERROR">错误</option>
            <option value="DEBUG">调试</option>
          </select>
          <select v-model="stageFilter">
            <option value="ALL">全部阶段</option>
            <option value="system">系统</option>
            <option value="links">链接</option>
            <option value="pdf">PDF</option>
            <option value="extract">提取</option>
          </select>
        </div>
        <div class="summary-pill">
          <strong>{{ filteredLogs.length }}</strong>
          <span>条日志</span>
        </div>
      </div>
    </header>

    <section class="surface logs-panel">
      <LogConsole :items="filteredLogs" class="logs-console" />
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import LogConsole from "@/components/LogConsole.vue";
import { useTaskStore } from "@/stores/task";

const taskStore = useTaskStore();
const levelFilter = ref("ALL");
const stageFilter = ref("ALL");

const filteredLogs = computed(() =>
  taskStore.logs.filter((item) => {
    const levelOk = levelFilter.value === "ALL" || item.level === levelFilter.value;
    const stageOk = stageFilter.value === "ALL" || item.stage === stageFilter.value;
    return levelOk && stageOk;
  }),
);
</script>

<style scoped>
.logs-page {
  display: grid;
  gap: 12px;
}

.logs-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.logs-copy {
  display: grid;
  gap: 6px;
}

.logs-head h2 {
  margin: 0;
  font-size: var(--type-page-title);
  line-height: 1.12;
}

.logs-head p:last-child {
  margin: 0;
  color: var(--muted);
  line-height: 1.5;
  font-size: var(--type-body);
}

.logs-tools {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filters {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filters select {
  min-width: 132px;
  min-height: 38px;
  border: 1px solid var(--control-tint-border);
  border-radius: 14px;
  padding: 8px 34px 8px 12px;
  background-color: var(--control-tint-bg);
  color: var(--control-tint-text);
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image:
    linear-gradient(45deg, transparent 50%, var(--control-tint-text) 50%),
    linear-gradient(135deg, var(--control-tint-text) 50%, transparent 50%);
  background-position:
    calc(100% - 20px) calc(50% - 3px),
    calc(100% - 13px) calc(50% - 3px);
  background-size: 7px 7px, 7px 7px;
  background-repeat: no-repeat;
}

.filters select option {
  color: var(--field-text);
  background: var(--field-bg);
}

.summary-pill {
  display: inline-grid;
  gap: 1px;
  min-width: 92px;
  padding: 8px 12px;
  border-radius: 16px;
  background: var(--accent-panel-soft);
  text-align: center;
}

.summary-pill strong {
  font-size: 18px;
  line-height: 1;
}

.summary-pill span {
  color: var(--muted);
  font-size: var(--type-caption);
}

.logs-panel {
  display: grid;
  padding: 14px;
}

.logs-console {
  width: 100%;
}

.logs-console:deep(.console) {
  height: calc(100vh - 260px);
  min-height: 420px;
  max-height: calc(100vh - 260px);
}

@media (max-width: 1180px) {
  .logs-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .logs-tools,
  .filters {
    width: 100%;
    flex-wrap: wrap;
  }

  .filters select {
    flex: 1 1 180px;
  }

  .summary-pill {
    min-width: 84px;
  }

  .logs-console:deep(.console) {
    height: 420px;
    min-height: 420px;
    max-height: 420px;
  }
}
</style>
