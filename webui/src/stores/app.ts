import { defineStore } from "pinia";
import type { PageKey, UpdateCheckResult } from "@/services/types";
import { bridge } from "@/services/bridge";

export type AppDialogType = "success" | "error" | "info" | "warning";
export type ThemeMode = "sunrise" | "midnight";
export type SidebarMode = "expanded" | "collapsed";

const UI_PREFS_KEY = "report_spider_ui_prefs_v1";
const THEME_TRANSITION_CLASS = "theme-transitioning";
const THEME_TRANSITION_DURATION_MS = 420;

let notificationModulePromise: Promise<typeof import("element-plus/es/components/notification/index")> | null = null;
let messageBoxModulePromise: Promise<typeof import("element-plus/es/components/message-box/index")> | null = null;
let themeTransitionTimer: number | null = null;

type ViewTransitionController = {
  finished: Promise<void>;
};

type DocumentWithViewTransition = Document & {
  startViewTransition?: (callback: () => void | Promise<void>) => ViewTransitionController;
};

function loadNotificationModule() {
  notificationModulePromise ||= import("element-plus/es/components/notification/index");
  return notificationModulePromise;
}

function loadMessageBoxModule() {
  messageBoxModulePromise ||= import("element-plus/es/components/message-box/index");
  return messageBoxModulePromise;
}

function markThemeTransition(active: boolean) {
  if (typeof document === "undefined") return;
  document.documentElement.classList.toggle(THEME_TRANSITION_CLASS, active);
  if (themeTransitionTimer !== null) {
    window.clearTimeout(themeTransitionTimer);
    themeTransitionTimer = null;
  }
  if (active) {
    themeTransitionTimer = window.setTimeout(() => {
      document.documentElement.classList.remove(THEME_TRANSITION_CLASS);
      themeTransitionTimer = null;
    }, THEME_TRANSITION_DURATION_MS + 80);
  }
}

export const useAppStore = defineStore("app", {
  state: () => ({
    currentPage: "command" as PageKey,
    themeMode: "sunrise" as ThemeMode,
    sidebarMode: "expanded" as SidebarMode,
    bridgeReady: false,
    loading: false,
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
    setTheme(mode: ThemeMode) {
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

      const transitionHost = document as DocumentWithViewTransition;
      if (transitionHost.startViewTransition) {
        markThemeTransition(true);
        transitionHost.startViewTransition(() => {
          commitTheme();
        }).finished.finally(() => {
          markThemeTransition(false);
        });
        return;
      }

      markThemeTransition(true);
      commitTheme();
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
      await ElMessageBox.confirm(payload.message, payload.title, {
        type: payload.type || "warning",
        confirmButtonText: payload.confirmText || "确认",
        cancelButtonText: payload.cancelText || "取消",
        distinguishCancelAndClose: true,
        closeOnClickModal: false,
      });
    },
  },
});
