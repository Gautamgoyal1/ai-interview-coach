import assert from 'node:assert/strict';
import {chromium} from '../storage/voice-acceptance/node_modules/playwright/index.mjs';
import {mkdir,writeFile} from 'node:fs/promises';
const dir='storage/ui-phase1';
await mkdir(dir,{recursive:true});
const failed=new Set();const requests={};const creates=[];
const passed=[];
function pass(name){passed.push(name);console.log(JSON.stringify({check:name,status:'PASS'}));}
const date='2026-11-14T09:30:00Z';
const user={id:1,email:'alex@example.com',full_name:'Alex Morgan',target_role:'Machine Learning Engineer',experience_level:'fresher',created_at:date};
const analysis={id:1,filename:'Alex_Morgan_ML_Resume.pdf',job_role:user.target_role,created_at:date,match_score:72,version:2,interview_count:3};
const result={analysis_id:1,version:2,job_role:user.target_role,resume_skills:['Python','pandas','machine learning','SQL'],matched_skills:['Python','pandas','machine learning'],missing_skills:['Docker','model evaluation','cloud platforms'],match_score:72,skill_evidence:{Python:'demonstrated',pandas:'mentioned_only'},strengths:['Built a Python pipeline to clean and validate tabular datasets.','Explains model selection using project context.'],improvement_suggestions:['Add precision and recall results to your model evaluation project.','Show a deployment example with Docker.','Quantify the business impact of your feature engineering choices.'],likely_interview_questions:['How would you handle data leakage in a training pipeline?']};
const rec={topic:'Model evaluation',interview_type:'technical',target_role:user.target_role,observed_gap:'Accuracy alone concealed poor minority-class recall.',suggested_action:'Practice selecting metrics for imbalanced data.',source_report_id:1,priority:'high'};
const reportSummary={id:1,session_id:'audit-interview',target_role:user.target_role,interview_type:'technical',interview_date:date,status:'completed',overall_score:68,rubric_version:'v1.0',created_at:date};
const dimNames={technical_correctness:'Technical Correctness',relevance:'Relevance',completeness:'Completeness',technical_depth:'Technical Depth'};
const dimensions=Object.fromEntries(Object.entries(dimNames).map(([key,label],i)=>[key,{dimension:key,label,weight:[.4,.2,.25,.15][i],average_score:[3.5,4,3,2.8][i],percentage:[70,80,60,56][i],evaluated_count:4}]));
const feedback={question_id:'q_001',question_index:1,is_follow_up:false,parent_question_id:null,topic:'Model evaluation',difficulty:'medium',question_text:'How would you evaluate an imbalanced classification model?',answer_text:'I would compare precision and recall, inspect the confusion matrix, and choose the threshold based on the cost of false negatives.',overall_score:68,grading_status:'completed',dimension_scores:Object.fromEntries(Object.keys(dimNames).map(key=>[key,{score:3.4,explanation:'Clear metric selection, but the threshold trade-off needs a concrete example.'}])),strengths:['Connects precision and recall to error costs.'],missing_concepts:['Threshold calibration'],improvement_suggestions:['Explain how you choose a threshold using validation data.']};
const report={...reportSummary,dimension_scores:dimensions,topic_scores:[{topic:'Model evaluation',score:68,questions_asked:3,evaluated_questions:3},{topic:'Python',score:82,questions_asked:1,evaluated_questions:1}],strengths:['Clear explanation of precision and recall.'],weaknesses:['Threshold selection lacked a concrete trade-off.'],missing_concepts:['Threshold calibration'],recommendations:[{area:'Model evaluation',observed_gap:rec.observed_gap,action:rec.suggested_action,priority:'high'}],question_feedback:[feedback],completion_stats:{questions_answered:4,primary_questions_completed:3,follow_ups_answered:1,total_primary_questions:3},evaluation_coverage:{evaluated_count:4,unavailable_count:0,total_answered:4,coverage_ratio:1,is_partial:false},rubric_weights:{technical_correctness:.4,relevance:.2,completeness:.25,technical_depth:.15},error_message:null,updated_at:date};
const coach={correct_points:['Correctly identifies precision and recall.'],missing_points:['Threshold selection example'],improvement_suggestions:['State the relative cost of false positives and negatives.'],suggested_structure:['Define the objective','Choose metrics','Discuss threshold trade-offs'],improved_example_answer:'I would measure precision and recall on held-out data, then choose a threshold based on the cost of missed positives. For fraud detection, I might prioritize recall while monitoring false-positive review costs.',next_action:'Retry with a concrete threshold example.',evaluation_status:'completed',evaluation_confidence:'high',improvements_from_previous:[]};
const practice={id:'audit-practice',user_id:1,interview_type:'technical',target_role:user.target_role,topic:'Model evaluation',source_report_id:1,experience_level:'fresher',weakness_context:rec.observed_gap,status:'active',created_at:date,updated_at:date,questions:[{id:'practice-q1',session_id:'audit-practice',question_text:'When would accuracy be misleading, and which metrics would you use instead?',topic:'Model evaluation',difficulty:'medium',hints_revealed:[1],revealed_hints:{'1':'Consider what happens when one class represents only one percent of examples.'},reference_revealed:false,reference_answer:null,reference_explanation:null,created_at:date,attempts:[{id:'attempt1',question_id:'practice-q1',attempt_number:1,answer_text:feedback.answer_text,assistance_level:'hint_assisted',hints_used:[1],reference_revealed:false,feedback:coach,created_at:date}]}]};
const interview={session_id:'audit-interview',analysis_id:1,target_role:user.target_role,interview_type:'technical',experience_level:'fresher',starting_difficulty:'medium',progression_mode:'adaptive',status:'in_progress',question_index:2,max_questions:8,follow_up_count:0,max_follow_ups:1,current_question:{question_id:'q_002',topic:'Model evaluation',difficulty:'medium',question_text:feedback.question_text,question_type:'applied',is_follow_up:false},conversation_history:[{...feedback,created_at:date,answered_at:date}],started_at:date,completed_at:null};
let scenario='populated';
const browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true});
const observations=[];
try{
 const context=await browser.newContext();
 await context.addInitScript(()=>{localStorage.setItem('access_token','offline-design-audit');localStorage.setItem('theme','light');});
 const page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',async route=>{
  const url=new URL(route.request().url());if(url.port!=='8000')return route.continue();
  const p=url.pathname;requests[p]=(requests[p]||0)+1;
  if(failed.has(p))return route.fulfill({status:503,json:{detail:'Simulated temporary failure'}});
  if(p==='/practice/sessions'&&route.request().method()==='POST'){const payload=route.request().postDataJSON();creates.push(payload);practice.interview_type=payload.interview_type;practice.source_report_id=payload.source_report_id??null;practice.target_role=payload.target_role||user.target_role;return route.fulfill({json:practice});}
  if(p==='/auth/me')return route.fulfill({json:user});
  if(scenario==='loading')await new Promise(r=>setTimeout(r,8000));
  if(scenario==='error')return route.fulfill({status:503,json:{detail:'The service is temporarily unavailable. Please try again.'}});
  const empty=scenario==='empty';
  if(p==='/resume/analyses')return route.fulfill({json:empty?[]:[analysis,{...analysis,id:2,job_role:'Data Scientist',match_score:61,filename:'Alex_Data_Science.pdf'}]});
  if(p==='/resume/analyses/1')return route.fulfill({json:{...analysis,result}});
  if(p==='/resume/analyze')return route.fulfill({json:{...result,reused:true}});
  if(p==='/reports')return route.fulfill({json:empty?[]:[reportSummary,{...reportSummary,id:2,session_id:'audit-hr',interview_type:'hr',overall_score:74}]});
  if(p.startsWith('/reports/interviews/'))return route.fulfill({json:scenario==='partial'?{...report,status:'partial',evaluation_coverage:{...report.evaluation_coverage,is_partial:true,unavailable_count:2,evaluated_count:2,coverage_ratio:.5}}:report});
  if(p==='/practice/recommendations')return route.fulfill({json:empty?[]:[rec,{...rec,topic:'Stakeholder communication',interview_type:'hr',observed_gap:'Decision rationale needs clearer structure.'}]});
  if(p==='/practice/sessions')return route.fulfill({json:empty?[]:[{...practice,question_count:1,attempt_count:1,latest_attempt_at:date}]});
  if(p.startsWith('/practice/sessions/'))return route.fulfill({json:practice});
  if(p.startsWith('/interview/'))return route.fulfill({json:{...interview,interview_type:p.includes('audit-hr')?'hr':'technical',current_question:p.includes('audit-hr')?{...interview.current_question,question_text:'Tell me about a time you resolved a disagreement in a project team.'}:interview.current_question}});
  if(p.startsWith('/speech/'))return route.fulfill({status:503,json:{detail:'Speech service unavailable in offline design audit.'}});
  return route.fulfill({json:[]});
 });
 async function capture(name,route,width=1440,mode='populated'){
  scenario=mode;errors.length=0;await page.setViewportSize({width,height:1000});
  await page.goto('http://localhost:5173'+route);await page.waitForTimeout(mode==='loading'?350:750);
  if(name==='landing'){
   for(let y=0;y<await page.locator('body').evaluate(e=>e.scrollHeight);y+=700){await page.evaluate(y=>scrollTo(0,y),y);await page.waitForTimeout(60);}await page.evaluate(()=>scrollTo(0,0));await page.waitForTimeout(400);
  }
  const outside = await page.locator('main button,main a,main input,main textarea,main select').evaluateAll(es=>es.filter(e=>e.getClientRects().length && getComputedStyle(e).visibility==='visible').map(e=>{const r=e.getBoundingClientRect();return {tag:e.tagName,label:e.getAttribute('aria-label')||e.textContent?.slice(0,50),left:r.left,right:r.right};}).filter(r=>r.left < -1 || r.right > innerWidth+1));
  assert.deepEqual(outside,[],JSON.stringify({name,width,outside}));
  await page.screenshot({path:`${dir}/${name}-${width}.png`,fullPage:true});
  await page.screenshot({path:`${dir}/${name}-${width}-viewport.png`});
  const stats=await page.evaluate(()=>({height:document.documentElement.scrollHeight,overflow:document.documentElement.scrollWidth>innerWidth,headings:[...document.querySelectorAll('h1,h2,h3')].map(e=>e.textContent.trim()),unnamedInputs:[...document.querySelectorAll('input:not([type=hidden]),textarea,select')].filter(e=>!e.labels?.length&&!e.getAttribute('aria-label')&&!e.getAttribute('aria-labelledby')).map(e=>({tag:e.tagName,id:e.id,placeholder:e.getAttribute('placeholder')})),text:document.body.innerText.slice(0,14000)}));
  observations.push({name,width,mode,errors:[...errors],...stats});console.log(JSON.stringify({name,width,mode,height:stats.height,overflow:stats.overflow,errors}));
 }

 report.interview_type='hr';reportSummary.interview_type='hr';rec.interview_type='hr';
 report.dimension_scores=Object.fromEntries(['reasoning_critical_thinking','decision_making_tradeoffs','communication_clarity','relevance_completeness','reflection_adaptability'].map((key,i)=>[key,{dimension:key,label:key.replaceAll('_',' '),weight:[.3,.25,.2,.15,.1][i],average_score:3.5,percentage:70,evaluated_count:4}]));
 await capture('hr-report','/reports/audit-interview');
 assert((await page.locator('body').innerText()).includes('82.0%'));
 assert(!(await page.locator('body').innerText()).includes('82.00 / 5'));
 assert(await page.getByRole('heading',{name:'Behavioral Topic Performance'}).isVisible());
 for(const href of await page.locator('a[href^="/practice?"]').evaluateAll(es=>es.map(e=>e.getAttribute('href')))){
   const params=new URL(href,'http://test').searchParams;
   assert.equal(params.get('type'),'hr');assert.equal(params.get('reportId'),'1');assert.equal(params.get('reportSessionId'),'audit-interview');
 }
 pass('HR report score units and every practice entry point');
 await page.locator('.roadmap-item').getByRole('link',{name:'Practice This Topic'}).click();
 await page.locator('.practice-question-text').waitFor();
 assert.equal(creates.length,1);assert.equal(creates[0].interview_type,'hr');assert.equal(creates[0].source_report_id,1);
 let backlink=page.getByRole('link',{name:/Return to Report/});await backlink.waitFor();assert.equal(await backlink.getAttribute('href'),'/reports/audit-interview');
 await page.reload();await page.locator('.practice-question-text').waitFor();assert.equal(creates.length,1);
 await page.getByRole('link',{name:/Return to Report/}).click();await page.getByRole('heading',{name:'Behavioral Topic Performance'}).waitFor();
 await page.goto('http://localhost:5173/practice/audit-practice');await page.getByRole('link',{name:/Return to Report/}).waitFor();
 assert.equal(await page.getByRole('link',{name:/Return to Report/}).getAttribute('href'),'/reports/audit-interview');
 pass('report to HR practice to report including reload and reopened session');
 failed.add('/practice/sessions');
 await page.goto('http://localhost:5173/practice?topic=Retry%20exercise&type=hr&reportId=1&reportSessionId=audit-interview');
 await page.getByRole('button',{name:'Retry',exact:true}).waitFor();
 const failedCount=requests['/practice/sessions'];failed.clear();
 await page.getByRole('button',{name:'Retry',exact:true}).click();await page.locator('.practice-question-text').waitFor();
 assert(requests['/practice/sessions']>failedCount);assert.equal(creates.at(-1).interview_type,'hr');
 assert.equal(await page.getByRole('link',{name:/Return to Report/}).getAttribute('href'),'/reports/audit-interview');
 pass('failed practice creation exits loading and Retry repeats creation');

 await capture('partial-report','/reports/audit-interview',1440,'partial');
 assert((await page.locator('.report-overall-box').innerText()).includes('2 of 4 answers graded'));
 pass('partial coverage adjacent to overall score');
 scenario='populated';
 failed.add('/resume/analyses');await capture('dashboard-partial','/dashboard');
 assert((await page.locator('body').innerText()).includes('68 / 100'));
 assert((await page.locator('body').innerText()).includes('Resume history unavailable.'));
 assert(!(await page.locator('body').innerText()).includes('No resume analyses yet.'));
 assert(!(await page.locator('body').innerText()).includes('Interviews Done'));
 const before=requests['/resume/analyses'];failed.clear();await page.getByRole('button',{name:'Retry',exact:true}).click();
 await page.locator('.command-caption').filter({hasText:'Recent Resume Profiles'}).waitFor();await page.waitForTimeout(250);assert(requests['/resume/analyses']>before);
 pass('dashboard independent panels and retry');
 failed.add('/practice/recommendations');await capture('practice-partial','/practice');
 assert(await page.getByRole('link',{name:'Resume',exact:true}).isVisible());
 assert((await page.locator('body').innerText()).includes('Recommendations unavailable'));
 await page.getByLabel('Topic / Concept').fill('Teamwork');assert(await page.getByLabel('Interview Type').isVisible());assert(await page.getByLabel('Difficulty',{exact:true}).isVisible());
 const recCount=requests['/practice/recommendations'];failed.clear();await page.getByRole('button',{name:'Retry',exact:true}).click();
 await page.getByRole('button',{name:'Practice Now'}).waitFor();assert(requests['/practice/recommendations']>recCount);
 await page.getByRole('button',{name:'Practice Now'}).click();await page.locator('.practice-question-text').waitFor();
 assert.equal(creates.at(-1).interview_type,'hr');assert.equal(creates.at(-1).source_report_id,1);
 assert(await page.getByLabel('Your practice answer').isVisible());
 pass('practice recovery preserves sessions, retries, and carries recommendation origin');
 const starts=requests['/interview/start']||0;const speech=requests['/speech/synthesize']||0;
 await capture('setup-confirmation','/interview?analysisId=2');
 assert.equal(await page.getByLabel('Resume profile',{exact:true}).inputValue(),'2');
 assert.equal(requests['/interview/start']||0,starts);assert.equal(requests['/speech/synthesize']||0,speech);
 assert(!(await page.locator('body').innerText()).includes('You can ask for progressive hints anytime'));
 pass('analysis shortcut requires explicit setup confirmation without voice startup');
 await capture('saved-analysis','/history/1');
 assert((await page.locator('body').innerText()).includes('Demonstrated (1)'));
 await page.locator('.skill-chip-unknown').first().click();
 assert((await page.locator('.skill-inspector').innerText()).includes('Evidence classification is unavailable'));
 assert((await page.locator('body').innerText()).includes('checkmarks are temporary'));
 pass('missing evidence stays unknown and temporary marks are disclosed');
 await capture('history-dialog','/history');
 const trigger=page.locator('.pm-menu-trigger').first();await trigger.click();await page.getByRole('menuitem',{name:/Delete/}).first().click();
 const dialog=page.getByRole('dialog');await dialog.waitFor();
 assert.equal(await page.evaluate(()=>document.activeElement.textContent),'Cancel');
 for(let i=0;i<8;i++){await page.keyboard.press('Tab');assert(await dialog.evaluate(e=>e.contains(document.activeElement)));}
 await page.keyboard.press('Escape');assert(await trigger.evaluate(e=>e===document.activeElement));
 pass('dialog contains focus, starts on Cancel, and restores its trigger');
 for(const width of [320,375,768,1440]){
  await capture('analyzer','/analyze',width);
  const bounds=await page.locator('.resume-form input:not([type=file]),.resume-form textarea,.upload-dropzone').evaluateAll(es=>es.map(e=>{const r=e.getBoundingClientRect();return{right:r.right,left:r.left}}));
  assert(bounds.every(b=>b.left>=0&&b.right<=width),JSON.stringify({width,bounds}));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('#resume-file').setInputFiles('backend/tests/fixtures/synthetic_profiles/profile_2_coursework_only.pdf');await page.getByRole('button',{name:'Analyze Resume',exact:true}).click();
  await page.getByRole('button',{name:'Analyze Again'}).waitFor();await page.screenshot({path:`${dir}/analyzer-results-${width}.png`,fullPage:true});
  await capture('practice','/practice',width);await capture('report','/reports/audit-interview',width);await capture('dashboard','/dashboard',width);
  if(width<=768){
   const opener=page.getByRole('button',{name:'Open navigation menu'});await opener.click();const drawer=page.getByRole('dialog');await drawer.waitFor();
   assert(await drawer.evaluate(e=>e.contains(document.activeElement)));
   for(let i=0;i<15;i++){await page.keyboard.press('Tab');assert(await drawer.evaluate(e=>e.contains(document.activeElement)));}
   await page.screenshot({path:`${dir}/drawer-${width}.png`,fullPage:true});await page.keyboard.press('Escape');assert(await opener.evaluate(e=>e===document.activeElement));
   assert(await page.locator('aside').evaluate(e=>e.inert));
   await opener.click();await page.locator('.sidebar-backdrop').click({position:{x:width-10,y:800}});assert(!(await page.locator('aside').getAttribute('class')).includes('sidebar-open'));
  }
  pass(`bounds and keyboard checks at ${width}px`);
 }
 await capture('profile','/profile');assert(!(await page.locator('body').innerText()).includes('Verified'));
 await capture('interview','/interview/audit-interview?mode=text',375);assert(await page.getByLabel('Your answer',{exact:true}).isVisible());
 pass('account email accuracy and explicit interview answer label');
 await writeFile(`${dir}/regression-results.json`,JSON.stringify({passed,requests,creates},null,2));
}finally{await writeFile(`${dir}/observations.json`,JSON.stringify(observations,null,2));await browser.close();}
