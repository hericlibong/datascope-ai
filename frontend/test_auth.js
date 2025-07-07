
const { spawn } = require('child_process');
const proc = spawn('node', ['-e', `
  const playwright = require('@playwright/test');
  playwright.test('test auth', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.evaluate(() => {
      localStorage.setItem('accessToken', 'test_token');
      localStorage.setItem('refreshToken', 'test_refresh');
      localStorage.setItem('username', 'testuser');
    });
    await page.reload();
    await page.screenshot({ path: 'auth_layout.png' });
  });
`]);

