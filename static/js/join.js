const joinForm = document.querySelector(".joinForm");
const arrowBtn = document.querySelector(".arrowBtnBg");
const joinBtn = document.querySelector(".joinBtnBg");
const loginBtn = document.querySelector(".loginBtn");

const userEmail = document.querySelector(".emailInput");
const userPassword = document.querySelector(".passwordInput");
const userCountry = document.querySelector(".selectCountry");
const userMajor = document.querySelector(".majorInput");
const userGrade = document.querySelector(".grade select");
const userIntroduce = document.querySelector(".introduceInput");

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

// 뒤로가기 버튼
arrowBtn.addEventListener("click", (event) => {
  event.preventDefault();
  location.href = "/";
});

// 가입하기 버튼
joinBtn.addEventListener("click", async (event) => {
  event.preventDefault();

  // 선택된 관심 주제 수집
  const topics = [];
  document.querySelectorAll(".chipInput:checked").forEach((chip) => {
    const label = chip.nextElementSibling;
    const text = Array.from(label.childNodes)
      .filter((node) => node.nodeType === Node.TEXT_NODE)
      .map((node) => node.textContent.trim())
      .join("");
    if (text) topics.push(text);
  });

  // 유효성 검사
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
  if (!userMajor.value) {
    alert("전공을 입력해주세요!");
    return;
  }
  if (topics.length === 0) {
    alert("관심 주제를 선택해주세요!");
    return;
  }
  if (!userIntroduce.value) {
    alert("자기소개를 입력해주세요!");
    return;
  }

  // 학년 텍스트 → 숫자 변환 ("1학년" → 1)
  const gradeNum = parseInt(userGrade.value.replace("학년", "").replace(" 이상", ""));

  // 국적 → role 판단
  const role = userCountry.value === "대한민국" ? "local" : "international";

  try {
    const csrfToken = getCookie("csrftoken");
    const response = await fetch("/api/signup/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,   // CSRF 토큰 헤더에 포함
      },
      credentials: "include",
      body: JSON.stringify({
        username: userEmail.value.trim(),
        email: userEmail.value.trim(),
        password: userPassword.value,
        role: role,
        nationality: userCountry.value,
        major: userMajor.value,
        grade: gradeNum,
        language: "한국어",
        interests: topics.join(", "),
        bio: userIntroduce.value,
      }),
    });

    if (response.ok) {
      alert("회원가입이 완료되었습니다!");
      location.href = "/";
    } else {
      const errorData = await response.json();
      const firstKey = Object.keys(errorData)[0];
      const msg = errorData[firstKey]?.[0] || "회원가입에 실패했습니다.";
      alert(`오류: ${msg}`);
    }
  } catch (error) {
    alert("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
    console.error("회원가입 오류:", error);
  }
});

// 로그인 버튼
loginBtn.addEventListener("click", (event) => {
  event.preventDefault();
  location.href = "/";
});

function checkEmail(email) {
  return email.includes("@");
}

function checkPassword(password) {
  const passRule = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{8,}/;
  return passRule.test(password);
}