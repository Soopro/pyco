/*
supWysiwygEditor

Author : Redy Ru
Email : redy.ru@gmail.com
License : 2014 MIT
Version 1.0.0

---- Usage ----
    On your html create a editor:
        <div sup-angular-wysiwyg name="sup-editor" toolbar="sup-editor-toolbar" textarea="sup-editor-textarea" components="sup-editor-components" strip-br="true" contenteditable="true" ng-model="...">
        <textarea name="sup-editor-textarea"></textarea>
    and make a toolbar:
        <div name="sup-editor-toolbar">.....</div>
    and make a components box:
        <div name="sup-editor-components"></div>
    
    if you wont use angularjs, you can always use it directly.
        var editor=new supWysiwygEditor();
        editor.init(editor,toolbar,components,options)

*/


var supWysiwygEditor = (function () {
    'use strict';

//---------------- Global Variables --------------
    /* Timestamp */
    var now=Date.now();
    /* Listeners */

    var selectHandler, focusHandler, blurHandler,
        orderedList, unorderedList, outdentText, indentText,
        makeH1, makeH2, makeH3, makeH4, makeH5, makeH6, makePre, makeQuote, insertCode,makeP, makeBold, makeItalic,
        clearStyles, makeTable, insertHR, insertA, insertImg,
        targetA, targetImg, justifyLeft, justifyRight, justifyCenter, justifyFull,
        makeStrike, makeUnderline, makeSup, makeSub, reDo, unDo, toggleHtml, blowupHtml, textareaFocus,
        editLink, unLink, editImg, removeImg, replaceImg;

    /* Callback*/
    var insertImgHook, insertHook, focusHook, blurHook, replaceImgHook, setHTMLOpenHook, setHTMLCloseHook;
    
    /* Components */
    var $componentGroup, $componentLocker;
    
    var $componentLink, 
        $currentLink={"element":null,"preview":null},
        $componentLinkTpl='<div component_link data-url="" class="link-property popover bottom"><div class="arrow"></div><div class="popover-content"><div class="btn-group"><button class="btn btn-default btn-edit-link compbtn"><i class="fa fa-edit"></i></button><button class="btn btn-default btn-remove-link compbtn"><i class="fa fa-unlink"></i></button><a href="#" target="_blank" class="btn btn-default btn-preview preview-link compbtn"><i class="fa fa-eye"></i></a></div></div></div>';

    var $componentImage, srcInput, altInput, linkInput, blankInput,
        $currentImage={"element":null,"link":null},
        $componentImageTpl='<div component_image data-url="" class="img-property popover bottom"><div class="arrow"></div><div class="popover-content"><fieldset class="form-group"><label class="subject">URL:</label><input name="src" type="text" value="" placeholder="Image URL here." class="form-control" /></fieldset><fieldset class="form-group"><label class="subject">Alt:</label><input name="alt" type="text" value="" placeholder="Description of this image." class="form-control" /></fieldset><fieldset class="form-group"><label class="subject">Link:</label><input name="link" type="text" value="" placeholder="Link of this image." class="form-control" /></fieldset><fieldset class="form-group window"><label for="link-target-'+now+'"><input id="link-target-'+now+'" name="link-target" type="checkbox">&nbsp;<span class="subject">Open in new window.</span></label></fieldset><fieldset class="form-group submit"><button class="btn btn-default btn-edit-img compbtn"><i class="fa fa-check"></i></button><button class="btn btn-default btn-replace-img compbtn"><i class="fa fa-th"></i></button><button class="btn btn-default btn-remove-img compbtn"><i class="fa fa-trash-o"></i></button></fieldset></div></div>';
    var compbtnList=[
            {name:"edit-link", handler:"editLink", ico:"", status:""},
            {name:"remove-link", handler:"unLink", ico:"", status:""},
            {name:"preview-link", handler:"", ico:"", status:""},
            {name:"edit-img", handler:"editImg", ico:"", status:""},
            {name:"remove-img", handler:"removeImg", ico:"", status:""},
            {name:"replace-img", handler:"replaceImg", ico:"", status:""},
        ];
    
    
    /* Variables */
    var $editor, $toolbar, $textarea,

        selectedNode,
        selectedOrg,
        startRange,
        endRange,
        selObj,
        selRange,
        savedRange,
        textareaTouched;

    
    var defaultToolbarBtns=[
            ['h1','h2','h3','h4','h5','h6','p','quote','pre','code'],
            ['i','b','strike','underline','sub','sup'],
            ['ol','ul','outdent','indent','hr','img','a','jleft','jcenter','jright','jfull'],
            ['ud','rd','clear','bomb','html'],
        ];
        
    var btnList=[
            {name:"h1", handler:"makeH1", ico:null, status:""},
            {name:"h2", handler:"makeH2", ico:null, status:""},
            {name:"h3", handler:"makeH3", ico:null, status:""},
            {name:"h4", handler:"makeH4", ico:null, status:""},
            {name:"h5", handler:"makeH5", ico:null, status:""},
            {name:"h6", handler:"makeH6", ico:null, status:""},
            {name:"p", handler:"makeP", ico:"paragraph"},
            {name:"quote", handler:"makeQuote", ico:"quote-right", status:""},
            {name:"pre", handler:"makePre", ico:null, status:""},
            {name:"code", handler:"insertCode", ico:null, status:""},
            
            {name:"i", handler:"makeItalic", ico:"italic", status:""},
            {name:"b", handler:"makeBold", ico:"bold", status:""},
            {name:"strike", handler:"makeStrike", ico:"strikethrough", status:""},
            {name:"underline", handler:"makeUnderline", ico:"underline", status:""},
            {name:"sub", handler:"makeSub", ico:"subscript", status:""},
            {name:"sup", handler:"makeSup", ico:"superscript", status:""},
            
            {name:"ol", handler:"orderedList", ico:"list-ol", status:""},
            {name:"ul", handler:"unorderedList", ico:"list-ul", status:""},
            {name:"outdent", handler:"outdentText", ico:"outdent", status:""},
            {name:"indent", handler:"indentText", ico:"indent", status:""},

            {name:"hr", handler:"insertHR", ico:"arrows-h", status:""},
            {name:"img", handler:"insertImg", ico:"picture-o", status:""},
            {name:"a", handler:"insertA", ico:"link", status:""},
            
            {name:"jleft", handler:"justifyLeft", ico:"align-left", status:""},
            {name:"jcenter", handler:"justifyCenter", ico:"align-center", status:""},
            {name:"jright", handler:"justifyRight", ico:"align-right", status:""},
            {name:"jfull", handler:"justifyFull", ico:"align-justify", status:""},
            
            {name:"rd", handler:"reDo", ico:"repeat", status:""},
            {name:"ud", handler:"unDo", ico:"undo", status:""},
            {name:"clear", handler:"clearStyles", ico:"eraser", status:""},
            {name:"bomb", handler:"blowupHtml", ico:"bomb", status:""},
            {name:"html", handler:"toggleHtml", ico:"code", status:""},
        ];
    var $btn_indent, $btn_outdent;
        
    var BFBL=['OL','UL','LI','TD','TH','TR','TBODY','TABLE','THEAD','TFOOT','DL','DD','DT'];
    var styleTags=['b','i','u','strong','sup','sub','strike','font'];
    var $options={
            free:true,
            nontoolbar:false,
            htmlfullscreen:true,
            firstview:'text',
            history:100,
        };
        
    var $property={
            name:'',
            order:0,
        };
        
    /* History */    
    var $history=[],
        $current_step=0;
    
    function historyManager(method){
        switch(method){
            case 'redo':
                if($current_step<$history.length-1){
                    $current_step+=1;
                    $editor.innerHTML=$history[$current_step];
                }
            break;
            case 'undo':
                if($current_step>0){
                    $current_step-=1;
                    $editor.innerHTML=$history[$current_step];
                }
            break;
            case 'record':
                $history.splice($current_step, Number.MAX_VALUE);
                $current_step++;
                if($current_step>=$options.history){
                    $current_step=$options.history;
                    $history.shift();
                }
                $history.push($editor.innerHTML);
            break;
        }
    }
    


//------------------- Event Handlers -----------------

    selectHandler = function (e) {
        stickyArea();
        getCurrentSelection();
        watcher();
    };
    
    focusHandler = function (e){
        savedRange=saveSelection();
        if($componentGroup){
            switchLinkComponent(false);
            if($componentLocker){
                $componentLocker=false;
            }else{
                switchImageComponent(false);
            }
        }
        focusHook();
        e.preventDefault();
    };
    
    blurHandler = function (e){
        if(!inEditor(e.target,true) && !childOf(e.target,$toolbar,true) && !childOf(e.target,$componentGroup,true) && !childOf(e.target,$textarea,true)){
            blurHook();
        }
    };

    targetImg = function (e) {
        var src, new_src, img, pos, alt, a;
        img=e.target;
        if(inEditor(img,true)){
            if(img.tagName && img.tagName=='IMG'){
                if(inEditor(img)){
                    src = img.getAttribute('src');
                    if($componentImage){
                        pos=cumulativeOffset(img);
                        switchImageComponent(src,pos,img,true);
                    }else{
                        new_src = prompt("Img:", src);
                        if (new_src) {
                            img.setAttribute('src',new_src);
                        } else if (new_src !== null) {
                            img.parentElement.removeChild(img);
                        }
                        historyManager('record');
                    }
                }
            }
        }
    };
    
    editImg = function (e) {
        var src, new_src, img
        
        historyManager('record');
        img=$currentImage.element;
        if (img && img.tagName =='IMG') {
            if(img.parentElement.tagName=="A" && img.parentElement.children.length==1){
                $currentImage.link=img.parentElement;
            }

            img.setAttribute('alt', altInput.value)
            img.setAttribute('src', srcInput.value);

            if($currentImage.link){
                $currentImage.link.setAttribute('href', linkInput.value);
                if(blankInput.checked){
                    $currentImage.link.setAttribute('target', '_blank');
                }else{
                    $currentImage.link.removeAttribute('target');
                }
                if(!linkInput.value){
                    $currentImage.link.outerHTML=$currentImage.link.innerHTML;
                }
            }else if(linkInput.value){
                $currentImage.link=document.createElement("a");
                $currentImage.link.setAttribute('href',linkInput.value);

                img.parentElement.replaceChild($currentImage.link,img);
                $currentImage.link.appendChild(img);
                if(blankInput.checked){
                    $currentImage.link.setAttribute('target', '_blank');
                }else{
                    $currentImage.link.removeAttribute('target');
                }
            }
            switchImageComponent(false);
        }
    };
    
    removeImg = function (e) {
        var src, new_src, img
        
        historyManager('record');
        img=$currentImage.element;
        if (img && img.tagName =='IMG') {
            if(!$currentImage.link){
                img.parentElement.removeChild(img);
            }else{
                $currentImage.link.parentElement.removeChild($currentImage.link);
            }
            switchImageComponent(false);
            
        }
    }
    
    targetA = function (e) {
        var url, new_url, a, pos;
        if(inEditor(selectedNode,true)){
            a = inElement(selectedNode,'A');
            if (a) {
                if(a.children.length==1){
                    var child=a.children[0];
                    if(child.tagName=='IMG'){
                        switchLinkComponent(false);
                        return;
                    }
                }
                url = a.getAttribute('href');

                if($componentLink){
                    pos=cumulativeOffset(a);
                    switchLinkComponent(url,pos,a,true);
                }else{
                    new_url=prompt("Link:", url);
                    if (new_url) {
                        a.setAttribute('href',new_url);
                    } else if (new_url !== null) {
                        a.outerHTML = a.innerHTML;
                    }
                    historyManager('record');
                }
            }
        }
    };
    
    editLink = function (e){
        var url, new_url, a
        
        historyManager('record');
        a=$currentLink.element;
        if (a && a.tagName =='A') {
            url = $componentLink.dataset.url;
            new_url=prompt("Link:", url);
            if(new_url){
                a.setAttribute('href',new_url);
                $componentLink.dataset.url=new_url;
                $currentLink.preview.setAttribute('href',new_url);
            }
        }
    };
    
    unLink = function (e){
        var a
        
        historyManager('record');
        a=$currentLink.element;
        if(a && a.tagName=="A"){
            a.outerHTML = a.innerHTML;
            switchLinkComponent(false);
        }
    };
    
    replaceImg = function (e){
        replaceImgHook();
        switchImageComponentDisplay(false);
    };

    orderedList = function (e) {
        var ol
        
        historyManager('record');
        if(inEditor(selectedNode)){
            execCmd('insertorderedlist');
            getCurrentSelection();
    
            ol = selectedNode.parentElement.parentElement;
            destroySpan(ol, true);
            if (ol.parentElement && ol.parentElement.tagName == "P") {
                ol.parentElement.outerHTML = ol.parentElement.innerHTML;
            }
        }
        switchIndentOutdentBtns();
    };

    unorderedList = function (e) {
        var ul
        
        historyManager('record');
        if(inEditor(selectedNode)){
            execCmd('insertunorderedlist');
            getCurrentSelection();
    
            ul = selectedNode.parentElement.parentElement;
            destroySpan(ul, true);
            if (ul.parentElement && ul.parentElement.tagName == "P") {
                ul.parentElement.outerHTML = ul.parentElement.innerHTML;
            }
        }
        switchIndentOutdentBtns();
    };
    
    outdentText = function (e) {
        if(inElement(selectedNode,'LI') || inElement(selectedNode,'OL')){
            execCmd('outdent');
            switchIndentOutdentBtns();
        }
    };

    indentText = function (e) {
        if(inElement(selectedNode,'LI') || inElement(selectedNode,'OL')){
            execCmd('indent');
            switchIndentOutdentBtns();
        }
    };

    makeH1 = function (e) {
        smartFormatBlock('h1');
    };
    makeH2 = function (e) {
        smartFormatBlock('h2');
    };
    makeH3 = function (e) {
        smartFormatBlock('h3');
    };
    makeH4 = function (e) {
        smartFormatBlock('h4');
    };
    makeH5 = function (e) {
        smartFormatBlock('h5');
    };
    makeH6 = function (e) {
        smartFormatBlock('h6');
    };

    makePre = function (e) {
        smartFormatBlock('pre');
    };
    
    makeQuote = function (e) {
        smartFormatBlock('blockquote');
    };
    
    insertCode = function (e) {
        var target, element
        
        historyManager('record');
        if(inEditor(selectedNode)){
            element=inElement(selectedNode,'CODE')
           
            if(!element){
                if(!testBlackList(selectedNode)){
                    selectedNode.outerHTML='<code>'+selectedNode.innerHTML+'</code>';
                    selObj.extend(selectedNode, 0);
                }
            }else{
                element.outerHTML='<div>'+element.innerHTML+'</div>';
                selObj.extend(element, 0);
            }
        }
    };

    makeP = function (e) {
        smartFormatBlock('p');
    };

    makeBold = function (e) {
        execCmd('bold');
    };

    makeItalic = function (e) {
        execCmd('italic');
    };

    clearStyles = function (e) {
        var element
        
        historyManager('record');
        if(inEditor(selectedNode)){
            element=selectedNode.parentElement;
            if(selObj.type=='Caret'){
                for (var i=0;i<styleTags.length;i++){
                    element.innerHTML=removeTag(element.innerHTML,styleTags[i],true);
                }
                element.removeAttribute('style');
            }else{
                execCmd('removeFormat');
            }
        }
    };
    
    blowupHtml =function(e){
        wildClear();
    };
    
    makeTable = function (e) {
        if (inEditor(selectedNode)) {
            e.preventDefault();
            pasteHtmlAtCaret('<table><tr><td>td1</td><td>td1</td></tr><tr><td>' +
                'td1</td><td>td1</td></tr></table>')
        }
    };

    insertHR = function (e) {
        execCmd('insertHorizontalRule');
    };

    insertA = function (e) {
        var link
        
        if (inEditor(selectedNode) || (inEditor(selectedOrg) && selectedOrg.nodeType !==1)) {
            link=prompt("Link:", "#");
            execCmd('createLink', false, link);
        }
        historyManager('record');
    };

    insertImg = function (e) {
        var src
        
        if (inEditor(selectedNode) || (inEditor(selectedOrg) && selectedOrg.nodeType !==1)) {
            if(typeof insertImgHook=='function'){
                savedRange=saveSelection();
                insertImgHook();
            }else{
                src = prompt("Img:", "http://");
                if(src!='' && src!="http://"){
                    execCmd('insertImage', false, src);
                    watcher();
                }
            }
        }
        historyManager('record');
    };

    justifyLeft = function (e) {
        execCmd('justifyLeft');
    };

    justifyRight = function (e) {
        execCmd('justifyRight');
    };

    justifyCenter = function (e) {
        execCmd('justifyCenter');
    };

    justifyFull = function (e) {
        execCmd('justifyFull');
    };

    makeStrike = function (e) {
        execCmd('strikeThrough');
    };

    makeUnderline = function (e) {
        execCmd('underline');
    };

    makeSup = function (e) {
        execCmd('superscript');
    };

    makeSub = function (e) {
        execCmd('subscript');
    };


    reDo = function (e) {
        historyManager('redo');
//        execCmd('redo');
    };

    unDo = function (e) {
        historyManager('undo');
//        execCmd('undo');
    };
    
    toggleHtml = function (e){
        if(inEditor(selectedNode,true) || textareaTouched){
            if($textarea){
                if($textarea.style.display=='none'){
                    historyManager('record');
                }
                stickyArea();
                if($textarea.style.display != 'none'){
                    $textarea.style.display = 'none';
                    toggleBodyScroll(false);
                    setHTMLCloseHook();
                }else{
                    $textarea.style.display = '';
                    toggleBodyScroll(true);
                    setHTMLOpenHook();
                }
                textareaTouched=false;
                switchImageComponent(false);
                switchLinkComponent(false);
            }
        }
    }
    function toggleBodyScroll(show){
        if($options.htmlfullscreen){
            if(show){
                document.body.style.overflow = 'hidden';
            }else{
                document.body.style.overflow = '';
            }
        }
    }
    
    textareaFocus =function(){
        textareaTouched=true;
        focusHook();
    };

//------------------- Functions -----------------
    
    function getCurrentSelection () {
        var node;

        selObj = window.getSelection();
        if (selObj.type != 'None' && selObj.rangeCount>0) {
            selRange = selObj.getRangeAt(0);
            startRange = selRange.startContainer;
            endRange = selRange.endContainer;
            node = selObj.anchorNode;
            selectedOrg = node;
            while (node.nodeType !== 1) {
                node = node.parentNode;
            }
            
            selectedNode = node;
        }
    };
    
    function inEditor (element, allowself) {
        return childOf(element, $editor, allowself);
    }
    
    function childOf (element, parent_element,allowself) {
        while (element != null) {
            if(allowself){
                if (element == parent_element) {
                    return true;
                }
            }else{
                if (element.parentNode == parent_element) {
                    return true;
                }
            }            
            element = element.parentNode;
        }
        return false;
    }
    
    function watcher(){
        var imgs, links
        
        imgs=$editor.querySelectorAll('img');
        for (var i=0;i<imgs.length;i++){
            imgs[i].addEventListener('click', targetImg);
        }
        
        links=$editor.querySelectorAll('a');
        for (var j=0;j<links.length;j++){
            links[j].addEventListener('click', function(e){
                e.preventDefault();
                return false;
            });
        }
        switchIndentOutdentBtns();
    }
    function switchIndentOutdentBtns(){
        var disabledClass=' disabled';
        
        getCurrentSelection();
        
        if(inElement(selectedNode,'LI') || inElement(selectedNode,'OL')){
            if($btn_indent){
                $btn_indent.className=$btn_indent.className.replace(disabledClass,'');
            }
            if($btn_outdent){
                $btn_outdent.className =$btn_outdent.className.replace(disabledClass,'');
            }
        }else{
            if($btn_indent){
                if($btn_indent.className.indexOf(disabledClass) <0){
                    $btn_indent.className +=disabledClass;
                }
            }
            if($btn_outdent){
                if($btn_outdent.className.indexOf(disabledClass) <0){
                    $btn_outdent.className +=disabledClass;
                }
            }
        }
    }
    
    function saveSelection() {
        var sel
        
        if (window.getSelection) {
            sel = window.getSelection();
            if (sel.getRangeAt && sel.rangeCount) {
                return sel.getRangeAt(0);
            }
        } else if (document.selection && document.selection.createRange) {
            return document.selection.createRange();
        }
        return null;
    }
    
    function restoreSelection(range) {
        var sel
        
        if (range) {
            if (window.getSelection) {
                sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
            } else if (document.selection && range.select) {
                range.select();
            }
        }
    }

    function isElement(o) {
        return (
                typeof HTMLElement === "object" ? o instanceof HTMLElement : //DOM2
            o && typeof o === "object" && o !== null && o.nodeType === 1 && typeof o.nodeName === "string"
            );
    };
    
    function inElement(element,tag) {
        tag=tag.toUpperCase();
        if(element){
            if (element.tagName && element.tagName == tag) {
                return element;
            } else {
                if (element.parentElement || element==$editor) {
                    return inElement(element.parentElement,tag);
                } else {
                    return false;
                }
            }
        }
    };
    function pasteHtmlAtCaret(html, selectPastedContent) {
        var sel, range;
        if (window.getSelection) {
            // IE9 and non-IE
            sel = window.getSelection();
            if (sel.getRangeAt && sel.rangeCount>0) {
                range = sel.getRangeAt(0);
                range.deleteContents();
    
                // Range.createContextualFragment() would be useful here but is
                // only relatively recently standardized and is not supported in
                // some browsers (IE9, for one)
                var el = document.createElement("div");
                el.innerHTML = html;
                var frag = document.createDocumentFragment(), node, lastNode;
                while ( (node = el.firstChild) ) {
                    lastNode = frag.appendChild(node);
                }
                var firstNode = frag.firstChild;
                range.insertNode(frag);
    
                // Preserve the selection
                if (lastNode) {
                    range = range.cloneRange();
                    range.setStartAfter(lastNode);
                    if (selectPastedContent) {
                        range.setStartBefore(firstNode);
                    } else {
                        range.collapse(true);
                    }
                    sel.removeAllRanges();
                    sel.addRange(range);
                }
            }
        } else if ( (sel = document.selection) && sel.type != "Control") {
            // IE < 9
            var originalRange = sel.createRange();
            originalRange.collapse(true);
            sel.createRange().pasteHTML(html);
            if (selectPastedContent) {
                range = sel.createRange();
                range.setEndPoint("StartToStart", originalRange);
                range.select();
            }
        }
    }


     function removeTag (str, tag, force) {
        var regex1, regex2;
        tag = tag.toLowerCase();
        regex1 = new RegExp('<' + tag + '>([^(<' + tag + '>)]*?)</' + tag + '>', 'g');
        while (regex1.test(str)) {
            str = str.replace(regex1, '$1')
        }
        if (force) {
            regex2 = new RegExp('<' + tag + '>|</' + tag + '>', 'g');
            while (regex2.test(str)) {
                str = str.replace(regex2, '')
            }
        }

        return str;
    };
    
    function placeCaretAfterNode(node) {
        if (typeof window.getSelection != "undefined" && node.parentNode) {
            var range = document.createRange();
            range.setStartAfter(node);
            range.collapse(true);
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        }
    };
    
    function wildClear(){
        var str, start, end, current, resultObj, trigger=null;
        
        historyManager('record');
        if (inEditor(selectedNode)) {
            start=startRange.parentElement;
            end=endRange.parentElement;
            
            if( start != end){
                resultObj=getSameParent(start,end);
                var room=resultObj.point.childNodes;
                for (var i=0; i<room.length; i++){
                    if(room[i].nodeType==1){
                        var tmp_trigger=false;
                        if(room[i]==resultObj.start || room[i]==resultObj.end){
                           if(trigger){
                               tmp_trigger=false;
                           }else{
                               trigger=true;
                               tmp_trigger=trigger;
                           }
                        }
                        if(trigger){
                            room[i].outerHTML='<div>'+room[i].innerText+'</dvi>';
                        }
                        trigger=tmp_trigger;
                    }
                }
            }else{
                current=testBlackList(selectedNode);
                if(current){
                    current=current.outerHTML='<div>'+current.innerText+'</div>';
                }else{
                    selectedNode.outerHTML='<div>'+selectedNode.innerText+'</div>';
                }
            }
        }else if(inEditor(selectedNode,true)){
            $editor.innerHTML=$editor.innerText;
        }
    };
    
    function getSameParent(start, end){
        var new_start, new_end
        new_start=start;
        while (new_start!= null){
            new_end=findSibling(new_start.parentNode,end);
            if(new_end){
                return {"point":new_start.parentNode,"start":new_start, "end":new_end};
            }else{
                new_start=new_start.parentNode;
            }
        }
    };
    
    function findSibling(parent, child){
        var node = child;
        while (node != null) {
            if (node.parentNode == parent) {
                 return node;
            }
            node = node.parentNode;
        }
        return false;
    };
    
    function isDescendant(parent, child){
        var node = child.parentNode;
        while (node != null) {
            if (node == parent) {
                 return true;
            }
            node = node.parentNode;
        }
        return false;
    };
    
    function testBlackList(element){
        if(!element || element==$editor){
            return false
        }
        if(BFBL.indexOf(element.tagName)>=0){
            return element;
        }else{
            return testBlackList(element.parentElement);
        }
    };
    
    function smartFormatBlock(tag){
        var element
        
        historyManager('record');
        
        if(inEditor(selectedOrg) && selectedOrg.nodeType !==1){
            execFormatBlock(tag,true);
        }
        if(inEditor(selectedNode)){
            if (selectedNode.tagName != tag.toUpperCase()) {
                element=testBlackList(selectedNode);
                if (element) {
                    if (element.innerText != '') {
                        element.innerHTML = '<'+tag+'>' + element.innerText + '</'+tag+'>';
                        placeCaretAfterNode(element.childNodes[0]);
                    }
                } else {
                    execFormatBlock(tag);
                }
            } else {
                if (selectedNode.parentNode.tagName == 'DIV') {
                    execFormatBlock('div');
                } else {
                    selectedNode.outerHTML = selectedNode.innerHTML;
                    placeCaretAfterNode(selectedNode);
                }
            }
            getCurrentSelection();
        }
    };
    
    function execFormatBlock (tag, force) {
        if(inEditor(selectedNode) || force){
            tag = tag.toLowerCase();
            if(startRange.parentElement===endRange.parentElement){
                document.execCommand('formatBlock', false, tag);
            }
        }
    };
    
    function execCmd (cmd,show_ui,str) {
        historyManager('record');
        
        if (inEditor(selectedNode) || (inEditor(selectedOrg) && selectedOrg.nodeType !==1)){
            if(typeof show_ui!=='boolean'){
                show_ui=false;
            }
            if(typeof str!='string'){
                str='';
            }
            document.execCommand(cmd, show_ui, str);
        }
    };

    function destroySpan (element, br) {
        var children = element.childNodes;
        for (var i = 0; i < children.length; i++) {
            if (children[i].tagName == "SPAN" && children[i].getAttribute('style')) {
                children[i].outerHTML = children[i].innerHTML;
            } else if (children[i].tagName == "BR" && br) {
                children[i].outerHTML = '';
            } else {
                if (children[i].childNodes) {
                    destroySpan(children[i], br);
                }
            }
        }
    };

    function setKeyboard (editor) {

        var key = [];
        key['shift'] = false;
        key['enter'] = false;

        editor.addEventListener('keydown', function(e) {
            if (e.keyCode == 16) {
                key['shift'] = true;
            }
            if (e.keyCode == 8 || e.keyCode == 46 || e.keyCode == 17 || e.keyCode == 91 || e.keyCode == 88 ) {
                historyManager('record');
            }
            if (e.keyCode == 13) {
                key['enter'] = true;
                historyManager('record');
            }
            
            if (key['shift'] && key['enter']) {
                e.preventDefault();
                pasteHtmlAtCaret('<br>');
            } else if (!key['shift'] && key['enter']) {
               //still don't know what can do...
            }
        });
        window.addEventListener('keyup', function(e) {
            if (e.keyCode == 16) {
                key['shift'] = false;
            }
            if (e.keyCode == 13) {
                key['enter'] = false;
            }
        });
    };

    function getSelectionHtml (strip) {
        var html = "";
        if (typeof window.getSelection != "undefined") {
            var sel = window.getSelection();
            if (!strip) {
                if (sel.rangeCount) {
                    var container = document.createElement("div");
                    for (var i = 0, len = sel.rangeCount; i < len; ++i) {
                        container.appendChild(sel.getRangeAt(i).cloneContents());
                    }
                    html = container.innerHTML;
                }
            } else {
                html = sel.toString();
            }
        } else if (typeof document.selection != "undefined") {
            if (document.selection.type == "Text") {
                html = document.selection.createRange().htmlText;
            }
        }
        return html;
    };
    
    function stickyArea(){
        if(!$options.free){
            $textarea.style.position = 'absolute';
            $textarea.style.left=$editor.offsetLeft+'px';
            $textarea.style.top=$editor.offsetTop+'px';
            $textarea.style.width=$editor.offsetWidth+'px';
            $textarea.style.height=$editor.offsetHeight+'px';
        }
    }
    
    function switchImageComponent(src,pos,img,on){
        if(!$componentImage){
            return;
        }
        if(on){
            $componentLocker=true;
            $componentImage.style.position = "absolute";
            $componentImage.style.left=pos.y+20+9999+'px';
            $componentImage.style.top=pos.x+50+'px';
            $componentImage.style.display="block";
            $componentImage.dataset.url=src;
            $currentImage.element=img;

            srcInput.value=$componentImage.dataset.url;
            altInput.value=$currentImage.element.getAttribute('alt');
            
            if(img.parentElement.tagName=="A" && img.parentElement.children.length==1){
                $currentImage.link=img.parentElement;
            }
            
            if($currentImage.link){
                linkInput.value=$currentImage.link.getAttribute('href');
                blankInput.checked=($currentImage.link.getAttribute('target')=='_blank')?true:false;
            }
        }else{
            $componentLocker=false;
            $componentImage.style.display="none";
            $componentImage.dataset.url='';
            $currentImage.element=null;
            $currentImage.link=null;
            srcInput.value='';
            altInput.value='';
            linkInput.value='';
            blankInput.checked=false;
        }
    };
    function switchImageComponentDisplay(toggle){
        if(!toggle){
            $componentImage.style.display="none";
        }else{
            $componentImage.style.display="block";
        }
    }
    
    
    function switchLinkComponent(url,pos,a,on){
        if(!$componentLink){
            return;
        }
        if(on){
            $componentLink.style.position = "absolute";
            $componentLink.style.left=pos.y-50+9999+'px';
            $componentLink.style.top=pos.x+20+'px';
            $componentLink.style.display="block";
            $componentLink.dataset.url=url;
            $currentLink.element=a;
            $currentLink.preview.setAttribute('href',url);
        }else{
            $componentLink.style.display="none";
            $componentLink.dataset.url='';
            $currentLink.element=null;
            $currentLink.preview.setAttribute('href','#');
        }
    };
    
    function cumulativeOffset(element) {
        var y = 0, x = 0;
        do {
            x += element.offsetTop  || 0;
            y += element.offsetLeft || 0;
            element = element.offsetParent;
        } while(element);
    
        return {
            "x": x,
            "y": y,
        };
    };
    
//-------------------------- Utils ------------------------
    
    function log(args) {
        console.log("---------------------------");
        console.log("SAW Editor Log: ("+$property.name+")");
        for (var i in arguments) {
            if (arguments.hasOwnProperty(i)) {
                console.log(arguments[i]);
                console.log("..........");
            }
        }
        console.log("---------------------------");
    };
    
    function isJsonString(str) {
        try {
            JSON.parse(str);
        } catch (e) {
            return false;
        }
        return true;
    }
    
    function mergeJSON(source1,source2){
        /*
         * Properties from the Souce1 object will be copied to Source2 Object.
         * Note: This method will return a new merged object, Source1 and Source2 original values will not be replaced.
         * */
        var mergedJSON = Object.create(source2);// Copying Source2 to a new Object
    
        for (var attrname in source1) {
            if(mergedJSON.hasOwnProperty(attrname)) {
              if ( source1[attrname]!=null && source1[attrname].constructor==Object ) {
                  /*
                   * Recursive call if the property is an object,
                   * Iterate the object and set all properties of the inner object.
                  */
                  mergedJSON[attrname] = zrd3.utils.mergeJSON(source1[attrname], mergedJSON[attrname]);
              } 
    
            } else {//else copy the property from source1
                mergedJSON[attrname] = source1[attrname];
    
            }
          }
    
          return mergedJSON;
    }
    
    function createToolbarBtns(toolbar){
        var tbs, tmp_tbs
        
        tbs=defaultToolbarBtns;
        tmp_tbs =toolbar.getAttribute('toolbar-btns');
        
        if(tmp_tbs){
            tbs=tmp_tbs.replace(/'/g,'"');
        }
        
        if(isJsonString(tbs)){
            tbs=JSON.parse(tbs);
        }
        
        for(var i=0;i<tbs.length;i++){
            var group=document.createElement("div");

            for (var j=0;j<tbs[i].length;j++){
                var val=tbs[i][j];

                if(toolbar.querySelector('.btn-'+val)){
                    continue;
                }
                
                var btn=document.createElement("button");
                btn.className= "btn btn-"+val;

                var ico;
                for (var k in btnList){
                    if(btnList[k].name==val){
                        ico=btnList[k].ico;
                        break;
                    }
                }
                
                if(ico){
                    btn.innerHTML='<i class="fa fa-'+ico+'"></i>';
                }else{
                    btn.innerHTML=val.toUpperCase();
                }
                group.appendChild(btn);
            }
            if(group.childNodes.length>1){
                group.className="btn-group";
                toolbar.appendChild(group);
            }else{
                group=null;
            }
        }
        return toolbar;
    }
    
    var evtManager={
        register: function (target,handler,event){
            if(typeof event!='string'){
                event='click';
            }
            if(typeof target=='object'){
                if(typeof handler=='function'){
                    target.addEventListener(event,handler);
                    target.addEventListener(event,function(){return false});
                }
            }
        },
        remove: function (target,handler,event){
            if(typeof event!='string'){
                event='click';
            }
            if(typeof target=='object'){
                if(typeof handler=='function'){
                    target.removeEventListener(event,handler);
                }
            }
        }
    }

//------------------ Callbacks -------------------

    function insertImgCallback(src,alt,link){
        var html
        
        if(savedRange){
            src=(typeof src=='string')?src:'';
            alt=(typeof alt=='string')?alt:'';
            link=(typeof alt=='string')?link:'';

            restoreSelection(savedRange);
            
            if(link){
                html='<a href="'+link+'"><img src="'+src+'" alt="'+alt+'"></a>';
            }else{
                html='<img src="'+src+'" alt="'+alt+'" />';
            }
            
            pasteHtmlAtCaret(html);
            watcher();
        }
    }

    function replaceImgCallback(src,alt){
            var img
            
            img=$currentImage.element;
            
            if(img){
                if(typeof src=='string'){
                    img.setAttribute('src', src);
                    srcInput.value=src;
                    $componentImage.dataset.url=src;
                }
                if(typeof alt=='string'){
                    img.setAttribute('alt', alt);
                    altInput.value=alt;
                }
                switchImageComponent(false);
            }
        }
    
    function insertCallback(obj){
        if(savedRange && typeof obj=='string'){
            restoreSelection(savedRange);
            pasteHtmlAtCaret(obj);
            watcher();
        }
    }
    
//------------------ Construction ----------------

    function init_editor(editor,toolbar,textarea,components,opt) {
        
        //Setup base options and attributes
        set_options(opt);
        
        if(typeof editor=='object'){
            $editor=editor;
        }else if(typeof editor=='string' && editor!=''){
            $editor=document.querySelector('div[name='+editor+']');
        }else{
             return 'Init editor failed !!';
        }
        if(typeof toolbar=='object'){
            $toolbar=toolbar;
        }else if(typeof toolbar=='string' && toolbar!=''){
            $toolbar=document.querySelector('div[name='+toolbar+']');
        }else{
            return 'Init toolbar failed !!';
        }
        
        if(typeof textarea=='object'){
            $textarea=textarea;
        }else if(typeof textarea=='string' && textarea!=''){
            $textarea=document.querySelector('textarea[name='+textarea+']');
        }else{
            return 'Init toolbar failed !!';
        }
        
        if(!$editor || !$toolbar || !$textarea){
            return 'Can not find editor !!';
        }
        
        if($options.firstview!='html'){
            $textarea.style.display = 'none';
        }
        if(typeof $options.history!='number' || $options.history<=0 || $options.history>1000){
            $options.history=100;
        }
        
        //make sure its editable
        $editor.setAttribute('contenteditable','true');
        
        //Setup options and property
        if(!$options.nontoolbar){
            $toolbar=createToolbarBtns($toolbar);
        }
        
        if($editor.getAttribute('sup-angular-wysiwyg')){
            $property.name=$editor.getAttribute('sup-angular-wysiwyg');
        }else if($editor.getAttribute('name')){
            $property.name=$editor.getAttribute('name');
        }
        
        if($editor.getAttribute('order')){
            var order=parseInt($editor.getAttribute('order'));
            $property.order=order?order:0;
        }
        
        //Setup components
        if(typeof components=='object'){
            $componentGroup=components;
        }else if(typeof components=='string' && components!=''){
            $componentGroup=document.querySelector('div[name='+components+']');
        }
        
        if($componentGroup){
            set_component_group($componentGroup);
            set_link_component();
            set_image_component();
        }
        
        //Add event listener
        $editor.addEventListener('mouseup', selectHandler);
        $editor.addEventListener('click', focusHandler);
        $editor.addEventListener('click', targetA);
        $textarea.addEventListener('focus', textareaFocus);
        window.addEventListener('keyup', selectHandler);
        window.addEventListener('mouseup', selectHandler);
        window.addEventListener('click', blurHandler);
        
        for (var i=0; i<btnList.length;i++){
            var obj=$toolbar.querySelector('.btn-'+btnList[i].name);
            if(obj){
                if(btnList[i].name=='indent'){
                    $btn_indent=obj;
                }
                if(btnList[i].name=='outdent'){
                    $btn_outdent=obj;
                }
                evtManager.register( obj, eval(btnList[i].handler));
            }
        }
        if($componentGroup){
            for (var i=0; i<compbtnList.length;i++){
                var obj=$componentGroup.querySelector('.btn-'+compbtnList[i].name);
                if(obj){
                    evtManager.register( obj, eval(compbtnList[i].handler));
                }
            }
        }
        
        
        stickyArea();
        setKeyboard($editor);
    };
    
    function set_component_group(){
        if(document.body && $componentGroup.parentElement){
            $componentGroup.parentElement.removeChild($componentGroup);
            document.body.appendChild($componentGroup);
            $componentGroup.style.position='absolute';
            $componentGroup.style.zIndex='9999';
            $componentGroup.style.top='0px';
            $componentGroup.style.left='-9999px';
            return $componentGroup;
        }else{
            return false;
        }
    }
    
    function set_image_component(){
        $componentImage=$componentGroup.querySelector('.popover[component_image]');
        if(!$componentImage){
            var compimg=document.createElement("div");
            $componentGroup.appendChild(compimg);
            compimg.outerHTML=$componentImageTpl;
            $componentImage=$componentGroup.querySelector('.popover[component_image]');
        }
        if($componentImage){
            srcInput=$componentImage.querySelector('input[name=src]');
            altInput=$componentImage.querySelector('input[name=alt]');
            linkInput=$componentImage.querySelector('input[name=link]');
            blankInput=$componentImage.querySelector('input[name=link-target]');
            $componentImage.style.display="none";
        }
    };
    
    function set_link_component(){
        $componentLink=$componentGroup.querySelector('.popover[component_link]');
        if(!$componentLink){
            var complink=document.createElement("div");
            $componentGroup.appendChild(complink);
            complink.outerHTML=$componentLinkTpl;
            $componentLink=$componentGroup.querySelector('.popover[component_link]');
        }
        if($componentLink){
            $currentLink.preview=$componentLink.querySelector('a.preview-link');
            $componentLink.style.display="none";
        }
    };
    
    function set_options(opt){
        if(opt){
            opt=opt.replace(/'/g,'"');
            if(isJsonString(opt)){
                $options=mergeJSON(JSON.parse(opt),$options);
            }
        }
    };
    
    function set_insert_img_hook(func){
        if (typeof func=='function'){
            return insertImgHook=func;
        }else{
            return false;
        }
    };
    
    function set_replace_img_hook(func){
        if (typeof func=='function'){
            return replaceImgHook=func;
        }else{
            return false;
        }
    };
    
    function set_focus_hook(func){
        if (typeof func=='function'){
            return focusHook=func;
        }else{
            return false;
        }
    };
    
    function set_blur_hook(func){
        if (typeof func=='function'){
            return blurHook=func;
        }else{
            return false;
        }
    };
    
    function set_html_on_open_hook(func){
        if (typeof func=='function'){
            return setHTMLOpenHook=func;
        }else{
            return false;
        }
    };
    
    function set_html_on_close_hook(func){
        if (typeof func=='function'){
            return setHTMLCloseHook=func;
        }else{
            return false;
        }
    };
    

    function get_property(){
        return $property;
    };
    
    function get_name(){
        return $property.name;
    };
    
    function get_order(){
        return $property.order;
    };
    
    function get_org_html(){
        return $editor.innerHTML;
    };

    return {
        'init': init_editor,
        'property': get_property,
        'name': get_name,
        'order':get_order,
        'options': set_options,
        'hooks': {
            'insert_image':set_insert_img_hook,
            'replace_image':set_replace_img_hook,
            'focus':set_focus_hook,
            'blur':set_blur_hook,
            'html_on_open':set_html_on_open_hook,
            'html_on_close':set_html_on_close_hook,
        },
        'insert_image':insertImgCallback,
        'replace_image':replaceImgCallback,
        'insert':insertCallback,
        'org_html':get_org_html,
    };
});


(function (angular) {
    var supAngularWysiwyg = angular.module('supAngularWysiwyg',[]);
    
    supAngularWysiwyg.directive('supAngularWysiwyg', ['$rootScope',
        function ($rootScope) {
            return {
                restrict: 'EA',
                require: '?ngModel',
                scope: {
                  'toolbar': '@',
                  'components':'@',
                  'textarea': '@',
                  'options': '@',
                },
                link: function (scope, element, attrs, ngModel) {
                    var editor=new supWysiwygEditor();
                    var editor_name='sup-editor';
                    
                    if (attrs.name){
                        editor_name=attrs.name;
                    }else{
                        editor_name=attrs.supAngularWysiwyg;
                    }

                    if(!scope.toolbar){
                        scope.toolbar=editor_name+'-toolbar';
                    }
                   
                    if(!scope.textarea){
                        scope.textarea=editor_name+'-textarea';
                    }
                    if(!scope.components){
                        scope.components=editor_name+'-components';
                    }
                    
                    editor.init(element[0],scope.toolbar,scope.textarea,scope.components,scope.options);
    
                    editor.hooks.insert_image(function(){
                        $rootScope.$emit('editor.insert_image',editor);
                    });
                    editor.hooks.replace_image(function(){
                        $rootScope.$emit('editor.replace_image',editor);
                    });
                    editor.hooks.focus(function(){
                        $rootScope.$emit('editor.focus',editor);
                    });
                    editor.hooks.blur(function(){
                        $rootScope.$emit('editor.blur',editor);
                    });
                    editor.hooks.html_on_open(function(){
                        $rootScope.$emit('editor.html.open');
                    });
                    editor.hooks.html_on_close(function(){
                        $rootScope.$emit('editor.html.close');
                    });
                    
                    
                    var clean_insert_image_ready = $rootScope.$on('editor.insert_image_ready', function(e,origin,imgObj){
                        if(origin===editor){
                            doInsertImage(editor, imgObj);
                        }
                    });
                    
                    var clean_replace_image_ready = $rootScope.$on('editor.replace_image_ready', function(e,origin,imgObj){
                        if(origin===editor){
                            doReplaceImage(editor, imgObj);
                        }
                    });
                    
                    var clean_insert_ready_ready = $rootScope.$on('editor.insert_ready', function(e,origin,textObj){
                        if(origin===editor){
                            doInsert(editor,textObj);
                        }
                    });
                    
                    scope.$on('$destroy', function() {
                        clean_insert_image_ready();
                        clean_replace_image_ready();
                        clean_insert_ready_ready();
                    });
                    
                    //Dispatch event editor complete
                    $rootScope.$emit('editor.complete',editor,editor.org_html());
                    
                    /*bind ng-model*/
                    if (!ngModel) return; // do nothing if no ng-model
                    
                    // Specify how UI should be updated
                    ngModel.$render = function () {
                    	element.html(ngModel.$viewValue || '');
                    };
                    // Listen for change events to enable binding
                    element.on('blur keyup change', function () {
                    	scope.$apply(readViewText);
                    });
                    window.addEventListener('click', function(){
                    	scope.$apply(readViewText);
                    });
                    window.addEventListener('mousedown', function(){
                    	scope.$apply(readViewText);
                    });
                    
                    // No need to initialize, AngularJS will initialize the text based on ng-model attribute
                    
                    // Write data to the model
                    function readViewText() {
                        var html = element.html();
                        // When we clear the content editable the browser leaves a <br> behind
                        // If strip-br attribute is provided then we strip this out
                        if (attrs.stripBr && html == '<br>') {
                          html = '';
                        }
                        ngModel.$setViewValue(html);
                    }
                }
            };
        }]);
        
    supAngularWysiwyg.service('SawEditor', [
        function () {
            this.insert= function (editor,obj) {
                doInsert(editor, obj);
            };
            this.insert_image= function (editor,imgObj) {
                doInsertImage(editor, imgObj);
            };
            this.replace_image= function (editor,imgObj) {
                doReplaceImage(editor, imgObj);
            };
        }]);
        
    function doInsertImage(editor, imgObj){
        var src, alt;
        src=(typeof imgObj.src==='string')?imgObj.src:'';
        alt=(typeof imgObj.alt==='string')?imgObj.alt:'';
        link=(typeof imgObj.link==='string')?imgObj.link:'';
        
        if(src){
            editor.insert_image(src,alt,link);
        }else{
            console.log('Insert object is not supported by insert_image().');
        }
    };
    
    function doReplaceImage(editor, imgObj){
        var src, alt;
        src=(typeof imgObj.src==='string')?imgObj.src:'';
        alt=(typeof imgObj.alt==='string')?imgObj.alt:'';
        if(src){
            editor.replace_image(src,alt);
        }else{
            console.log('Replace object is not supported by replace_image().');
        }
    };
    
    function doInsert(editor, textObj){
        var text
        if(typeof text==='string'){
            editor.insert(textObj);
        }else{
            console.log('Insert object is not supported by insert().');
        }
    };
})(angular);