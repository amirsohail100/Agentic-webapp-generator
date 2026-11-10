const API_URL = "/api/generate";

const FILES = {
    streamlit: { field: "streamlit_code", filename: "streamlit_app.py", label: "Streamlit" },
    fastapi: { field: "fastapi_code", filename: "backend_main.py", label: "FastAPI" },
    html: { field: "html_code", filename: "index.html", label: "HTML" },
};

const specInput = document.getElementById("spec");
const charCount = document.getElementById("charCount");
const generateBtn = document.getElementById("generateBtn");
const statusBox = document.getElementById("status");
const output = document.getElementById("output");
const promptsDetails = document.getElementById("promptsDetails");
const promptsOutput = document.getElementById("promptsOutput");
const toast = document.getElementById("toast");
const tabs = document.querySelectorAll(".tab");

let generatedResult = null;
let activeTab = "streamlit";
let toastTimer = null;

specInput.addEventListener("input", updateCharCount);
generateBtn.addEventListener("click", generateCode);
tabs.forEach((tab) => tab.addEventListener("click", () => selectTab(tab.dataset.tab)));

function updateCharCount() {
    const length = specInput.value.length;
    charCount.textContent = `${length} character${length === 1 ? "" : "s"}`;
}

function showStatus(type, message) {
    statusBox.className = `status visible ${type}`;
    statusBox.innerHTML = "";

    if (type === "loading") {
        const spinner = document.createElement("span");
        spinner.className = "spinner";
        statusBox.appendChild(spinner);
    }

    statusBox.appendChild(document.createTextNode(message));
}

function hideStatus() {
    statusBox.className = "status";
    statusBox.innerHTML = "";
}

function setLoading(isLoading) {
    generateBtn.disabled = isLoading;
    generateBtn.textContent = isLoading ? "Generating..." : "Generate code";
}

async function readErrorMessage(response) {
    try {
        const data = await response.json();
        if (typeof data.detail === "string") {
            return data.detail;
        }
        return JSON.stringify(data.detail);
    } catch (_) {
        return `Request failed with status ${response.status}.`;
    }
}

async function generateCode() {
    const spec = specInput.value.trim();

    if (!spec) {
        showStatus("error", "Please describe the application you want to build.");
        specInput.focus();
        return;
    }

    setLoading(true);
    showStatus("loading", "Generating code. This can take a minute, please wait...");

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ payload_with_models: spec }),
        });

        if (response.status === 429) {
            throw new Error("Too many requests. Please wait a minute and try again.");
        }

        if (!response.ok) {
            const message = await readErrorMessage(response);
            throw new Error(message);
        }

        generatedResult = await response.json();
        hideStatus();
        renderResult();
    } catch (error) {
        showStatus("error", error.message || "Something went wrong. Please try again.");
    } finally {
        setLoading(false);
    }
}

function renderResult() {
    tabs.forEach((tab) => {
        tab.disabled = false;
    });

    renderPrompts();
    selectTab(activeTab);
}

function renderPrompts() {
    const prompts = generatedResult.llm_gen_system_prompts;

    if (!prompts || prompts.length === 0) {
        promptsDetails.hidden = true;
        return;
    }

    promptsOutput.textContent = JSON.stringify(prompts, null, 2);
    promptsDetails.hidden = false;
}

function selectTab(tabName) {
    activeTab = tabName;

    tabs.forEach((tab) => {
        tab.classList.toggle("active", tab.dataset.tab === tabName);
    });

    if (!generatedResult) {
        return;
    }

    const file = FILES[tabName];
    const code = generatedResult[file.field] || "";

    output.innerHTML = "";

    const toolbar = document.createElement("div");
    toolbar.className = "toolbar";

    const filename = document.createElement("span");
    filename.className = "filename";
    filename.textContent = file.filename;

    const actions = document.createElement("div");
    actions.className = "actions";

    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "secondary";
    copyBtn.textContent = "Copy";
    copyBtn.addEventListener("click", () => copyCode(code));

    const downloadBtn = document.createElement("button");
    downloadBtn.type = "button";
    downloadBtn.className = "secondary";
    downloadBtn.textContent = "Download";
    downloadBtn.addEventListener("click", () => downloadCode(code, file.filename));

    actions.append(copyBtn, downloadBtn);
    toolbar.append(filename, actions);

    const pre = document.createElement("pre");
    const codeEl = document.createElement("code");
    codeEl.textContent = code || `No ${file.label} code was generated.`;
    pre.appendChild(codeEl);

    output.append(toolbar, pre);
}

async function copyCode(code) {
    try {
        await navigator.clipboard.writeText(code);
        showToast("Copied to clipboard");
    } catch (_) {
        showToast("Copy failed. Please select and copy manually.", true);
    }
}

function downloadCode(code, filename) {
    const blob = new Blob([code], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    showToast(`Downloaded ${filename}`);
}

function showToast(message, isError = false) {
    toast.textContent = message;
    toast.style.color = isError ? "var(--danger)" : "var(--success)";
    toast.classList.add("visible");

    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("visible"), 2000);
}

updateCharCount();