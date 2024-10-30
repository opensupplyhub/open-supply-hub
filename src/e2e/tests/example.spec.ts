import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('http://react:6543/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Open Supply Hub/);
});
