from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/subscription", response_class=HTMLResponse)
async def subscription_web_app() -> HTMLResponse:
    return HTMLResponse(
        """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Тарифы Sol de Mañana</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      --sun: #ffc857;
      --sun-soft: #fff1c7;
      --tomato: #ef3e36;
      --tomato-dark: #b9231f;
      --ink: #241818;
      --muted: #705f58;
      --cream: #fffaf0;
      --paper: #ffffff;
      --green: #16a36c;
      --line: rgba(36, 24, 24, 0.1);
      --shadow: 0 18px 48px rgba(185, 35, 31, 0.16);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 12% 4%, rgba(255, 200, 87, 0.7), transparent 28%),
        linear-gradient(150deg, #fff7dd 0%, #fffaf0 46%, #ffe0d9 100%);
    }

    .shell {
      width: min(100%, 760px);
      margin: 0 auto;
      padding: 22px 16px calc(24px + env(safe-area-inset-bottom));
    }

    .hero {
      padding: 18px 0 14px;
    }

    .brand {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 7px 12px;
      border: 1px solid rgba(239, 62, 54, 0.2);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.62);
      color: var(--tomato-dark);
      font-size: 14px;
      font-weight: 800;
    }

    .brand-mark {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: conic-gradient(from 30deg, var(--sun), var(--tomato), var(--sun));
      box-shadow: 0 0 0 4px rgba(255, 200, 87, 0.22);
    }

    h1 {
      margin: 18px 0 8px;
      max-width: 620px;
      font-size: clamp(30px, 7vw, 48px);
      line-height: 1;
      letter-spacing: 0;
    }

    .lead {
      margin: 0;
      max-width: 620px;
      color: var(--muted);
      font-size: 17px;
      line-height: 1.45;
    }

    .plans {
      display: grid;
      gap: 12px;
      margin-top: 18px;
    }

    .plan {
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.86);
      box-shadow: var(--shadow);
    }

    .plan.is-open {
      border-color: rgba(239, 62, 54, 0.36);
    }

    .plan-toggle {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      align-items: center;
      width: 100%;
      min-height: 76px;
      padding: 16px;
      border: 0;
      color: inherit;
      background: transparent;
      text-align: left;
      cursor: pointer;
    }

    .plan-name {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: baseline;
      font-weight: 900;
      font-size: 22px;
    }

    .plan-price {
      color: var(--tomato-dark);
      font-size: 15px;
      font-weight: 800;
    }

    .plan-summary {
      margin-top: 5px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.35;
    }

    .chevron {
      display: grid;
      place-items: center;
      width: 34px;
      height: 34px;
      border-radius: 50%;
      background: var(--sun-soft);
      color: var(--tomato-dark);
      font-size: 18px;
      font-weight: 900;
      transition: transform 0.2s ease;
    }

    .plan.is-open .chevron {
      transform: rotate(180deg);
    }

    .plan-body {
      display: none;
      padding: 0 16px 18px;
    }

    .plan.is-open .plan-body {
      display: block;
    }

    .divider {
      height: 1px;
      margin-bottom: 16px;
      background: var(--line);
    }

    .intro,
    .outro,
    .includes {
      margin: 0 0 12px;
      color: var(--ink);
      font-size: 15px;
      line-height: 1.45;
    }

    .includes {
      font-weight: 800;
      color: var(--tomato-dark);
    }

    ul {
      display: grid;
      gap: 8px;
      margin: 0 0 16px;
      padding: 0;
      list-style: none;
    }

    li {
      position: relative;
      padding-left: 25px;
      color: #3c2d29;
      font-size: 15px;
      line-height: 1.35;
    }

    li::before {
      content: "";
      position: absolute;
      left: 0;
      top: 0.48em;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--sun), var(--tomato));
    }

    .cta-row {
      display: grid;
      gap: 8px;
    }

    .cta {
      width: 100%;
      min-height: 48px;
      border: 0;
      border-radius: 8px;
      color: #fff;
      background: linear-gradient(135deg, var(--tomato), #ff7a45);
      font-size: 16px;
      font-weight: 900;
      cursor: pointer;
      box-shadow: 0 10px 22px rgba(239, 62, 54, 0.25);
    }

    .cta.secondary {
      color: var(--tomato-dark);
      background: var(--sun-soft);
      box-shadow: none;
    }

    .cta:disabled {
      color: rgba(36, 24, 24, 0.48);
      background: #eee0d1;
      cursor: not-allowed;
      box-shadow: none;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      width: fit-content;
      min-height: 26px;
      margin-bottom: 12px;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(22, 163, 108, 0.12);
      color: var(--green);
      font-size: 13px;
      font-weight: 900;
    }

    .premium .badge {
      background: rgba(239, 62, 54, 0.11);
      color: var(--tomato-dark);
    }

    @media (min-width: 680px) {
      .shell {
        padding-top: 34px;
      }

      .plans {
        gap: 14px;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="brand"><span class="brand-mark"></span>Sol de Mañana</div>
      <h1>Выберите темп изучения испанского</h1>
      <p class="lead">
        Три понятных тарифа: начните бесплатно, прокачивайте привычку каждый день
        или готовьтесь к персональному AI Spanish Coach.
      </p>
    </section>

    <section class="plans" aria-label="Тарифы">
      <article class="plan is-open">
        <button class="plan-toggle" type="button" aria-expanded="true">
          <span>
            <span class="plan-name">FREE <span class="plan-price">Бесплатно</span></span>
            <span class="plan-summary">Начните учить испанский бесплатно</span>
          </span>
          <span class="chevron">⌄</span>
        </button>
        <div class="plan-body">
          <div class="divider"></div>
          <p class="intro">Начните учить испанский бесплатно</p>
          <ul>
            <li>10 сообщений в день</li>
            <li>Практика разговорного испанского</li>
            <li>Простые диалоги и упражнения</li>
            <li>Базовые исправления ошибок</li>
            <li>Отлично для знакомства с ботом</li>
          </ul>
          <p class="outro">Попробуйте общаться на испанском уже сейчас!</p>
          <button class="cta secondary" type="button" data-action="close">
            Продолжить бесплатно
          </button>
        </div>
      </article>

      <article class="plan">
        <button class="plan-toggle" type="button" aria-expanded="false">
          <span>
            <span class="plan-name">
              BASIC <span class="plan-price">299₽ / 3.99$ в месяц</span>
            </span>
            <span class="plan-summary">Для стабильного ежедневного прогресса</span>
          </span>
          <span class="chevron">⌄</span>
        </button>
        <div class="plan-body">
          <div class="divider"></div>
          <span class="badge">Доступен первым</span>
          <p class="intro">Для тех, кто хочет стабильно прогрессировать каждый день 📈</p>
          <p class="includes">Всё из FREE, плюс:</p>
          <ul>
            <li>50 сообщений в день</li>
            <li>Бот запоминает ваш уровень и ошибки</li>
            <li>Практика по темам: путешествия, работа, знакомства и другое.</li>
            <li>Персональный словарь.</li>
            <li>Ежедневные цели и streaks.</li>
            <li>Более быстрые ответы AI.</li>
          </ul>
          <p class="outro">Учитесь регулярно и говорите увереннее с каждым днём!</p>
          <button class="cta" type="button" data-action="basic">Перейти на Basic</button>
        </div>
      </article>

      <article class="plan premium">
        <button class="plan-toggle" type="button" aria-expanded="false">
          <span>
            <span class="plan-name">
              PREMIUM <span class="plan-price">999₽ / 14.99$ в месяц</span>
            </span>
            <span class="plan-summary">Ваш персональный AI Spanish Coach</span>
          </span>
          <span class="chevron">⌄</span>
        </button>
        <div class="plan-body">
          <div class="divider"></div>
          <span class="badge">Скоро</span>
          <p class="intro">Ваш персональный AI Spanish Coach</p>
          <p class="includes">Всё из BASIC, плюс:</p>
          <ul>
            <li>Безлимитные сообщения</li>
            <li>Продвинутый AI-репетитор</li>
            <li>Голосовые диалоги и speaking practice</li>
            <li>Реалистичные roleplay-сценарии</li>
            <li>Персональная программа обучения</li>
            <li>Продвинутые объяснения грамматики</li>
            <li>Weekly progress reports</li>
            <li>Приоритетная скорость ответов</li>
            <li>Максимально естественные диалоги</li>
          </ul>
          <p class="outro">
            Практикуйте испанский так, будто общаетесь с настоящим преподавателем!
          </p>
          <button class="cta" type="button" disabled>Перейти на Premium</button>
        </div>
      </article>
    </section>
  </main>

  <script>
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
      document.documentElement.style.setProperty("--paper", tg.themeParams.bg_color || "#ffffff");
    }

    document.querySelectorAll(".plan-toggle").forEach((button) => {
      button.addEventListener("click", () => {
        const plan = button.closest(".plan");
        const isOpen = plan.classList.toggle("is-open");
        button.setAttribute("aria-expanded", String(isOpen));
      });
    });

    document.querySelectorAll("[data-action]").forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.dataset.action;
        if (action === "close" && tg) {
          tg.close();
          return;
        }
        const message = action === "basic"
          ? "Оплату подключим позже. Сейчас это рекламная витрина тарифов."
          : "Продолжайте пользоваться бесплатным тарифом в боте.";
        if (tg) {
          tg.showAlert(message);
        } else {
          window.alert(message);
        }
      });
    });
  </script>
</body>
</html>
        """
    )
