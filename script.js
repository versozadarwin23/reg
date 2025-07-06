const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const url = "http://192.168.254.254/index.html#index_status";
  await page.goto(url);

  try {
    await page.click('#loginlink', { timeout: 10000 });
  } catch (e) {
    console.log('No login link found or click failed.');
  }

  try {
    await page.fill('#txtUsr', 'user');
    await page.fill('#txtPwd', '@l03e1t3');
    await page.click('#btnLogin');
  } catch (e) {
    console.log('Login form interaction failed.');
  }

  try {
    await page.click('input[type="button"][value="Restart Device"]', { timeout: 10000 });
    await page.click('#yesbtn', { timeout: 10000 });
  } catch (e) {
    console.log('Restart button click failed.');
  }

  console.log('Airplane Mode Done');
  await browser.close();
})();
