import { create } from 'zustand';

export type ViewMode = 'view' | 'edit';

export interface DashboardState {
  yamlContent: string;
  isDirty: boolean;
  lastSaved: Date | null;
  currentDashboardSlug: string | null;
  selectedTable: string | null;
  selectedDataset: string | null;
  viewMode: ViewMode;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface UIState {
  leftPanelWidth: number;
  rightPanelWidth: number;
  leftPanelSplitRatio: number; // 0-1, ratio of dataset browser to YAML viewer
  isLeftPanelCollapsed: boolean;
  isRightPanelCollapsed: boolean;
}

interface AppStore {
  // Dashboard State
  dashboard: DashboardState;
  setYamlContent: (content: string) => void;
  setDirty: (dirty: boolean) => void;
  setLastSaved: (date: Date | null) => void;
  setCurrentDashboard: (slug: string | null) => void;
  setSelectedTable: (table: string | null) => void;
  setSelectedDataset: (dataset: string | null) => void;
  setViewMode: (mode: ViewMode) => void;

  // Chat State
  chatMessages: ChatMessage[];
  addChatMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  clearChat: () => void;

  // UI State
  ui: UIState;
  setLeftPanelWidth: (width: number) => void;
  setRightPanelWidth: (width: number) => void;
  setLeftPanelSplitRatio: (ratio: number) => void;
  toggleLeftPanel: () => void;
  toggleRightPanel: () => void;

  // Actions
  resetDashboard: () => void;
}

const defaultDashboardState: DashboardState = {
  yamlContent: '',
  isDirty: false,
  lastSaved: null,
  currentDashboardSlug: null,
  selectedTable: null,
  selectedDataset: null,
  viewMode: 'view',
};

const defaultUIState: UIState = {
  leftPanelWidth: 280,
  rightPanelWidth: 360,
  leftPanelSplitRatio: 0.6,
  isLeftPanelCollapsed: false,
  isRightPanelCollapsed: false,
};

export const useAppStore = create<AppStore>((set) => ({
  // Initial state
  dashboard: defaultDashboardState,
  chatMessages: [],
  ui: defaultUIState,

  // Dashboard actions
  setYamlContent: (content) =>
    set((state) => ({
      dashboard: { ...state.dashboard, yamlContent: content, isDirty: true },
    })),

  setDirty: (dirty) =>
    set((state) => ({
      dashboard: { ...state.dashboard, isDirty: dirty },
    })),

  setLastSaved: (date) =>
    set((state) => ({
      dashboard: { ...state.dashboard, lastSaved: date },
    })),

  setCurrentDashboard: (slug) =>
    set((state) => ({
      dashboard: { ...state.dashboard, currentDashboardSlug: slug },
    })),

  setSelectedTable: (table) =>
    set((state) => ({
      dashboard: { ...state.dashboard, selectedTable: table },
    })),

  setSelectedDataset: (dataset) =>
    set((state) => ({
      dashboard: { ...state.dashboard, selectedDataset: dataset },
    })),

  setViewMode: (mode) =>
    set((state) => ({
      dashboard: { ...state.dashboard, viewMode: mode },
    })),

  // Chat actions
  addChatMessage: (message) =>
    set((state) => ({
      chatMessages: [
        ...state.chatMessages,
        {
          ...message,
          id: Math.random().toString(36).substring(7),
          timestamp: new Date(),
        },
      ],
    })),

  clearChat: () => set({ chatMessages: [] }),

  // UI actions
  setLeftPanelWidth: (width) =>
    set((state) => ({
      ui: { ...state.ui, leftPanelWidth: Math.max(240, Math.min(600, width)) },
    })),

  setRightPanelWidth: (width) =>
    set((state) => ({
      ui: { ...state.ui, rightPanelWidth: Math.max(320, Math.min(800, width)) },
    })),

  setLeftPanelSplitRatio: (ratio) =>
    set((state) => ({
      ui: { ...state.ui, leftPanelSplitRatio: Math.max(0.2, Math.min(0.8, ratio)) },
    })),

  toggleLeftPanel: () =>
    set((state) => ({
      ui: { ...state.ui, isLeftPanelCollapsed: !state.ui.isLeftPanelCollapsed },
    })),

  toggleRightPanel: () =>
    set((state) => ({
      ui: { ...state.ui, isRightPanelCollapsed: !state.ui.isRightPanelCollapsed },
    })),

  // Reset
  resetDashboard: () =>
    set({
      dashboard: defaultDashboardState,
      chatMessages: [],
    }),
}));
