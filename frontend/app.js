// ============ State ============
const state = {
  token: localStorage.getItem("token"),
  user: JSON.parse(localStorage.getItem("user") || "null"),
  cart: JSON.parse(localStorage.getItem("cart") || "[]"),
  products: [],
  currentView: "catalog",
}

// ============ API Client ============
const api = {
  async request(url, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...options.headers,
    }

    if (state.token) {
      headers["Authorization"] = `Bearer ${state.token}`
    }

    try {
      const response = await fetch(url, { ...options, headers })

      if (response.status === 401) {
        this.logout()
        throw new Error("Сессия истекла. Войдите снова.")
      }

      if (response.status === 204) return null

      const data = response.headers
        .get("content-type")
        ?.includes("application/json")
        ? await response.json()
        : await response.text()

      if (!response.ok) {
        throw new Error(data.detail || "Ошибка запроса")
      }

      return data
    } catch (error) {
      showNotification(error.message, "error")
      throw error
    }
  },

  // Auth
  register(data) {
    return this.request("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    })
  },

  login(data) {
    return this.request("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    })
  },

  // Products
  getProducts() {
    return this.request("/api/v1/guitars/?limit=100")
  },

  getProduct(id) {
    return this.request(`/api/v1/guitars/${id}`)
  },

  getRecommendations(id) {
    return this.request(`/api/v1/guitars/${id}/recommendations`)
  },

  askAssistant(message) {
    return this.request("/api/v1/guitars/assistant", {
      method: "POST",
      body: JSON.stringify({ message }),
    })
  },

  // Orders
  createOrder(items) {
    return this.request("/api/v1/orders/", {
      method: "POST",
      body: JSON.stringify({
        username: state.user?.username,
        items: items,
      }),
    })
  },

  getOrders() {
    return this.request("/api/v1/orders/")
  },
}

// ============ Helpers ============
function $(selector) {
  return document.querySelector(selector)
}

function $$(selector) {
  return document.querySelectorAll(selector)
}

function showNotification(message, type = "success") {
  const notification = document.createElement("div")
  notification.className = `notification ${type}`
  notification.textContent = message
  document.body.appendChild(notification)

  setTimeout(() => notification.remove(), 3000)
}

function formatPrice(price) {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(price)
}

function getGuitarEmoji(type) {
  const map = {
    электрогитара: "🎸",
    "акустическая гитара": "🪕",
    "классическая гитара": "🎻",
    "бас гитара": "🎸",
  }
  return map[type] || "🎸"
}

// ============ Auth ============
function setAuth(token, user) {
  state.token = token
  state.user = user
  localStorage.setItem("token", token)
  localStorage.setItem("user", JSON.stringify(user))
  updateAuthUI()
}

function logout() {
  state.token = null
  state.user = null
  localStorage.removeItem("token")
  localStorage.removeItem("user")
  updateAuthUI()
  showView("catalog")
}

function updateAuthUI() {
  const authLinks = $("#auth-links")
  if (state.user) {
    authLinks.innerHTML = `
            <span style="color: #86868b;">👤 ${state.user.username}</span>
            <a href="#" id="logout-btn" class="nav-link">Выход</a>
        `
    $("#logout-btn").addEventListener("click", (e) => {
      e.preventDefault()
      logout()
    })
  } else {
    authLinks.innerHTML = `<a href="#" data-view="login" class="nav-link">Вход</a>`
    authLinks.querySelector("a").addEventListener("click", (e) => {
      e.preventDefault()
      openModal("login-modal")
    })
  }
}

// ============ Cart ============
function addToCart(product) {
  const existing = state.cart.find((item) => item.product_id === product.id)
  if (existing) {
    existing.quantity += 1
  } else {
    state.cart.push({
      product_id: product.id,
      sku: product.sku,
      title: product.title,
      brand: product.brand,
      price: product.price,
      quantity: 1,
      type: product.type,
      body_wood: product.body_wood,
      neck_wood: product.neck_wood,
      fretboard_wood: product.fretboard_wood,
      fret_count: product.fret_count,
      scale_length: product.scale_length,
      pickup_config: product.pickup_config,
      image_url: product.image_url,
    })
  }
  saveCart()
  showNotification(`${product.title} добавлен в корзину!`)
}

function removeFromCart(productId) {
  state.cart = state.cart.filter((item) => item.product_id !== productId)
  saveCart()
  renderCart()
}

function updateQuantity(productId, delta) {
  const item = state.cart.find((item) => item.product_id === productId)
  if (item) {
    item.quantity += delta
    if (item.quantity <= 0) {
      removeFromCart(productId)
    } else {
      saveCart()
      renderCart()
    }
  }
}

function saveCart() {
  localStorage.setItem("cart", JSON.stringify(state.cart))
  updateCartCount()
}

function updateCartCount() {
  const count = state.cart.reduce((sum, item) => sum + item.quantity, 0)
  $("#cart-count").textContent = count
}

function getCartTotal() {
  return state.cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
}

// ============ Views ============
function showView(view) {
  state.currentView = view
  $$(".nav-link").forEach((link) => link.classList.remove("active"))
  const activeLink = document.querySelector(`[data-view="${view}"]`)
  if (activeLink) activeLink.classList.add("active")

  if (view === "catalog") {
    renderCatalog()
  } else if (view === "orders") {
    if (!state.user) {
      openModal("login-modal")
      return
    }
    showOrders()
  } else if (view === "login") {
    openModal("login-modal")
  }
}

async function renderCatalog() {
  $("#app").innerHTML = `
        <section id="catalog-view">
            <h1>Каталог гитар</h1>
            <div class="filters">
                <select id="type-filter">
                    <option value="">Все типы</option>
                    <option value="электрогитара">Электрогитары</option>
                    <option value="акустическая гитара">Акустические</option>
                    <option value="классическая гитара">Классические</option>
                    <option value="бас гитара">Бас-гитары</option>
                </select>
                <input type="text" id="search-input" placeholder="Поиск по названию...">
            </div>
            <div id="products-grid" class="products-grid">
                <div class="empty-state">
                    <div class="empty-state-icon">⏳</div>
                    <p>Загрузка каталога...</p>
                </div>
            </div>
        </section>
    `

  try {
    state.products = await api.getProducts()
    renderProducts(state.products)

    $("#type-filter").addEventListener("change", filterProducts)
    $("#search-input").addEventListener("input", filterProducts)
  } catch (error) {
    $("#products-grid").innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">❌</div>
                <p>Не удалось загрузить каталог</p>
            </div>
        `
  }
}

function filterProducts() {
  const type = $("#type-filter").value
  const search = $("#search-input").value.toLowerCase()

  const filtered = state.products.filter((p) => {
    const matchType = !type || p.type === type
    const matchSearch =
      !search ||
      p.title.toLowerCase().includes(search) ||
      p.brand.toLowerCase().includes(search)
    return matchType && matchSearch
  })

  renderProducts(filtered)
}

function renderProducts(products) {
  const grid = $("#products-grid")

  if (products.length === 0) {
    grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-state-icon">🔍</div>
                <p>Ничего не найдено</p>
            </div>
        `
    return
  }

  grid.innerHTML = products
    .map(
      (p) => `
        <div class="product-card" data-product-id="${p.id}">
            <div class="product-image">${getGuitarEmoji(p.type)}</div>
            <div class="product-info">
                <div class="product-brand">${p.brand}</div>
                <div class="product-title">${p.title}</div>
                <div class="product-specs">
                    ${p.type} • ${p.body_wood} • ${p.pickup_config}
                </div>
                <div class="product-price">${formatPrice(p.price)}</div>
                <button class="add-to-cart-btn" data-add-to-cart="${p.id}">
                    В корзину
                </button>
            </div>
        </div>
    `,
    )
    .join("")

  // Product card click
  $$(".product-card").forEach((card) => {
    card.addEventListener("click", (e) => {
      if (!e.target.matches(".add-to-cart-btn")) {
        showProductDetail(parseInt(card.dataset.productId))
      }
    })
  })

  // Add to cart buttons
  $$("[data-add-to-cart]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation()
      const product = state.products.find(
        (p) => p.id === parseInt(btn.dataset.addToCart),
      )
      if (product) addToCart(product)
    })
  })
}

async function showProductDetail(productId) {
  try {
    const product = await api.getProduct(productId)
    let recs = []
    try {
      recs = await api.getRecommendations(productId)
    } catch (e) {
      // recommendations might be empty
    }

    $("#product-detail").innerHTML = `
            <div class="product-detail">
                <div class="product-detail-image">${getGuitarEmoji(product.type)}</div>
                <div class="product-detail-info">
                    <div class="brand">${product.brand}</div>
                    <h2>${product.title}</h2>
                    <div class="price">${formatPrice(product.price)}</div>
                    
                    <table class="specs-table">
                        <tr><td>Артикул</td><td>${product.sku}</td></tr>
                        <tr><td>Тип</td><td>${product.type}</td></tr>
                        <tr><td>Корпус</td><td>${product.body_wood}</td></tr>
                        <tr><td>Гриф</td><td>${product.neck_wood}</td></tr>
                        <tr><td>Накладка</td><td>${product.fretboard_wood}</td></tr>
                        <tr><td>Ладов</td><td>${product.fret_count}</td></tr>
                        <tr><td>Мензура</td><td>${product.scale_length}"</td></tr>
                        <tr><td>Звукосниматели</td><td>${product.pickup_config}</td></tr>
                    </table>
                    
                    <button class="add-to-cart-btn" id="detail-add-to-cart">
                        Добавить в корзину
                    </button>
                </div>
                
                ${
                  recs.length > 0
                    ? `
                    <div class="recommendations">
                        <h3>🎯 Похожие товары</h3>
                        <div class="recs-grid">
                            ${recs
                              .map(
                                (r) => `
                                <div class="rec-card" data-rec-id="${r.id}">
                                    <div style="font-size: 2rem; text-align: center;">${getGuitarEmoji(r.type)}</div>
                                    <div style="font-weight: 600; margin: 0.5rem 0;">${r.brand}</div>
                                    <div style="font-size: 0.85rem; color: #86868b;">${r.title}</div>
                                    <div style="font-weight: bold; margin-top: 0.5rem;">${formatPrice(r.price)}</div>
                                </div>
                            `,
                              )
                              .join("")}
                        </div>
                    </div>
                `
                    : ""
                }
            </div>
        `

    $("#detail-add-to-cart").addEventListener("click", () => addToCart(product))

    $$("[data-rec-id]").forEach((card) => {
      card.addEventListener("click", () => {
        closeModal("product-modal")
        setTimeout(() => showProductDetail(parseInt(card.dataset.recId)), 300)
      })
    })

    openModal("product-modal")
  } catch (error) {
    showNotification("Не удалось загрузить товар", "error")
  }
}

function renderCart() {
  const cartItems = $("#cart-items")
  const cartTotal = $("#cart-total")
  const checkoutBtn = $("#checkout-btn")

  if (state.cart.length === 0) {
    cartItems.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🛒</div>
                <p>Корзина пуста</p>
            </div>
        `
    cartTotal.innerHTML = ""
    checkoutBtn.style.display = "none"
    return
  }

  cartItems.innerHTML = state.cart
    .map(
      (item) => `
        <div class="cart-item">
            <div class="cart-item-image">${getGuitarEmoji(item.type)}</div>
            <div class="cart-item-info">
                <div class="cart-item-title">${item.brand} ${item.title}</div>
                <div style="color: #86868b; font-size: 0.9rem;">${formatPrice(item.price)}</div>
            </div>
            <div class="cart-item-controls">
                <button class="qty-btn" data-qty-minus="${item.product_id}">−</button>
                <span>${item.quantity}</span>
                <button class="qty-btn" data-qty-plus="${item.product_id}">+</button>
                <button class="remove-btn" data-remove="${item.product_id}">🗑</button>
            </div>
            <div style="font-weight: bold; min-width: 100px; text-align: right;">
                ${formatPrice(item.price * item.quantity)}
            </div>
        </div>
    `,
    )
    .join("")

  cartTotal.innerHTML = `<div class="cart-total">Итого: ${formatPrice(getCartTotal())}</div>`
  checkoutBtn.style.display = "block"

  $$("[data-qty-minus]").forEach((btn) => {
    btn.addEventListener("click", () =>
      updateQuantity(parseInt(btn.dataset.qtyMinus), -1),
    )
  })

  $$("[data-qty-plus]").forEach((btn) => {
    btn.addEventListener("click", () =>
      updateQuantity(parseInt(btn.dataset.qtyPlus), 1),
    )
  })

  $$("[data-remove]").forEach((btn) => {
    btn.addEventListener("click", () =>
      removeFromCart(parseInt(btn.dataset.remove)),
    )
  })
}

async function showOrders() {
  try {
    const response = await api.getOrders()
    const orders = response.orders || []

    if (orders.length === 0) {
      $("#orders-list").innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📦</div>
                    <p>У вас пока нет заказов</p>
                </div>
            `
    } else {
      $("#orders-list").innerHTML = orders
        .map(
          (order) => `
                <div class="order-card">
                    <div class="order-header">
                        <div>
                            <strong>Заказ #${order.id}</strong>
                            <div style="color: #86868b; font-size: 0.85rem;">
                                ${new Date().toLocaleDateString("ru-RU")}
                            </div>
                        </div>
                        <span class="order-status ${order.status}">${order.status}</span>
                    </div>
                    <ul class="order-items">
                        ${order.items
                          .map(
                            (item) => `
                            <li class="order-item">
                                <span>${item.brand} ${item.title} × ${item.quantity}</span>
                                <span>${formatPrice(item.price * item.quantity)}</span>
                            </li>
                        `,
                          )
                          .join("")}
                    </ul>
                    <div style="text-align: right; font-weight: bold; margin-top: 0.5rem;">
                        Итого: ${formatPrice(order.items.reduce((sum, i) => sum + i.price * i.quantity, 0))}
                    </div>
                </div>
            `,
        )
        .join("")
    }

    openModal("orders-modal")
  } catch (error) {
    showNotification("Не удалось загрузить заказы", "error")
  }
}

// ============ Modals ============
function openModal(modalId) {
  $(`#${modalId}`).classList.remove("hidden")

  if (modalId === "cart-modal") {
    renderCart()
  }
}

function closeModal(modalId) {
  $(`#${modalId}`).classList.add("hidden")
}

// ============ Chat Widget (с памятью диалога) ============
const chatState = {
  sessionId: localStorage.getItem("chat_session_id") || null,
  messages: [],
}

async function sendChatMessage(message) {
  const messagesEl = $("#chat-messages")

  // Добавляем сообщение пользователя
  const userMsg = document.createElement("div")
  userMsg.className = "message user"
  userMsg.textContent = message
  messagesEl.appendChild(userMsg)
  chatState.messages.push({ role: "user", content: message })

  // Индикатор загрузки
  const loadingMsg = document.createElement("div")
  loadingMsg.className = "message loading"
  loadingMsg.innerHTML = '🤖 Печатает<span class="typing-dots">...</span>'
  messagesEl.appendChild(loadingMsg)
  messagesEl.scrollTop = messagesEl.scrollHeight

  try {
    const response = await api.request("/api/v1/guitars/assistant", {
      method: "POST",
      body: JSON.stringify({
        message: message,
        session_id: chatState.sessionId,
      }),
    })

    // Сохраняем session_id после первого ответа
    if (response.session_id && !chatState.sessionId) {
      chatState.sessionId = response.session_id
      localStorage.setItem("chat_session_id", chatState.sessionId)
    }

    loadingMsg.remove()

    const botMsg = document.createElement("div")
    botMsg.className = "message bot"
    botMsg.textContent = response.reply
    messagesEl.appendChild(botMsg)
    chatState.messages.push({ role: "assistant", content: response.reply })

    // Добавляем кнопку "Новый диалог" после нескольких сообщений
    if (chatState.messages.length >= 4 && !$("#new-chat-btn")) {
      const newChatBtn = document.createElement("button")
      newChatBtn.id = "new-chat-btn"
      newChatBtn.className = "new-chat-btn"
      newChatBtn.innerHTML = "🔄 Новый диалог"
      newChatBtn.onclick = resetChat
      messagesEl.appendChild(newChatBtn)
    }
  } catch (error) {
    loadingMsg.remove()
    const errorMsg = document.createElement("div")
    errorMsg.className = "message bot"
    errorMsg.textContent = "Извините, произошла ошибка. Попробуйте позже."
    messagesEl.appendChild(errorMsg)
  }

  messagesEl.scrollTop = messagesEl.scrollHeight
}

function resetChat() {
  // Очищаем историю на сервере
  if (chatState.sessionId) {
    api
      .request(`/api/v1/guitars/assistant/history/${chatState.sessionId}`, {
        method: "DELETE",
      })
      .catch(() => {})
  }

  // Очищаем локальное состояние
  chatState.sessionId = null
  chatState.messages = []
  localStorage.removeItem("chat_session_id")

  // Перерисовываем чат
  const messagesEl = $("#chat-messages")
  messagesEl.innerHTML = `
        <div class="message bot">
            Привет! Я AI-консультант Guitar Shop. Помогу подобрать идеальную гитару! 🎸
            <br><small style="color: #86868b;">Я помню контекст нашего разговора</small>
        </div>
    `
}

// ============ Event Listeners ============
document.addEventListener("DOMContentLoaded", () => {
  // Init
  updateAuthUI()
  updateCartCount()
  showView("catalog")

  // Navigation
  $$(".nav-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault()
      const view = link.dataset.view
      if (view) showView(view)
    })
  })

  // Cart button
  $("#cart-btn").addEventListener("click", () => openModal("cart-modal"))

  // Checkout
  $("#checkout-btn").addEventListener("click", async () => {
    if (!state.user) {
      closeModal("cart-modal")
      openModal("login-modal")
      showNotification("Войдите, чтобы оформить заказ", "error")
      return
    }

    if (state.cart.length === 0) return

    try {
      await api.createOrder(state.cart)
      state.cart = []
      saveCart()
      closeModal("cart-modal")
      showNotification("Заказ успешно оформлен! 🎉")
    } catch (error) {
      showNotification("Ошибка при оформлении заказа", "error")
    }
  })

  // Orders link
  $('[data-view="orders"]')?.addEventListener("click", (e) => {
    e.preventDefault()
    showView("orders")
  })

  // Close modals
  $$(".close-btn").forEach((btn) => {
    btn.addEventListener("click", () => closeModal(btn.dataset.modal))
  })

  // Click outside modal
  $$(".modal").forEach((modal) => {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.classList.add("hidden")
      }
    })
  })

  // Switch between login/register
  $$(".switch-form a").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault()
      closeModal("login-modal")
      closeModal("register-modal")
      openModal(link.dataset.modalTarget)
    })
  })

  // Login form
  $("#login-form").addEventListener("submit", async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const data = Object.fromEntries(formData)

    try {
      const response = await api.login(data)
      // Decode JWT to get user info
      const payload = JSON.parse(atob(response.access_token.split(".")[1]))
      setAuth(response.access_token, {
        id: payload.sub,
        email: payload.email,
        username: payload.username,
        is_admin: payload.is_admin,
      })
      closeModal("login-modal")
      showNotification("Добро пожаловать! 👋")
      e.target.reset()
    } catch (error) {
      $("#login-error").textContent = error.message
    }
  })

  // Register form
  $("#register-form").addEventListener("submit", async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const data = Object.fromEntries(formData)

    try {
      const user = await api.register(data)
      closeModal("register-modal")
      showNotification("Регистрация успешна! Теперь войдите.")
      openModal("login-modal")
      e.target.reset()
    } catch (error) {
      $("#register-error").textContent = error.message
    }
  })

  // Chat widget
  $("#chat-toggle").addEventListener("click", () => {
    $("#chat-window").classList.toggle("hidden")
  })

  $("#chat-close").addEventListener("click", () => {
    $("#chat-window").classList.add("hidden")
  })

  $("#chat-form").addEventListener("submit", (e) => {
    e.preventDefault()
    const input = $("#chat-input")
    const message = input.value.trim()
    if (message) {
      sendChatMessage(message)
      input.value = ""
    }
  })
})
