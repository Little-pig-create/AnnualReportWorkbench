<template>
  <section class="editor-page" v-if="settings">
    <header class="editor-head">
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
  display: grid;
  gap: 14px;
}

.editor-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.editor-copy {
  display: grid;
  gap: 6px;
}

.editor-head h2 {
  margin: 0;
  font-size: var(--type-page-title);
  line-height: 1.12;
}

.editor-head p:last-child {
  margin: 0;
  color: var(--muted);
  line-height: 1.5;
  max-width: 720px;
  font-size: var(--type-body);
}

.save-button {
  border: 0;
  border-radius: 999px;
  min-height: 40px;
  padding: 0 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f766e, #155e75);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}

.config-grid {
  display: grid;
  grid-template-columns: minmax(300px, 0.78fr) minmax(0, 1.22fr);
  gap: 14px;
}

.config-card {
  display: grid;
  gap: 14px;
  align-content: start;
}

.section-header--tight {
  margin-bottom: -2px;
}

.hero-metric {
  display: grid;
  gap: 2px;
  padding: 14px 16px;
  border-radius: 18px;
  background: var(--accent-panel-soft-alt);
}

.hero-metric strong {
  font-size: 30px;
  line-height: 1;
}

.hero-metric span,
.field span {
  color: var(--muted);
  font-size: var(--type-body-small);
}

.field {
  display: grid;
  gap: 8px;
}

.field input {
  width: 100%;
  min-height: 40px;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--field-bg);
  color: var(--field-text);
}

.field input::placeholder {
  color: var(--field-placeholder);
}

.inline-note,
.mini-tip,
.toggle-row {
  padding: 12px 14px;
  border-radius: 16px;
  background: var(--panel-alt);
}

.inline-note {
  display: grid;
  gap: 6px;
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
  gap: 12px;
  align-items: start;
}

.mini-tips {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.mini-tip {
  display: grid;
  gap: 6px;
}

.mini-tip small {
  color: var(--muted);
  font-size: var(--type-caption);
  text-transform: uppercase;
  letter-spacing: 0.16em;
}

@media (max-width: 1180px) {
  .editor-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .config-grid,
  .mini-tips {
    grid-template-columns: 1fr;
  }
}
</style>
