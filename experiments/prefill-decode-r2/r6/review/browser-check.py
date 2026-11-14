"""Check the actual delivered local movie and computed experiment in Chrome."""
import json
import math
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1];out=root/'review/qa';out.mkdir(exist_ok=True)
url='http://127.0.0.1:8885/'
record=sorted((root/'video/production/episodes/ep01/delivery-records').iterdir())[-1]
timeline=json.loads((record/'timeline.json').read_text());duration=timeline['duration_seconds']
expected_cues=(root/'review-site/captions.vtt').read_text().count(' --> ')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
 context=browser.new_context(viewport={'width':1440,'height':1100},reduced_motion='reduce')
 page=context.new_page();errors=[];console=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
 page.on('request',lambda r:requests.append(r.url))
 page.goto(url+'#film')
 assert page.locator('#film-panel').is_visible() and page.locator('#lesson').is_hidden()
 assert str(math.ceil(duration/60))+' min' in page.locator('#film-mode').inner_text()
 assert page.locator('#film-chapters button').count()==8
 target=timeline['scenes'][3]['start_seconds']
 page.locator('#film-chapters button').nth(3).click()
 page.locator('#sound').click()
 page.wait_for_function('()=>{const v=document.querySelector("video");return v.readyState>=3&&!v.seeking&&!v.paused&&v.videoWidth===1920&&v.videoHeight===1080&&v.currentTime>1}',timeout=30000)
 before=page.locator('video').evaluate('(v)=>v.currentTime')
 page.wait_for_function('(before)=>{const v=document.querySelector("video");return !v.paused&&!v.seeking&&v.currentTime>before+.5}',arg=before,timeout=30000)
 media=page.locator('video').evaluate('(v)=>({duration:v.duration,time:v.currentTime,width:v.videoWidth,height:v.videoHeight,muted:v.muted,volume:v.volume,audio_decoded_bytes:v.webkitAudioDecodedByteCount})')
 assert target<=before<target+4,(target,before)
 assert media['time']>before and media['width']==1920 and media['height']==1080
 assert not media['muted'] and media['volume']==1 and media['audio_decoded_bytes']>0
 assert page.locator('#media-status').inner_text().startswith('Playing with sound.')
 assert abs(media['duration']-duration)<.2
 page.wait_for_function('()=>{const t=document.querySelector("video").textTracks[0];return t?.cues?.length>0}')
 track=page.locator('video').evaluate('(v)=>({cues:v.textTracks[0].cues.length,mode:v.textTracks[0].mode})')
 assert track['cues']==expected_cues and track['mode']=='showing'
 for i,scene in enumerate(timeline['scenes']):
  page.locator('video').evaluate('(v)=>v.pause()');page.locator('#film-chapters button').nth(i).click()
  page.wait_for_function('(target)=>{const v=document.querySelector("video");return !v.seeking&&v.readyState>=2&&Math.abs(v.currentTime-target)<.1}',arg=scene['start_seconds'],timeout=30000)
  at=page.locator('video').evaluate('(v)=>v.currentTime');assert abs(at-scene['start_seconds'])<.1
 page.locator('video').evaluate('(v)=>{v.muted=true;v.currentTime=310}')
 page.locator('video').evaluate('(v)=>v.play()')
 page.wait_for_function('()=>{const v=document.querySelector("video");return !v.seeking&&!v.paused&&v.currentTime>310.5&&v.textTracks[0].activeCues?.length>0}',timeout=30000)
 assert page.locator('#media-status').inner_text().startswith('Playing silently.')
 page.locator('#sound').click()
 page.wait_for_function('()=>document.querySelector("#media-status").textContent.startsWith("Playing with sound.")')
 page.locator('video').evaluate('(v)=>v.pause()')
 page.wait_for_function('()=>document.querySelector("#media-status").textContent.startsWith("Paused.")')
 page.locator('#film-panel').scroll_into_view_if_needed();page.screenshot(path=str(out/'desktop-film.png'))
 page.locator('#core-mode').click();assert page.locator('#lesson').is_visible() and page.locator('video').evaluate('(v)=>v.paused')
 layout=[];scenarios=[]
 for width in [390,768,1440]:
  page.set_viewport_size({'width':width,'height':1000})
  for word in ['sky','and','blue']:
   page.locator('#word').select_option(word)
   for phase in ['0','1']:
    page.locator('#pass').select_option(phase)
    for layer in ['0','1']:
     page.locator('#layer').select_option(layer)
     choices=[]
     for cache in ['keep','clear']:
      page.locator('#cache').select_option(cache)
      assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,word,phase,layer,cache)
      metrics=page.locator('.metric').all_text_contents();choices.append(metrics[1])
      expected=3 if phase=='0' else (1 if cache=='keep' else 4)
      assert metrics[0].startswith(str(expected)+' '),metrics
      assert page.locator('tbody tr').count()==(3 if phase=='0' else 4)
      layout.append([width,word,phase,layer,cache])
     assert choices[0]==choices[1]
     scenarios.append([word,phase,layer,choices[0]])
  page.locator('#reset').click()
  assert page.locator('#word').input_value()=='sky' and page.locator('#cache').input_value()=='keep'
  page.locator('#lesson').scroll_into_view_if_needed();page.screenshot(path=str(out/f'experiment-{width}.png'))
  page.locator('#film-mode').click();assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  page.locator('#film-panel').scroll_into_view_if_needed();page.screenshot(path=str(out/f'film-{width}.png'));page.locator('#core-mode').click()
 page.locator('#read-along summary').click();assert page.locator('#transcript').is_visible() and 'chosen' in page.locator('#transcript').inner_text()
 page.locator('#reset').click();assert page.locator('video').evaluate('(v)=>v.paused&&v.currentTime===0')
 page.wait_for_function('()=>document.querySelector("#media-status").textContent.startsWith("Paused.")')
 page.locator('#pass').select_option('0');page.locator('#film-mode').click();page.locator('#core-mode').click();assert page.locator('#pass').input_value()=='0'
 page.locator('#reset').focus();page.keyboard.press('Enter');assert page.locator('#pass').input_value()=='1'
 assert context.request.get(url+'captions.vtt').status==200
 rr=context.request.get(url+'film.mp4',headers={'Range':'bytes=100-199'});assert rr.status==206 and rr.body()==(root/'review-site/film.mp4').read_bytes()[100:200]
 assert context.request.get(url+'film.mp4',headers={'Range':'bytes=999999999999-'}).status==416
 assert context.request.head(url+'film.mp4').status==200
 assert context.request.post(url).status==405
 for private in ['authoring/','review/core-readiness.json','../.env.local','video/production/plan.yaml']:assert context.request.get(url+private).status==404
 assert not errors and not console,(errors,console)
 assert all(r.startswith(url) for r in requests),requests
 result={'browser':browser.version,'media':media,'captions':track,'chapter_seek_before_play':True,'all_eight_chapters_seek':True,'all_chapter_seek_decodes_complete':True,'active_caption_during_playback':True,'sound_and_pause_status_tracks_media':True,'reset_seeks_and_pauses':True,'computed_scenarios':scenarios,'responsive_states_checked':len(layout),'widths':[390,768,1440],'keyboard_reset':True,'mode_preserves_experiment':True,'http_ranges_and_private_paths':True,'page_errors':errors,'console_errors':console,'no_external_requests':True}
 (out/'browser-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='computed_scenarios'},indent=2))
 browser.close()
