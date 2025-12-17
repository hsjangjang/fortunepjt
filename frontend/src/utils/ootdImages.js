/**
 * OOTD 이미지 매핑 유틸리티
 */

// 상의 이미지
import topSleeveless from '@/assets/images/ootd/top_sleeveless.png'
import topTshirt from '@/assets/images/ootd/top_tshirt.png'
import topLinenShirt from '@/assets/images/ootd/top_linen_shirt.png'
import topLongsleeve from '@/assets/images/ootd/top_longsleeve.png'
import topThinKnit from '@/assets/images/ootd/top_thin_knit.png'
import topSweatshirt from '@/assets/images/ootd/top_sweatshirt.png'
import topHoodie from '@/assets/images/ootd/top_hoodie.png'
import topShirt from '@/assets/images/ootd/top_shirt.png'
import topKnit from '@/assets/images/ootd/top_knit.png'
import topThickKnit from '@/assets/images/ootd/top_thick_knit.png'
import topTurtleneck from '@/assets/images/ootd/top_turtleneck.png'
import topFleeceSweatshirt from '@/assets/images/ootd/top_fleece_sweatshirt.png'
import topPolo from '@/assets/images/ootd/top_polo.png'
import topCrop from '@/assets/images/ootd/top_crop.png'

// 하의 이미지
import bottomShorts from '@/assets/images/ootd/bottom_shorts.png'
import bottomLinen from '@/assets/images/ootd/bottom_linen.png'
import bottomCotton from '@/assets/images/ootd/bottom_cotton.png'
import bottomJeans from '@/assets/images/ootd/bottom_jeans.png'
import bottomSlacks from '@/assets/images/ootd/bottom_slacks.png'
import bottomJogger from '@/assets/images/ootd/bottom_jogger.png'
import bottomFleece from '@/assets/images/ootd/bottom_fleece.png'
import bottomCorduroy from '@/assets/images/ootd/bottom_corduroy.png'
import bottomWool from '@/assets/images/ootd/bottom_wool.png'
import bottomLeggings from '@/assets/images/ootd/bottom_leggings.png'
import bottomSkirt from '@/assets/images/ootd/bottom_skirt.png'
import bottomLongskirt from '@/assets/images/ootd/bottom_longskirt.png'
import bottomFleeceLeggings from '@/assets/images/ootd/bottom_fleece_leggings.png'
import bottomWide from '@/assets/images/ootd/bottom_wide.png'
import bottomCargo from '@/assets/images/ootd/bottom_cargo.png'

// 아우터 이미지
import outerCardigan from '@/assets/images/ootd/outer_cardigan.png'
import outerWindbreaker from '@/assets/images/ootd/outer_windbreaker.png'
import outerDenim from '@/assets/images/ootd/outer_denim.png'
import outerLeather from '@/assets/images/ootd/outer_leather.png'
import outerTrench from '@/assets/images/ootd/outer_trench.png'
import outerBlazer from '@/assets/images/ootd/outer_blazer.png'
import outerBomber from '@/assets/images/ootd/outer_bomber.png'
import outerCoat from '@/assets/images/ootd/outer_coat.png'
import outerPuffer from '@/assets/images/ootd/outer_puffer.png'
import outerLongPuffer from '@/assets/images/ootd/outer_long_puffer.png'
import outerShortPuffer from '@/assets/images/ootd/outer_short_puffer.png'
import outerShearling from '@/assets/images/ootd/outer_shearling.png'
import outerFleeceJacket from '@/assets/images/ootd/outer_fleece_jacket.png'
import outerRaincoat from '@/assets/images/ootd/outer_raincoat.png'

// 액세서리 이미지
import accScarf from '@/assets/images/ootd/acc_scarf.png'
import accGloves from '@/assets/images/ootd/acc_gloves.png'
import accBeanie from '@/assets/images/ootd/acc_beanie.png'
import accCap from '@/assets/images/ootd/acc_cap.png'
import accUmbrella from '@/assets/images/ootd/acc_umbrella.png'

// 상의 이미지 매핑
export const topImageMap = {
  '민소매': topSleeveless,
  '반팔 티셔츠': topTshirt,
  '반팔': topTshirt,
  '린넨 셔츠': topLinenShirt,
  '얇은 긴팔 티': topLongsleeve,
  '얇은 긴팔': topLongsleeve,
  '긴팔': topLongsleeve,
  '얇은 니트': topThinKnit,
  '맨투맨': topSweatshirt,
  '후드티': topHoodie,
  '후드': topHoodie,
  '셔츠': topShirt,
  '니트': topKnit,
  '두꺼운 니트': topThickKnit,
  '터틀넥': topTurtleneck,
  '기모 맨투맨': topFleeceSweatshirt,
  '카라 티셔츠': topPolo,
  '폴로': topPolo,
  '크롭티': topCrop,
}

// 하의 이미지 매핑
export const bottomImageMap = {
  '반바지': bottomShorts,
  '숏팬츠': bottomShorts,
  '린넨 팬츠': bottomLinen,
  '린넨': bottomLinen,
  '면바지': bottomCotton,
  '청바지': bottomJeans,
  '데님': bottomJeans,
  '슬랙스': bottomSlacks,
  '정장 바지': bottomSlacks,
  '조거팬츠': bottomJogger,
  '조거': bottomJogger,
  '기모 바지': bottomFleece,
  '코듀로이 팬츠': bottomCorduroy,
  '코듀로이': bottomCorduroy,
  '울 팬츠': bottomWool,
  '울': bottomWool,
  '레깅스': bottomLeggings,
  '치마': bottomSkirt,
  '스커트': bottomSkirt,
  '롱스커트': bottomLongskirt,
  '기모 레깅스': bottomFleeceLeggings,
  '와이드 팬츠': bottomWide,
  '와이드': bottomWide,
  '카고 팬츠': bottomCargo,
  '카고': bottomCargo,
}

// 아우터 이미지 매핑
export const outerImageMap = {
  '얇은 가디건': outerCardigan,
  '가디건': outerCardigan,
  '바람막이': outerWindbreaker,
  '윈드브레이커': outerWindbreaker,
  '청자켓': outerDenim,
  '데님 자켓': outerDenim,
  '가죽자켓': outerLeather,
  '레더 자켓': outerLeather,
  '트렌치코트': outerTrench,
  '트렌치': outerTrench,
  '블레이저': outerBlazer,
  '항공점퍼': outerBomber,
  '봄버 자켓': outerBomber,
  '코트': outerCoat,
  '패딩': outerPuffer,
  '롱패딩': outerLongPuffer,
  '숏패딩': outerShortPuffer,
  '무스탕': outerShearling,
  '플리스 자켓': outerFleeceJacket,
  '레인코트': outerRaincoat,
  '우비': outerRaincoat,
}

// 액세서리 이미지 매핑
export const accImageMap = {
  '머플러': accScarf,
  '스카프': accScarf,
  '목도리': accScarf,
  '장갑': accGloves,
  '비니': accBeanie,
  '모자': accCap,
  '캡': accCap,
  '우산': accUmbrella,
}

// 기본 이미지 export
export const defaultTopImage = topKnit
export const defaultBottomImage = bottomJeans
export const defaultOuterImage = outerCoat
export const defaultAccImage = accScarf

/**
 * 상의 이름으로 이미지 가져오기
 * @param {string} name - 상의 이름
 * @returns {string} 이미지 경로
 */
export const getTopImage = (name) => {
  if (!name) return defaultTopImage
  return topImageMap[name] || defaultTopImage
}

/**
 * 하의 이름으로 이미지 가져오기
 * @param {string} name - 하의 이름
 * @returns {string} 이미지 경로
 */
export const getBottomImage = (name) => {
  if (!name) return defaultBottomImage
  return bottomImageMap[name] || defaultBottomImage
}

/**
 * 아우터 이름으로 이미지 가져오기
 * @param {string} name - 아우터 이름
 * @returns {string} 이미지 경로
 */
export const getOuterImage = (name) => {
  if (!name) return defaultOuterImage
  return outerImageMap[name] || defaultOuterImage
}

/**
 * 액세서리 이름으로 이미지 가져오기
 * @param {string} name - 액세서리 이름
 * @returns {string} 이미지 경로
 */
export const getAccessoryImage = (name) => {
  if (!name) return defaultAccImage
  return accImageMap[name] || defaultAccImage
}
