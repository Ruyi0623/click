/**
 * 将 emoji 字符转换为 Fluent UI Emoji 图片 URL
 * Windows 10 Segoe UI Emoji 风格（有黑色描边）
 */

// emoji 文件名映射
const emojiFileMap: Record<string, string> = {
  '😊': 'smiling-face-with-smiling-eyes_1f60a',
  '😍': 'smiling-face-with-heart-shaped-eyes_1f60d',
  '😌': 'relieved-face_1f60c',
  '🤩': 'grinning-face-with-star-eyes_1f929',
  '😘': 'face-throwing-a-kiss_1f618',
  '😪': 'sleepy-face_1f62a',
  '😢': 'crying-face_1f622',
  '😤': 'face-with-look-of-triumph_1f624',
}

/**
 * 获取 emoji 图片路径（本地）
 */
export function getTwemojiUrl(emoji: string): string {
  const fileName = emojiFileMap[emoji]
  if (fileName) {
    return `/static/emojis/${fileName}.png`
  }
  // 降级到 Twemoji CDN
  const codepoint = emojiToCodepoint(emoji)
  return `https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/${codepoint}.png`
}

/**
 * 将 emoji 字符转换为 Unicode 码点
 */
function emojiToCodepoint(emoji: string): string {
  const codePoints: string[] = []
  for (const char of emoji) {
    const code = char.codePointAt(0)
    if (code !== undefined && code > 0x1f) {
      codePoints.push(code.toString(16))
    }
  }
  return codePoints.join('-')
}

/**
 * 将文本中的 emoji 替换为 Fluent UI Emoji 图片标签
 */
export function replaceEmojis(text: string): string {
  // 匹配 emoji 的正则表达式
  const emojiRegex = /[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu

  return text.replace(emojiRegex, (emoji) => {
    const url = getTwemojiUrl(emoji)
    return `<image src="${url}" class="twemoji" mode="aspectFit" />`
  })
}
