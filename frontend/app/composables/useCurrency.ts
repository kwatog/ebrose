export const cleanCurrencyFields = (form: any, fields: string[]) => {
  const cleaned = { ...form }
  fields.forEach(field => {
    if (cleaned[field]) {
      // Remove currency symbols and commas
      cleaned[field] = String(cleaned[field]).replace(/[^0-9.-]+/g, '')
    }
  })
  return cleaned
}
