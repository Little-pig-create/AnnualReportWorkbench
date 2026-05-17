<template>
  <section class="editor-page" v-if="settings">
    <header class="editor-head">
      <div class="editor-copy">
        <p class="section-kicker">PDF 阶段</p>
        <h2>下载并发设置</h2>
        <p>这一页只保留下载阶段最常调的核心参数，并把依赖关系和建议收成紧凑提示。</p>
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
            <h3>下载线程数</h3>
          </div>
        </header>

        <div class="hero-metric">
          <strong>{{ settings.pdf.downloadConcurrency }}</strong>
          <span>当前工作线程</span>
        </div>

        <label class="field">
          <span>工作线程数</span>
          <input type="number" v-model.number="settings.pdf.downloadConcurrency" @input="settingsStore.touch()" />
        </label>

        <div class="mini-tips">
          <article class="mini-tip">
            <small>适合</small>
            <strong>稳定网络下提速</strong>
          </article>
          <article class="mini-tip">
            <small>注意</small>
            <strong>过高并发可能触发失败重试</strong>
          </article>
        </div>
      </section>

      <section class="surface config-card">
        <header class="section-header section-header--tight">
          <div>
            <p class="section-kicker">依赖</p>
            <h3>阶段关系说明</h3>
          </div>
        </header>

        <div class="note-stack">
          <article class="note-card">
            <strong>输入来源</strong>
            <p>PDF 下载依赖链接抓取阶段生成的清单和元数据，建议先确认链接结果完整。</p>
          </article>
          <article class="note-card">
            <strong>调参顺序</strong>
            <p>建议先低并发完成一次全流程验证，再根据网络和磁盘情况逐步提高线程数。</p>
          </article>
          <article class="note-card">
            <strong>排错方向</strong>
            <p>如果失败偏多，优先检查网络稳定性、下载目录权限和目标站点响应节奏。</p>
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
  grid-template-columns: minmax(300px, 0.72fr) minmax(0, 1.28fr);
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
  background: var(--accent-panel-soft);
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

.mini-tips {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.mini-tip,
.note-card {
  display: grid;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 16px;
  background: var(--panel-alt);
}

.mini-tip small {
  color: var(--muted);
  font-size: var(--type-caption);
  text-transform: uppercase;
  letter-spacing: 0.16em;
}

.mini-tip strong,
.note-card strong {
  font-size: var(--type-strong);
}

.note-stack {
  display: grid;
  gap: 10px;
}

.note-card p {
  margin: 0;
  color: var(--muted);
  font-size: var(--type-body-small);
  line-height: 1.5;
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
