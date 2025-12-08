// Toast Notification Composable
export function useToast() {
  const showToast = (message, type = 'info') => {
    const container = document.getElementById('toast-container')
    if (!container) return

    const toast = document.createElement('div')

    // Map types to our CSS variables/classes
    let iconColor = 'var(--info-color)'
    let icon = 'fa-info-circle'

    if (type.includes('success')) {
      icon = 'fa-check-circle'
      iconColor = 'var(--success)'
    } else if (type.includes('error')) {
      icon = 'fa-exclamation-circle'
      iconColor = 'var(--danger)'
    } else if (type.includes('warning')) {
      icon = 'fa-exclamation-triangle'
      iconColor = 'var(--warning)'
    }

    toast.className = 'toast-message glass-card'
    toast.style.cssText = `
      display: flex;
      align-items: center;
      justify-content: space-between;
      min-width: 300px;
      padding: 1rem 1.5rem;
      margin-bottom: 10px;
      border-left: 4px solid ${iconColor};
      color: white;
      transform: translateX(120%);
      transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    `

    toast.innerHTML = `
      <div class="d-flex align-items-center gap-3">
        <i class="fas ${icon}" style="color: ${iconColor}; font-size: 1.2rem;"></i>
        <span style="font-weight: 500;">${message}</span>
      </div>
      <i class="fas fa-times ms-3" style="cursor: pointer; opacity: 0.7;"></i>
    `

    // Add close button event
    const closeBtn = toast.querySelector('.fa-times')
    closeBtn.addEventListener('click', () => toast.remove())

    container.appendChild(toast)

    // Trigger animation
    requestAnimationFrame(() => {
      toast.style.transform = 'translateX(0)'
    })

    // Auto remove
    setTimeout(() => {
      toast.style.transform = 'translateX(120%)'
      setTimeout(() => toast.remove(), 400)
    }, 4000)
  }

  return {
    showToast
  }
}
