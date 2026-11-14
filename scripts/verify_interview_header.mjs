/** Offline UI regression against the running frontend; no account or Azure calls. */
import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { mkdir, writeFile } from 'node:fs/promises';
const modulePath = process.env.PREPMATE_PLAYWRIGHT_MODULE || path.resolve('storage/voice-acceptance/node_modules/playwright/index.mjs');
const { chromium } = await import(pathToFileURL(modulePath).href);
const out = path.resolve('storage/voice-release-regression');
await mkdir(out, {recursive:true});
const browser = await chromium.launch({
  executablePath: process.env.PREPMATE_BROWSER_PATH || 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', headless:true,
});
const results=[];
try {
  const context=await browser.newContext();
  await context.addInitScript(()=>localStorage.setItem('access_token','offline-header-regression'));
  let ended=0;
  let completed=false;
  const fixture=()=>({session_id:'offline-header',analysis_id:1,target_role:'Machine Learning Engineer',interview_type:'technical',experience_level:'fresher',starting_difficulty:'medium',progression_mode:'adaptive',status:completed?'completed':'in_progress',question_index:1,max_questions:8,follow_up_count:0,max_follow_ups:1,current_question:completed?null:{question_id:'q_001',topic:'Model evaluation',difficulty:'medium',question_text:'How would you evaluate an imbalanced classification model?',question_type:'conceptual',is_follow_up:false},conversation_history:[],started_at:'2026-11-14T12:00:00Z',completed_at:null});
  const page=await context.newPage();
  await page.route('**/*',async route=>{
    const url=new URL(route.request().url());
    if(url.port!=='8000')return route.continue();
    if(url.pathname==='/auth/me')return route.fulfill({json:{id:1,email:'offline@example.com',full_name:'Header Regression',target_role:null,experience_level:'fresher'}});
    if(url.pathname==='/interview/offline-header/end'){ended++;completed=true;return route.fulfill({json:fixture()});}
    if(url.pathname==='/interview/offline-header')return route.fulfill({json:fixture()});
    throw new Error('Unexpected backend request: '+url.pathname);
  });
  for(const width of [320,375,390,768,1440]){
    completed=false;
    await page.setViewportSize({width,height:1000});
    await page.goto('http://localhost:5173/interview/offline-header?mode=text');
    const end=page.getByRole('button',{name:'End interview',exact:true});
    await end.waitFor();
    const bounds=await page.locator('.iv-header-btn, .iv-header-theme-toggle, .iv-brand').evaluateAll(elements=>elements.map(element=>{
      const b=element.getBoundingClientRect();
      return {name:element.getAttribute('aria-label')||element.textContent.trim(),left:b.left,right:b.right,top:b.top,bottom:b.bottom,inside:b.left>=0&&b.right<=innerWidth&&b.top>=0&&b.bottom<=innerHeight};
    }));
    assert(bounds.every(b=>b.inside),JSON.stringify({width,bounds}));
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Horizontal overflow at '+width);
    await page.screenshot({path:path.join(out,`header-${width}.png`),fullPage:true});
    // Reach End interview from Dashboard with Tab, then activate using Enter.
    await page.getByRole('link',{name:'Dashboard',exact:true}).focus();
    await page.keyboard.press('Tab');
    assert(await end.evaluate(e=>e===document.activeElement),'End interview is not keyboard reachable');
    const before=ended;
    await page.keyboard.press('Enter');
    await page.getByRole('heading',{name:'Machine Learning Engineer Interview Complete',exact:true}).waitFor();
    assert.equal(ended,before+1);
    const newInterview=page.locator('.iv-header').getByRole('link',{name:'New Interview'});
    const newBounds=await newInterview.boundingBox();
    assert(newBounds&&newBounds.x>=0&&newBounds.x+newBounds.width<=width,'Completed header clips at '+width);
    results.push({width,status:'PASS',bounds,keyboard_activation:'PASS',completed_header:'PASS'});
    console.log(JSON.stringify({width,status:'PASS',keyboard_activation:'PASS',completed_header:'PASS'}));
  }
} finally {
  await writeFile(path.join(out,'header-results.json'),JSON.stringify(results,null,2));
  await browser.close();
}
