<template>
  <section class="editor-page" v-if="settings">
    <header class="editor-head surface">
      <div class="editor-copy">
        <p class="section-kicker">提取阶段</p>
        <h2>文本提取控制台</h2>
        <p>把提取并发和断点策略压缩到一页，方便在 PDF 已落盘后单独微调执行节奏。</p>
      </div>
      <button class="save-button" @click="settingsStore.save()" :disabled="settingsStore.saving">
        {{ settingsStore.saving ? "保存中..." : "保存配置" }}
      </button>
    </header>

    <div class="config-grid">
      <section class="surface config-card">
        <header class="section-header section-header--tight">
          <div>
            <p class="section-kicker">并发</p>
            <h3>提取线程数</h3>
          </div>
        </header>

        <div class="hero-metric">
          <strong>{{ settings.extract.concurrency }}</strong>
          <span>当前工作线程</span>
        </div>

        <label class="field">
          <span>工作线程数</span>
          <input type="number" v-model.number="settings.extract.concurrency" @input="settingsStore.touch()" />
        </label>

        <article class="inline-note">
          <strong>使用建议</strong>
          <p>如果文本提取依赖 OCR 或磁盘读取较多，先保守设置并发，稳定后再逐步加大。</p>
        </article>
      </section>

      <section class="surface config-card">
        <header class="section-header section-header--tight">
          <div>
            <p class="section-kicker">断点</p>
            <h3>恢复与清理</h3>
          </div>
        </header>

        <div class="toggle-stack">
          <label class="toggle-row">
            <input type="checkbox" v-model="settings.extract.resetCheckpoint" @change="settingsStore.touch()" />
            <div>
              <strong>运行前重置断点</strong>
              <p>适合重新全量提取或校验规则变动后的结果。</p>
            </div>
          </label>

          <label class="toggle-row">
            <input type="checkbox" v-model="settings.extract.deleteCheckpointOnSuccess" @change="settingsStore.touch()" />
            <div>
              <strong>成功后删除断点</strong>
              <p>批处理流程更整洁，但不保留成功任务的中间状态。</p>
            </div>
          </label>
        </div>

        <div class="mini-tips">
          <article class="mini-tip">
            <small>适合</small>
            <strong>单阶段补跑</strong>
          </article>
          <article class="mini-tip">
            <small>关注</small>
            <strong>失败率与磁盘占用</strong>
          </article>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSettingsStore } from "@/stores/settings";

const settingsStore = useSettingsStore();
const settings = computed(() => settingsStore.data);
</script>

<style scoped>
.editor-page {
  --config-grid-columns: minmax(300px, 0.78fr) minmax(0, 1.22fr);
  --config-side-card-min-height: clamp(300px, 33vh, 340px);
}

.hero-metric {
  display: grid;
  gap: 4px;
  align-content: start;
  padding: 16px 18px;
  border-radius: var(--radius-2xl);
  background: var(--accent-panel-soft-alt);
  border: 1px solid var(--line-strong);
  box-shadow: inset 0 0 0 1px var(--surface-outline);
}

.hero-metric strong {
  font-size: var(--type-metric-large);
  line-height: 1;
}

.hero-metric span,
.field span {
  color: var(--muted);
  font-size: var(--type-body-small);
}

.inline-note,
.mini-tip,
.toggle-row {
  padding: 10px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--line);
}

.inline-note {
  display: grid;
  gap: 6px;
  background: var(--field-bg-soft);
}

.inline-note strong,
.toggle-row strong,
.mini-tip strong {
  font-size: var(--type-strong);
}

.inline-note p,
.toggle-row p {
  margin: 0;
  color: var(--muted);
  font-size: var(--type-body-small);
  line-height: 1.5;
}

.toggle-stack {
  display: grid;
  gap: 10px;
}

.toggle-row {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 8px;
  align-items: center;
  background: var(--surface-muted);
}

.mini-tips {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.mini-tip {
  display: grid;
  gap: 6px;
  background: var(--field-bg-soft);
}

.mini-tip small {
  color: var(--muted);
  font-size: var(--type-caption);
  text-transform: uppercase;
  letter-spacing: 0.16em;
}

@media (max-width: 1180px) {
  .mini-tips {
    grid-template-columns: 1fr;
  }
}
</style>
