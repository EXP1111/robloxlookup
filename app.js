const queryInput = document.getElementById("query");
const searchButton = document.getElementById("searchButton");
const results = document.getElementById("results");
const errorBox = document.getElementById("error");

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
  results.classList.add("hidden");
}

function showResults(data) {
  errorBox.classList.add("hidden");
  results.classList.remove("hidden");

  const user = data.user;
  const groups = data.groups?.data || [];
  const badges = data.badges?.data || [];

  results.innerHTML = `
    <div class="card">
      <div class="profile">
        <img class="avatar" src="${data.avatar || ""}" alt="Avatar" />
        <div>
          <h2>${user.displayName}</h2>
          <p>@${user.name}</p>
          <p class="muted">User ID: ${user.id}</p>
        </div>
      </div>
      <p>${user.description || "No description."}</p>
      <div class="stats">
        <div><span>Friends</span><strong>${data.friends.count}</strong></div>
        <div><span>Followers</span><strong>${data.followers.count}</strong></div>
        <div><span>Following</span><strong>${data.following.count}</strong></div>
      </div>
    </div>

    <div class="card">
      <h3>Groups (${groups.length})</h3>
      <ul>
        ${groups
          .slice(0, 12)
          .map(
            (g) => `
            <li>
              <strong>${g.group.name}</strong>
              <span class="muted">${g.role.name}</span>
            </li>`
          )
          .join("")}
      </ul>
    </div>

    <div class="card">
      <h3>Badges (${badges.length})</h3>
      <ul>
        ${badges
          .slice(0, 12)
          .map(
            (b) => `
            <li>
              <strong>${b.name}</strong>
              <span class="muted">${b.created}</span>
            </li>`
          )
          .join("")}
      </ul>
    </div>
  `;
}

async function fetchUser() {
  const query = queryInput.value.trim();
  if (!query) {
    showError("Enter a username or user id.");
    return;
  }

  results.classList.add("hidden");
  errorBox.classList.add("hidden");

  try {
    const response = await fetch(`/api/user?query=${encodeURIComponent(query)}`);
    const data = await response.json();

    if (!response.ok) {
      showError(data.detail || "Request failed.");
      return;
    }

    showResults(data);
  } catch (error) {
    showError("Network error. Try again.");
  }
}

searchButton.addEventListener("click", fetchUser);
queryInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    fetchUser();
  }
});
