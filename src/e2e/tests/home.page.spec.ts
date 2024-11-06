import { test, expect } from '@playwright/test';


/**
 * @description Verifies that the home page loads with the correct title
 */
test('Home page loads with the correct title', async ({ page }) => {
  await page.goto('/');

  await expect(page).toHaveTitle('Open Supply Hub');;
});
