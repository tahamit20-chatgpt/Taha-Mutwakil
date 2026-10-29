import {test,expect} from '@playwright/test';
import path from 'node:path';
for(const [scenario,outcome] of [['go','GO'],['missing','INSUFFICIENT DATA']]){
 test(`synthetic ${scenario}: upload → review → evaluate → export`,async({page})=>{
  await page.goto('/');
  await page.getByRole('button',{name:'Enter local demo as Alice (engineer)',exact:true}).click();
  await page.getByRole('button',{name:'New RFQ',exact:true}).click();
  await page.getByRole('button',{name:'Original quick demo',exact:true}).click();
  await page.getByLabel('Project reference').fill('Browser '+scenario+' '+Date.now());
  await page.getByRole('button',{name:'Create project',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Document manifest'})).toBeVisible();
  await page.locator('input[type=file]').setInputFiles(path.join(process.cwd(),'../fixtures/synthetic/'+scenario+'.txt'));
  await page.getByRole('button',{name:'Review extracted facts →'}).click();
  const facts=page.locator('.fact');
  await expect(facts).toHaveCount(scenario==='go'?10:9);
  await expect(facts.first().locator('blockquote')).toContainText('flow: 100 m3/h');
  for(let i=0;i<await facts.count();i++){
   await facts.nth(i).getByRole('button',{name:'Accept / correct'}).click();
   await expect(facts.nth(i).locator('.badge')).toHaveText('ACCEPTED');
  }
  if(scenario==='go'){
   await page.getByLabel('head value',{exact:true}).fill('55');
   await facts.nth(1).getByRole('button',{name:'Accept / correct'}).click();
   await expect(facts.nth(1)).toContainText('Normalized: 55 m');
  }
  await page.getByRole('button',{name:'Technical evaluation',exact:true}).click();
  await page.getByRole('button',{name:'Run technical evaluation'}).click();
  await expect(page.locator('.exports .badge')).toHaveText(outcome);
  const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('link',{name:'Export JSON ↓'}).click()]);
  expect(download.suggestedFilename()).toMatch(/bidfit-.*\.json/);
  await expect(page.locator('.tag-result')).toContainText('UNVERIFIED — no approved curves');
  const file=await download.path();
  const fs=await import('node:fs/promises');
  const report=JSON.parse(await fs.readFile(file!, 'utf8'));
  expect(report.outcome).toBe(outcome);
  expect(report.facts[0].source.document_version_id).toBeTruthy();
  await page.screenshot({path:'../.runtime/browser-'+scenario+'.png',fullPage:true});
  expect(await page.getByRole('alert').count()).toBe(0);
 });
}
