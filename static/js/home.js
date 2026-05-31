const recmdBtn = document.querySelector(".recmdBtn"); // [친구 추천 · 매칭] 버튼
const friendBtn = document.querySelector(".friendBtn"); // [채팅 · 번역 지원] 버튼
const homeNav = document.querySelector(".homeNav"); // 바텀 내비게이션 바 - [홈] 버튼
const friendNav = document.querySelector(".friendNav"); // 바텀 내비게이션 바 - [채팅] 버튼
const profileNav = document.querySelector(".profileNav"); // 바텀 내비게이션 바 - [프로필] 버튼

twemoji.parse(document.body); // 트위터 이모지 적용

// [친구 추천 · 매칭] 버튼 클릭 시
recmdBtn.addEventListener("click", (event) => {
    event.preventDefault();
    location.href = "/recommend/";
});

// [채팅 · 번역 지원] 버튼 클릭 시
friendBtn.addEventListener("click", (event) => {
    event.preventDefault();
    location.href = "/friend/";
});

// 바텀 네비 - [홈]
homeNav.addEventListener("click", (event) => {
    event.preventDefault();
    location.href = "/home/";
});

// 바텀 네비 - [채팅]
friendNav.addEventListener("click", (event) => {
    event.preventDefault();
    location.href = "/friend/";
});

// 바텀 네비 - [프로필]
profileNav.addEventListener("click", (event) => {
    event.preventDefault();
    location.href="/profile/";
})
