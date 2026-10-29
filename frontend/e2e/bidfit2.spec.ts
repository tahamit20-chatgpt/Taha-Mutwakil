import {test,expect} from '@playwright/test';
const complete=`SYNTHETIC TRAINING ONLY\nTag: P-101\nflow: 100 m3/h\nhead: 50 m\nliquid: demo-water\nmaterial: demo-alloy\napproval: demo-approved\nnpsh_basis: demo-datum\nprohibition: none\naction: none\nnpsha: 6 m\n`;
for(const missingStandard of [false,true]){
 test(`BidFit 2.0 classification and reviewed-summary gate ${missingStandard?'with unavailable standard':'complete training'}`,async({page})=>{
  await page.goto('/');await page.getByRole('button',{name:'Enter local demo as Alice (engineer)',exact:true}).click();
  await page.getByRole('button',{name:'New RFQ',exact:true}).click();
  await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.getByRole('combobox',{name:'Market area',exact:true}).selectOption('Building Services');
  await expect(page.getByRole('combobox',{name:'Application',exact:true})).toContainText('Fire Protection');
  await expect(page.getByRole('combobox',{name:'Application',exact:true})).not.toContainText('Desalination');
  await page.getByRole('combobox',{name:'Market area',exact:true}).selectOption('Water');await page.getByRole('combobox',{name:'Application',exact:true}).selectOption('Water Supply');
  await page.getByRole('button',{name:'Continue',exact:true}).click();
  await page.getByLabel('Project name',{exact:true}).fill('BidFit 2 browser '+Date.now());
  await page.getByLabel('Customer name',{exact:true}).fill('Synthetic browser customer');
  await page.getByLabel('RFQ reference',{exact:true}).fill('SYN-BROWSER');
  await page.getByRole('button',{name:'Create RFQ workspace',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Document manifest',exact:true})).toBeVisible();
  await page.locator('input[type=file]').setInputFiles({name:'synthetic-v2.txt',mimeType:'text/plain',buffer:Buffer.from(complete+(missingStandard?'standard: API 610 edition 12\n':''))});
  await page.getByRole('button',{name:'Review extracted facts →',exact:true}).click();
  const facts=page.locator('.fact');await expect(facts).toHaveCount(missingStandard?10:9);
  await expect(page.getByRole('button',{name:'PROCESS RFQ',exact:true})).toBeDisabled();
  for(let i=0;i<await facts.count();i++){
   await facts.nth(i).getByRole('button',{name:'Accept / correct',exact:true}).click();
   await expect(facts.nth(i).locator('.badge')).toHaveText('ACCEPTED');
  }
  await page.getByLabel('Summary review reason',{exact:true}).fill('Reviewed all synthetic source requirements and remaining gaps');
  await page.getByRole('button',{name:'Acknowledge reviewed summary',exact:true}).click();
  await expect(page.getByRole('button',{name:'PROCESS RFQ',exact:true})).toBeEnabled();
  await page.getByRole('button',{name:'Standards',exact:true}).click();
  if(missingStandard){await expect(page.getByText('P-101 · API 610 · edition 12',{exact:true})).toBeVisible();await expect(page.getByText('REFERENCE NOT AVAILABLE / REQUIRES REVIEW',{exact:true}).first()).toBeVisible()}
  await page.getByRole('button',{name:'PROCESS RFQ',exact:true}).click();
  await expect(page.locator('.exports .badge')).toHaveText(missingStandard?'INSUFFICIENT DATA':'GO');
  await page.locator('.finding').first().locator('summary').click();
  await expect(page.getByText('Requirement source',{exact:true}).first()).toBeVisible();
  const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('link',{name:'Export JSON ↓',exact:true}).click()]);
  const fs=await import('node:fs/promises');const data=JSON.parse(await fs.readFile((await download.path())!,'utf8'));
  expect(data.classification.market_area).toBe('Water');expect(data.summary.reviewed).toBe(true);expect(data.compliance_matrix.length).toBeGreaterThan(0);
  await page.getByRole('button',{name:'Quotation Studio',exact:true}).click();
  await page.getByRole('button',{name:'Create preliminary quotation draft',exact:true}).click();
  await expect(page.getByRole('link',{name:'Download draft HTML',exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Go to RFQ History',exact:true}).click();
  await expect(page.getByRole('heading',{name:'My RFQs & authorized history',exact:true})).toBeVisible();
  expect(await page.getByRole('alert').count()).toBe(0);
  await page.screenshot({path:'../.runtime/bidfit2-'+(missingStandard?'standards':'complete')+'.png',fullPage:true});
 });
}
