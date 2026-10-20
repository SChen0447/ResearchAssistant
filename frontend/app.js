(function () {
  "use strict";

  var STREAM_URL = "/research_assistant/ask_stream";
  var USER_KEY = "ra_user_id";
  var SESSION_KEY = "ra_session_id";
  var URL_SPLIT = /(https?:\/\/[^\s<>"']+)/g;
  var URL_TEST = /^https?:\/\//;

  var messagesEl = document.getElementById("messages");
  var emptyStateEl = document.getElementById("empty-state");
  var inputEl = document.getElementById("input");
  var sendBtn = document.getElementById("send");
  var newChatBtn = document.getElementById("new-chat");

  var busy = false;

  /* ---------------- 身份与会话 ---------------- */

  function uuid() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return window.crypto.randomUUID();
    }
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = (Math.random() * 16) | 0;
      var v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  function getUserId() {
    var id = localStorage.getItem(USER_KEY);
    if (!id) {
      id = uuid();
      localStorage.setItem(USER_KEY, id);
    }
    return id;
  }

  function getSessionId() {
    var id = sessionStorage.getItem(SESSION_KEY);
    if (!id) {
      id = uuid();
      sessionStorage.setItem(SESSION_KEY, id);
    }
    return id;
  }

  function resetSession() {
    sessionStorage.setItem(SESSION_KEY, uuid());
  }

  /* ---------------- 渲染 ---------------- */

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function appendRichText(container, text) {
    var parts = String(text).split(URL_SPLIT);
    parts.forEach(function (part) {
      if (!part) {
        return;
      }
      if (URL_TEST.test(part)) {
        var link = document.createElement("a");
        link.href = part;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = part;
        container.appendChild(link);
      } else {
        container.appendChild(document.createTextNode(part));
      }
    });
  }

  function createMessage(role, text) {
    var row = document.createElement("div");
    row.className = "msg msg--" + role;

    var avatar = document.createElement("div");
    avatar.className = "msg-avatar";
    avatar.textContent = role === "user" ? "我" : "AI";

    var bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    if (role === "user") {
      bubble.textContent = text;
    } else {
      appendRichText(bubble, text);
    }

    row.appendChild(avatar);
    row.appendChild(bubble);
    return row;
  }

  function addMessage(role, text) {
    emptyStateEl.hidden = true;
    var row = createMessage(role, text);
    messagesEl.appendChild(row);
    scrollToBottom();
    return row;
  }

  function addError(text) {
    emptyStateEl.hidden = true;
    var row = createMessage("assistant", text);
    row.classList.add("msg--error");
    messagesEl.appendChild(row);
    scrollToBottom();
    return row;
  }

  function showTyping() {
    emptyStateEl.hidden = true;
    var row = document.createElement("div");
    row.className = "msg msg--assistant msg--typing";

    var avatar = document.createElement("div");
    avatar.className = "msg-avatar";
    avatar.textContent = "AI";

    var bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    for (var i = 0; i < 3; i++) {
      var dot = document.createElement("span");
      dot.className = "dot";
      bubble.appendChild(dot);
    }

    row.appendChild(avatar);
    row.appendChild(bubble);
    messagesEl.appendChild(row);
    scrollToBottom();
    return row;
  }

  /* ---------------- 交互 ---------------- */

  function autoGrow() {
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + "px";
  }

  function setComposerEnabled(enabled) {
    inputEl.disabled = !enabled;
    sendBtn.disabled = !enabled;
  }

  function extractErrorDetail(res, data) {
    if (data && typeof data.detail === "string") {
      return data.detail;
    }
    if (data && data.detail) {
      return JSON.stringify(data.detail);
    }
    return "HTTP " + res.status;
  }

  async function send(question) {
    var q = String(question === undefined ? inputEl.value : question).trim();
    if (!q || busy) {
      return;
    }

    busy = true;
    addMessage("user", q);
    inputEl.value = "";
    autoGrow();
    var typingRow = showTyping();
    setComposerEnabled(false);

    var bubble = null;        // 流式气泡，收到首个 token 时才创建
    var fullText = "";        // 累积的完整回答
    var streamError = null;   // 流中途由后端下发的错误
    var done = false;         // 是否收到 [DONE] 结束标记

    function ensureBubble() {
      if (bubble) {
        return;
      }
      typingRow.remove();
      emptyStateEl.hidden = true;
      var row = createMessage("assistant", "");
      bubble = row.querySelector(".msg-bubble");
      messagesEl.appendChild(row);
    }

    try {
      var res = await fetch(STREAM_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "text/event-stream"
        },
        body: JSON.stringify({
          user_id: getUserId(),
          session_id: getSessionId(),
          question: q
        })
      });

      // 校验失败等非流式错误仍返回普通 JSON
      if (!res.ok || !res.body) {
        typingRow.remove();
        var data = null;
        try {
          data = await res.json();
        } catch (e) {
          data = null;
        }
        addError("请求失败：" + extractErrorDetail(res, data));
        return;
      }

      var reader = res.body.getReader();
      var decoder = new TextDecoder("utf-8");
      var buffer = "";

      while (!done) {
        var chunk = await reader.read();
        if (chunk.done) {
          break;
        }
        buffer += decoder.decode(chunk.value, { stream: true });

        // SSE 以空行分隔事件，逐条拆出 "data: ..." 行
        var sep;
        while ((sep = buffer.indexOf("\n\n")) !== -1) {
          var event = buffer.slice(0, sep).trim();
          buffer = buffer.slice(sep + 2);
          if (!event.startsWith("data:")) {
            continue;
          }
          var payload = event.slice(5).trim();

          if (payload === "[DONE]") {
            done = true;
            break;
          }

          var obj;
          try {
            obj = JSON.parse(payload);
          } catch (e) {
            continue;
          }

          if (obj.error) {
            streamError = obj.error;
          } else if (obj.delta) {
            ensureBubble();
            fullText += obj.delta;
            // 逐 token 追加文本节点，实现打字机效果
            bubble.appendChild(document.createTextNode(obj.delta));
            scrollToBottom();
          }
        }
      }

      typingRow.remove();

      if (fullText) {
        // 流结束后整体重排一次，使回答中的链接可点击
        bubble.textContent = "";
        appendRichText(bubble, fullText);
        if (streamError) {
          bubble.appendChild(document.createTextNode("\n\n（回答中断：" + streamError + "）"));
        }
      } else if (streamError) {
        addError("回答中断：" + streamError);
      } else {
        addMessage("assistant", "（未返回内容）");
      }
    } catch (err) {
      typingRow.remove();
      addError("网络错误：" + (err && err.message ? err.message : err));
    } finally {
      busy = false;
      setComposerEnabled(true);
      inputEl.focus();
    }
  }

  function newChat() {
    if (busy) {
      return;
    }
    var rows = messagesEl.querySelectorAll(".msg");
    rows.forEach(function (row) {
      row.remove();
    });
    emptyStateEl.hidden = false;
    resetSession();
    inputEl.value = "";
    autoGrow();
    inputEl.focus();
  }

  /* ---------------- 事件绑定 ---------------- */

  sendBtn.addEventListener("click", function () {
    send();
  });

  newChatBtn.addEventListener("click", newChat);

  inputEl.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });

  inputEl.addEventListener("input", autoGrow);

  document.querySelectorAll(".suggestion").forEach(function (btn) {
    btn.addEventListener("click", function () {
      send(btn.getAttribute("data-q"));
    });
  });

  inputEl.focus();
})();
