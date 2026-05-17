<template>
  <section class="about-page">
    <header class="surface about-hero">
      <div class="about-hero__copy">
        <p class="section-kicker">关于软件</p>
        <h2>{{ about?.appName || "Annual Report Workbench Webview Console" }}</h2>
        <p class="about-desc">
          面向年报公告抓取、PDF 下载与文本提取的一体化工作台，强调可视化进度、阶段化执行和紧凑高效的操作体验。
        </p>
      </div>

      <div ref="aboutMainRef" class="about-main" :style="aboutMainStyle">
        <div class="about-meta-row">
          <article class="info-card">
            <small>开发者</small>
            <strong>小毛尖</strong>
            <span>负责产品设计与工作台界面的整体实现。</span>
          </article>

          <article class="info-card info-card--links">
            <small>开源地址</small>
            <div class="meta-links">
              <a
                v-if="about?.githubUrl"
                class="meta-link"
                :href="about.githubUrl"
                target="_blank"
                rel="noreferrer"
              >
                GitHub
              </a>
              <a
                v-if="about?.giteeUrl"
                class="meta-link meta-link--gitee"
                :href="about.giteeUrl"
                target="_blank"
                rel="noreferrer"
              >
                Gitee
              </a>
            </div>
          </article>
        </div>

        <div class="about-quick-grid">
          <article class="quick-card quick-card--accent">
            <small>工作方式</small>
            <strong>三阶段协同</strong>
            <span>支持完整流程，也支持按阶段单独补跑。</span>
          </article>
          <article class="quick-card">
            <small>界面重点</small>
            <strong>进度与日志联动</strong>
            <span>顶部进度、图表和日志可以同时追踪。</span>
          </article>
          <article class="quick-card">
            <small>配置体验</small>
            <strong>路径与参数集中管理</strong>
            <span>高频设置尽量保持在首屏内完成。</span>
          </article>
        </div>

        <section class="reward-card reward-card--main">
          <div class="reward-card__copy">
            <p class="section-kicker">赞赏支持</p>
            <p class="reward-card__title">喜欢这个工作台的话，欢迎扫码支持作者</p>
            <span>你的支持会直接帮助这个项目持续优化界面、流程和使用体验。</span>
            <div class="reward-card__hint">扫码支持</div>
          </div>
          <img :src="rewardCodeUrl" alt="赞赏二维码" />
        </section>
      </div>

      <aside class="about-side" :style="aboutSideStyle">
        <section class="surface update-card">
          <div class="update-card__copy">
            <p class="section-kicker">版本更新</p>
            <h3>更新检查</h3>
          </div>

          <div class="update-card__actions">
            <button class="update-button" @click="checkUpdate" :disabled="appStore.updateChecking">
              {{ appStore.updateChecking ? "检查中..." : "检查更新" }}
            </button>
            <a
              v-if="appStore.updateInfo?.downloadUrl"
              class="update-button update-button--ghost"
              :href="appStore.updateInfo.downloadUrl"
              target="_blank"
              rel="noreferrer"
            >
              下载更新
            </a>
          </div>

          <div class="update-board">
            <div class="update-result">
              <div>
                <span>当前版本</span>
                <strong>{{ currentVersionText }}</strong>
              </div>
              <div>
                <span>更新状态</span>
                <strong>{{ updateStateText }}</strong>
              </div>
              <div>
                <span>更新通道</span>
                <strong>{{ updateChannelText }}</strong>
              </div>
              <div>
                <span>发布来源</span>
                <strong>{{ updateSourceText }}</strong>
              </div>
            </div>

            <article class="update-note-card">
              <span>更新说明</span>
              <strong>{{ updateNoteText }}</strong>
            </article>
            <div class="update-card__footer">
              <a
                class="update-source-link"
                :href="releasePageUrl || undefined"
                target="_blank"
                rel="noreferrer"
              >
                查看发布页
              </a>
            </div>
          </div>

        </section>
      </aside>
    </header>

    <div class="about-grid">
      <article class="surface about-card about-card--wide">
        <header class="section-header section-header--tight">
          <div>
            <p class="section-kicker">流程</p>
            <h3>推荐使用顺序</h3>
          </div>
        </header>
        <ol class="step-grid">
          <li>
            <strong>先确认工作区</strong>
            <span>检查项目目录、数据目录和输出目录是否映射正确。</span>
          </li>
          <li>
            <strong>再配置参数</strong>
            <span>按需设置链接抓取、PDF 下载和文本提取的阶段参数。</span>
          </li>
          <li>
            <strong>启动并观察进度</strong>
            <span>结合顶部进度条、图表和日志实时跟进执行状态。</span>
          </li>
          <li>
            <strong>最后检查产物</strong>
            <span>回到输出目录查看抓取结果、PDF 文件和文本提取结果。</span>
          </li>
        </ol>
      </article>

      <article class="surface about-card">
        <header class="section-header section-header--tight">
          <div>
            <p class="section-kicker">功能</p>
            <h3>核心能力</h3>
          </div>
        </header>
        <ul class="feature-list">
          <li>支持公告链接抓取、PDF 下载、文本提取三阶段串联执行。</li>
          <li>支持单阶段独立运行，适合补跑、校验和调试。</li>
          <li>支持工作目录、年份范围和输出目录集中管理。</li>
          <li>支持状态、进度、图表和日志联动查看。</li>
        </ul>
      </article>

      <article class="surface about-card">
        <header class="section-header section-header--tight">
          <div>
            <p class="section-kicker">目录</p>
            <h3>数据说明</h3>
          </div>
        </header>
        <ul class="feature-list">
          <li>链接结果目录保存抓取到的公告链接和过滤后的记录。</li>
          <li>PDF 目录保存已下载的年报文件。</li>
          <li>文本目录保存提取后的纯文本结果。</li>
          <li>日志与状态目录用于回溯运行过程和异常信息。</li>
        </ul>
      </article>

      <article class="surface about-card">
        <header class="section-header section-header--tight">
          <div>
            <p class="section-kicker">建议</p>
            <h3>使用提醒</h3>
          </div>
        </header>
        <ul class="feature-list">
          <li>首次使用建议先跑一遍链接阶段，确认年份和目录映射无误。</li>
          <li>任务中断后可按阶段补跑，不必每次都重走完整流程。</li>
          <li>日志页适合定位卡点、异常和当前执行阶段。</li>
          <li>任务总览页更适合观察按年份的分布与推进情况。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import rewardCodeUrl from "@/assets/wechat_reward_code.png";
import { useAppStore } from "@/stores/app";

const appStore = useAppStore();
const about = computed(() => appStore.about);
const aboutMainRef = ref<HTMLElement | null>(null);
const syncedSideHeight = ref<number | null>(null);

let aboutMainObserver: ResizeObserver | null = null;
const handleAboutWindowResize = () => {
  syncedSideHeight.value = null;
  void nextTick(() => {
    syncAboutColumnsHeight({ allowShrink: true });
  });
};

const aboutSideStyle = computed(() => {
  if (!syncedSideHeight.value) return undefined;
  return {
    height: `${syncedSideHeight.value}px`,
    minHeight: `${syncedSideHeight.value}px`,
  };
});

const aboutMainStyle = computed(() => {
  if (!syncedSideHeight.value) return undefined;
  return {
    minHeight: `${syncedSideHeight.value}px`,
  };
});

const updateStateText = computed(() => {
  if (appStore.updateChecking) return "检查中";
  return {
    available: "发现更新",
    current: "已是最新",
    error: "获取失败",
  }[appStore.updateInfo?.status || "current"] || "待检查";
});

const currentVersionText = computed(() => appStore.updateInfo?.currentVersion || about.value?.version || "未检查");
const updateChannelText = computed(() => appStore.updateInfo?.downloadChannel || "默认通道");
const FALLBACK_RELEASE_PAGE_URL = "https://github.com/Little-pig-create/AnnualReportWorkbench/releases/latest";

const releasePageUrl = computed(() => {
  const githubUrl = String(about.value?.githubUrl || "").trim();
  if (githubUrl) return `${githubUrl.replace(/\/+$/, "")}/releases/latest`;
  return appStore.updateInfo?.sourceUrl || appStore.updateInfo?.downloadUrl || FALLBACK_RELEASE_PAGE_URL;
});

const updateSourceText = computed(() => {
  const rawUrl = releasePageUrl.value;
  if (!rawUrl) return "待检查";
  try {
    const url = new URL(rawUrl);
    if (url.hostname.includes("github.com") && url.pathname.includes("/releases")) {
      return "github.com/releases";
    }
    return url.host.replace(/^www\./, "");
  } catch {
    return "在线发布页";
  }
});

const updateNoteText = computed(() => {
  const notes = appStore.updateInfo?.notes?.filter(Boolean) || [];
  if (notes.length) return notes.join("\n");
  if (appStore.updateInfo?.message) return appStore.updateInfo.message;
  if (appStore.updateChecking) return "正在拉取远端版本信息，请稍候。";
  return "这里会展示更新说明、版本检查结果以及对应的发布信息。";
});

function syncAboutColumnsHeight(options?: { allowShrink?: boolean }) {
  if (typeof window === "undefined") return;
  if (window.innerWidth <= 1180) {
    syncedSideHeight.value = null;
    return;
  }
  const measuredHeight = aboutMainRef.value
    ? Math.ceil(aboutMainRef.value.getBoundingClientRect().height)
    : null;
  if (!measuredHeight) {
    syncedSideHeight.value = null;
    return;
  }
  if (options?.allowShrink || !syncedSideHeight.value) {
    syncedSideHeight.value = measuredHeight;
    return;
  }
  syncedSideHeight.value = Math.max(syncedSideHeight.value, measuredHeight);
}

onMounted(() => {
  appStore.loadAbout();
  appStore.autoCheckUpdate().catch(() => {});

  void nextTick(() => {
    syncAboutColumnsHeight({ allowShrink: true });
    if (typeof window !== "undefined") {
      window.addEventListener("resize", handleAboutWindowResize);
    }
    if (typeof ResizeObserver !== "undefined" && aboutMainRef.value) {
      aboutMainObserver = new ResizeObserver(() => {
        syncAboutColumnsHeight();
      });
      aboutMainObserver.observe(aboutMainRef.value);
    }
  });
});

function checkUpdate() {
  appStore.checkUpdate({ force: true }).catch(() => {});
}

onBeforeUnmount(() => {
  aboutMainObserver?.disconnect();
  aboutMainObserver = null;
  if (typeof window !== "undefined") {
    window.removeEventListener("resize", handleAboutWindowResize);
  }
});
</script>

<style scoped>
.about-page {
  display: grid;
  gap: 14px;
}

.about-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.75fr);
  gap: 16px;
  align-items: start;
}

.about-hero__copy {
  grid-column: 1 / -1;
  display: grid;
  gap: 8px;
  max-width: 980px;
}

.about-hero__copy h2 {
  margin: 0;
  font-size: var(--type-page-title);
  line-height: 1.12;
}

.about-main {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  --about-lead-column: clamp(220px, 24vw, 248px);
  --about-fill-column: minmax(0, 1fr);
  gap: 14px;
  min-width: 0;
  align-content: start;
  align-self: start;
}

.about-desc {
  margin: 0;
  max-width: 720px;
  color: var(--muted);
  line-height: 1.6;
  font-size: var(--type-body);
}

.about-meta-row {
  display: grid;
  grid-template-columns: var(--about-lead-column) var(--about-fill-column);
  gap: 12px;
  align-items: start;
}

.info-card {
  display: grid;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.12), rgba(59, 130, 246, 0.08));
  border: 1px solid var(--line);
  align-content: start;
}

.info-card--links {
  background: var(--surface-muted);
}

.info-card small,
.quick-card small,
.update-result span,
.update-note-card span {
  color: var(--muted);
  font-size: var(--type-caption);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.info-card strong {
  font-size: var(--type-strong);
  line-height: 1.25;
}

.info-card span {
  color: var(--muted);
  font-size: var(--type-body-small);
  line-height: 1.45;
}

.about-quick-grid {
  display: grid;
  grid-template-columns: var(--about-lead-column) minmax(0, 1fr) minmax(0, 1fr);
  gap: 10px;
}

.quick-card {
  display: grid;
  gap: 6px;
  padding: 14px 15px;
  border-radius: 18px;
  background: var(--surface-muted);
  border: 1px solid var(--line);
}

.quick-card--accent {
  background: linear-gradient(135deg, rgba(15, 118, 110, 0.12), rgba(59, 130, 246, 0.08));
}

.quick-card strong {
  font-size: var(--type-strong);
  line-height: 1.2;
}

.quick-card span {
  color: var(--muted);
  font-size: var(--type-body-small);
  line-height: 1.45;
}

.meta-links {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  width: 100%;
}

.meta-link {
  display: inline-flex;
  width: 100%;
  min-height: 38px;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  border-radius: 14px;
  color: #fff;
  text-decoration: none;
  background: linear-gradient(135deg, #4f8cff, #6f7cff);
  font-size: var(--type-body);
  font-weight: 700;
}

.meta-link--gitee {
  background: linear-gradient(135deg, #16a34a, #22c55e);
}

.about-side {
  --about-side-scale: 1;
  --about-side-shift: 0px;
  --about-side-content-shift: 0px;
  --about-side-content-opacity: 1;
  display: grid;
  min-height: 0;
  align-self: start;
  transform: translate3d(var(--about-side-shift), 0, 0) scale(var(--about-side-scale));
  transform-origin: top right;
  will-change: transform, height;
  transition:
    transform var(--sidebar-motion-duration) var(--sidebar-motion-ease),
    height calc(var(--sidebar-motion-duration) - 0.08s) ease,
    min-height calc(var(--sidebar-motion-duration) - 0.08s) ease;
}

.update-card {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  gap: 12px;
  width: 100%;
  height: 100%;
  min-height: 100%;
  overflow: hidden;
  padding: 16px 18px;
  border-radius: 22px;
  background: var(--surface-muted);
  border: 1px solid var(--line);
  box-shadow: none;
  transition:
    padding calc(var(--sidebar-motion-duration) - 0.1s) ease,
    border-radius calc(var(--sidebar-motion-duration) - 0.12s) ease,
    background calc(var(--sidebar-motion-duration) - 0.08s) ease,
    border-color calc(var(--sidebar-motion-duration) - 0.08s) ease,
    box-shadow calc(var(--sidebar-motion-duration) - 0.08s) ease;
}

.update-card__copy {
  display: grid;
  gap: 2px;
}

.update-card__copy h3 {
  margin: 0;
  font-size: var(--type-section-title);
}

.update-card__actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.update-card__actions > * {
  flex: 1 1 0;
  min-width: 132px;
}

.update-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0 16px;
  border-radius: 14px;
  border: 0;
  text-decoration: none;
  cursor: pointer;
  background: linear-gradient(135deg, #4f8cff, #6f7cff);
  color: #fff;
  font-weight: 700;
}

.update-button--ghost {
  background: var(--control-tint-bg);
  color: var(--control-tint-text);
}

.update-board {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 12px;
  min-height: 0;
  height: 100%;
  align-content: start;
}

.update-card__footer {
  display: flex;
  align-items: flex-start;
  min-height: 0;
  margin-top: 2px;
}

.update-card__copy,
.update-card__actions,
.update-result > div,
.update-note-card,
.update-card__footer {
  opacity: var(--about-side-content-opacity);
  transform: translate3d(0, var(--about-side-content-shift), 0);
  transition:
    transform calc(var(--sidebar-motion-duration) - 0.08s) var(--sidebar-motion-ease-soft),
    opacity calc(var(--sidebar-motion-duration) - 0.16s) ease,
    background calc(var(--sidebar-motion-duration) - 0.08s) ease,
    border-color calc(var(--sidebar-motion-duration) - 0.08s) ease,
    box-shadow calc(var(--sidebar-motion-duration) - 0.08s) ease;
}

.update-result {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-auto-rows: auto;
  gap: 8px;
  align-content: start;
}

.update-result > div {
  display: grid;
  align-content: start;
  padding: 10px 12px;
  border-radius: 14px;
  background: var(--surface-muted);
  border: 1px solid var(--line);
  box-shadow: none;
}

.update-result strong {
  display: block;
  margin-top: 4px;
  font-size: var(--type-body);
  line-height: 1.5;
  word-break: break-word;
}

.update-note-card {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 8px;
  padding: 12px 14px;
  border-radius: 18px;
  border: 1px solid var(--line-strong);
  border-bottom-width: 1px;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.03);
  min-height: 0;
  height: 104px;
  max-height: 104px;
  overflow: hidden;
  background: var(--surface-muted);
  margin-bottom: 0;
}

.update-note-card strong {
  display: block;
  min-height: 0;
  overflow: auto;
  padding-right: 4px;
  padding-bottom: 2px;
  color: var(--text);
  font-size: var(--type-body-small);
  line-height: 1.65;
  white-space: pre-line;
  word-break: break-word;
  scrollbar-width: none;
}

.update-note-card strong::-webkit-scrollbar {
  width: 0;
  height: 0;
}

.update-source-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 38px;
  padding: 0 14px;
  border-radius: 14px;
  color: var(--brand-strong);
  text-decoration: none;
  background: var(--field-bg-soft);
  border: 1px solid var(--line);
  font-size: var(--type-body);
  font-weight: 700;
  transition:
    transform calc(var(--sidebar-motion-duration) - 0.1s) var(--sidebar-motion-ease-soft),
    background calc(var(--sidebar-motion-duration) - 0.08s) ease,
    border-color calc(var(--sidebar-motion-duration) - 0.08s) ease,
    color calc(var(--sidebar-motion-duration) - 0.08s) ease;
}

:global(.workbench-shell[data-sidebar-mode="collapsed"]) .about-page .about-side {
  --about-side-scale: 0.992;
  --about-side-shift: -4px;
  --about-side-content-shift: 3px;
}

:global(.workbench-shell[data-sidebar-mode="expanded"]) .about-page .about-side {
  --about-side-scale: 1;
  --about-side-shift: 0px;
  --about-side-content-shift: 0px;
}

:global(.workbench-shell[data-sidebar-mode="collapsed"]) .about-page .update-card__copy {
  transition-delay: 0.02s;
}

:global(.workbench-shell[data-sidebar-mode="collapsed"]) .about-page .update-card__actions {
  transition-delay: 0.04s;
}

:global(.workbench-shell[data-sidebar-mode="collapsed"]) .about-page .update-note-card {
  transition-delay: 0.06s;
}

:global(.workbench-shell[data-sidebar-mode="collapsed"]) .about-page .update-card__footer {
  transition-delay: 0.08s;
}

@media (prefers-reduced-motion: reduce) {
  .about-side,
  .update-card,
  .update-card__copy,
  .update-card__actions,
  .update-result > div,
  .update-note-card,
  .update-card__footer,
  .update-source-link {
    transition: none;
  }
}

.reward-card {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 152px;
  gap: 18px;
  align-items: center;
  padding: 18px 20px;
  border-radius: 22px;
  background: var(--surface-muted);
  border: 1px solid var(--line);
}

.reward-card--main {
  height: 100%;
  min-height: 214px;
  align-self: stretch;
}

.reward-card__copy {
  display: grid;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.reward-card__title {
  margin: 0;
  color: var(--text);
  font-size: var(--type-section-title);
  font-weight: 700;
  line-height: 1.3;
}

.reward-card__copy span {
  color: var(--muted);
  font-size: var(--type-body);
  line-height: 1.5;
}

.reward-card__hint {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: var(--field-bg);
  color: var(--brand-strong);
  font-size: var(--type-body-small);
  font-weight: 700;
}

.reward-card img {
  width: 148px;
  height: 148px;
  object-fit: cover;
  border-radius: 20px;
  background: var(--field-bg);
  box-shadow: none;
  justify-self: end;
  position: relative;
  z-index: 1;
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.about-card {
  display: grid;
  gap: 12px;
  align-content: start;
}

.about-card--wide {
  grid-column: 1 / -1;
}

.section-header--tight {
  margin-bottom: -2px;
}

.section-header--tight h3 {
  font-size: var(--type-section-title);
}

.step-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
  counter-reset: step;
}

.step-grid li {
  position: relative;
  display: grid;
  gap: 6px;
  min-height: 120px;
  padding: 16px 14px 14px;
  border-radius: 18px;
  background: var(--surface-muted);
  border: 1px solid var(--line);
}

.step-grid li::before {
  counter-increment: step;
  content: "0" counter(step);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: var(--accent-soft);
  color: var(--brand-strong);
  font-size: var(--type-body-small);
  font-weight: 800;
}

.step-grid strong {
  font-size: var(--type-strong);
  line-height: 1.3;
}

.step-grid span,
.feature-list {
  color: var(--muted);
}

.step-grid span {
  font-size: var(--type-body-small);
  line-height: 1.5;
}

.feature-list {
  margin: 0;
  padding-left: 18px;
  line-height: 1.65;
  font-size: var(--type-body);
}

.feature-list li + li {
  margin-top: 6px;
}

:global(body[data-theme="midnight"]) .about-page .info-card,
:global(body[data-theme="midnight"]) .about-page .quick-card,
:global(body[data-theme="midnight"]) .about-page .update-card,
:global(body[data-theme="midnight"]) .about-page .reward-card,
:global(body[data-theme="midnight"]) .about-page .update-result > div,
:global(body[data-theme="midnight"]) .about-page .update-note-card,
:global(body[data-theme="midnight"]) .about-page .about-card {
  background: var(--surface-muted);
  border-color: rgba(148, 163, 184, 0.14);
  box-shadow: none;
}

:global(body[data-theme="midnight"]) .about-page .update-note-card {
  border-color: rgba(148, 163, 184, 0.24);
  box-shadow: 0 8px 18px rgba(2, 6, 23, 0.12);
  border-bottom-width: 1px;
}

:global(body[data-theme="midnight"]) .about-page .reward-card__hint {
  background: rgba(30, 41, 59, 0.92);
  color: #93c5fd;
}

:global(body[data-theme="midnight"]) .about-page .reward-card__title {
  color: #e5eef9;
}

:global(body[data-theme="midnight"]) .about-page .reward-card img {
  background: rgba(8, 13, 23, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.14);
  box-shadow: none;
}

:global(body[data-theme="midnight"]) .about-page .meta-link,
:global(body[data-theme="midnight"]) .about-page .update-button {
  box-shadow: none;
}

@media (max-width: 1180px) {
  .about-hero,
  .about-grid,
  .about-quick-grid,
  .update-result,
  .step-grid,
  .about-meta-row {
    grid-template-columns: 1fr;
  }

  .about-hero__copy {
    grid-column: auto;
  }

  .reward-card {
    grid-template-columns: 1fr;
  }

  .reward-card img {
    justify-self: start;
  }

  .update-card {
    min-height: auto;
  }
}
</style>
