// one colour per portfolio slot, checked for dark surfaces. never reuse a slot for another asset.
export const SERIES_COLORS = [
  '#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#008300',
  '#9085e9', '#e66767', '#1d95b8', '#76930a', '#b360c8', '#c0683c',
]

export const colorOf = (slot) => SERIES_COLORS[slot] ?? '#8490a5'
