const ADMIN_EMAIL = "goprojects452@gmail.com";
const TYPE_DELAY_MS = 0;

const DEFAULT_PREFS = {
  displayName: "",
  avatar: "",
  theme: "light",
  profileAvatarBgMode: "system",
  profileAvatarBg: "#303030",
  goTalkVoice: "",
};

let bootStartTime = Date.now();

const state = {
  user: null,
  tempChats: [],
  historyChats: [],
  currentChatId: null,
  currentIsTemp: false,
  messages: [],
  isStreaming: false,
  sidebarHidden: false,
  isListening: false,
  goTalkActive: false,
  recognition: null,
  prefs: { ...DEFAULT_PREFS },
  adminUnlocked: false,
  pendingAttachments: [],
  lastAdminPin: null,
  pendingShareToken: null,
  searchQuery: "",
  searchTimer: null,
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const els = {
  splash: $("#splash"),
  authScreen: $("#authScreen"),
  app: $("#app"),
  thread: $("#thread"),
  welcome: $("#welcome"),
  promptInput: $("#promptInput"),
  btnSend: $("#btnSend"),
  btnMic: $("#btnMic"),
  btnGoTalk: $("#btnGoTalk"),
  btnAttach: $("#btnAttach"),
  fileInput: $("#fileInput"),
  attachmentPreview: $("#attachmentPreview"),
  composerForm: $("#composerForm"),
  composerHint: $("#composerHint"),
  main: document.querySelector(".main"),
  chatSearch: $("#chatSearch"),
  btnNewChat: $("#btnNewChat"),
  btnTempChat: $("#btnTempChat"),
  btnLogout: $("#btnLogout"),
  userChip: $("#userChip"),
  profileAvatar: $("#profileAvatar"),
  profileEmail: $("#profileEmail"),
  profileBtn: $("#profileBtn"),
  profileMenu: $("#profileMenu"),
  profileWrap: $("#profileWrap"),
  btnCustomize: $("#btnCustomize"),
  btnApiKeys: $("#btnApiKeys"),
  btnToggleSidebar: $("#btnToggleSidebar"),
  sidebarToggleLabel: $("#sidebarToggleLabel"),
  btnAdminPanel: $("#btnAdminPanel"),
  tempChatList: $("#tempChatList"),
  historyChatList: $("#historyChatList"),
  sidebar: $("#sidebar"),
  sidebarOverlay: $("#sidebarOverlay"),
  btnSidebarToggle: $("#btnSidebarToggle"),
  btnHideSidebar: $("#btnHideSidebar"),
  composerPlaceholder: $("#composerPlaceholder"),
  messagesWrap: $("#messagesWrap"),
  loginForm: $("#loginForm"),
  signupForm: $("#signupForm"),
  loginError: $("#loginError"),
  signupError: $("#signupError"),
  dialogOverlay: $("#dialogOverlay"),
  dialogTitle: $("#dialogTitle"),
  dialogMessage: $("#dialogMessage"),
  dialogInput: $("#dialogInput"),
  dialogCancel: $("#dialogCancel"),
  dialogConfirm: $("#dialogConfirm"),
  settingsOverlay: $("#settingsOverlay"),
  settingsName: $("#settingsName"),
  settingsAvatar: $("#settingsAvatar"),
  settingsAvatarBgMode: $("#settingsAvatarBgMode"),
  settingsAvatarBg: $("#settingsAvatarBg"),
  settingsChatBg: $("#settingsChatBg"),
  settingsUserBubbleMode: $("#settingsUserBubbleMode"),
  settingsUserBubble: $("#settingsUserBubble"),
  settingsAiBubble: $("#settingsAiBubble"),
  settingsPreviewAvatar: $("#settingsPreviewAvatar"),
  settingsPreviewName: $("#settingsPreviewName"),
  settingsCancel: $("#settingsCancel"),
  settingsSave: $("#settingsSave"),
  adminPinOverlay: $("#adminPinOverlay"),
  adminPinTitle: $("#adminPinTitle"),
  adminPinMessage: $("#adminPinMessage"),
  adminPinInput: $("#adminPinInput"),
  adminPinError: $("#adminPinError"),
  adminPinCancel: $("#adminPinCancel"),
  adminPinConfirm: $("#adminPinConfirm"),
  adminPanelOverlay: $("#adminPanelOverlay"),
  adminStats: $("#adminStats"),
  btnServerToggle: $("#btnServerToggle"),
  adminReportsList: $("#adminReportsList"),
  adminPanelClose: $("#adminPanelClose"),
  toast: $("#toast"),
  shareOverlay: $("#shareOverlay"),
  shareLinkInput: $("#shareLinkInput"),
  shareClose: $("#shareClose"),
  shareCopy: $("#shareCopy"),
  sharedChatOverlay: $("#sharedChatOverlay"),
  sharedChatTitle: $("#sharedChatTitle"),
  sharedChatMeta: $("#sharedChatMeta"),
  sharedChatDismiss: $("#sharedChatDismiss"),
  sharedChatContinue: $("#sharedChatContinue"),
  apiKeysOverlay: $("#apiKeysOverlay"),
  apiKeysList: $("#apiKeysList"),
  apiKeyCreate: $("#apiKeyCreate"),
  apiKeysClose: $("#apiKeysClose"),
  apiKeyNewDisplay: $("#apiKeyNewDisplay"),
  goTalkScreen: $("#goTalkScreen"),
  goTalkStatus: $("#goTalkStatus"),
  goTalkTranscript: $("#goTalkTranscript"),
  btnGoTalkClose: $("#btnGoTalkClose"),
  settingsGoTalkVoice: $("#settingsGoTalkVoice"),
  otpOverlay: $("#otpOverlay"),
  otpInput: $("#otpInput"),
  otpError: $("#otpError"),
  otpCancel: $("#otpCancel"),
  otpConfirm: $("#otpConfirm"),
  settingsTwoFa: $("#settingsTwoFa"),
  settingsNotifications: $("#settingsNotifications"),
  forgotPasswordOverlay: $("#forgotPasswordOverlay"),
  forgotPasswordEmail: $("#forgotPasswordEmail"),
  forgotPasswordError: $("#forgotPasswordError"),
  forgotPasswordCancel: $("#forgotPasswordCancel"),
  forgotPasswordSend: $("#forgotPasswordSend"),
  resetPasswordOverlay: $("#resetPasswordOverlay"),
  resetPasswordCode: $("#resetPasswordCode"),
  resetPasswordNew: $("#resetPasswordNew"),
  resetPasswordError: $("#resetPasswordError"),
  resetPasswordCancel: $("#resetPasswordCancel"),
  resetPasswordConfirm: $("#resetPasswordConfirm"),
  btnForgotPassword: $("#btnForgotPassword"),
};

const SENSITIVE_PATTERNS = [
  /\bapi\s*key\b/i, /\bz\.?ai\b/i, /\bopenrouter\b/i, /\bsource\s*code\b/i,
  /\bcodebase\b/i,
  /what\s+(api|language|languages|file|files|tech)/i, /which\s+(api|language|languages|file|files)/i,
  /programming\s+language/i, /\bfastapi\b/i, /\bsqlite\b/i, /\bdatabase\b/i, /\.env\b/i,
  /tech\s*stack/i, /\bbackend\b/i, /\bfrontend\b/i, /architecture/i, /built\s+using/i,
  /built\s+with/i, /what\s+are\s+you\s+built/i, /personal\s+information\s+about\s+(you|go\s*ai)/i,
  /how\s+do\s+you\s+work\s+internally/i, /what\s+model\s+do\s+you\s+use/i, /glm-/i,
];

function isSensitiveAdminQuery(text) {
  const t = (text || "").trim();
  if (!t) return false;
  return SENSITIVE_PATTERNS.some((re) => re.test(t));
}

function configureMarkdown() {
  if (typeof marked === "undefined") return;
  const opts = { breaks: true, gfm: true };
  if (typeof marked.use === "function") marked.use(opts);
  else if (typeof marked.setOptions === "function") marked.setOptions(opts);
}
configureMarkdown();

function prefsKey() {
  return `goai_prefs_${state.user?.id || "guest"}`;
}

function loadPrefs() {
  try {
    const raw = localStorage.getItem(prefsKey());
    state.prefs = raw ? { ...DEFAULT_PREFS, ...JSON.parse(raw) } : { ...DEFAULT_PREFS };
  } catch {
    state.prefs = { ...DEFAULT_PREFS };
  }
  applyPrefs();
}

function savePrefs() {
  localStorage.setItem(prefsKey(), JSON.stringify(state.prefs));
  applyPrefs();
}

function applyPrefs() {
  const p = state.prefs;
  let theme = p.theme || "light";
  if (theme === "system") {
    theme = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "night";
  }
  document.documentElement.setAttribute("data-theme", theme);

  let avatarBg = "#303030";
  if (p.profileAvatarBgMode === "custom") {
    avatarBg = p.profileAvatarBg || "#303030";
  } else {
    avatarBg = theme === "light" ? "#e5e5e5" : "#303030";
  }
  document.documentElement.style.setProperty("--profile-avatar-bg", avatarBg);
}

function parseRouteChatId() {
  const m = window.location.pathname.match(/^\/c\/([a-f0-9-]+)$/i);
  return m ? m[1] : null;
}

function chatPath(chatId) {
  return chatId ? `/c/${chatId}` : "/";
}

function syncChatUrl(chatId, replace = false) {
  if (new URLSearchParams(window.location.search).get("share") || window.location.pathname.startsWith("/share/")) return;
  const path = chatPath(chatId);
  if (window.location.pathname === path) return;
  const fn = replace ? "replaceState" : "pushState";
  window.history[fn]({ chatId }, "", path);
}

function setPageTitle(title, isTemp = false) {
  const base = (title || "Go Ai").trim() || "Go Ai";
  document.title = base + (isTemp ? " (temp)" : "");
}

function updateComposerPlaceholder() {
  const hasText = els.promptInput?.value.trim().length > 0;
  els.composerPlaceholder?.classList.toggle("hidden", !!hasText);
}

function updateSidebarToggleButton() {
  const hideIcon = els.btnSidebarToggle?.querySelector(".sidebar-icon-hide");
  const showIcon = els.btnSidebarToggle?.querySelector(".sidebar-icon-show");
  if (!hideIcon || !showIcon) return;
  hideIcon.classList.toggle("hidden", state.sidebarHidden);
  showIcon.classList.toggle("hidden", !state.sidebarHidden);
  els.btnSidebarToggle.title = state.sidebarHidden
    ? "Show chat history"
    : "Hide chat history";
}

function displayName() {
  return state.prefs.displayName || state.user?.username || "You";
}

function userInitial() {
  return displayName().charAt(0).toUpperCase();
}

function avatarHtml(className) {
  if (state.prefs.avatar) {
    return `<img src="${state.prefs.avatar}" alt="" />`;
  }
  return userInitial();
}

function showToast(msg) {
  els.toast.textContent = msg;
  els.toast.classList.remove("hidden");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => els.toast.classList.add("hidden"), 2200);
}

async function api(path, options = {}) {
  let res;
  try {
    res = await fetch(path, {
      credentials: "include",
      headers: { "Content-Type": "application/json", ...options.headers },
      ...options,
    });
  } catch {
    throw new Error(
      "Cannot reach server. Run python run.py and open http://localhost:8000"
    );
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err.detail;
    const msg = Array.isArray(detail)
      ? detail.map((d) => d.msg || d).join(", ")
      : detail || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return res;
}

function renderMarkdown(text) {
  if (typeof marked === "undefined") {
    const esc = (text || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return `<p>${esc.replace(/\n/g, "<br>")}</p>`;
  }
  const html = marked.parse(text || "");
  const wrap = document.createElement("div");
  wrap.innerHTML = html;
  wrap.querySelectorAll("pre code").forEach((block) => {
    if (typeof hljs !== "undefined") hljs.highlightElement(block);
    const pre = block.parentElement;
    if (pre && !pre.querySelector(".copy-btn")) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "copy-btn";
      btn.textContent = "Copy";
      btn.addEventListener("click", () => {
        navigator.clipboard.writeText(block.textContent);
        btn.textContent = "Copied!";
        setTimeout(() => (btn.textContent = "Copy"), 1500);
      });
      pre.style.position = "relative";
      pre.appendChild(btn);
    }
  });
  return wrap.innerHTML;
}

function showWelcome(show) {
  els.welcome.classList.toggle("hidden", !show);
}

function scrollToBottom() {
  els.messagesWrap.scrollTop = els.messagesWrap.scrollHeight;
}

function updateSendButton() {
  const hasText = els.promptInput.value.trim().length > 0;
  const hasAttach = state.pendingAttachments.length > 0;
  els.btnSend.disabled = (!hasText && !hasAttach) || state.isStreaming;
}

function autoResizeTextarea() {
  const ta = els.promptInput;
  ta.style.height = "auto";
  ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
}

function setProfileUI() {
  if (!state.user) return;
  const name = displayName();
  els.profileAvatar.innerHTML = avatarHtml();
  if (!state.prefs.avatar) els.profileAvatar.textContent = userInitial();
  els.userChip.textContent = name;
  els.profileEmail.textContent = state.user.email || "";
  els.btnAdminPanel.classList.toggle("hidden", !state.user.is_admin_account);
  els.sidebarToggleLabel.textContent = state.sidebarHidden
    ? "Show chat history"
    : "Hide chat history";
}

function toggleSidebar(hidden) {
  state.sidebarHidden = hidden;
  els.app.classList.toggle("sidebar-collapsed", hidden);
  localStorage.setItem("goai_sidebar", hidden ? "hidden" : "visible");
  updateSidebarToggleButton();
  setProfileUI();
}

function attachmentHtml(attachments = []) {
  if (!attachments.length) return "";
  return attachments
    .map((a) => {
      if ((a.type || "").startsWith("image/")) {
        return `<a class="msg-attachment" href="${a.url}" target="_blank" rel="noopener"><img src="${a.url}" alt="${a.name || "image"}" /></a>`;
      }
      return `<a class="msg-attachment file" href="${a.url}" target="_blank" rel="noopener">${a.name || "file"}</a>`;
    })
    .join("");
}

function buildUserTurn(text, attachments = []) {
  const turn = document.createElement("article");
  turn.className = "turn turn-user";
  turn.innerHTML = `
    <div class="turn-col">
      <div class="bubble">
        ${attachmentHtml(attachments)}
        <div class="bubble-user-text"></div>
      </div>
    </div>`;
  turn.querySelector(".bubble-user-text").textContent = text;
  return turn;
}

function buildMsgActions(msgIndex) {
  const actions = document.createElement("div");
  actions.className = "msg-actions";
  actions.innerHTML = `
    <button type="button" class="msg-action-btn" data-action="copy">Copy</button>
    <button type="button" class="msg-action-btn" data-action="regenerate">Regenerate</button>
    <button type="button" class="msg-action-btn" data-action="report">Report</button>`;
  actions.querySelector('[data-action="copy"]').addEventListener("click", () => {
    const text = state.messages[msgIndex]?.content || "";
    navigator.clipboard.writeText(text);
    showToast("Copied to clipboard");
  });
  actions.querySelector('[data-action="regenerate"]').addEventListener("click", () => {
    regenerateFrom(msgIndex);
  });
  actions.querySelector('[data-action="report"]').addEventListener("click", () => {
    reportMessage(msgIndex);
  });
  return actions;
}

function buildAssistantTurn(content, streaming = false, msgIndex = -1) {
  const turn = document.createElement("article");
  turn.className = "turn turn-assistant";
  turn.dataset.msgIndex = msgIndex;
  turn.innerHTML = `
    <div class="turn-avatar turn-avatar-ai${streaming ? " generating" : ""}" title="Go Ai">
      <img src="/logo.png" alt="Go Ai" />
    </div>
    <div class="turn-col">
      <span class="turn-sender">Go Ai</span>
      <div class="bubble">
        <div class="turn-content${streaming ? " typing-cursor" : ""}"></div>
      </div>
    </div>`;
  const contentEl = turn.querySelector(".turn-content");
  if (content) contentEl.innerHTML = renderMarkdown(content);
  if (!streaming && content && msgIndex >= 0) {
    turn.querySelector(".turn-col").appendChild(buildMsgActions(msgIndex));
  }
  return turn;
}

function buildTypingTurn() {
  const turn = document.createElement("article");
  turn.className = "turn turn-assistant turn-typing";
  turn.innerHTML = `
    <div class="turn-avatar turn-avatar-ai generating" title="Go Ai">
      <img src="/logo.png" alt="Go Ai" />
    </div>
    <div class="turn-col">
      <span class="turn-sender">Go Ai</span>
      <div class="bubble bubble-typing">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    </div>`;
  return turn;
}

function renderThread() {
  els.thread.innerHTML = "";
  const hasMessages = state.messages.length > 0;
  showWelcome(!hasMessages);
  state.messages.forEach((msg, i) => {
    if (msg.role === "user") {
      els.thread.appendChild(buildUserTurn(msg.content, msg.attachments || []));
    } else {
      const streaming =
        state.isStreaming &&
        i === state.messages.length - 1 &&
        msg.role === "assistant";
      els.thread.appendChild(buildAssistantTurn(msg.content, streaming, i));
    }
  });
  scrollToBottom();
}

function createChatRow(chat) {
  const row = document.createElement("div");
  row.className =
    "chat-row" +
    (chat.is_temp ? " temp" : "") +
    (chat.id === state.currentChatId ? " active" : "");

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "chat-item";
  btn.textContent = chat.title;
  btn.title = chat.title;
  btn.addEventListener("click", () => loadChat(chat.id));

  const menuBtn = document.createElement("button");
  menuBtn.type = "button";
  menuBtn.className = "chat-menu-btn";
  menuBtn.setAttribute("aria-label", "Chat options");
  menuBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>`;

  const menu = document.createElement("div");
  menu.className = "chat-dropdown hidden";
  menu.innerHTML = `
    <button type="button" class="chat-dropdown-item" data-action="share">Share</button>
    <button type="button" class="chat-dropdown-item" data-action="rename">Rename</button>
    <button type="button" class="chat-dropdown-item danger" data-action="delete">Delete</button>`;

  menuBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    $$(".chat-dropdown").forEach((d) => {
      if (d !== menu) d.classList.add("hidden");
    });
    menu.classList.toggle("hidden");
  });

  menu.querySelector('[data-action="share"]').addEventListener("click", (e) => {
    e.stopPropagation();
    menu.classList.add("hidden");
    shareChatById(chat.id);
  });

  menu.querySelector('[data-action="rename"]').addEventListener("click", (e) => {
    e.stopPropagation();
    menu.classList.add("hidden");
    renameChatById(chat.id, chat.title, chat.is_temp);
  });

  menu.querySelector('[data-action="delete"]').addEventListener("click", (e) => {
    e.stopPropagation();
    menu.classList.add("hidden");
    deleteChatById(chat.id);
  });

  row.appendChild(btn);
  row.appendChild(menuBtn);
  row.appendChild(menu);
  return row;
}

function renderChatLists() {
  const renderList = (container, chats, emptyText) => {
    container.innerHTML = "";
    if (!chats.length) {
      const p = document.createElement("p");
      p.className = "sidebar-empty";
      p.textContent = emptyText;
      container.appendChild(p);
      return;
    }
    chats.forEach((chat) => container.appendChild(createChatRow(chat)));
  };
  if (els.tempChatList) renderList(els.tempChatList, state.tempChats, "No temp chats");
  if (els.historyChatList) renderList(els.historyChatList, state.historyChats, "No history yet");
}

async function refreshChats(query) {
  const q = (query !== undefined ? query : state.searchQuery || "").trim();
  state.searchQuery = q;
  const url = q ? `/api/chats?q=${encodeURIComponent(q)}` : "/api/chats";
  const res = await api(url);
  const data = await res.json();
  state.tempChats = data.temp || [];
  state.historyChats = data.history || [];
  renderChatLists();
}

async function saveCurrentChat() {
  if (!state.currentChatId || state.messages.length === 0 || state.currentIsTemp) return;
  await api(`/api/chats/${state.currentChatId}`, {
    method: "PATCH",
    body: JSON.stringify({ messages: state.messages }),
  });
  await refreshChats();
}

async function loadChat(chatId, opts = {}) {
  if (state.isStreaming) return;
  const res = await api(`/api/chats/${chatId}`);
  const chat = await res.json();
  state.currentChatId = chat.id;
  state.currentIsTemp = chat.is_temp;
  state.messages = chat.messages || [];
  setPageTitle(chat.title, chat.is_temp);
  if (!opts.skipUrl && !chat.is_temp) syncChatUrl(chat.id, !!opts.replace);
  renderChatLists();
  renderThread();
  closeSidebarMobile();
}

async function createChat(isTemp = false) {
  if (state.isStreaming) return;
  state.currentChatId = null;
  state.currentIsTemp = isTemp;
  state.messages = [];
  setPageTitle(isTemp ? "Temp chat" : "New chat", isTemp);
  syncChatUrl(null, true); // Revert to / immediately
  document.querySelectorAll(".chat-row").forEach(el => el.classList.remove("active"));
  renderThread();
  els.promptInput.focus();
  closeSidebarMobile();
}

async function deleteChatById(chatId) {
  if (state.isStreaming) return;
  const ok = await showConfirmDialog("Delete chat", "Are you sure you want to delete this chat?");
  if (!ok) return;
  await api(`/api/chats/${chatId}`, { method: "DELETE" });
  if (state.currentChatId === chatId) {
    state.currentChatId = null;
    state.messages = [];
    await refreshChats();
    await createChat(false);
  } else {
    await refreshChats();
  }
}

async function renameChatById(chatId, currentTitle, isTemp) {
  if (state.isStreaming) return;
  const clean = await showInputDialog(
    "Rename chat",
    "Enter a new title for this conversation.",
    currentTitle || "New chat"
  );
  if (!clean) return;
  await api(`/api/chats/${chatId}`, {
    method: "PATCH",
    body: JSON.stringify({ title: clean }),
  });
  await refreshChats();
  if (state.currentChatId === chatId) {
    setPageTitle(clean, isTemp);
  }
}

function showConfirmDialog(title, message) {
  return new Promise((resolve) => {
    els.dialogTitle.textContent = title;
    els.dialogMessage.textContent = message;
    els.dialogConfirm.textContent = "Delete";
    els.dialogInput.classList.add("hidden");
    els.dialogOverlay.classList.remove("hidden");
    const cleanup = () => {
      els.dialogOverlay.classList.add("hidden");
      els.dialogCancel.removeEventListener("click", onCancel);
      els.dialogConfirm.removeEventListener("click", onConfirm);
      els.dialogOverlay.removeEventListener("click", onBackdrop);
    };
    const onCancel = () => { cleanup(); resolve(false); };
    const onConfirm = () => { cleanup(); resolve(true); };
    const onBackdrop = (e) => { if (e.target === els.dialogOverlay) onCancel(); };
    els.dialogCancel.addEventListener("click", onCancel);
    els.dialogConfirm.addEventListener("click", onConfirm);
    els.dialogOverlay.addEventListener("click", onBackdrop);
  });
}

function showInputDialog(title, message, value = "") {
  return new Promise((resolve) => {
    els.dialogTitle.textContent = title;
    els.dialogMessage.textContent = message;
    els.dialogConfirm.textContent = "Save";
    els.dialogInput.classList.remove("hidden");
    els.dialogInput.value = value;
    els.dialogOverlay.classList.remove("hidden");
    els.dialogInput.focus();
    els.dialogInput.select();
    const cleanup = () => {
      els.dialogOverlay.classList.add("hidden");
      els.dialogInput.classList.add("hidden");
      els.dialogCancel.removeEventListener("click", onCancel);
      els.dialogConfirm.removeEventListener("click", onConfirm);
      els.dialogOverlay.removeEventListener("click", onBackdrop);
      els.dialogInput.removeEventListener("keydown", onEnter);
    };
    const onCancel = () => { cleanup(); resolve(null); };
    const onConfirm = () => { cleanup(); resolve(els.dialogInput.value.trim() || null); };
    const onBackdrop = (e) => { if (e.target === els.dialogOverlay) onCancel(); };
    const onEnter = (e) => { if (e.key === "Enter") { e.preventDefault(); onConfirm(); } };
    els.dialogCancel.addEventListener("click", onCancel);
    els.dialogConfirm.addEventListener("click", onConfirm);
    els.dialogOverlay.addEventListener("click", onBackdrop);
    els.dialogInput.addEventListener("keydown", onEnter);
  });
}

function speakText(text) {
  if (!state.goTalkActive || !window.speechSynthesis) return;
  const plain = text.replace(/[#*_`>\[\]()]/g, " ").replace(/\s+/g, " ").trim();
  if (!plain) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(plain.slice(0, 800));
  
  if (navigator.language) {
    u.lang = navigator.language;
  }
  
  if (state.prefs.goTalkVoice) {
    const voices = window.speechSynthesis.getVoices();
    const voice = voices.find((v) => v.name === state.prefs.goTalkVoice);
    if (voice) u.voice = voice;
  }
  
  u.rate = 1;
  u.pitch = 1;
  window.speechSynthesis.speak(u);
}

// Removed waitForTypewriter

async function streamResponse(adminPin = null) {
  state.isStreaming = true;
  updateSendButton();

  state.messages.push({ role: "assistant", content: "" });
  const typingEl = buildTypingTurn();
  els.thread.appendChild(typingEl);
  showWelcome(false);
  scrollToBottom();

  const idx = state.messages.length - 1;
  let assistantEl = null;
  let contentEl = null;
  let gotContent = false;
  const showAssistantBubble = () => {
    if (assistantEl) return;
    typingEl.remove();
    assistantEl = buildAssistantTurn("", true, idx);
    els.thread.appendChild(assistantEl);
    contentEl = assistantEl.querySelector(".turn-content");
    scrollToBottom();
  };

  const updateContent = () => {
    if (!contentEl) return;
    contentEl.innerHTML = renderMarkdown(state.messages[idx].content);
    scrollToBottom();
    if (state.goTalkActive && els.goTalkTranscript) {
      els.goTalkTranscript.textContent = state.messages[idx].content;
    }
  };

  try {
    const payload = { messages: state.messages.slice(0, -1) };
    if (adminPin) payload.admin_pin = adminPin;

    const res = await fetch("/api/chat", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Chat failed");
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const payload = line.slice(6);
        if (payload === "[DONE]") continue;
        let data;
        try {
          data = JSON.parse(payload);
        } catch {
          continue;
        }
        if (data.error) throw new Error(data.error);
        if (data.content) {
          if (!gotContent) {
            gotContent = true;
            showAssistantBubble();
          }
          state.messages[idx].content += data.content;
          updateContent();
        }
      }
    }
  } catch (err) {
    typingEl.remove();
    if (!assistantEl) {
      assistantEl = buildAssistantTurn("", false, idx);
      els.thread.appendChild(assistantEl);
      contentEl = assistantEl.querySelector(".turn-content");
    }
    let emsg = err.message || "Unknown error";
    if (emsg.includes("fetch") || emsg.includes("Failed") || emsg.includes("network") || emsg.includes("ZAIError")) {
      emsg = "We are facing some errors check your connection or may be our server is closed due to update";
    }
    state.messages[idx].content = emsg;
    contentEl.innerHTML = renderMarkdown(state.messages[idx].content);
    if (state.goTalkActive && els.goTalkTranscript) {
      els.goTalkTranscript.textContent = state.messages[idx].content;
    }
  }

  if (!gotContent && typingEl.parentNode) {
    typingEl.remove();
    assistantEl = buildAssistantTurn("No response received.", false, idx);
    state.messages[idx].content = "No response received.";
    els.thread.appendChild(assistantEl);
    contentEl = assistantEl.querySelector(".turn-content");
  }

  if (contentEl) {
    contentEl.innerHTML = renderMarkdown(state.messages[idx].content);
    contentEl.classList.remove("typing-cursor");
    const avatarAi = assistantEl.querySelector(".turn-avatar-ai");
    if (avatarAi) avatarAi.classList.remove("generating");
    assistantEl.querySelector(".turn-col").appendChild(buildMsgActions(idx));
  }

  state.isStreaming = false;
  updateSendButton();
  speakText(state.messages[idx].content);
  await saveCurrentChat();
  
  if (state.goTalkActive) {
    els.goTalkStatus.textContent = "AI is speaking...";
    setTimeout(() => {
      if (state.goTalkActive && state.recognition && !state.isListening && !state.isStreaming) {
        try {
          state.recognition.start();
        } catch (e) {}
      }
    }, 1500); // Small pause before listening again
  }
  
  if (!state.currentIsTemp && state.currentChatId) {
    syncChatUrl(state.currentChatId);
    if (state.messages.length <= 2) {
      await refreshChats(state.searchQuery);
    }
  }
}

async function regenerateFrom(msgIndex) {
  if (state.isStreaming) return;
  const msg = state.messages[msgIndex];
  if (!msg || msg.role !== "assistant") return;
  const priorUser = [...state.messages.slice(0, msgIndex)].reverse().find((m) => m.role === "user");
  const adminPin = await requireAdminPinForChat(priorUser?.content || "");
  if (adminPin === false) return;
  state.messages = state.messages.slice(0, msgIndex);
  renderThread();
  await streamResponse(adminPin || null);
}

async function reportMessage(msgIndex) {
  const msg = state.messages[msgIndex];
  if (!msg) return;
  const reason = await showInputDialog(
    "Report message",
    "Why are you reporting this AI reply?",
    ""
  );
  if (reason === null) return;
  try {
    await api("/api/report", {
      method: "POST",
      body: JSON.stringify({
        message_content: msg.content,
        reason: reason || "No reason given",
        chat_id: state.currentChatId,
      }),
    });
    showToast("Report submitted. Thank you.");
  } catch (err) {
    showToast(err.message);
  }
}

async function requireAdminPinForChat(text) {
  if (!state.user?.is_admin_account || !isSensitiveAdminQuery(text)) return null;
  const pin = await showAdminPinDialog(
    "S-Pin required",
    "Enter S-Pin to ask about Go Ai internals, API, languages, or files."
  );
  if (!pin) return false;
  return pin;
}

function showAdminPinDialog(
  title = "Admin access",
  message = "If you are admin, enter your S-Pin."
) {
  return new Promise((resolve) => {
    els.adminPinTitle.textContent = title;
    els.adminPinMessage.textContent = message;
    els.adminPinError.textContent = "";
    els.adminPinInput.value = "";
    els.adminPinOverlay.classList.remove("hidden");
    const cleanup = () => {
      els.adminPinOverlay.classList.add("hidden");
      els.adminPinCancel.removeEventListener("click", onCancel);
      els.adminPinConfirm.removeEventListener("click", onConfirm);
      els.adminPinOverlay.removeEventListener("click", onBackdrop);
      els.adminPinInput.removeEventListener("keydown", onEnter);
    };
    const onCancel = () => { cleanup(); resolve(null); };
    const onConfirm = async () => {
      const pin = els.adminPinInput.value.trim();
      if (!pin) {
        els.adminPinError.textContent = "Enter your S-Pin";
        return;
      }
      if (title === "S-Pin required") {
        cleanup();
        resolve(pin);
        return;
      }
      try {
        await api("/api/admin/verify", {
          method: "POST",
          body: JSON.stringify({ pin }),
        });
        state.adminUnlocked = true;
        setProfileUI();
        cleanup();
        showToast("Admin features unlocked");
        resolve(pin);
      } catch (err) {
        els.adminPinError.textContent = err.message;
      }
    };
    const onBackdrop = (e) => { if (e.target === els.adminPinOverlay) onCancel(); };
    const onEnter = (e) => { if (e.key === "Enter") { e.preventDefault(); onConfirm(); } };
    els.adminPinCancel.addEventListener("click", onCancel);
    els.adminPinConfirm.addEventListener("click", onConfirm);
    els.adminPinOverlay.addEventListener("click", onBackdrop);
    els.adminPinInput.addEventListener("keydown", onEnter);
    els.adminPinInput.focus();
  });
}

function renderAdminReports(reports) {
  els.adminReportsList.innerHTML = "";
  if (!reports.length) {
    els.adminReportsList.innerHTML = '<p class="sidebar-empty">No reports yet</p>';
    return;
  }
  reports.forEach((r) => {
    const item = document.createElement("div");
    item.className = "admin-report-item" + (r.status === "fixed" ? " fixed" : "");
    item.innerHTML = `
      <div class="admin-report-meta">${r.username} · ${r.status} · ${new Date(r.created_at).toLocaleString()}</div>
      <div class="admin-report-text">${r.reason ? r.reason + " — " : ""}${r.message_content.slice(0, 200)}</div>
      <div class="admin-report-actions">
        <button type="button" class="btn-fix-report" ${r.status === "fixed" ? "disabled" : ""}>Mark fixed</button>
        <button type="button" class="btn-edit-report">Edit msg</button>
        ${r.chat_id ? `<button type="button" class="btn-reply-chat">Reply</button>` : ""}
      </div>`;
    const btn = item.querySelector(".btn-fix-report");
    if (r.status !== "fixed") {
      btn.addEventListener("click", async () => {
        try {
          await api(`/api/admin/reports/${r.id}/fix`, {
            method: "PATCH",
            body: JSON.stringify({ pin: state.lastAdminPin }),
          });
          r.status = "fixed";
          item.classList.add("fixed");
          btn.disabled = true;
          showToast("Report marked as fixed");
          await openAdminPanel();
        } catch (err) {
          showToast(err.message);
        }
      });
    }

    const btnEdit = item.querySelector(".btn-edit-report");
    btnEdit.addEventListener("click", async () => {
      const newMsg = await showInputDialog("Edit Message", "Edit the reported message content:", r.message_content);
      if (newMsg === null) return;
      try {
        await api(`/api/admin/reports/${r.id}/edit`, {
          method: "PATCH",
          body: JSON.stringify({ pin: state.lastAdminPin, message_content: newMsg }),
        });
        showToast("Message updated");
        await openAdminPanel();
      } catch (err) {
        showToast(err.message);
      }
    });

    const btnReply = item.querySelector(".btn-reply-chat");
    if (btnReply && r.chat_id) {
      btnReply.addEventListener("click", async () => {
        const replyText = await showInputDialog("Reply to User", "Enter text to send to user instead of AI:");
        if (!replyText) return;
        try {
          await api(`/api/admin/chats/${r.chat_id}/reply`, {
            method: "POST",
            body: JSON.stringify({ pin: state.lastAdminPin, content: replyText }),
          });
          showToast("Reply sent to user's chat");
        } catch (err) {
          showToast(err.message);
        }
      });
    }

    els.adminReportsList.appendChild(item);
  });
}

async function shareChatById(chatId) {
  try {
    const res = await api(`/api/chats/${chatId}/share`, { method: "POST" });
    const data = await res.json();
    const origin = window.location.origin;
    els.shareLinkInput.value =
      data.chat_url?.startsWith("http")
        ? data.chat_url
        : `${origin}${data.chat_url || `/c/${chatId}`}`;
    els.shareOverlay.classList.remove("hidden");
  } catch (err) {
    showToast(err.message);
  }
}

async function loadApiKeys() {
  const res = await api("/api/keys");
  const keys = await res.json();
  if (!keys.length) {
    els.apiKeysList.innerHTML = '<p class="sidebar-empty">No API keys yet.</p>';
    return;
  }
  els.apiKeysList.innerHTML = "";
  keys.forEach((k) => {
    const row = document.createElement("div");
    row.className = "api-key-row";
    row.innerHTML = `<div><strong>${k.name}</strong><br><code>${k.prefix}…</code></div>`;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn-revoke-key";
    btn.textContent = "Revoke";
    btn.addEventListener("click", async () => {
      try {
        await api(`/api/keys/${k.id}`, { method: "DELETE" });
        showToast("API key revoked");
        await loadApiKeys();
      } catch (err) {
        showToast(err.message);
      }
    });
    row.appendChild(btn);
    els.apiKeysList.appendChild(row);
  });
}

async function openApiKeysModal() {
  els.apiKeyNewDisplay.classList.add("hidden");
  els.apiKeyNewDisplay.textContent = "";
  els.apiKeysOverlay.classList.remove("hidden");
  try {
    await loadApiKeys();
  } catch (err) {
    showToast(err.message);
  }
}

async function initChatFromRoute() {
  await refreshChats();
  const routeId = parseRouteChatId();
  if (routeId) {
    try {
      await loadChat(routeId, { skipUrl: true });
      return;
    } catch {
      /* fall through to new chat */
    }
  }
  await createChat(false);
}

async function openAdminPanel() {
  const pin = await showAdminPinDialog(
    "Admin access",
    "Enter S-Pin to view reports and stats."
  );
  if (!pin) return;
  state.lastAdminPin = pin;
  try {
    const [statsRes, reportsRes] = await Promise.all([
      api("/api/admin/stats", { method: "POST", body: JSON.stringify({ pin }) }),
      api("/api/admin/reports", { method: "POST", body: JSON.stringify({ pin }) }),
    ]);
    const stats = await statsRes.json();
    const reports = await reportsRes.json();
    els.adminStats.innerHTML = `
      <div class="admin-stat"><strong>${stats.users}</strong><span>Users</span></div>
      <div class="admin-stat"><strong>${stats.chats}</strong><span>Chats</span></div>
      <div class="admin-stat"><strong>${stats.messages}</strong><span>Messages</span></div>
      <div class="admin-stat"><strong>${stats.pending_reports ?? stats.reports}</strong><span>Pending reports</span></div>`;
    
    const serverStopped = stats.server_stopped || false;
    els.adminStats.insertAdjacentHTML('afterend', `
      <div style="margin-top: 20px;">
        <label style="display:flex; align-items:center; gap: 8px;">
          <input type="checkbox" id="serverStopToggle" ${serverStopped ? 'checked' : ''}>
          <strong>Stop Go Ai Server</strong>
        </label>
        <p class="settings-hint">When checked, users will receive "Server is stop" instead of AI responses.</p>
      </div>
    `);
    document.getElementById("serverStopToggle").addEventListener("change", async (e) => {
      try {
        await api("/api/admin/server-state", {
          method: "POST",
          body: JSON.stringify({ pin: state.lastAdminPin, stopped: e.target.checked })
        });
        showToast(e.target.checked ? "Server stopped" : "Server started");
      } catch(err) {
        alert(err.message);
        e.target.checked = !e.target.checked;
      }
    });

    renderAdminReports(reports);
    els.adminPanelOverlay.classList.remove("hidden");
  } catch (err) {
    showToast(err.message);
  }
}

function renderAttachmentPreview() {
  if (!state.pendingAttachments.length) {
    els.attachmentPreview.classList.add("hidden");
    els.attachmentPreview.innerHTML = "";
    return;
  }
  els.attachmentPreview.classList.remove("hidden");
  els.attachmentPreview.innerHTML = "";
  state.pendingAttachments.forEach((att, i) => {
    const chip = document.createElement("span");
    chip.className = "attach-chip";
    chip.innerHTML = `${att.name} <button type="button" aria-label="Remove">&times;</button>`;
    chip.querySelector("button").onclick = () => {
      state.pendingAttachments.splice(i, 1);
      renderAttachmentPreview();
      updateSendButton();
    };
    els.attachmentPreview.appendChild(chip);
  });
}

async function uploadFiles(files) {
  for (const file of files) {
    const form = new FormData();
    form.append("file", file);
    let res;
    try {
      res = await fetch("/api/upload", { method: "POST", credentials: "include", body: form });
    } catch {
      throw new Error("Upload failed. Is the server running?");
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Upload failed");
    }
    const data = await res.json();
    state.pendingAttachments.push(data);
  }
  renderAttachmentPreview();
  updateSendButton();
}

async function sendMessage(text) {
  const content = (text || els.promptInput.value).trim();
  const attachments = [...state.pendingAttachments];
  if ((!content && !attachments.length) || state.isStreaming) return;

  const adminPin = await requireAdminPinForChat(content);
  if (adminPin === false) return;

  if (!state.currentChatId && !state.currentIsTemp) {
    const res = await api(`/api/chats?temp=false`, { method: "POST" });
    const chat = await res.json();
    state.currentChatId = chat.id;
  }

  els.promptInput.value = "";
  state.pendingAttachments = [];
  renderAttachmentPreview();
  autoResizeTextarea();
  updateSendButton();
  updateComposerPlaceholder();

  const userMsg = { role: "user", content, attachments };
  state.messages.push(userMsg);
  els.thread.appendChild(buildUserTurn(content, attachments));
  showWelcome(false);
  scrollToBottom();

  await streamResponse(adminPin || null);
}

function closeSidebarMobile() {
  els.sidebar.classList.remove("open");
  els.sidebarOverlay.classList.remove("visible");
}

function openSettings() {
  els.settingsName.value = state.prefs.displayName || state.user?.username || "";
  
  // Backwards compatibility for people who had dark chatBg but now use themes
  let themeVal = state.prefs.theme;
  if (!themeVal) themeVal = "system";
  const themeSelect = $("#settingsTheme");
  if (themeSelect) themeSelect.value = themeVal;

  els.settingsAvatarBgMode.value = state.prefs.profileAvatarBgMode || "system";
  els.settingsAvatarBg.value = state.prefs.profileAvatarBg || "#303030";
  els.settingsAvatarBg.disabled = els.settingsAvatarBgMode.value === "system";
  els.settingsPreviewName.textContent = els.settingsName.value || "You";
  els.settingsPreviewAvatar.innerHTML = avatarHtml();
  if (!state.prefs.avatar) els.settingsPreviewAvatar.textContent = userInitial();
  
  api("/api/settings")
    .then(res => res.json())
    .then(data => {
      els.settingsTwoFa.checked = data.two_fa_enabled;
      els.settingsNotifications.checked = data.notifications_enabled;
    })
    .catch(err => console.error("Could not load server settings", err));

  els.settingsOverlay.classList.remove("hidden");
}

function updateSettingsPreview() {
  const name = els.settingsName.value.trim() || state.user?.username || "You";
  els.settingsPreviewName.textContent = name;
  els.settingsPreviewAvatar.textContent = name.charAt(0).toUpperCase();
}

function setupSpeechRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    els.btnMic.disabled = true;
    els.btnMic.title = "Voice not supported in this browser";
    return;
  }
  state.recognition = new SR();
  state.recognition.continuous = false;
  state.recognition.interimResults = true;
  if (navigator.language) {
    state.recognition.lang = navigator.language;
  }

  state.recognition.onstart = () => {
    state.isListening = true;
    els.btnMic.classList.add("listening");
    els.composerHint.textContent = "Listening... tap mic to stop";
    if (state.goTalkActive) els.goTalkStatus.textContent = "Listening...";
  };

  state.recognition.onend = () => {
    state.isListening = false;
    els.btnMic.classList.remove("listening");
    els.composerHint.textContent = "Go Ai can make mistakes. Check important info.";
    updateSendButton();
  };

  state.recognition.onresult = (e) => {
    let transcript = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      transcript += e.results[i][0].transcript;
    }
    els.promptInput.value = transcript;
    autoResizeTextarea();
    updateSendButton();
    if (state.goTalkActive && els.goTalkTranscript) {
      els.goTalkTranscript.textContent = transcript;
    }
    if (e.results[e.results.length - 1].isFinal && transcript.trim()) {
      state.recognition.stop();
      if (state.goTalkActive) els.goTalkStatus.textContent = "Processing...";
      sendMessage(transcript.trim());
    }
  };

  state.recognition.onerror = () => {
    state.isListening = false;
    els.btnMic.classList.remove("listening");
    if (state.goTalkActive) {
      els.btnGoTalk.classList.remove("active");
      state.goTalkActive = false;
    }
  };
}

function toggleMic() {
  if (!state.recognition) {
    showToast("Voice features are not supported on this device/browser.");
    return;
  }
  if (state.isListening) {
    state.recognition.stop();
    if (state.goTalkActive) {
      state.goTalkActive = false;
      els.btnGoTalk.classList.remove("active");
    }
    return;
  }
  if (state.isStreaming) return;
  try {
    state.recognition.start();
  } catch (err) {
    showToast("Microphone access denied or unavailable.");
  }
}

function toggleGoTalk() {
  if (!state.recognition) {
    showToast("Voice features are not supported on this device/browser.");
    return;
  }
  if (state.goTalkActive) {
    state.goTalkActive = false;
    els.btnGoTalk.classList.remove("active");
    els.goTalkScreen.classList.add("hidden");
    if (state.isListening) state.recognition.stop();
  } else {
    state.goTalkActive = true;
    els.btnGoTalk.classList.add("active");
    els.goTalkScreen.classList.remove("hidden");
    els.goTalkTranscript.textContent = "Say something...";
    els.goTalkStatus.textContent = "Connecting...";
    
    if (!state.isListening && !state.isStreaming) {
      try {
        state.recognition.start();
      } catch (e) {
        showToast("Microphone access denied or unavailable.");
      }
    } else if (state.isListening) {
      els.goTalkStatus.textContent = "Listening...";
    }
  }
}

function showAuth() {
  els.authScreen.classList.remove("hidden");
  els.app.classList.add("hidden");
}

function showApp() {
  els.authScreen.classList.add("hidden");
  els.app.classList.remove("hidden");
}

async function fetchTimeout(url, options = {}, ms = 6000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms);
  try {
    return await fetch(url, { ...options, signal: ctrl.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function bootApp() {
  let configRes;
  try {
    configRes = await fetchTimeout("/api/config", { credentials: "include" });
  } catch {
    els.loginError.textContent =
      "Cannot reach API. Run: python run.py  then open http://localhost:8000";
    return;
  }
  if (!configRes.ok) {
    showAuth();
    els.loginError.textContent = "API not available. Start the server with: python run.py";
    return;
  }
  const config = await configRes.json();
  document.title = config.app_title;

  const meRes = await fetchTimeout("/api/me", { credentials: "include" });
  if (!meRes.ok) {
    showAuth();
    return;
  }
  state.user = await meRes.json();
  state.adminUnlocked = !!state.user.admin_unlocked;
  loadPrefs();
  setProfileUI();
  showApp();

  if (localStorage.getItem("goai_sidebar") === "hidden") {
    toggleSidebar(true);
  } else {
    updateSidebarToggleButton();
  }
  updateComposerPlaceholder();

  try {
    await initChatFromRoute();
    await handleShareFromUrl();
  } catch (err) {
    console.warn("Chat load failed:", err);
  }
}

async function handleShareFromUrl() {
  const params = new URLSearchParams(window.location.search);
  let token = params.get("share");
  const pathMatch = window.location.pathname.match(/^\/share\/([a-zA-Z0-9_-]+)$/i);
  if (pathMatch) {
    token = pathMatch[1];
  }
  if (!token) return;
  state.pendingShareToken = token;
  try {
    const res = await fetch(`/api/share/${token}`);
    if (!res.ok) return;
    const shared = await res.json();
    state.currentChatId = null;
    state.currentIsTemp = true;
    state.messages = shared.messages || [];
    setPageTitle("Shared: " + shared.title, true);
    renderThread();
    showWelcome(false);
    
    // Convert overlay to a bottom banner
    els.sharedChatTitle.textContent = shared.title || "Shared chat";
    els.sharedChatMeta.textContent = `Shared by ${shared.shared_by} · ${shared.message_count} messages`;
    els.sharedChatOverlay.classList.remove("hidden");
    els.sharedChatOverlay.classList.add("banner-mode");
    $("#composerForm").style.display = "none";
  } catch {
    /* ignore */
  }
}

async function continueSharedChat() {
  if (!state.pendingShareToken) return;
  try {
    const res = await api(`/api/share/${state.pendingShareToken}/continue`, { method: "POST" });
    const chat = await res.json();
    state.pendingShareToken = null;
    els.sharedChatOverlay.classList.remove("banner-mode");
    els.sharedChatOverlay.classList.add("hidden");
    $("#composerForm").style.display = "";
    window.history.replaceState({}, "", window.location.pathname);
    state.currentChatId = chat.id;
    state.currentIsTemp = chat.is_temp;
    state.messages = chat.messages || [];
    setPageTitle(chat.title, chat.is_temp);
    syncChatUrl(chat.id, true);
    await refreshChats(state.searchQuery);
    renderThread();
    showToast("Shared chat added to your account");
  } catch (err) {
    showToast(err.message);
  }
}

function setupAuth() {
  $$(".auth-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      $$(".auth-tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      const isLogin = tab.dataset.tab === "login";
      els.loginForm.classList.toggle("hidden", !isLogin);
      els.signupForm.classList.toggle("hidden", isLogin);
      els.loginError.textContent = "";
      els.signupError.textContent = "";
    });
  });

  async function afterAuthSuccess() {
    const meRes = await fetch("/api/me", { credentials: "include" });
    if (!meRes.ok) {
      throw new Error("Login succeeded but session failed. Hard-refresh and try again.");
    }
    state.user = await meRes.json();
    state.adminUnlocked = !!state.user.admin_unlocked;
    loadPrefs();
    setProfileUI();
    showApp();
    updateComposerPlaceholder();
    if (localStorage.getItem("goai_sidebar") === "hidden") {
      toggleSidebar(true);
    } else {
      updateSidebarToggleButton();
    }
    try {
      await initChatFromRoute();
      await handleShareFromUrl();
    } catch (err) {
      console.warn("Chat init failed:", err);
    }
  }

  els.loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    els.loginError.textContent = "";
    const fd = new FormData(els.loginForm);
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: fd.get("email"), password: fd.get("password") }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
      
      if (data.requires_verification || data.requires_2fa) {
        state.pendingUserId = data.user_id;
        els.otpOverlay.classList.remove("hidden");
        els.otpInput.value = "";
        els.otpInput.focus();
        return;
      }
      
      await afterAuthSuccess();
    } catch (err) {
      els.loginError.textContent = err.message;
    }
  });

  els.signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    els.signupError.textContent = "";
    const fd = new FormData(els.signupForm);
    try {
      const res = await fetch("/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: fd.get("username"),
          email: fd.get("email"),
          password: fd.get("password"),
          agreed_terms: fd.get("agreed_terms") === "on",
          notifications_enabled: fd.get("notifications_enabled") === "on",
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Signup failed");
      
      if (data.requires_verification) {
        state.pendingUserId = data.user_id;
        els.otpOverlay.classList.remove("hidden");
        els.otpInput.value = "";
        els.otpInput.focus();
        return;
      }
      
      await afterAuthSuccess();
    } catch (err) {
      els.signupError.textContent = err.message;
    }
  });

  els.otpCancel.addEventListener("click", () => els.otpOverlay.classList.add("hidden"));
  els.otpConfirm.addEventListener("click", async () => {
    els.otpError.textContent = "";
    const code = els.otpInput.value.trim();
    if (!code) return;
    try {
      const res = await fetch("/api/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: state.pendingUserId, otp_code: code }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Invalid code");
      els.otpOverlay.classList.add("hidden");
      await afterAuthSuccess();
    } catch (err) {
      els.otpError.textContent = err.message;
    }
  });

  els.btnForgotPassword.addEventListener("click", () => {
    els.forgotPasswordOverlay.classList.remove("hidden");
    els.forgotPasswordError.textContent = "";
    els.forgotPasswordEmail.value = "";
  });
  els.forgotPasswordCancel.addEventListener("click", () => els.forgotPasswordOverlay.classList.add("hidden"));
  els.forgotPasswordSend.addEventListener("click", async () => {
    els.forgotPasswordError.textContent = "";
    const email = els.forgotPasswordEmail.value.trim();
    if (!email) return;
    try {
      await api("/api/forgot-password", { method: "POST", body: JSON.stringify({ email }) });
      els.forgotPasswordOverlay.classList.add("hidden");
      els.resetPasswordOverlay.classList.remove("hidden");
      els.resetPasswordError.textContent = "";
    } catch (err) {
      els.forgotPasswordError.textContent = err.message;
    }
  });

  els.resetPasswordCancel.addEventListener("click", () => els.resetPasswordOverlay.classList.add("hidden"));
  els.resetPasswordConfirm.addEventListener("click", async () => {
    els.resetPasswordError.textContent = "";
    const token = els.resetPasswordCode.value.trim();
    const new_password = els.resetPasswordNew.value;
    if (!token || !new_password) return;
    try {
      await api("/api/reset-password", { method: "POST", body: JSON.stringify({ token, new_password }) });
      els.resetPasswordOverlay.classList.add("hidden");
      showToast("Password updated. Please log in.");
    } catch (err) {
      els.resetPasswordError.textContent = err.message;
    }
  });
}

function setupChat() {
  els.composerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage();
  });
  els.promptInput.addEventListener("input", () => {
    autoResizeTextarea();
    updateSendButton();
    updateComposerPlaceholder();
  });
  els.promptInput.addEventListener("focus", updateComposerPlaceholder);
  els.promptInput.addEventListener("blur", updateComposerPlaceholder);
  els.promptInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  els.btnNewChat.addEventListener("click", () => createChat(false));
  els.btnTempChat.addEventListener("click", () => createChat(true));
  els.btnMic.addEventListener("click", toggleMic);
  els.btnGoTalk?.addEventListener("click", toggleGoTalk);
  els.btnGoTalkClose?.addEventListener("click", () => {
    if (state.goTalkActive) toggleGoTalk();
  });
  els.btnAttach.addEventListener("click", () => els.fileInput.click());
  els.fileInput.addEventListener("change", async (e) => {
    const files = [...(e.target.files || [])];
    e.target.value = "";
    if (!files.length) return;
    try {
      await uploadFiles(files);
      showToast(files.length > 1 ? "Files attached" : "File attached");
    } catch (err) {
      showToast(err.message);
    }
  });

  els.shareClose.addEventListener("click", () => els.shareOverlay.classList.add("hidden"));
  els.shareCopy.addEventListener("click", () => {
    navigator.clipboard.writeText(els.shareLinkInput.value);
    showToast("Share link copied");
  });
  els.sharedChatDismiss.addEventListener("click", () => {
    els.sharedChatOverlay.classList.add("hidden");
    state.pendingShareToken = null;
    window.history.replaceState({}, "", window.location.pathname);
  });
  els.sharedChatContinue.addEventListener("click", () => continueSharedChat());

  els.btnHideSidebar.addEventListener("click", () => toggleSidebar(true));
  els.btnSidebarToggle.addEventListener("click", () => {
    if (state.sidebarHidden) {
      toggleSidebar(false);
    } else if (window.innerWidth <= 768) {
      els.sidebar.classList.add("open");
      els.sidebarOverlay.classList.add("visible");
    } else {
      toggleSidebar(true);
    }
  });
  els.sidebarOverlay.addEventListener("click", closeSidebarMobile);

  els.btnToggleSidebar.addEventListener("click", () => {
    toggleSidebar(!state.sidebarHidden);
    els.profileMenu.classList.add("hidden");
  });

  els.profileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = !els.profileMenu.classList.contains("hidden");
    els.profileMenu.classList.toggle("hidden", open);
    els.profileBtn.setAttribute("aria-expanded", !open);
  });

  document.addEventListener("click", (e) => {
    if (!els.profileWrap.contains(e.target)) {
      els.profileMenu.classList.add("hidden");
      els.profileBtn.setAttribute("aria-expanded", "false");
    }
    if (!e.target.closest(".chat-row")) {
      $$(".chat-dropdown").forEach((d) => d.classList.add("hidden"));
    }
  });

  els.btnCustomize.addEventListener("click", () => {
    els.profileMenu.classList.add("hidden");
    openSettings();
  });

  els.btnApiKeys?.addEventListener("click", () => {
    els.profileMenu.classList.add("hidden");
    openApiKeysModal();
  });

  els.apiKeysClose?.addEventListener("click", () => {
    els.apiKeysOverlay.classList.add("hidden");
  });

  els.apiKeyCreate?.addEventListener("click", async () => {
    try {
      const res = await api("/api/keys", {
        method: "POST",
        body: JSON.stringify({ name: "Default" }),
      });
      const data = await res.json();
      els.apiKeyNewDisplay.textContent = `Copy your key now (shown once): ${data.key}`;
      els.apiKeyNewDisplay.classList.remove("hidden");
      els.apiKeyNewDisplay.style.color = "#10a37f";
      els.apiKeyNewDisplay.style.fontSize = "13px";
      els.apiKeyNewDisplay.style.wordBreak = "break-all";
      els.apiKeyNewDisplay.style.userSelect = "all";
      await loadApiKeys();
    } catch (err) {
      els.apiKeyNewDisplay.textContent = err.message;
      els.apiKeyNewDisplay.classList.remove("hidden");
      els.apiKeyNewDisplay.style.color = "#f87171";
    }
  });

  els.chatSearch?.addEventListener("input", () => {
    clearTimeout(state.searchTimer);
    state.searchTimer = setTimeout(() => refreshChats(els.chatSearch.value), 280);
  });

  window.addEventListener("popstate", async () => {
    if (state.isStreaming || !state.user) return;
    const routeId = parseRouteChatId();
    if (routeId && routeId !== state.currentChatId) {
      try {
        await loadChat(routeId, { skipUrl: true });
      } catch {
        showToast("Chat not found");
      }
    } else if (!routeId && state.currentChatId) {
      await createChat(false);
    }
  });

  els.settingsCancel.addEventListener("click", () => {
    els.settingsOverlay.classList.add("hidden");
  });

  els.settingsName.addEventListener("input", updateSettingsPreview);



  els.settingsAvatarBgMode?.addEventListener("change", () => {
    const isSystem = els.settingsAvatarBgMode.value === "system";
    els.settingsAvatarBg.disabled = isSystem;
    if (prefs.profileAvatarBgMode === "system") {
      const isLight = document.documentElement.getAttribute("data-theme") === "light";
      document.documentElement.style.setProperty("--profile-avatar-bg", isLight ? "#e5e5e5" : "#303030");
    } else {
      document.documentElement.style.setProperty("--profile-avatar-bg", prefs.profileAvatarBg || "#303030");
    }
  });

  els.settingsAvatarBg?.addEventListener("input", () => {
    if (els.settingsAvatarBgMode.value === "custom") {
      document.documentElement.style.setProperty(
        "--profile-avatar-bg",
        els.settingsAvatarBg.value
      );
    }
  });

  if (window.speechSynthesis) {
    const populateVoices = () => {
      if (!els.settingsGoTalkVoice) return;
      const voices = window.speechSynthesis.getVoices();
      if (!voices.length) return;
      els.settingsGoTalkVoice.innerHTML = '<option value="">System Default</option>';
      voices.forEach(v => {
        const opt = document.createElement("option");
        opt.value = v.name;
        opt.textContent = `${v.name} (${v.lang})`;
        els.settingsGoTalkVoice.appendChild(opt);
      });
      if (state.prefs.goTalkVoice) {
        els.settingsGoTalkVoice.value = state.prefs.goTalkVoice;
      }
    };
    window.speechSynthesis.onvoiceschanged = populateVoices;
    populateVoices();
  }

  els.settingsAvatar.addEventListener("change", (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      state.prefs.avatar = reader.result;
      els.settingsPreviewAvatar.innerHTML = `<img src="${reader.result}" alt="" />`;
    };
    reader.readAsDataURL(file);
  });

  els.settingsSave.addEventListener("click", async () => {
    state.prefs.displayName = els.settingsName.value.trim();
    const themeSelect = $("#settingsTheme");
    if (themeSelect) state.prefs.theme = themeSelect.value;
    state.prefs.profileAvatarBgMode = els.settingsAvatarBgMode.value;
    state.prefs.profileAvatarBg = els.settingsAvatarBg.value;
    if (els.settingsGoTalkVoice) state.prefs.goTalkVoice = els.settingsGoTalkVoice.value;
    savePrefs();
    setProfileUI();
    renderThread();
    
    try {
      await api("/api/settings", {
        method: "POST",
        body: JSON.stringify({
          two_fa_enabled: els.settingsTwoFa.checked,
          notifications_enabled: els.settingsNotifications.checked
        })
      });
    } catch (err) {
      console.error("Could not save server settings", err);
    }
    
    els.settingsOverlay.classList.add("hidden");
    showToast("Profile updated");
  });

  els.btnAdminPanel.addEventListener("click", () => {
    els.profileMenu.classList.add("hidden");
    openAdminPanel();
  });

  els.adminPanelClose.addEventListener("click", () => {
    els.adminPanelOverlay.classList.add("hidden");
  });

  els.btnLogout.addEventListener("click", async () => {
    els.profileMenu.classList.add("hidden");
    try {
      await fetch("/api/logout", { method: "POST", credentials: "include" });
    } catch {
      /* ignore network errors — still log out locally */
    }
    state.user = null;
    state.adminUnlocked = false;
    state.messages = [];
    state.currentChatId = null;
    state.currentIsTemp = false;
    state.tempChats = [];
    state.historyChats = [];
    // Clear session-related UI
    if (els.thread) els.thread.innerHTML = "";
    if (els.historyChatList) els.historyChatList.innerHTML = "";
    showAuth();
  });

  $$(".suggestion").forEach((btn) => {
    btn.addEventListener("click", () => sendMessage(btn.dataset.prompt));
  });
}

function hideSplash() {
  if (!els.splash) return;
  const elapsed = Date.now() - bootStartTime;
  const remaining = Math.max(0, 3500 - elapsed);
  setTimeout(() => {
    els.splash.classList.add("hide");
    setTimeout(() => { els.splash.style.display = "none"; }, 500);
  }, remaining);
}

async function init() {
  try {
    setupAuth();
    setupChat();
    setupSpeechRecognition();
  } catch (err) {
    console.error("Go Ai setup error:", err);
    hideSplash();
    return;
  }

  try {
    await bootApp();
  } catch (err) {
    console.error("Go Ai boot error:", err);
    if (els.loginError) {
      els.loginError.textContent =
        "Cannot connect. Run: python run.py  then open http://localhost:8000";
    }
  } finally {
    hideSplash();
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
