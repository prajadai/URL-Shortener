const registerTab = document.getElementById("registerTab");
const loginTab = document.getElementById("loginTab");
const registerForm = document.getElementById("registerForm");
const loginForm = document.getElementById("loginForm");
const createLinkForm = document.getElementById("createLinkForm");
const linksTableBody = document.getElementById("linksTableBody");
const rowTemplate = document.getElementById("rowTemplate");
const alertBox = document.getElementById("alert");
const sessionState = document.getElementById("sessionState");
const logoutBtn = document.getElementById("logoutBtn");
const tokenKey = "url_shortener_token";

function getToken() {
  return localStorage.getItem(tokenKey);
}

function setToken(token) {
  localStorage.setItem(tokenKey, token);
}

function clearToken() {
  localStorage.removeItem(tokenKey);
}

function showAlert(message, isError = false) {
  alertBox.textContent = message;
  alertBox.classList.remove("hidden");
  alertBox.style.background = isError ? "#ffeef0" : "#eef8ff";
  alertBox.style.borderColor = isError ? "#ffc6cd" : "#c8e7f6";
}

function hideAlert() {
  alertBox.classList.add("hidden");
}

function switchAuthView(showLogin) {
  if (showLogin) {
    loginTab.classList.add("active");
    registerTab.classList.remove("active");
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
    return;
  }

  registerTab.classList.add("active");
  loginTab.classList.remove("active");
  registerForm.classList.remove("hidden");
  loginForm.classList.add("hidden");
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parseResponse(response) {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function getErrorMessage(data, fallback) {
  if (!data) {
    return fallback;
  }
  if (typeof data === "string") {
    return data;
  }
  if (data.detail) {
    return data.detail;
  }
  return fallback;
}

function setSessionText() {
  sessionState.textContent = getToken() ? "Signed in" : "Not signed in";
}

async function fetchLinks() {
  const token = getToken();
  linksTableBody.innerHTML = "";

  if (!token) {
    setSessionText();
    return;
  }

  const response = await fetch("/links", {
    headers: {
      ...authHeaders()
    }
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    showAlert(getErrorMessage(data, "Could not load links."), true);
    return;
  }

  const links = data?.results || [];
  for (const link of links) {
    renderRow(link);
  }

  if (!links.length) {
    const emptyRow = document.createElement("tr");
    emptyRow.innerHTML = '<td colspan="4">No links yet. Create your first short link.</td>';
    linksTableBody.appendChild(emptyRow);
  }

  setSessionText();
}

function renderRow(link) {
  const fragment = rowTemplate.content.cloneNode(true);
  const row = fragment.querySelector("tr");
  const shortLink = row.querySelector(".short-link");
  const originalCol = row.querySelector(".original-col");
  const clickCol = row.querySelector(".click-col");
  const statsBtn = row.querySelector(".stats-btn");
  const editBtn = row.querySelector(".edit-btn");
  const deleteBtn = row.querySelector(".delete-btn");

  const shortUrl = `${window.location.origin}/${link.short_code}`;

  shortLink.href = shortUrl;
  shortLink.textContent = shortUrl;
  originalCol.textContent = link.original_url;

  statsBtn.addEventListener("click", async () => {
    const response = await fetch(`/${link.short_code}/stats`, {
      headers: {
        ...authHeaders()
      }
    });

    const data = await parseResponse(response);
    if (!response.ok) {
      showAlert(getErrorMessage(data, "Could not fetch stats."), true);
      return;
    }

    clickCol.textContent = String(data.clicks ?? 0);
  });

  editBtn.addEventListener("click", async () => {
    const newUrl = window.prompt("Enter new URL:", link.original_url);
    if (!newUrl) {
      return;
    }

    const response = await fetch(`/${link.short_code}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders()
      },
      body: JSON.stringify({ original_url: newUrl })
    });

    const data = await parseResponse(response);

    if (!response.ok) {
      showAlert(getErrorMessage(data, "Could not update link."), true);
      return;
    }

    showAlert("Link updated successfully.");
    await fetchLinks();
  });

  deleteBtn.addEventListener("click", async () => {
    const confirmed = window.confirm("Delete this short URL?");
    if (!confirmed) {
      return;
    }

    const response = await fetch(`/${link.short_code}`, {
      method: "DELETE",
      headers: {
        ...authHeaders()
      }
    });

    const data = await parseResponse(response);

    if (!response.ok) {
      showAlert(getErrorMessage(data, "Could not delete link."), true);
      return;
    }

    showAlert("Link deleted.");
    await fetchLinks();
  });

  linksTableBody.appendChild(fragment);
}

registerTab.addEventListener("click", () => switchAuthView(false));
loginTab.addEventListener("click", () => switchAuthView(true));

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideAlert();

  const payload = {
    username: registerForm.username.value.trim(),
    password: registerForm.password.value
  };

  const response = await fetch("/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    showAlert(getErrorMessage(data, "Registration failed."), true);
    return;
  }

  showAlert("Account created. Sign in from the Login tab.");
  registerForm.reset();
  switchAuthView(true);
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideAlert();

  const form = new URLSearchParams();
  form.append("username", loginForm.username.value.trim());
  form.append("password", loginForm.password.value);

  const response = await fetch("/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: form
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    showAlert(getErrorMessage(data, "Login failed."), true);
    return;
  }

  setToken(data.access_token);
  loginForm.reset();
  showAlert("Logged in successfully.");
  await fetchLinks();
});

createLinkForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideAlert();

  if (!getToken()) {
    showAlert("Sign in before creating links.", true);
    return;
  }

  const originalUrl = document.getElementById("urlInput").value.trim();

  const response = await fetch("/shorten_url", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders()
    },
    body: JSON.stringify({ original_url: originalUrl })
  });

  const data = await parseResponse(response);

  if (!response.ok) {
    showAlert(getErrorMessage(data, "Could not create short URL."), true);
    return;
  }

  createLinkForm.reset();
  showAlert("Short URL created.");
  await fetchLinks();
});

logoutBtn.addEventListener("click", () => {
  clearToken();
  linksTableBody.innerHTML = "";
  setSessionText();
  showAlert("Signed out.");
});

setSessionText();
fetchLinks();
