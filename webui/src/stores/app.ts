import { defineStore } from "pinia";
import type { PageKey, UpdateCheckResult } from "@/services/types";
import { bridge } from "@/services/bridge";

export type AppDialogType = "success" | "error" | "info" | "warning";
export type ThemeMode = "sunrise" | "midnight";
export type SidebarMode = "expanded" | "collapsed";

const UI_PREFS_KEY = "report_spider_ui_prefs_v1";
const THEME_TRANSITION_CLASS = "theme-transitioning";
const THEME_TRANSITION_DURATION_MS = 440;

let notificationModulePromise: Promise<typeof import("element-plus/es/components/notification/index")> | null = null;
let messageBoxModulePromise: Promise<typeof import("element-plus/es/components/message-box/index")> | null = null;
let themeTransitionTimer: number | null = null;

type ViewTransitionController = {
  finished: Promise<void>;
};

type DocumentWithViewTransition = Document & {
  startViewTransition?: (callback: () => void | Promise<void>) => ViewTransitionController;
};

function applyThemeTransitionOrigin(sourceElement?: HTMLElement | null) {
  if (typeof document === "undefined" || typeof window === "undefined") return;

  const root = document.documentElement;
  const fallbackX = window.innerWidth * 0.5;
  const fallbackY = window.innerHeight * 0.28;
  const rect = sourceElement?.getBoundingClientRect();
  const originX = rect ? rect.left + rect.width / 2 : fallbackX;
  const originY = rect ? rect.top + rect.height / 2 : fallbackY;
  const radius = Math.hypot(
    Math.max(originX, window.innerWidth - originX),
    Math.max(originY, window.innerHeight - originY),
  );

  root.style.setProperty("--theme-transition-origin-x", `${originX.toFixed(1)}px`);
  root.style.setProperty("--theme-transition-origin-y", `${originY.toFixed(1)}px`);
  root.style.setProperty("--theme-transition-radius", `${Math.ceil(radius)}px`);
  root.style.setProperty("--theme-transition-radius-soft", `${Math.ceil(radius * 0.72)}px`);
}

function applyThemeTransitionPalette(targetMode: ThemeMode) {
  if (typeof document === "undefined") return;

  const root = document.documentElement;
  if (targetMode === "midnight") {
    root.style.setProperty("--theme-transition-core", "rgba(56, 189, 248, 0.1)");
    root.style.setProperty("--theme-transition-glow", "rgba(34, 211, 238, 0.035)");
  } else {
    root.style.setProperty("--theme-transition-core", "rgba(251, 146, 60, 0.09)");
    root.style.setProperty("--theme-transition-glow", "rgba(245, 158, 11, 0.03)");
  }
}

function loadNotificationModule() {
  notificationModulePromise ||= import("element-plus/es/components/notification/index");
  return notificationModulePromise;
}

function loadMessageBoxModule() {
  messageBoxModulePromise ||= import("element-plus/es/components/message-box/index");
  return messageBoxModulePromise;
}

function markThemeTransition(active: boolean, targetMode?: ThemeMode) {
  if (typeof document === "undefined") return;
  const root = document.documentElement;
  root.classList.toggle(THEME_TRANSITION_CLASS, active);
  if (active && targetMode) {
    root.dataset.themeTransitionTarget = targetMode;
  } else {
    delete root.dataset.themeTransitionTarget;
  }
  if (themeTransitionTimer !== null) {
    window.clearTimeout(themeTransitionTimer);
    themeTransitionTimer = null;
  }
}

export const useAppStore = defineStore("app", {
  state: () => ({
    currentPage: "command" as PageKey,
    themeMode: "sunrise" as ThemeMode,
    sidebarMode: "expanded" as SidebarMode,
    bridgeReady: false,
    loading: false,
    themeTransitioning: false,
    about: null as Record<string, any> | null,
    updateChecking: false,
    updateInfo: null as UpdateCheckResult | null,
    updateAutoChecked: false,
  }),
  actions: {
    hydrateUiPrefs() {
      if (typeof window === "undefined") return;
      try {
        const raw = window.localStorage.getItem(UI_PREFS_KEY);
        if (!raw) {
          this.applyTheme();
          return;
        }
        const parsed = JSON.parse(raw || "{}");
        if (parsed?.themeMode === "sunrise" || parsed?.themeMode === "midnight") {
          this.themeMode = parsed.themeMode;
        }
        if (parsed?.sidebarMode === "expanded" || parsed?.sidebarMode === "collapsed") {
          this.sidebarMode = parsed.sidebarMode;
        }
      } catch {
        // ignore malformed prefs
      }
      this.applyTheme();
    },
    saveUiPrefs() {
      if (typeof window === "undefined") return;
      window.localStorage.setItem(
        UI_PREFS_KEY,
        JSON.stringify({
          themeMode: this.themeMode,
          sidebarMode: this.sidebarMode,
        }),
      );
    },
    applyTheme() {
      if (typeof document === "undefined") return;
      document.body.dataset.theme = this.themeMode;
      document.documentElement.dataset.theme = this.themeMode;
    },
    setPage(page: PageKey) {
      this.currentPage = page;
    },
    setTheme(mode: ThemeMode, sourceElement?: HTMLElement | null) {
      if (this.themeMode === mode) return;
      const commitTheme = () => {
        this.themeMode = mode;
        this.applyTheme();
        this.saveUiPrefs();
      };

      if (typeof document === "undefined" || typeof window === "undefined") {
        commitTheme();
        return;
      }

      const prefersReducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;
      if (prefersReducedMotion) {
        commitTheme();
        return;
      }

      applyThemeTransitionOrigin(sourceElement);
      applyThemeTransitionPalette(mode);

      const finishTransition = () => {
        this.themeTransitioning = false;
        markThemeTransition(false);
      };

      const transitionHost = document as DocumentWithViewTransition;
      if (transitionHost.startViewTransition) {
        this.themeTransitioning = true;
        markThemeTransition(true, mode);
        transitionHost.startViewTransition(() => {
          commitTheme();
        }).finished.finally(() => {
          finishTransition();
        });
        return;
      }

      this.themeTransitioning = true;
      markThemeTransition(true, mode);
      commitTheme();
      themeTransitionTimer = window.setTimeout(() => {
        finishTransition();
        themeTransitionTimer = null;
      }, THEME_TRANSITION_DURATION_MS + 80);
    },
    setSidebarMode(mode: SidebarMode) {
      this.sidebarMode = mode;
      this.saveUiPrefs();
    },
    toggleSidebar() {
      this.sidebarMode = this.sidebarMode === "expanded" ? "collapsed" : "expanded";
      this.saveUiPrefs();
    },
    async loadAbout() {
      if (this.about) return;
      this.about = await bridge.getAbout();
    },
    async checkUpdate(options?: { silentCurrent?: boolean; silentError?: boolean; force?: boolean }) {
      if (this.updateAutoChecked && !options?.force) return this.updateInfo;
      if (this.updateChecking) return this.updateInfo;
      this.updateChecking = true;
      try {
        const result = await bridge.checkUpdate();
        this.updateInfo = result;
        if (result.status === "available") {
          this.showAlert(`发现新版本：${result.latestVersion}`, "success", "版本更新");
        } else if (result.status === "current" && !options?.silentCurrent) {
          this.showAlert("当前已是最新版本", "info", "版本更新");
        } else if (result.status === "error" && !options?.silentError) {
          this.showAlert(result.message || "未能获取更新信息", "warning", "版本更新");
        }
        this.updateAutoChecked = true;
        return result;
      } finally {
        this.updateChecking = false;
      }
    },
    async autoCheckUpdate() {
      return this.checkUpdate({ silentCurrent: true, silentError: true });
    },
    showAlert(message: string, type: AppDialogType = "info", title?: string) {
      void loadNotificationModule()
        .then(({ ElNotification }) => {
          ElNotification({
            title: title || "系统通知",
            message,
            type,
            duration: 2600,
            position: "top-right",
          });
        })
        .catch(() => {});
    },
    async showConfirm(payload: {
      title: string;
      message: string;
      type?: AppDialogType;
      confirmText?: string;
      cancelText?: string;
    }) {
      const { ElMessageBox } = await loadMessageBoxModule();
      const dialogType = payload.type || "warning";
      await ElMessageBox.confirm(payload.message, payload.title, {
        type: dialogType,
        confirmButtonText: payload.confirmText || "确认",
        cancelButtonText: payload.cancelText || "取消",
        distinguishCancelAndClose: true,
        closeOnClickModal: false,
        showClose: false,
        modalClass: "app-confirm-overlay",
        customClass: `app-confirm-dialog app-confirm-dialog--${dialogType}`,
      });
    },
  },
});
