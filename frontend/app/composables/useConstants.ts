export const DEFAULT_CURRENCY = 'USD'

export const CURRENCIES = [
  'USD',
  'EUR',
  'GBP',
  'JPY',
  'SGD',
  'AUD',
  'CAD'
] as const

export const CURRENCY_OPTIONS = CURRENCIES.map(code => ({
  value: code,
  label: code
}))

export const SPEND_CATEGORIES = ['CAPEX', 'OPEX'] as const

export const SPEND_CATEGORY_OPTIONS = SPEND_CATEGORIES.map(category => ({
  value: category,
  label: category
}))

export const PO_TYPES = [
  'Service',
  'Software',
  'Hardware',
  'Subscription',
  'Consulting'
] as const

export const PO_TYPE_OPTIONS = PO_TYPES.map(poType => ({
  value: poType,
  label: poType
}))

export const STATUSES = [
  'Open',
  'Approved',
  'In Progress',
  'Completed',
  'Cancelled'
] as const

export const STATUS_OPTIONS = STATUSES.map(status => ({
  value: status,
  label: status
}))

export const LINE_ITEM_STATUSES = [
  'Draft',
  'Submitted',
  'Under Review',
  'Approved',
  'Rejected',
  'Cancelled'
] as const

export const LINE_ITEM_STATUS_OPTIONS = LINE_ITEM_STATUSES.map(status => ({
  value: status,
  label: status
}))
