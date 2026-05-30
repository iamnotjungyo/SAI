const loginForm = document.querySelector(".loginForm");
const loginBtn = document.querySelector(".loginBtn");
const joinBtn = document.querySelector(".joinBtn");
const passwordToggle = document.querySelector(".passwordToggle");

const userEmail = document.querySelector(".userEmail");
const userPassword = document.querySelector(".userPassword");

// CSRF 토큰 가져오는 함수
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// 비밀번호 토글
passwordToggle.addEventListener("click", (event) => {
  event.preventDefault();
  userPassword.type = userPassword.type === "password" ? "text" : "password";
});

// 로그인 버튼
loginBtn.addEventListener("click", async (event) => {
  event.preventDefault();

  if (!userEmail || !checkEmail(userEmail.value)) {
    alert("이메일을 입력해주세요!");
    return;
  }
  if (!userPassword.value) {
    alert("비밀번호를 입력해주세요!");
    return;
  }
  if (!checkPassword(userPassword.value)) {
    alert("비밀번호는 영문·숫자 8자 이상으로 구성되어야 합니다.");
    return;
  }

  try {
    const csrfToken = getCookie("csrftoken");
    const response = await fetch("/api/login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,   // CSRF 토큰 헤더에 포함
      },
      credentials: "include",
      body: JSON.stringify({
        email: userEmail.value.trim(),
        password: userPassword.value,
      }),
    });

    if (response.ok) {
      location.href = "/home/";
    } else {
      const errorData = await response.json();
      const msg =
        errorData.non_field_errors?.[0] ||
        errorData.detail ||
        "로그인에 실패했습니다. 이메일 또는 비밀번호를 확인해주세요.";
      alert(msg);
    }
  } catch (error) {
    alert("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
    console.error("로그인 오류:", error);
  }
});

// 회원가입 버튼
joinBtn.onclick = function () {
  location.href = "/join/";
};

function checkEmail(email) {
  return email.includes("@");
}

function checkPassword(password) {
  const passRule = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{8,}/;
  return passRule.test(password);
}