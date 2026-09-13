with open('static/js/app.js', 'a', encoding='utf-8') as f:
    f.write('''\n
els.btnForgotPassword.addEventListener("click", () => {
  els.forgotPasswordError.textContent = "";
  els.forgotPasswordEmail.value = els.loginForm.email.value || "";
  els.forgotPasswordOverlay.classList.remove("hidden");
});

els.forgotPasswordCancel.addEventListener("click", () => {
  els.forgotPasswordOverlay.classList.add("hidden");
});

els.forgotPasswordSend.addEventListener("click", async () => {
  const email = els.forgotPasswordEmail.value.trim();
  if (!email) {
    els.forgotPasswordError.textContent = "Please enter your email";
    return;
  }
  els.forgotPasswordSend.disabled = true;
  els.forgotPasswordSend.textContent = "Sending...";
  try {
    await api("/api/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email })
    });
    els.forgotPasswordOverlay.classList.add("hidden");
    els.resetPasswordError.textContent = "";
    els.resetPasswordCode.value = "";
    els.resetPasswordNew.value = "";
    els.resetPasswordOverlay.classList.remove("hidden");
  } catch (err) {
    els.forgotPasswordError.textContent = err.message;
  } finally {
    els.forgotPasswordSend.disabled = false;
    els.forgotPasswordSend.textContent = "Send Code";
  }
});

els.resetPasswordCancel.addEventListener("click", () => {
  els.resetPasswordOverlay.classList.add("hidden");
});

els.resetPasswordConfirm.addEventListener("click", async () => {
  const email = els.forgotPasswordEmail.value.trim();
  const code = els.resetPasswordCode.value.trim();
  const new_password = els.resetPasswordNew.value;
  if (!code || !new_password) {
    els.resetPasswordError.textContent = "Please fill all fields";
    return;
  }
  els.resetPasswordConfirm.disabled = true;
  els.resetPasswordConfirm.textContent = "Resetting...";
  try {
    await api("/api/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ email, code, new_password })
    });
    els.resetPasswordOverlay.classList.add("hidden");
    showToast("Password reset successfully. Please log in.");
  } catch (err) {
    els.resetPasswordError.textContent = err.message;
  } finally {
    els.resetPasswordConfirm.disabled = false;
    els.resetPasswordConfirm.textContent = "Reset Password";
  }
});
''')
print('Appended')
