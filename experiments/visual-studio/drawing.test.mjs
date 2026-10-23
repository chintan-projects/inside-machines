import test from 'node:test';
import assert from 'node:assert/strict';
import {pixel} from './drawing.ts';
const luminance=rgb=>rgb.map(v=>{const n=v/255;return n<=.04045?n/12.92:((n+.055)/1.055)**2.4;})
  .reduce((sum,n,i)=>sum+n*[.2126,.7152,.0722][i],0);
test('every supported toy brightness retains readable numeral contrast at phone text sizes',()=>{
  for(let value=0;value<=10;value++) {
    const svg=pixel(0,0,78,value),fills=[...svg.matchAll(/fill="([^"]+)"/g)].map(m=>m[1]);
    const background=fills[0].match(/\d+/g).map(Number),foreground=fills[1].slice(1).match(/../g).map(n=>parseInt(n,16));
    const a=luminance(background),b=luminance(foreground),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
    assert.ok(ratio>=4.5,`brightness ${value}: ${ratio}`);
  }
});
