import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
})

test('browses source-linked recall records', async ({ page }) => {
  await expect(page.getByRole('heading', { name: 'Browse official recalls' })).toBeVisible()
  await expect(page.locator('.recall-row').first()).toBeVisible()
  await page.locator('.recall-row').first().click()
  await expect(page.getByRole('link', { name: 'Open official source' })).toBeVisible()
  await expect(page.getByText('Hazard', { exact: true })).toBeVisible()
})

test('checks and saves a product locally', async ({ page }) => {
  await page.getByRole('button', { name: 'Check a product' }).click()
  await page.getByRole('button', { name: 'Fill example' }).click()
  await page.getByRole('button', { name: 'Save product' }).click()
  await expect(page.getByText('Product saved in this browser.')).toBeVisible()

  await page.getByRole('button', { name: /My watchlist/ }).click()
  await expect(page.getByText('QuickHeat toaster')).toBeVisible()
  await expect(page.getByText('QH-220')).toBeVisible()
})
