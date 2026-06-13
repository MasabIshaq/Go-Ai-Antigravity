import os

js = open('static/js/app.js', 'r', encoding='utf-8').read()

# Add server settings state
js = js.replace('adminStats: $("#adminStats"),', 'adminStats: $("#adminStats"),\n  btnServerToggle: $("#btnServerToggle"),')

if "forgotPassword" not in js:
    # Append the JS logic at the end
    js += """

// Forgot Password
const fpBtn = document.createElement("button");
fpBtn.type = "button";
fpBtn.className = "btn-secondary";
fpBtn.style.marginTop = "10px";
fpBtn.textContent = "Forgot password?";
fpBtn.onclick = async () => {
  const email = prompt("Enter your email address to reset password:");
  if (!email) return;
  try {
    const res = await api("/api/forgot-password", { method: "POST", body: JSON.stringify({ email }) });
    const code = prompt("Check your email for the reset code.\\nEnter reset code:");
    if (!code) return;
    const newPass = prompt("Enter new password (min 6 chars):");
    if (!newPass) return;
    await api("/api/reset-password", { method: "POST", body: JSON.stringify({ token: code, new_password: newPass }) });
    alert("Password reset successful. You can now log in.");
  } catch (err) {
    alert("Error: " + err.message);
  }
};
document.querySelector("#loginForm").appendChild(fpBtn);

"""

# Change openAdminPanel to fetch server_stopped status
if "stats.server_stopped" not in js:
    js = js.replace('api("/api/admin/stats", { method: "POST", body: JSON.stringify({ pin }) }),', 'api("/api/admin/stats", { method: "POST", body: JSON.stringify({ pin }) }),')

    admin_panel_insert = """
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
"""
    js = js.replace('renderAdminReports(reports);', admin_panel_insert + '\n    renderAdminReports(reports);')

open('static/js/app.js', 'w', encoding='utf-8').write(js)

# Wait, I need to update the python api_admin_stats to include server_stopped
py = open('app/main.py', 'r', encoding='utf-8').read()
if "'server_stopped'" not in py:
    py = py.replace('return get_admin_stats()', 'stats = get_admin_stats()\n    stats["server_stopped"] = get_server_stopped()\n    return stats')
    open('app/main.py', 'w', encoding='utf-8').write(py)

print("Done")
