<template>
  <section class="editor-page" v-if="settings">
    <header class="editor-head">
      <div class="editor-copy">
        <p class="section-kicker">链接阶段</p>
        <h2>公告链接抓取</h2>
        <p>统一设置市场范围、查询日期、分页节奏和断点策略，尽量把高频参数收在一屏内。</p>
      </div>
      <button class="save-button" @click="settingsStore.save()" :disabled="settingsStore.saving">
        {{ settingsStore.saving ? "保存中..." : "保存配置" }}
      </button>
    </header>

    <div class="config-grid">
      <section class="surface config-card">
        <header class="section-header section-header--tight">
          <div>
            <p class="section-kicker">抓取范围</p>
            <h3>市场与请求参数</h3>
          </div>
        </header>

        <div class="checkbox-group">
          <label class="checkbox-card">
            <input type="checkbox" value="a_share" v-model="settings.links.marketScopes" @change="ensureMarketScopes" />
            <div>
              <strong>沪深 A 股</strong>
              <p>包含主板、创业板与科创板。</p>
            </div>
          </label>

          <label class="checkbox-card">
            <input type="checkbox" value="b_share" v-model="settings.links.marketScopes" @change="ensureMarketScopes" />
            <div>
              <strong>B 股</strong>
              <p>补充深市与沪市 B 股公告。</p>
            </div>
          </label>

          <label class="checkbox-card">
            <input type="checkbox" value="bjse" v-model="settings.links.marketScopes" @change="ensureMarketScopes" />
            <div>
              <strong>北交所</strong>
              <p>纳入北京证券交易所公告源。</p>
            </div>
          </label>
        </div>

        <div class="form-grid">
          <label class="field">
            <span>查询日期</span>
            <input v-model="settings.links.seDate" @input="settingsStore.touch()" placeholder="可选，例如 2024-12-31" />
          </label>

          <label class="field">
            <span>分页大小</span>
            <input type="number" v-model.number="settings.links.pageSize" @input="settingsStore.touch()" />
          </label>

          <label class="field">
            <span>请求间隔（秒）</span>
            <input type="number" step="0.1" v-model.number="settings.links.requestInterval" @input="settingsStore.touch()" />
          </label>

          <label class="field">
            <span>公告并发数</span>
            <input type="number" v-model.number="settings.links.announcementConcurrency" @input="settingsStore.touch()" />
          </label>
        </div>
      </section>

      <section class="surface config-card">
        <header class="section-header section-header--tight">
          <div>
            <p class="section-kicker">断点控制</p>
            <h3>恢复与清理</h3>
          </div>
        </header>

        <div class="toggle-stack">
          <label class="toggle-row">
            <input type="checkbox" v-model="settings.links.resetCheckpoint" @change="settingsStore.touch()" />
            <div>
              <strong>运行前重置断点</strong>
              <p>适合需要从头重跑链接阶段时启用。</p>
            </div>
          </label>

          <label class="toggle-row">
            <input type="checkbox" v-model="settings.links.deleteCheckpointOnSuccess" @change="settingsStore.touch()" />
            <div>
              <strong>成功后删除断点</strong>
              <p>执行完成后自动清理状态文件，目录会更干净。</p>
            </div>
          </label>
        </div>

        <div class="note-grid">
          <article class="note-card">
            <small>建议</small>
            <strong>先低并发验证</strong>
            <span>先确认目录、日期和范围正确，再提高节奏。</span>
          </article>
          <article class="note-card">
            <small>默认</small>
            <strong>至少保留一个市场</strong>
            <span>如果全部取消，会自动回退到 A 股范围。</span>
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

function ensureMarketScopes() {
  if (!settings.value) return;
  if (settings.value.links.marketScopes.length === 0) {
    settings.value.links.marketScopes = ["a_share"];
  }
  settingsStore.touch();
}
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
  grid-template-columns: minmax(0, 1.2fr) minmax(340px, 0.8fr);
  gap: 14px;
  align-items: start;
}

.config-card {
  display: grid;
  gap: 14px;
  align-content: start;
}

.section-header--tight {
  margin-bottom: -2px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.field {
  display: grid;
  gap: 8px;
}

.field span {
  font-size: var(--type-body-small);
  color: var(--muted);
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

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.checkbox-card {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: start;
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: var(--panel-alt);
}

.checkbox-card strong {
  display: block;
  margin-bottom: 4px;
  font-size: var(--type-strong);
}

.checkbox-card p {
  margin: 0;
  color: var(--muted);
  font-size: var(--type-body-small);
  line-height: 1.45;
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
  padding: 12px 14px;
  border-radius: 16px;
  background: var(--panel-alt);
}

.toggle-row strong {
  display: block;
  margin-bottom: 4px;
  font-size: var(--type-strong);
}

.toggle-row p {
  margin: 0;
  color: var(--muted);
  font-size: var(--type-body-small);
  line-height: 1.45;
}

.note-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.note-card {
  display: grid;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: var(--field-bg-soft);
}

.note-card small {
  color: var(--muted);
  font-size: var(--type-caption);
  text-transform: uppercase;
  letter-spacing: 0.16em;
}

.note-card strong {
  font-size: var(--type-strong);
}

.note-card span {
  color: var(--muted);
  font-size: var(--type-body-small);
  line-height: 1.45;
}

@media (max-width: 1180px) {
  .editor-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .config-grid,
  .checkbox-group,
  .form-grid,
  .note-grid {
    grid-template-columns: 1fr;
  }
}
</style>
