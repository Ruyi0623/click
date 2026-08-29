/**
 * 轻量 Markdown 解析器（零依赖）
 * 输出结构化 token 数组，由自定义组件渲染
 */

// ========== 行内 token ==========
export interface InlineToken {
  type: 'text' | 'bold' | 'italic' | 'code' | 'emoji'
  content: string
}

// ========== 块级 token ==========
export interface BlockToken {
  type: 'heading' | 'paragraph' | 'list' | 'blockquote' | 'hr'
  level?: number          // heading: 2/3
  ordered?: boolean       // list: 是否有序
  items?: InlineToken[][] // list: 每个列表项的行内 token
  children?: InlineToken[] // heading / paragraph / blockquote
}

// ========== 行内解析 ==========
function parseInline(text: string): InlineToken[] {
  const tokens: InlineToken[] = []
  let remaining = text

  while (remaining.length > 0) {
    // 行内代码 `code`
    let match = remaining.match(/^`([^`]+)`/)
    if (match) {
      tokens.push({ type: 'code', content: match[1] })
      remaining = remaining.slice(match[0].length)
      continue
    }

    // 粗体 **bold**
    match = remaining.match(/^\*\*(.+?)\*\*/)
    if (match) {
      tokens.push({ type: 'bold', content: match[1] })
      remaining = remaining.slice(match[0].length)
      continue
    }

    // 斜体 *italic*
    match = remaining.match(/^\*(.+?)\*/)
    if (match) {
      tokens.push({ type: 'italic', content: match[1] })
      remaining = remaining.slice(match[0].length)
      continue
    }

    // 普通文本 — 一直读到下一个特殊字符
    match = remaining.match(/^[^`*]+/)
    if (match) {
      tokens.push({ type: 'text', content: match[0] })
      remaining = remaining.slice(match[0].length)
      continue
    }

    // 单个特殊字符（不匹配任何格式）当作普通文本
    tokens.push({ type: 'text', content: remaining[0] })
    remaining = remaining.slice(1)
  }

  return tokens
}

// ========== 块级解析 ==========
export function parseMarkdown(md: string): BlockToken[] {
  if (!md) return []

  let clean = md.trim()
  // 去掉可能的代码块包裹
  if (clean.startsWith('```')) {
    clean = clean.replace(/^```(?:markdown)?\n?/, '').replace(/\n?```$/, '')
  }

  const lines = clean.split('\n')
  const blocks: BlockToken[] = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i].trimEnd()
    const trimmed = line.trim()

    // 空行 — 跳过
    if (!trimmed) { i++; continue }

    // 分割线 --- 或 ***
    if (/^[-*]{3,}$/.test(trimmed)) {
      blocks.push({ type: 'hr' })
      i++
      continue
    }

    // 标题 ## / ###
    const headingMatch = trimmed.match(/^(#{1,4})\s+(.+)/)
    if (headingMatch) {
      blocks.push({
        type: 'heading',
        level: headingMatch[1].length,
        children: parseInline(headingMatch[2]),
      })
      i++
      continue
    }

    // 引用块 > text
    if (trimmed.startsWith('> ')) {
      const quoteLines: string[] = []
      while (i < lines.length && lines[i].trim().startsWith('> ')) {
        quoteLines.push(lines[i].trim().slice(2))
        i++
      }
      blocks.push({
        type: 'blockquote',
        children: parseInline(quoteLines.join('\n')),
      })
      continue
    }

    // 无序列表 - item / * item
    if (/^[-*]\s+/.test(trimmed)) {
      const items: InlineToken[][] = []
      while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
        items.push(parseInline(lines[i].trim().replace(/^[-*]\s+/, '')))
        i++
      }
      blocks.push({ type: 'list', ordered: false, items })
      continue
    }

    // 有序列表 1. item
    if (/^\d+\.\s+/.test(trimmed)) {
      const items: InlineToken[][] = []
      while (i < lines.length && /^\d+\.\s+/.test(lines[i].trim())) {
        items.push(parseInline(lines[i].trim().replace(/^\d+\.\s+/, '')))
        i++
      }
      blocks.push({ type: 'list', ordered: true, items })
      continue
    }

    // 普通段落
    blocks.push({
      type: 'paragraph',
      children: parseInline(trimmed),
    })
    i++
  }

  return blocks
}
