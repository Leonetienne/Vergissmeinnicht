// Calls operations from the registry through the REST API with the session and CSRF token.
let routes = null;

function csrfToken() {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

export async function op(name, args = {}) {
  routes = routes || JSON.parse(document.getElementById("vm-api-routes").textContent);
  const [method, template] = routes[name];
  const rest = { ...args };
  const url = template.replace(/\{(\w+)\}/g, (_, key) => {
    const value = rest[key];
    delete rest[key];
    return encodeURIComponent(value);
  });
  const init = { method, headers: { "X-CSRFToken": csrfToken() }, credentials: "same-origin" };
  let target = url;
  if (method === "GET" || method === "DELETE") {
    const query = new URLSearchParams(rest).toString();
    if (query) target += "?" + query;
  } else {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(rest);
  }
  let response;
  try {
    response = await fetch(target, init);
  } catch {
    throw new ApiError("Server not reachable", 0);
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new ApiError(data.error || `Request failed (${response.status})`, response.status);
  return data;
}

// Runs async steps one after another so the server sees changes in the order they were made.
export function queue() {
  let chain = Promise.resolve();
  return (step) => {
    const run = chain.then(step);
    chain = run.catch(() => {});
    return run;
  };
}
