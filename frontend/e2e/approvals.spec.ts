import {test,expect} from '@playwright/test';

test('Aramco registry filters, product evidence and protected administration',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Enter local demo as Alice (engineer)',exact:true}).click();
 await page.getByRole('button',{name:'Go to Knowledge Library',exact:true}).click();
 await page.getByRole('button',{name:'Customer Approvals',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Customer Approvals → Saudi Aramco',exact:true})).toBeVisible();
 await page.getByLabel('Filter 9COM code',{exact:true}).fill('6000002288');
 const row=page.locator('.approval-registry tbody tr');await expect(row).toHaveCount(1);
 await expect(row).toContainText('WKB, RPH-V, WKTR');await expect(row).toContainText('REQUIRES_VERIFICATION');
 await page.getByLabel('Filter 9COM code',{exact:true}).fill('');
 await page.getByLabel('Filter product series',{exact:true}).fill('MegaCPK');await expect(row).toHaveCount(1);await expect(row).toContainText('6000002350');
 await page.getByRole('button',{name:'Go to Product Library',exact:true}).click();
 await page.getByRole('button',{name:'KSB Product Series',exact:true}).click();
 await page.getByLabel('Filter product series',{exact:true}).fill('Omega');
 await expect(page.getByText('BB1 with deviations from API 610. Never infer full API 610 compliance.',{exact:true})).toBeVisible();
 await page.getByText('Manage approval references & append review history',{exact:true}).click();
 await page.getByRole('combobox',{name:'Management operation',exact:true}).selectOption('Evidence');
 await page.getByLabel('Source document title',{exact:true}).fill('Synthetic browser source '+Date.now());
 await page.getByLabel('Source reference / revision identifier',{exact:true}).fill('SYNTHETIC-BROWSER-ONLY');
 await page.getByLabel('Issuing authority / provenance',{exact:true}).fill('Fictional browser test authority');
 await page.getByLabel('Source review notes',{exact:true}).fill('Test metadata only, never a customer approval');
 await page.getByRole('button',{name:'Add evidence reference',exact:true}).click();
 await expect(page.getByRole('combobox',{name:'Supporting evidence reference',exact:true})).toContainText('SYNTHETIC-BROWSER-ONLY');
 expect(await page.getByRole('alert').count()).toBe(0);
});

test('Aramco source review, candidate mapping, matrix and frozen report export',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Enter local demo as Alice (engineer)',exact:true}).click();
 await page.getByRole('button',{name:'New RFQ',exact:true}).click();
 await page.getByRole('button',{name:'Continue',exact:true}).click();await page.getByRole('button',{name:'Continue',exact:true}).click();
 await page.getByLabel('Project name',{exact:true}).fill('Synthetic Aramco browser '+Date.now());
 await page.getByLabel('Customer name',{exact:true}).fill('Saudi Aramco');
 await page.getByRole('button',{name:'Create RFQ workspace',exact:true}).click();
 await page.locator('input[type=file]').setInputFiles('../fixtures/synthetic/aramco-rph.txt');
 await page.getByRole('button',{name:'Review extracted facts →',exact:true}).click();
 const facts=page.locator('.fact');await expect(facts).toHaveCount(16);
 for(let i=0;i<await facts.count();i++){
  await facts.nth(i).getByRole('button',{name:'Accept / correct',exact:true}).click();
  await expect(facts.nth(i).locator('.badge')).toHaveText('ACCEPTED');
 }
 await expect(page.getByRole('region',{name:'Saudi Aramco Approval Requirements'})).toContainText('6000002356');
 await page.getByText('Review proposed product and manufacturing reference',{exact:true}).click();
 await page.getByRole('combobox',{name:'Candidate KSB product series',exact:true}).selectOption({label:'RPH · OH2 – Horizontal Centerline-Mounted, Radially Split · reference only'});
 await page.getByLabel('Proposed vendor code',{exact:true}).fill('10066368');
 await page.getByLabel('Proposed manufacturing plant ID',{exact:true}).fill('30008606');
 await page.getByRole('combobox',{name:'Component supplier / 9CAT applicability',exact:true}).selectOption('NOT_APPLICABLE');
 await page.getByLabel('Component evidence / applicability reason',{exact:true}).fill('Synthetic example excludes component suppliers');
 await page.getByLabel('Candidate review reason',{exact:true}).fill('Selected a historical product reference, no technical selection claimed');
 await page.getByRole('button',{name:'Save approval candidate review',exact:true}).click();
 await expect(page.getByRole('region',{name:'Saudi Aramco Approval Requirements'})).toContainText('RPH · OH2');
 await page.getByLabel('Summary review reason',{exact:true}).fill('Reviewed all synthetic facts, historical mapping and missing current approval evidence');
 await page.getByRole('button',{name:'Acknowledge reviewed summary',exact:true}).click();
 await page.getByRole('button',{name:'PROCESS RFQ',exact:true}).click();
 await expect(page.locator('.exports .badge')).toHaveText('INSUFFICIENT DATA');
 await expect(page.getByRole('region',{name:'Saudi Aramco Approval Requirements'})).toContainText('FROZEN EVIDENCE');
 const check=page.locator('.finding').filter({hasText:'ARAMCO-007'});await check.locator(':scope > summary').click();
 await expect(check).toContainText('No authorized current verification');
 const [download]=await Promise.all([page.waitForEvent('download'),page.getByRole('link',{name:'Export JSON ↓',exact:true}).click()]);
 const fs=await import('node:fs/promises');const snapshot=JSON.parse(await fs.readFile((await download.path())!,'utf8'));
 expect(snapshot.customer_approvals.assessments[0].matched_9com).toBe('6000002356');
 expect(snapshot.customer_approvals.assessments[0].current_approval_verification.status).toBe('REQUIRES_VERIFICATION');
 expect(snapshot.outcome).toBe('INSUFFICIENT DATA');expect(snapshot.approval_registry_hash).toBeTruthy();
 expect(await page.getByRole('alert').count()).toBe(0);
 await page.screenshot({path:'../.runtime/aramco-approval-matrix.png',fullPage:true});
});
