import '@testing-library/jest-dom/vitest'

const storage = new Map<string, string>()

Object.defineProperty(globalThis, 'localStorage', {
  value: {
    clear: () => storage.clear(),
    getItem: (key: string) => storage.get(key) ?? null,
    key: (index: number) => [...storage.keys()][index] ?? null,
    get length() {
      return storage.size
    },
    removeItem: (key: string) => storage.delete(key),
    setItem: (key: string, value: string) => storage.set(key, String(value)),
  },
  configurable: true,
})

Object.defineProperty(globalThis.crypto, 'randomUUID', {
  value: () => '00000000-0000-4000-8000-000000000001',
  configurable: true,
})
