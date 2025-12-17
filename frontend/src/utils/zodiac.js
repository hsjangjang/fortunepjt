/**
 * 별자리 및 띠 관련 유틸리티
 */

// 별자리 아이콘 import
import ariesIcon from '@/assets/zodiac/aries.png'
import taurusIcon from '@/assets/zodiac/taurus.png'
import geminiIcon from '@/assets/zodiac/gemini.png'
import cancerIcon from '@/assets/zodiac/cancer.png'
import leoIcon from '@/assets/zodiac/leo.png'
import virgoIcon from '@/assets/zodiac/virgo.png'
import libraIcon from '@/assets/zodiac/libra.png'
import scorpioIcon from '@/assets/zodiac/scorpio.png'
import sagittariusIcon from '@/assets/zodiac/sagittarius.png'
import capricornIcon from '@/assets/zodiac/capricorn.png'
import aquariusIcon from '@/assets/zodiac/aquarius.png'
import piscesIcon from '@/assets/zodiac/pisces.png'

// 별자리 아이콘 매핑
export const zodiacIcons = {
  '양자리': ariesIcon,
  '황소자리': taurusIcon,
  '쌍둥이자리': geminiIcon,
  '게자리': cancerIcon,
  '사자자리': leoIcon,
  '처녀자리': virgoIcon,
  '천칭자리': libraIcon,
  '전갈자리': scorpioIcon,
  '사수자리': sagittariusIcon,
  '염소자리': capricornIcon,
  '물병자리': aquariusIcon,
  '물고기자리': piscesIcon
}

// 십이지(띠) 이모지 매핑
export const chineseZodiacEmojis = {
  '쥐띠': '🐭',
  '소띠': '🐮',
  '호랑이띠': '🐯',
  '토끼띠': '🐰',
  '용띠': '🐲',
  '뱀띠': '🐍',
  '말띠': '🐴',
  '양띠': '🐑',
  '원숭이띠': '🐵',
  '닭띠': '🐔',
  '개띠': '🐶',
  '돼지띠': '🐷'
}

/**
 * 별자리 아이콘 가져오기
 * @param {string} zodiac - 별자리 이름
 * @returns {string|null} 아이콘 경로 또는 null
 */
export const getZodiacIcon = (zodiac) => {
  if (!zodiac) return null
  return zodiacIcons[zodiac] || null
}

/**
 * 십이지 이모지 가져오기
 * @param {string} zodiac - 띠 이름
 * @returns {string} 이모지 또는 빈 문자열
 */
export const getChineseZodiacEmoji = (zodiac) => {
  if (!zodiac) return ''
  return chineseZodiacEmojis[zodiac] || ''
}