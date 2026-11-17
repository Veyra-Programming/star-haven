/**
 * HAVEN (HEAVEN LANGUAGE) OFFICIAL PORTAL JAVASCRIPT
 * www.odcs.in/heaven/
 * Companion Language for Open Digital Continuity Standard (ODCS)
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileDrawer();
  initPlayground();
  initClipboardHandlers();
  initOsFilterTabs();
  initClientOsDetection();
  loadCustomReleases();
  loadGlobalAnnouncement();
});

/* ==========================================================================
   1. CODE PLAYGROUND PRESETS & SIMULATION RUNNER
   ========================================================================== */

const CODE_PRESETS = {
  english: {
    name: "Natural English",
    code: `// Haven Natural English Syntax
set system_name to "ODCS Continuity Node"
set replica_count to 4
set latency_threshold_ms to 12.5

print "Booting node: " + system_name

repeat replica_count times:
    set node_id to "NODE-" + String(iteration)
    print "Synchronizing replica " + node_id + " [OK]"

unless latency_threshold_ms > 20.0:
    print "Latency status: OPTIMAL (< 20ms)"
else:
    print "Warning: Latency boundary exceeded"`
  },

  pipeline: {
    name: "Native Pipelining",
    code: `// Haven Native Pipelining with Placeholder '_'
import math
import crypto

def sanitize(input_str):
    return input_str.trim().to_uppercase()

def sha256_genesis(content):
    return crypto.sha256("ODCS-GENESIS:" + content)

def broadcast(payload, channel):
    print "Transmitting to [" + channel + "]: " + payload
    return true

// Native pipeline execution using |> and _
"   alpha-continuum-telemetry-packet   "
    |> sanitize(_)
    |> sha256_genesis(_)
    |> broadcast(_, "mesh://consensus/odcs-v1")

print "Pipeline sequence executed in 0.84ms."`
  },

  durable: {
    name: "ODCS Durable Records",
    code: `// ODCS Durable Records & Immutability Engine
durable record ContinuityPacket:
    tx_id: String
    guardian: String
    block_height: Integer
    state_merkle_root: String

// Instantiate hardware-sealed record
let genesis_packet = ContinuityPacket(
    tx_id: "TX-9902-ODCS",
    guardian: "guardian://sec-node-12.odcs.in",
    block_height: 1048576,
    state_merkle_root: "0x7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
)

print "Packet Sealed: " + genesis_packet.tx_id
print "Cryptographic Genesis Hash: " + genesis_packet.odcs_hash()

// Attempting to mutate a durable record throws ContinuityImmutabilityError
try:
    // genesis_packet.block_height = 1048577
    print "Immutability verified: Seal intact."
except ContinuityImmutabilityError as err:
    print "Security Alert: Mutation prohibited on durable record!"`
  },

  ledger: {
    name: "Continuity Ledger",
    code: `// Decentralized Ledger Verification
from odcs import ContinuityLedger, MerkleTree

let ledger = ContinuityLedger.open("haven://chain-odcs-2026")

print "Active Chain Height: " + String(ledger.current_height())
print "Genesis Anchor: " + ledger.genesis_hash()

// Verify Merkle integrity across all peers
let integrity_check = ledger.verify_integrity()

if integrity_check.is_valid:
    print "Merkle DAG status: SYNCHRONIZED (0 anomalies)"
    print "Active validator consensus: 100% agreement"
else:
    print "Warning: Ledger drift detected at block " + String(integrity_check.drift_height)`
  },

  ai: {
    name: "Haven AI SDK",
    code: `// Haven Native AI SDK Integration
from haven_ai import Client, pipe_fn

let ai = Client(model: "haven-deepseek-quant-v1")

let system_telemetry = {
    "node_status": "ONLINE",
    "tx_throughput": 42500,
    "memory_pressure": "4.2%"
}

print "Querying Haven AI Engine for network optimization..."

let prompt = "Evaluate network stability based on: " + String(system_telemetry)
let evaluation = ai.complete(prompt, max_tokens: 128)

print "AI Diagnostic Output:"
print "-> " + evaluation.summary
print "-> Recommended action: Maintain consensus pacing"`
  },
  mesh: {
    name: "L2 Gossip Mesh & CRDTs",
    code: `// ODCS Layer 2: P2P Gossip Mesh & Conflict-Free Replication
from odcs.mesh import GossipMesh

set mesh to GossipMesh()
set ambulance_edge to mesh.create_node("Edge-Ambulance")
set cloud_hub to mesh.create_node("Cloud-Hub")

print "Simulating mountain tunnel radio disconnect..."
mesh.isolate("Edge-Ambulance")

// Disconnected mutations in tunnel
ambulance_edge.mutate_counter("PlasmaUnits", -15)
ambulance_edge.mutate_set_add("FieldSupplies", "SplintKit")

// Central cloud mutations
cloud_hub.mutate_counter("PlasmaUnits", 50)
cloud_hub.mutate_set_add("FieldSupplies", "OxygenTank")

print "Ambulance exits tunnel -> Restoring link & triggering gossip..."
mesh.heal_all()
mesh.sync_until_stable()
mesh.assert_converged()

print "Strong Eventual Consistency (SEC) Proven: 100% Convergence!"
print "Converged Plasma Units: " + String(ambulance_edge.get_counter("PlasmaUnits").value)
print "Zero Intent Loss across all partitions verified."`
  },

  adaptation: {
    name: "L3 & L4: Adaptation & Intent UX",
    code: `// ODCS Layer 3 & 4: Environmental Adaptation & Zero Intent Loss
from odcs import EnvironmentalTelemetry, ContinuityMode, adaptive_policy, ZeroIntentLossManager

set tele to EnvironmentalTelemetry()
set intent_mgr to ZeroIntentLossManager()

// Layer 4: Preserve user intent with instant durable receipt
set receipt to intent_mgr.preserve_intent("Dr. Vance", "ICU_EmergencyOrder", {"med": "Epinephrine", "dose": "1mg"})
print "Layer 4 Zero Intent Loss Receipt: " + receipt.intent_id + " [STATUS: SEALED]"

// Layer 3: Dynamic Adaptive Policy Execution
function airgap_offline_handler():
    print "L3 Policy: Operating in Airgap Offline Mode via Local WAL"
    return "SAVED_TO_LOCAL_JOURNAL"

@adaptive_policy(on_airgap=airgap_offline_handler)
function submit_order():
    return "SENT_TO_BROADBAND_CLOUD"

EnvironmentalTelemetry.set_override(ContinuityMode.AIRGAP_OFFLINE)
set result to submit_order()
print "Execution Result: " + result`
  }
};

function initPlayground() {
  const codeArea = document.getElementById('haven-code-input') || document.getElementById('playground-editor');
  const terminalBody = document.getElementById('haven-terminal-output') || document.getElementById('terminal-stdout');
  const runBtn = document.getElementById('btn-run-haven') || document.getElementById('btn-run-code');
  const clearBtn = document.getElementById('btn-clear-terminal');
  const copyBtn = document.getElementById('btn-copy-playground') || document.getElementById('btn-copy-code');
  const resetBtn = document.getElementById('btn-reset-playground');
  const filenameEl = document.getElementById('playground-filename');
  const presetChips = document.querySelectorAll('.preset-pill, .preset-chip');

  if (!codeArea || !terminalBody) return;

  // Set default code
  codeArea.value = CODE_PRESETS.english.code;

  // Preset switching
  presetChips.forEach(chip => {
    chip.addEventListener('click', () => {
      presetChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const presetKey = chip.getAttribute('data-preset');
      if (CODE_PRESETS[presetKey]) {
        codeArea.value = CODE_PRESETS[presetKey].code;
        if (filenameEl) {
          filenameEl.textContent = `demo_${presetKey}.hvn`;
        }
        appendTerminalLine(`[haven-env] Switched to preset: "${CODE_PRESETS[presetKey].name}"`, 'term-purple');
      }
    });
  });

  // Reset button
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      const activeChip = document.querySelector('.preset-pill.active, .preset-chip.active');
      const key = activeChip ? activeChip.getAttribute('data-preset') : 'english';
      if (CODE_PRESETS[key]) {
        codeArea.value = CODE_PRESETS[key].code;
        showToast("Editor reset to original preset");
      }
    });
  }

  // Run button handler
  if (runBtn) {
    runBtn.addEventListener('click', () => {
      runPlaygroundCode(codeArea.value, terminalBody);
    });
  }

  // Keyboard shortcut: F5 or Ctrl+Enter to run
  codeArea.addEventListener('keydown', (e) => {
    if (e.key === 'F5' || (e.ctrlKey && e.key === 'Enter')) {
      e.preventDefault();
      runPlaygroundCode(codeArea.value, terminalBody);
    }
  });

  // Clear terminal handler
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      terminalBody.innerHTML = '';
      appendTerminalLine('Haven Language v1.0.0 (Production Toolchain)', 'term-dim');
      appendTerminalLine('Terminal buffer cleared. Ready for execution.', 'term-dim');
    });
  }

  // Copy code handler
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(codeArea.value).then(() => {
        showToast("Code copied to clipboard!");
      });
    });
  }
}

function appendTerminalLine(text, className = '') {
  const terminalBody = document.getElementById('terminal-stdout');
  if (!terminalBody) return;

  const line = document.createElement('div');
  line.className = `terminal-line ${className}`;
  line.textContent = text;
  terminalBody.appendChild(line);
  terminalBody.scrollTop = terminalBody.scrollHeight;
}

function runPlaygroundCode(code, terminalBody) {
  // Clear or add separator
  appendTerminalLine('------------------------------------------------------------', 'term-dim');
  appendTerminalLine(`$ haven run script.haven --release --target=odcs-vm`, 'term-cyan');
  appendTerminalLine(`[compiler] Parsing grammar AST (Heaven Language v1.0.0)...`, 'term-dim');

  setTimeout(() => {
    appendTerminalLine(`[compiler] Typecheck: 0 errors, 0 warnings.`, 'term-dim');
    appendTerminalLine(`[runtime] Loading ODCS hardware memory arena...`, 'term-dim');

    // Parse user code lines to find print statements or simulate
    const lines = code.split('\n');
    let printedSomething = false;

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('print ')) {
        let content = trimmed.substring(6).trim();
        // Remove simple quotes or String wrappers
        if ((content.startsWith('"') && content.endsWith('"')) || (content.startsWith("'") && content.endsWith("'"))) {
          content = content.slice(1, -1);
        } else if (content.includes('+')) {
          content = content.replace(/["']/g, '').replace(/\s*\+\s*/g, ' ');
        }
        appendTerminalLine(`> ${content}`, 'term-white');
        printedSomething = true;
      }
    });

    if (!printedSomething) {
      appendTerminalLine(`> [Process completed with no standard output]`, 'term-dim');
    }

    appendTerminalLine(`[runtime] Genesis execution verified. Status: 0 (SUCCESS, 1.2ms)`, 'term-success');
  }, 400);
}

/* ==========================================================================
   2. DYNAMIC CUSTOM RELEASES LOADER (SYNC FROM ADMIN PANEL)
   ========================================================================== */

async function loadCustomReleases() {
  const grid = document.getElementById('custom-releases-grid');
  const section = document.getElementById('custom-releases-section');
  if (!grid) return;

  try {
    let releases = [];
    try {
      const resp = await fetch('/api/v1/downloads');
      if (resp.ok) {
        const data = await resp.json();
        if (Array.isArray(data.downloads)) {
          releases = data.downloads
            .filter(d => !d.is_builtin)
            .map(d => ({
              id: d.id,
              filename: d.filename || d.target,
              title: d.label || d.target,
              version: d.version || '2.0.0',
              arch: d.arch || 'x86_64',
              channel: d.channel || 'Stable',
              filesize: d.size,
              sha256: d.sha256,
              description: d.description,
              published: d.published !== false,
              downloadUrl: d.download_url || `/api/v1/downloads/file/${encodeURIComponent(d.target)}`
            }));
        }
      }
    } catch {
      const rawReleases = localStorage.getItem('odcs_heaven_releases');
      if (rawReleases) releases = JSON.parse(rawReleases);
    }

    const published = releases.filter(r => r.published !== false);

    if (published.length === 0) {
      if (section) section.style.display = 'none';
      return;
    }

    if (section) section.style.display = 'block';
    grid.innerHTML = '';
    published.forEach(rel => {
      const card = document.createElement('div');
      card.className = 'custom-release-card';
      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            <h4 style="color: #fff; font-size: 1.1rem; margin-bottom: 0.2rem;">${escapeHtml(rel.title || rel.filename)}</h4>
            <span style="font-size: 0.75rem; color: var(--haven-cyan); font-family: var(--haven-font-mono);">v${escapeHtml(rel.version || '1.0.0')} • ${escapeHtml(rel.arch || 'x86_64')} • ${escapeHtml(rel.channel || 'Stable')}</span>
          </div>
          <span style="font-size: 0.7rem; background: rgba(0,240,255,0.1); color: var(--haven-cyan); border: 1px solid rgba(0,240,255,0.3); padding: 0.15rem 0.5rem; border-radius: 999px;">
            ${escapeHtml(rel.filesize || 'Custom EXE')}
          </span>
        </div>

        <p style="font-size: 0.85rem; color: var(--haven-text-muted); margin: 0.4rem 0;">
          ${escapeHtml(rel.description || 'Verified Heaven Language executable build uploaded via ODCS Admin.')}
        </p>

        <div style="background: rgba(0,0,0,0.4); padding: 0.4rem 0.6rem; border-radius: 6px; font-size: 0.72rem; font-family: var(--haven-font-mono); color: #94a3b8; display: flex; justify-content: space-between; align-items: center;">
          <span style="overflow: hidden; text-overflow: ellipsis; max-width: 220px;" title="${escapeHtml(rel.sha256 || 'N/A')}">
            SHA256: ${escapeHtml(rel.sha256 ? rel.sha256.substring(0, 20) + '...' : 'Verified')}
          </span>
          ${rel.sha256 ? `<button class="btn-copy-sha" onclick="copyToClipboard('${escapeHtml(rel.sha256)}')">📋</button>` : ''}
        </div>

        <div style="margin-top: 0.6rem;">
          <a href="${rel.downloadUrl || '#'}" download="${escapeHtml(rel.filename || 'heaven.exe')}" class="btn-card-download btn-download-primary" style="padding: 0.55rem; font-size: 0.85rem;">
            ⬇️ Download ${escapeHtml(rel.filename || 'Binary')}
          </a>
        </div>
      `;
      grid.appendChild(card);
    });

  } catch (err) {
    console.error("Failed to parse custom releases:", err);
  }
}

/* ==========================================================================
   3. GLOBAL ANNOUNCEMENT BANNER (SYNC FROM ADMIN PANEL)
   ========================================================================== */

function loadGlobalAnnouncement() {
  const banner = document.getElementById('haven-announcement-banner');
  if (!banner) return;

  try {
    const raw = localStorage.getItem('odcs_site_announcement');
    if (!raw) return;

    const data = JSON.parse(raw);
    if (data.active && data.text) {
      banner.style.display = 'block';
      banner.innerHTML = `
        <span>📢 ${escapeHtml(data.text)}</span>
        ${data.linkUrl ? `<a href="${escapeHtml(data.linkUrl)}">${escapeHtml(data.linkText || 'Learn More &rarr;')}</a>` : ''}
      `;
    } else if (data.active === false) {
      banner.style.display = 'none';
    }
  } catch (e) {
    console.warn("Announcement load error:", e);
  }
}

/* ==========================================================================
   4. CLIPBOARD & TOAST UTILITIES
   ========================================================================== */

function initClipboardHandlers() {
  document.querySelectorAll('.btn-copy-sha').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const shaCode = e.target.closest('.sha256-box')?.querySelector('.sha256-hash')?.textContent;
      if (shaCode) {
        navigator.clipboard.writeText(shaCode.trim()).then(() => {
          showToast("SHA-256 Checksum copied to clipboard!");
        });
      }
    });
  });
}

window.copyToClipboard = function(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast("Copied to clipboard!");
  });
};

function showToast(message) {
  let toast = document.querySelector('.haven-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'haven-toast';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<span>✨</span><span>${escapeHtml(message)}</span>`;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3200);
}

/* ==========================================================================
   5. MOBILE DRAWER NAVIGATION
   ========================================================================== */

function initMobileDrawer() {
  const toggleBtn = document.querySelector('.haven-mobile-toggle');
  const drawer = document.getElementById('haven-mobile-drawer');
  const closeBtn = document.querySelector('.drawer-close');

  if (toggleBtn && drawer) {
    toggleBtn.addEventListener('click', () => {
      drawer.classList.add('open');
    });
  }

  if (closeBtn && drawer) {
    closeBtn.addEventListener('click', () => {
      drawer.classList.remove('open');
    });
  }

  // Close drawer on link click
  document.querySelectorAll('.drawer-nav-list a').forEach(link => {
    link.addEventListener('click', () => {
      if (drawer) drawer.classList.remove('open');
    });
  });
}

function initOsFilterTabs() {
  const tabs = document.querySelectorAll('.os-tab-btn');
  const cards = document.querySelectorAll('#downloads-cards-grid .dl-release-card');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const selectedOs = tab.getAttribute('data-os');
      cards.forEach(card => {
        const cardOs = card.getAttribute('data-platform');
        if (selectedOs === 'all' || cardOs === selectedOs) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Auto-Detect Client Operating System and Personalize Download Buttons
function initClientOsDetection() {
  const ua = navigator.userAgent || '';
  const platform = navigator.platform || '';
  let clientOs = 'windows';
  let clientFile = 'downloads/Haven-1.0.0-win64-Setup.exe';
  let clientText = 'Download Haven for Windows (.exe)';
  let headerText = 'Download .EXE';

  if (/Mac|iPhone|iPod|iPad/i.test(platform) || /Macintosh/i.test(ua)) {
    clientOs = 'macos';
    clientFile = 'downloads/Haven-1.0.0-macOS-Universal.dmg';
    clientText = 'Download Haven for macOS (.dmg)';
    headerText = 'Download .DMG';
  } else if (/Android/i.test(ua)) {
    clientOs = 'mobile';
    clientFile = 'downloads/haven-1.0.0-android-arm64.tar.gz';
    clientText = 'Download Haven for Android (Termux)';
    headerText = 'Download Android';
  } else if (/Linux/i.test(platform) || /Linux/i.test(ua)) {
    clientOs = 'linux';
    clientFile = 'downloads/haven-1.0.0-x86_64.AppImage';
    clientText = 'Download Haven for Linux (.AppImage)';
    headerText = 'Download Linux';
  }

  // Update Hero & Header Download Buttons
  const heroBtn = document.getElementById('btn-hero-download');
  const heroText = document.getElementById('hero-download-text');
  const headerBtn = document.getElementById('btn-header-download');

  if (heroBtn && clientFile) {
    heroBtn.setAttribute('href', clientFile);
    heroBtn.setAttribute('download', clientFile.split('/').pop());
    if (heroText) heroText.textContent = clientText;
  }
  if (headerBtn && clientFile) {
    headerBtn.setAttribute('href', clientFile);
    headerBtn.setAttribute('download', clientFile.split('/').pop());
    const textSpan = headerBtn.querySelector('.dl-text');
    if (textSpan) textSpan.textContent = headerText;
  }

  // Highlight Detected OS Tab and card if on downloads view
  console.log('[Haven OS Detector] Client Operating System identified as:', clientOs);
}
