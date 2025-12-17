/**
 * 행운 아이템 이미지 매핑 유틸리티
 */

// 행운 아이템 이미지 import
import perfumeImg from '@/assets/images/lucky_items/perfume.png'
import cardCaseImg from '@/assets/images/lucky_items/card_case.png'
import watchImg from '@/assets/images/lucky_items/watch.png'
import miniKeyringImg from '@/assets/images/lucky_items/mini_keyring.png'
import scarfImg from '@/assets/images/lucky_items/scarf.png'
import penImg from '@/assets/images/lucky_items/pen.png'
import handkerchiefImg from '@/assets/images/lucky_items/handkerchief.png'
import diaryImg from '@/assets/images/lucky_items/diary.png'
import walletImg from '@/assets/images/lucky_items/wallet.png'
import bookmarkImg from '@/assets/images/lucky_items/bookmark.png'
import mirrorImg from '@/assets/images/lucky_items/mirror.png'
import tumblerImg from '@/assets/images/lucky_items/tumbler.png'
import memoImg from '@/assets/images/lucky_items/memo.png'
import hairpinImg from '@/assets/images/lucky_items/hairpin.png'
import lipbalmImg from '@/assets/images/lucky_items/lipbalm.png'
import miniPouchImg from '@/assets/images/lucky_items/mini_pouch.png'
import braceletImg from '@/assets/images/lucky_items/bracelet.png'
import ringImg from '@/assets/images/lucky_items/ring.png'
import sunglassesImg from '@/assets/images/lucky_items/sunglasses.png'
import earringsImg from '@/assets/images/lucky_items/earrings.png'
import noteImg from '@/assets/images/lucky_items/note.png'
import keyImg from '@/assets/images/lucky_items/key.png'
import pencaseImg from '@/assets/images/lucky_items/pencase.png'
import beltImg from '@/assets/images/lucky_items/belt.png'
import earphoneCaseImg from '@/assets/images/lucky_items/earphone_case.png'
import faceRollerImg from '@/assets/images/lucky_items/face_roller.png'
import necklaceImg from '@/assets/images/lucky_items/necklace.png'
import badgeImg from '@/assets/images/lucky_items/badge.png'
import bagImg from '@/assets/images/lucky_items/bag.png'
import photoAlbumImg from '@/assets/images/lucky_items/photo_album.png'

// 아이템명 → 이미지 매핑
export const luckyItemImages = {
  '향수': perfumeImg,
  '미니 향수': perfumeImg,
  '카드케이스': cardCaseImg,
  '시계': watchImg,
  '손목시계': watchImg,
  '열쇠고리': miniKeyringImg,
  '미니 키링': miniKeyringImg,
  '동전 키링': miniKeyringImg,
  '스카프': scarfImg,
  '머플러': scarfImg,
  '펜': penImg,
  '볼펜': penImg,
  '손수건': handkerchiefImg,
  '다이어리': diaryImg,
  '지갑': walletImg,
  '명함지갑': walletImg,
  '카드지갑': walletImg,
  '책갈피': bookmarkImg,
  '북마크': bookmarkImg,
  '손거울': mirrorImg,
  '텀블러': tumblerImg,
  '메모지': memoImg,
  '메모장': memoImg,
  '헤어핀': hairpinImg,
  '립밤': lipbalmImg,
  '미니 파우치': miniPouchImg,
  '팔찌': braceletImg,
  '반지': ringImg,
  '선글라스': sunglassesImg,
  '귀걸이': earringsImg,
  '노트': noteImg,
  '열쇠': keyImg,
  '펜케이스': pencaseImg,
  '벨트': beltImg,
  '이어폰 케이스': earphoneCaseImg,
  '페이스 롤러': faceRollerImg,
  '목걸이': necklaceImg,
  '뱃지': badgeImg,
  '가방': bagImg,
  '사진 앨범': photoAlbumImg
}

/**
 * 아이템 이름으로 이미지 가져오기
 * @param {string} itemName - 아이템 이름
 * @returns {string|null} 이미지 경로 또는 null
 */
export const getLuckyItemImage = (itemName) => {
  if (!itemName) return null
  return luckyItemImages[itemName] || null
}