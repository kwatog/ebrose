import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useApiFetch } from '../../composables/useApiFetch'

describe('useApiFetch', () => {
  const apiBase = 'http://localhost:8000'

  beforeEach(() => {
    vi.stubGlobal('useRuntimeConfig', () => ({
      public: { apiBase },
      apiBase
    }))
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('passes URL through without modification', async () => {
    const mockFetch = vi.fn().mockResolvedValue('success')
    vi.stubGlobal('$fetch', mockFetch)

    await useApiFetch('/test')
    
    expect(mockFetch).toHaveBeenCalledWith(`${apiBase}/test`, expect.objectContaining({ credentials: 'include' }))
  })

  it('preserves existing trailing slash', async () => {
    const mockFetch = vi.fn().mockResolvedValue('success')
    vi.stubGlobal('$fetch', mockFetch)

    await useApiFetch('/test/')
    
    expect(mockFetch).toHaveBeenCalledWith(`${apiBase}/test/`, expect.objectContaining({ credentials: 'include' }))
  })

  it('preserves file paths as-is', async () => {
    const mockFetch = vi.fn().mockResolvedValue('success')
    vi.stubGlobal('$fetch', mockFetch)

    await useApiFetch('/static/home.html')
    
    expect(mockFetch).toHaveBeenCalledWith(`${apiBase}/static/home.html`, expect.objectContaining({ credentials: 'include' }))
  })

  it('performs a basic fetch', async () => {
    const mockFetch = vi.fn().mockResolvedValue('success')
    vi.stubGlobal('$fetch', mockFetch)

    const result = await useApiFetch('/test')
    
    expect(result).toBe('success')
    expect(mockFetch).toHaveBeenCalledWith(`${apiBase}/test`, expect.objectContaining({ credentials: 'include' }))
  })

  it('retries on 401 token expiry', async () => {
    const mockFetch = vi.fn()
      .mockRejectedValueOnce({ response: { status: 401 } })
      .mockResolvedValueOnce({})
      .mockResolvedValueOnce('retry-success')
    
    vi.stubGlobal('$fetch', mockFetch)

    const result = await useApiFetch('/protected')
    
    expect(result).toBe('retry-success')
    expect(mockFetch).toHaveBeenCalledTimes(3)
    expect(mockFetch).toHaveBeenNthCalledWith(1, `${apiBase}/protected`, expect.anything())
    expect(mockFetch).toHaveBeenNthCalledWith(2, `${apiBase}/auth/refresh/`, expect.objectContaining({ method: 'POST' }))
    expect(mockFetch).toHaveBeenNthCalledWith(3, `${apiBase}/protected`, expect.anything())
  })

  it('fails if refresh fails', async () => {
    const mockFetch = vi.fn()
      .mockRejectedValueOnce({ response: { status: 401 } })
      .mockRejectedValueOnce({ response: { status: 401 } })
    
    vi.stubGlobal('$fetch', mockFetch)

    await expect(useApiFetch('/protected')).rejects.toMatchObject({ response: { status: 401 } })
  })

  it('handles query parameters correctly', async () => {
    const mockFetch = vi.fn().mockResolvedValue('success')
    vi.stubGlobal('$fetch', mockFetch)

    await useApiFetch('/items/?limit=100&status=active')
    
    expect(mockFetch).toHaveBeenCalledWith(`${apiBase}/items/?limit=100&status=active`, expect.objectContaining({ credentials: 'include' }))
  })
})
