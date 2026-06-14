const fs = require('fs');
const path = require('path');

const viewHtml = path.join(__dirname, '../dist/build/app/__uniappview.html');
let content = fs.readFileSync(viewHtml, 'utf-8');

const headPatches = `<script>
// Suppress HBuilderX debug bridge __uuid__ errors
window.addEventListener('error',function(e){
  if(e.message&&typeof e.message==='string'&&e.message.indexOf('__uuid__')!==-1){
    e.preventDefault();
  }
},true);
</script>
<script>
// Wrap native plus (Android addJavascriptInterface) with a Proxy that
// patches currentWebview().app.__uuid__ to suppress debug-bridge errors,
// WITHOUT breaking native messaging (service↔view communication).
(function(){
  if(typeof plus==='undefined')return;
  try{
    var _np=plus;
    window.plus=new Proxy(_np,{
      get:function(t,p){
        if(typeof p==='symbol')return t[p];
        if(p==='ready')return function(cb){try{cb()}catch(e){}};
        var v=t[p];
        if(typeof v==='function')return v.bind(t);
        if(p==='webview'){
          var _wv=v;
          return new Proxy(_wv,{
            get:function(wt,wp){
              if(typeof wp==='symbol')return wt[wp];
              var wv=wt[wp];
              if(typeof wv==='function')return wv.bind(wt);
              if(wp==='currentWebview'){
                return function(){
                  var cw=wt.currentWebview();
                  if(cw&&typeof cw==='object'){
                    return new Proxy(cw,{
                      get:function(ct,cp){
                        if(typeof cp==='symbol')return ct[cp];
                        if(cp==='app')return ct.app||{__uuid__:''};
                        var cv=ct[cp];
                        return typeof cv==='function'?cv.bind(ct):cv;
                      }
                    });
                  }
                  return cw;
                };
              }
              return wv;
            }
          });
        }
        return v;
      }
    });
  }catch(e){}
})();
console.log('[VIEW] plus proxied');
</script>
`;

let patched = false;

if (!content.includes('[VIEW] plus proxied')) {
  content = content.replace('<meta charset="UTF-8" />',
    '<meta charset="UTF-8" />' + headPatches);
  console.log('✓ Inserted plus Proxy wrapper and __uuid__ handler');
  patched = true;
}

if (patched) {
  fs.writeFileSync(viewHtml, content);
  console.log('✓ __uniappview.html updated successfully');
} else {
  console.log('→ __uniappview.html already up to date');
}
