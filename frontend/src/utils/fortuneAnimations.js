/**
 * Fortune 운세 애니메이션 유틸리티
 * - 점수 원형 프로그레스 애니메이션
 * - 바 애니메이션
 * - 탭 변경 이벤트 핸들링
 */

// easeOutCubic easing 함수
const easeOutCubic = (x) => {
  return 1 - Math.pow(1 - x, 3)
}

/**
 * 애니메이션 값 업데이트 헬퍼
 * @param {number} duration - 애니메이션 지속 시간 (ms)
 * @param {Function} onUpdate - 업데이트 콜백 (progress: 0~1)
 */
export const animateValue = (duration, onUpdate) => {
  const startTime = performance.now()

  const step = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easedProgress = easeOutCubic(progress)

    onUpdate(easedProgress)

    if (progress < 1) {
      requestAnimationFrame(step)
    }
  }

  requestAnimationFrame(step)
}

/**
 * 원형 점수 프로그레스 애니메이션
 * @param {Object} options - 옵션
 * @param {Function} options.setDisplayScore - displayScore ref setter
 */
export const animateScore = ({ setDisplayScore }) => {
  const progressCircle = document.querySelector('.fortune-circle-progress')
  const scoreElement = document.querySelector('.fortune-score-text .score')

  if (progressCircle && scoreElement) {
    let targetScore = parseInt(progressCircle.getAttribute('data-score'))
    if (isNaN(targetScore)) targetScore = 0

    const circumference = 2 * Math.PI * 100

    progressCircle.style.transition = 'none'
    progressCircle.style.strokeDasharray = circumference
    progressCircle.style.strokeDashoffset = circumference
    setDisplayScore(0)

    animateValue(1500, (progress) => {
      const currentScore = targetScore * progress
      const offset = circumference - (currentScore / 100 * circumference)

      setDisplayScore(Math.round(currentScore))
      progressCircle.style.strokeDashoffset = offset
    })
  }
}

/**
 * 점수 바 애니메이션
 * @param {HTMLElement} container - .sub-score-bar 컨테이너
 */
export const animateBar = (container) => {
  const fill = container.querySelector('.sub-score-fill')
  const text = container.querySelector('.score-text')

  if (fill && text) {
    let targetScore = parseFloat(fill.getAttribute('data-target'))
    if (isNaN(targetScore)) {
      targetScore = parseFloat(fill.style.width) || 0
      fill.setAttribute('data-target', targetScore)
    }

    fill.style.transition = 'none'
    fill.style.width = '0%'
    text.textContent = '0%'

    animateValue(1000, (progress) => {
      const currentScore = targetScore * progress
      fill.style.width = `${currentScore}%`
      text.textContent = `${Math.round(currentScore)}%`
    })
  }
}

/**
 * 탭 변경 시 바 애니메이션 설정
 */
export const setupTabAnimations = () => {
  const tabEls = document.querySelectorAll('a[data-bs-toggle="tab"]')
  tabEls.forEach(tabEl => {
    tabEl.addEventListener('shown.bs.tab', function (event) {
      const targetId = event.target.getAttribute('href')
      const targetPane = document.querySelector(targetId)
      if (targetPane) {
        const bar = targetPane.querySelector('.sub-score-bar')
        if (bar) animateBar(bar)
      }
    })
  })
}

/**
 * 활성 탭의 바 애니메이션 실행
 */
export const animateActiveTabBar = () => {
  const activeTabPane = document.querySelector('.tab-pane.active')
  if (activeTabPane) {
    const bar = activeTabPane.querySelector('.sub-score-bar')
    if (bar) animateBar(bar)
  }
}

/**
 * 로또 볼 스타일 반환 (Django today.html과 동일)
 * @param {number} number - 로또 번호
 * @returns {string} CSS style 문자열
 */
export const getLottoBallStyle = (number) => {
  let background
  if (number <= 10) background = 'linear-gradient(135deg, #fbbf24, #d97706)'
  else if (number <= 20) background = 'linear-gradient(135deg, #60a5fa, #2563eb)'
  else if (number <= 30) background = 'linear-gradient(135deg, #f87171, #dc2626)'
  else if (number <= 40) background = 'linear-gradient(135deg, #34d399, #059669)'
  else background = 'linear-gradient(135deg, #c084fc, #7c3aed)'

  return `background: ${background};`
}
