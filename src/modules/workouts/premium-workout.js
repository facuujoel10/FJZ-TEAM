(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.TeamFJZPremiumWorkout=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const VERSION='22.2B-V';
  const commentDrafts=new Map();
  const commentBusy=new Set();
  let currentSaveState={kind:'idle',at:null,detail:null};

  function normalizeDecimal(value){
    let s=String(value??'').trim().replace(',','.');
    s=s.replace(/[^0-9.]/g,'');
    const first=s.indexOf('.');
    if(first>=0)s=s.slice(0,first+1)+s.slice(first+1).replace(/\./g,'');
    return s;
  }
  function fieldContract(field){
    if(field==='weight')return Object.freeze({inputMode:'decimal',step:'0.5',min:'0',label:'Carga actual'});
    if(field==='rir')return Object.freeze({inputMode:'decimal',step:'0.5',min:'0',max:'10',label:'RIR'});
    return Object.freeze({inputMode:'numeric',step:'1',min:'0',label:'Repeticiones'});
  }
  function hasDOM(){return typeof document!=='undefined'&&!!document.querySelector}
  function activeWorkout(){
    if(!hasDOM())return false;
    return !!document.querySelector('#view .session-card')&&!!document.querySelector('#view button[onclick*="finishWorkout"]');
  }
  function statusCopy(kind,detail){
    if(kind==='saving')return {label:'Guardando sesión',copy:'Confirmando el entrenamiento en la nube.',tone:'saving'};
    if(kind==='success')return {label:'Guardado confirmado',copy:'La sesión fue confirmada por el servidor.',tone:'success'};
    if(kind==='failed')return {label:'Guardado pendiente',copy:'No hubo confirmación del servidor. Podés reintentar sin duplicar la sesión.',tone:'error'};
    if(kind==='draft_saved')return {label:'Borrador protegido',copy:detail&&detail.when?'Guardado local '+detail.when+'. La sesión todavía no está finalizada.':'Tus cambios están protegidos localmente. La sesión todavía no está finalizada.',tone:'draft'};
    if(kind==='pending')return {label:'Cambios pendientes',copy:'Tus datos están en el borrador del entrenamiento; aún no es una sesión finalizada.',tone:'pending'};
    return {label:'Entrenamiento en curso',copy:'Registrá tus series. El éxito final sólo aparece después de confirmación cloud.',tone:'idle'};
  }
  function renderSaveState(){
    if(!hasDOM()||!activeWorkout())return null;
    const view=document.getElementById('view');if(!view)return null;
    let node=document.getElementById('v22WorkoutSaveState');
    if(!node){
      node=document.createElement('div');
      node.id='v22WorkoutSaveState';
      node.className='v22-workout-save-state';
      node.setAttribute('role','status');
      node.setAttribute('aria-live','polite');
      const anchor=document.getElementById('v145AutosaveBox')||view.querySelector('.hero');
      if(anchor)anchor.insertAdjacentElement('afterend',node);
    }
    const copy=statusCopy(currentSaveState.kind,currentSaveState.detail);
    node.dataset.state=copy.tone;
    node.innerHTML='<span class="v22-save-dot" aria-hidden="true"></span><div><strong>'+copy.label+'</strong><small>'+copy.copy+'</small></div>';
    return node;
  }
  function setSaveState(kind,detail){
    currentSaveState={kind:String(kind||'idle'),at:new Date().toISOString(),detail:detail||null};
    renderSaveState();
    return currentSaveState;
  }
  function markDraftChanged(){setSaveState('pending');updateProgress()}
  function draftProtected(when){
    let label=null;
    try{label=when?new Date(when).toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'}):null}catch(_e){}
    setSaveState('draft_saved',{when:label});
  }
  function labelSetGrid(grid,cardIndex,setIndex){
    const inputs=Array.from(grid.querySelectorAll('input'));
    [['weight',0],['reps',1],['rir',2]].forEach(function(pair){
      const field=pair[0],pos=pair[1],input=inputs[pos];
      if(!input)return;
      const contract=fieldContract(field);
      input.dataset.v22Field=field;
      input.inputMode=contract.inputMode;
      input.setAttribute('step',contract.step);
      if(contract.min!=null)input.setAttribute('min',contract.min);
      if(contract.max!=null)input.setAttribute('max',contract.max);
      input.setAttribute('aria-label',contract.label+' · ejercicio '+(cardIndex+1)+' · serie '+(setIndex+1));
      input.autocomplete='off';
      const label=input.closest('label');
      if(label)label.classList.add('v22-set-field','v22-set-field-'+field);
    });
    grid.classList.add('v22-premium-set');
    grid.dataset.series=String(setIndex+1);
  }
  function decorateReference(card){
    card.querySelectorAll('.v205-prev-load').forEach(function(node){
      node.classList.add('v22-previous-load');
      node.setAttribute('aria-label','Carga anterior de referencia');
    });
    card.querySelectorAll('.recommend').forEach(function(node){
      node.classList.add('v22-recommendation');
      if(!node.querySelector('.v22-reference-label')){
        const label=document.createElement('div');
        label.className='v22-reference-label';
        label.textContent=node.classList.contains('coach')?'Indicación del coach':'Recomendación';
        node.prepend(label);
      }
    });
    card.querySelectorAll('.coach-note').forEach(function(node){node.classList.add('v22-last-session-reference')});
  }
  function decorateCard(card,index){
    card.classList.add('v22-premium-exercise');
    card.dataset.exerciseNumber=String(index+1);
    const head=card.querySelector('.day-head');
    const strong=head&&head.querySelector('strong');
    if(head&&!head.querySelector('.v22-exercise-kicker')&&strong){
      const kicker=document.createElement('span');
      kicker.className='v22-exercise-kicker';
      kicker.textContent='EJERCICIO '+String(index+1).padStart(2,'0');
      strong.parentElement.insertBefore(kicker,strong);
    }
    card.querySelectorAll('.set-grid').forEach(function(grid,si){labelSetGrid(grid,index,si)});
    const comment=Array.from(card.querySelectorAll('button')).find(function(x){return /comentario/i.test(String(x.textContent||''))});
    if(comment){
      comment.classList.add('v22-comment-action');
      comment.setAttribute('aria-label','Agregar comentario a '+String(strong?strong.textContent:'este ejercicio').replace(/^\d+\.\s*/,''));
    }
    decorateReference(card);
  }
  function updateProgress(){
    if(!hasDOM()||!activeWorkout())return null;
    const grids=Array.from(document.querySelectorAll('#view .set-grid'));
    const completed=grids.filter(function(grid){
      const inputs=Array.from(grid.querySelectorAll('input'));
      return inputs.length>=3&&inputs.every(function(input){
        const v=String(input.value??'').trim();
        return v!==''&&Number.isFinite(Number(v.replace(',','.')));
      });
    }).length;
    let label=document.getElementById('v22WorkoutProgressLabel');
    if(!label){
      const progress=document.querySelector('#view .session-progress');
      if(progress){
        label=document.createElement('div');
        label.id='v22WorkoutProgressLabel';
        label.className='v22-workout-progress-label';
        progress.insertAdjacentElement('afterend',label);
      }
    }
    if(label)label.innerHTML='<strong>'+completed+'/'+grids.length+'</strong><span>series con registro</span>';
    return {completed:completed,total:grids.length};
  }
  function enhanceWorkout(){
    if(!activeWorkout())return false;
    const view=document.getElementById('view');
    if(view)view.classList.add('v22-premium-workout');
    const hero=view&&view.querySelector('.hero');
    if(hero)hero.classList.add('v22-workout-hero');
    if(hero&&!hero.querySelector('.v22-workout-eyebrow')){
      const h=hero.querySelector('h2');
      if(h){
        const eyebrow=document.createElement('div');
        eyebrow.className='v22-workout-eyebrow';
        eyebrow.textContent='ENTRENAMIENTO ACTIVO';
        h.parentElement.insertBefore(eyebrow,h);
      }
    }
    const finish=view&&view.querySelector('button[onclick*="finishWorkout"]');
    if(finish){
      finish.classList.add('v22-finish-workout');
      finish.setAttribute('aria-label','Finalizar sesión y guardar entrenamiento');
    }
    Array.from(view.querySelectorAll('.session-card')).forEach(decorateCard);
    renderSaveState();
    updateProgress();
    try{globalThis.TeamFJZVisualRedesign?.enhanceWorkout(view)}catch(_e){}
    return true;
  }
  function decorateSuccessModal(){
    if(!hasDOM())return false;
    const host=document.querySelector('#modal .v207-save-actions');
    if(!host||host.querySelector('.v22-history-after-save'))return false;
    const button=document.createElement('button');
    button.className='btn v22-history-after-save';
    button.textContent='Ver historial';
    button.onclick=function(){
      try{closeModal()}catch(_e){}
      try{studentTab='history';currentDay=-1;render()}catch(_e){}
    };
    host.prepend(button);
    return true;
  }
  function commentDraft(uid){return commentDrafts.get(String(uid||''))||null}
  function bindCommentDraft(target){
    if(!hasDOM()||!target||!target.uid)return false;
    const key=String(target.uid);
    const saved=commentDrafts.get(key);
    const text=document.getElementById('v73FeedbackMessage');
    if(text){
      if(saved&&saved.message&&!text.value)text.value=saved.message;
      text.dataset.v22ExerciseUid=key;
      text.oninput=function(){
        const prior=commentDrafts.get(key)||{};
        commentDrafts.set(key,{message:this.value,type:prior.type||'comment'});
      };
    }
    const radios=Array.from(document.querySelectorAll('input[name="v73FeedbackType"]'));
    if(saved&&saved.type){
      const wanted=radios.find(function(x){return x.value===saved.type});
      if(wanted)wanted.checked=true;
    }
    radios.forEach(function(radio){
      radio.onchange=function(){
        const prior=commentDrafts.get(key)||{};
        commentDrafts.set(key,{message:prior.message||'',type:this.value});
      };
    });
    const modal=document.getElementById('modal');
    if(modal){
      modal.classList.add('v22-comment-modal');
      if(!modal.querySelector('#v22CommentClose')){
        const close=document.createElement('button');
        close.id='v22CommentClose';
        close.type='button';
        close.className='btn ghost small v22-comment-close';
        close.textContent='Cerrar';
        close.setAttribute('aria-label','Cerrar comentario');
        close.onclick=function(){try{closeModal()}catch(_e){}};
        modal.prepend(close);
      }
    }
    try{globalThis.TeamFJZVisualRedesign?.enhanceCommentModal(modal)}catch(_e){}
    return true;
  }
  function beginCommentSubmit(uid,message,type){
    const key=String(uid||'');
    if(!key||commentBusy.has(key))return false;
    commentBusy.add(key);
    commentDrafts.set(key,{message:String(message||''),type:String(type||'comment')});
    if(hasDOM()){
      const button=document.querySelector('#modal button[onclick*="submitExerciseFeedbackV73"]');
      if(button){
        button.disabled=true;
        button.dataset.v22OriginalText=button.textContent;
        button.textContent='Guardando comentario…';
      }
    }
    return true;
  }
  function endCommentSubmit(uid,success){
    const key=String(uid||'');
    commentBusy.delete(key);
    if(success){
      commentDrafts.delete(key);
      try{globalThis.__fjzQuickSavedV264&&globalThis.__fjzQuickSavedV264('Comentario guardado')}catch(_e){}
      return true;
    }
    if(hasDOM()){
      const button=document.querySelector('#modal button[onclick*="submitExerciseFeedbackV73"]');
      if(button){
        button.disabled=false;
        button.textContent=button.dataset.v22OriginalText||'Enviar al coach';
      }
    }
    return false;
  }
  function clearCommentDraft(uid){commentDrafts.delete(String(uid||''))}
  return Object.freeze({
    VERSION:VERSION,normalizeDecimal:normalizeDecimal,fieldContract:fieldContract,
    enhanceWorkout:enhanceWorkout,updateProgress:updateProgress,setSaveState:setSaveState,
    decorateSuccessModal:decorateSuccessModal,
    markDraftChanged:markDraftChanged,draftProtected:draftProtected,commentDraft:commentDraft,
    bindCommentDraft:bindCommentDraft,beginCommentSubmit:beginCommentSubmit,
    endCommentSubmit:endCommentSubmit,clearCommentDraft:clearCommentDraft
  });
});
