export function useCurrency() {
  function formatCLP(value) {
    const num = Math.round(Number(value) || 0)
    return '$' + num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.')
  }
  
  function formatUSD(value) {
    const num = Number(value) || 0
    return 'US$' + num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  }
  
  function formatCurrency(value, currency = 'CLP') {
    if (currency === 'USD') {
      return formatUSD(value)
    }
    return formatCLP(value)
  }
  
  function parseCurrency(formattedValue) {
    if (!formattedValue) return 0
    const cleaned = formattedValue.toString().replace(/[^0-9,-]/g, '').replace(',', '.')
    return parseFloat(cleaned) || 0
  }
  
  return {
    formatCLP,
    formatUSD,
    formatCurrency,
    parseCurrency
  }
}

export function formatMoney(value, currency = 'CLP') {
  const num = Math.round(Number(value) || 0)
  if (currency === 'USD') {
    return 'US$' + Number(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  }
  return '$' + num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.')
}

export function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString + 'T00:00:00')
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}

