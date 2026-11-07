(() => {
  function extractCodeBlock(root) {
    const langEl = root.querySelector('.ActionBar-KWWAct .truncate, [class*="ActionBar"] .truncate');
    const lang = (langEl && langEl.textContent.trim()) || '';
    const pre = root.querySelector('pre');
    const cm = root.querySelector('.cm-content, .cm-scroller, .ViewerContent-Cg8AgN, [class*="ViewerContent"]');
    let code = '';
    if (pre) code = pre.innerText; else if (cm) code = cm.innerText; else {
      const clone = root.cloneNode(true);
      clone.querySelectorAll('button, [class*="ActionBar"]').forEach(n => n.remove());
      code = clone.innerText;
    }
    return '\n\n```' + lang.toLowerCase() + '\n' + code.replace(/\u00a0/g,' ').replace(/\n+$/, '') + '\n```\n\n';
  }
  function nodeToMd(node, depth=0) {
    if (!node || depth > 50) return '';
    if (node.nodeType === Node.TEXT_NODE) return node.textContent.replace(/\u00a0/g,' ');
    if (node.nodeType !== Node.ELEMENT_NODE) return '';
    const tag = node.tagName.toLowerCase();
    const cls = String(node.className || '');
    if (['script','style','noscript','svg','button','nav','img','textarea','input'].includes(tag)) return '';
    if (/ActionBar|sr-only|visually-hidden/.test(cls)) return '';
    if (/Root-iW7ipz/.test(cls) || (node.querySelector && node.querySelector('.cm-scroller') && /rounded/.test(cls) && node.querySelector('[class*="ActionBar"]'))) return extractCodeBlock(node);
    if (tag === 'pre') { const code = node.querySelector('code'); return '\n\n```\n' + (code||node).innerText.replace(/\n+$/, '') + '\n```\n\n'; }
    if (tag === 'code' && (!node.parentElement || node.parentElement.tagName.toLowerCase() !== 'pre')) return '`' + node.innerText + '`';
    if (tag === 'br') return '\n';
    if (tag === 'hr') return '\n\n---\n\n';
    if (/^h[1-6]$/.test(tag)) {
      const level = Number(tag[1]);
      const inner = Array.from(node.childNodes).map(n => nodeToMd(n, depth+1)).join('').replace(/\s+/g,' ').trim();
      return '\n\n' + '#'.repeat(level) + ' ' + inner + '\n\n';
    }
    if (tag === 'li') {
      const parent = node.parentElement && node.parentElement.tagName.toLowerCase();
      const bullet = parent === 'ol' ? '1. ' : '- ';
      return bullet + Array.from(node.childNodes).map(n => nodeToMd(n, depth+1)).join('').trim().replace(/\n+/g, '\n  ') + '\n';
    }
    if (tag === 'ul' || tag === 'ol') return '\n' + Array.from(node.childNodes).map(n => nodeToMd(n, depth+1)).join('') + '\n';
    if (tag === 'p') { const inner = Array.from(node.childNodes).map(n => nodeToMd(n, depth+1)).join('').trim(); return inner ? inner + '\n\n' : ''; }
    if (tag === 'strong' || tag === 'b') return '**' + Array.from(node.childNodes).map(n => nodeToMd(n, depth+1)).join('') + '**';
    if (tag === 'em' || tag === 'i') return '*' + Array.from(node.childNodes).map(n => nodeToMd(n, depth+1)).join('') + '*';
    if (tag === 'blockquote') { const inner = Array.from(node.childNodes).map(n => nodeToMd(n, depth+1)).join('').trim(); return '\n' + inner.split('\n').map(l => '> ' + l).join('\n') + '\n\n'; }
    if (tag === 'table') return '\n\n' + node.innerText.trim() + '\n\n';
    const role = node.getAttribute && node.getAttribute('role');
    if (role === 'navigation' || role === 'complementary') return '';
    return Array.from(node.childNodes).map(n => nodeToMd(n, depth+1)).join('');
  }
  function msgKey(el, md) {
    const id = el.getAttribute('data-message-id') || el.id || '';
    if (id) return 'id:' + id;
    const h = (md.match(/^#+\s+.+$/m)||[md.slice(0,60)])[0];
    return 'h:' + h + '|' + Math.round(md.length/200);
  }
  function harvest(store, order) {
    const roots = [...document.querySelectorAll('[class*="MarkdownRoot"]')]
      .map(el => ({el, top: el.getBoundingClientRect().top}))
      .sort((a,b)=>a.top-b.top);
    for (const {el} of roots) {
      const md = nodeToMd(el).replace(/\n{3,}/g,'\n\n').trim();
      if (!md || md.length < 40) continue;
      const k = msgKey(el, md);
      if (!store.has(k)) { store.set(k, md); order.push(k); }
      else if (md.length > store.get(k).length) store.set(k, md);
    }
  }
  async function run() {
    for (let i=0;i<40;i++) { if (document.querySelectorAll('[class*="MarkdownRoot"]').length) break; await new Promise(r=>setTimeout(r,200)); }
    let scroller=null,max=0;
    document.querySelectorAll('*').forEach(el => {
      const st=getComputedStyle(el);
      if ((st.overflowY==='auto'||st.overflowY==='scroll') && el.scrollHeight>el.clientHeight+50 && el.clientHeight>200 && el.scrollHeight>max){max=el.scrollHeight;scroller=el;}
    });
    const store=new Map(); let order=[];
    if (!scroller) {
      harvest(store, order);
      const full=order.map(k=>store.get(k)).join('\n\n\n');
      return {title:document.title,url:location.href,full,h1s:[...full.matchAll(/^#\s+(.+)$/gm)].map(m=>m[1]),len:full.length,msgCount:order.length};
    }
    for (let i=0;i<70;i++) {
      const before=scroller.scrollHeight;
      scroller.scrollTop=0;
      await new Promise(r=>setTimeout(r,320));
      if (i>10 && scroller.scrollHeight===before) break;
    }
    store.clear(); order=[];
    scroller.scrollTop=0;
    await new Promise(r=>setTimeout(r,250));
    for (let i=0;i<150;i++) {
      harvest(store, order);
      const prev=scroller.scrollTop;
      const target=Math.min(scroller.scrollHeight, scroller.scrollTop + Math.floor(scroller.clientHeight*0.65));
      scroller.scrollTop=target;
      await new Promise(r=>setTimeout(r,200));
      if (Math.abs(scroller.scrollTop-prev)<2) {
        scroller.scrollTop=scroller.scrollHeight;
        await new Promise(r=>setTimeout(r,250));
        harvest(store, order);
        break;
      }
    }
    const full=order.map(k=>store.get(k)).join('\n\n\n');
    const h1s=[...full.matchAll(/^#\s+(.+)$/gm)].map(m=>m[1]);
    return {title:document.title,url:location.href,full,h1s,len:full.length,msgCount:order.length};
  }
  return run();
})()
