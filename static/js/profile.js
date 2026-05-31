let isEditing = false; // 학적 정보 수정 중인지
let isIntroEditing = false; // 자기소개 수정 중인지
let isInterestAdd = false; // 관심사, 취미 수정 중인지

const editBtn = document.querySelector(".editBtn"); // 학적 정보 수정 버튼
const editIntroBtn = document.querySelector(".editIntroBtn"); // 자기소개 수정 버튼
const addInterestBtn = document.querySelector(".addInterestBtn"); // 관심사, 취미 수정 버튼
const friendBtn = document.querySelector(".friendBtnBg"); // [관심 페이지로 이동] 버튼
const resignBtn = document.querySelector(".resignBtn"); // [회원 탈퇴] 버튼

const homeNav = document.querySelector(".homeNav"); // 바텀 내비게이션 바 - [홈] 버튼
const friendNav = document.querySelector(".friendNav"); // 바텀 내비게이션 바 - [채팅] 버튼
const profileNav = document.querySelector(".profileNav"); // 바텀 내비게이션 바 - [프로필] 버튼

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

// 타인 프로필 조회 (GET)
async function getUserProfile(userId) {
  const res = await fetch(`/api/profile/${userId}/`, {
    method: "GET",
    credentials: "include",
  });

  // 프로필 조회 실패
  if (!res.ok) {
    throw new Error("프로필 조회 실패");
  }

  const profile = await res.json();

  // 프로필 렌더링
  renderProfile(profile);

  return profile;
}

// 내 프로필 조회 (GET)
async function getMyProfile() {
  const res = await fetch("/api/profile/me/", {
    method: "GET",
    credentials: "include",
  });

  // 내 프로필 조회 실패
  if (!res.ok) {
    throw new Error("프로필 조회 실패");
  }

  const profile = await res.json();

  renderProfile(profile);

  return profile;
}

// 프로필 렌더링
function renderProfile(profile) {
  // 받은 profile 데이터 확인
  console.log(profile);

  document.querySelector(".userName").textContent = profile.username; // 사용자 이름
  document.querySelector(".userCountry").textContent = profile.nationality; // 사용자 국적

  // 사용자 전공
  document
    .querySelectorAll(".userMajor")
    .forEach((el) => (el.textContent = profile.major));

  // 사용자 학년
  document
    .querySelectorAll(".userGrade")
    .forEach((el) => (el.textContent = `${profile.grade}학년`));

  // 사용자 자기소개
  document.querySelector(".introduce").textContent = profile.bio;

  // 사용자 관심사,취미
  const container = document.querySelector(".hobbyInterest");

  // 사용자 관심사 및 취미 -> Element 요소 하나씩 추가
  container.innerHTML = "";

  profile.interests
    .split(",")
    .map((item) => item.trim())
    .forEach((interest) => {
      const tag = document.createElement("div");

      tag.classList.add("interestTag"); // 스타일 지정
      tag.textContent = `#${interest}`; // 텍스트 설정

      container.appendChild(tag); // 요소 하나씩 추가
    });
}

// 내 프로필 수정 (PATCH)
const csrfToken = getCookie("csrftoken");

async function updateProfile(data) {
  const res = await fetch("/api/profile/me/", {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    credentials: "include",
    body: JSON.stringify(data),
  });

  // 프로필 수정 실패
  if (!res.ok) {
    throw new Error("프로필 수정 실패");
  }

  if (res.ok) alert("프로필이 수정되었습니다.");

  return await res.json();
}

// 회원 탈퇴 DELETE 요청
async function resign() {
  const res = await fetch("/api/users/me/", {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    credentials: "include",
  });

  // 회원탈퇴 실패
  if (!res.ok) {
    throw new Error("회원탈퇴 실패");
    return;
  }
  alert("회원탈퇴가 완료되었습니다.");
  location.href = "/";

  return await res.json();
}

// 현재 url에 userId가 포함되어 있는지 (타인 프로필 조회 vs 내 프로필 조회 -> 분기)
const params = new URLSearchParams(window.location.search);
const userId = params.get("userId");

// userId가 없으면 내 프로필 조회
// userId가 있으면 타인 프로필 조회
!userId ? getMyProfile() : getUserProfile(userId);

// 학적 정보 편집 버튼 클릭
editBtn.addEventListener("click", async (event) => {
  event.preventDefault();

  if (!isEditing) {
    // 프로필 수정 시작
    // UI 변경 (입력창 보여주기)
    document.querySelector(".personalTxt").style.display = "none";
    document.querySelector(".personalInput").style.display = "block";
  } else {
    // 프로필 수정 완료

    // 사용자가 입력한 값 (국적, 전공, 학년)
    const data = {
      nationality: document.querySelector(".personalInput .userCountry").value,
      major: document.querySelector(".personalInput .userMajor").value,
      grade: Number(document.querySelector(".personalInput .userGrade").value),
    };

    // 사용자 입력값 확인
    console.log(data);

    // 사용자 정보 PATCH 요청
    await updateProfile(data);

    // 내 프로필 조회 (GET 요청)
    await getMyProfile();

    // UI 변경 (입력창 다시 숨기기)
    document.querySelector(".personalTxt").style.display = "block";
    document.querySelector(".personalInput").style.display = "none";
  }

  // 현재 수정 진행 중인지 여부(상태 플래그) 변경
  isEditing = !isEditing;
});

// 자기소개 버튼 클릭
editIntroBtn.addEventListener("click", async (event) => {
  event.preventDefault();

  if (!isIntroEditing) {
    // 프로필 수정 시작
    // UI 변경 (입력창 보여주기)
    document.querySelector(".introduce").style.display = "none";
    document.querySelector(".introduceInput").style.display = "block";
  } else {
    // 프로필 수정 완료

    // 사용자 입력값 (자기소개 내용)
    const data = {
      bio: document.querySelector(".introduceInput").value,
    };

    // 사용자 입력값 확인
    console.log(data);

    // 사용자 프로필 PATCH 요청
    await updateProfile(data);

    // 내 프로필 GET 요청
    await getMyProfile();

    // UI 변경 (입력창 다시 숨기기)
    document.querySelector(".introduce").style.display = "block";
    document.querySelector(".introduceInput").style.display = "none";
  }

  // 현재 수정 진행 중인지 여부(상태 플래그) 변경
  isIntroEditing = !isIntroEditing;
});

// 취미/관심사 수정 버튼 클릭
addInterestBtn.addEventListener("click", async (event) => {
  event.preventDefault();

  if (!isInterestAdd) {
    // 프로필 수정 시작
    //
    document.querySelector(".hobbyInterest").style.display = "none";
    document.querySelector(".hobbyInterestInput").style.display = "block";
  } else {
    // 프로필 수정 완료
    // 사용자가 선택한 값(취미/관심사) 가져오기
    const checkedLabels = [
      ...document.querySelectorAll(".chipInput:checked"),
    ].map((checkbox) => checkbox.nextElementSibling.textContent.trim());

    const interests = checkedLabels.join(", ");
    // 사용자가 입력한 값 확인
    console.log(interests);

    // 사용자 프로필 PATCH 요청
    await updateProfile({
      interests: interests,
    });

    // 내 프로필 GET 요청
    await getMyProfile();

    // UI 변경 (취미/관심사 선택창 다시 숨기기)
    document.querySelector(".hobbyInterest").style.display = "grid";
    document.querySelector(".hobbyInterestInput").style.display = "none";
  }

  // 현재 수정 진행 중인지 여부(상태 플래그) 변경
  isInterestAdd = !isInterestAdd;
});

// [관심 페이지로 이동] 버튼 클릭
friendBtn.addEventListener("click", async (event) => {
  event.preventDefault();
  location.href = "/friend/";
});

// [회원 탈퇴] 버튼 클릭
resignBtn.addEventListener("click", async (event) => {
  event.preventDefault();
  resign();
});

// 바텀 내비게이션 바 - [홈] 버튼 클릭 시, home(홈)으로 이동
homeNav.addEventListener("click", (event) => {
  event.preventDefault();
  location.href = "/home/";
});

// 바텀 내비게이션 바 - [채팅] 버튼 클릭 시, friend(관심 친구 목록 페이지)로 이동
friendNav.addEventListener("click", (event) => {
  event.preventDefault();
  location.href = "/friend/";
});

// 바텀 내비게이션 바 - [프로필] 버튼 클릭 시, profile(프로필 페이지)로 이동
profileNav.addEventListener("click", (event) => {
  event.preventDefault();
  location.href = "/profile/";
});
