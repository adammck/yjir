/*
Script: dbug.js
	A wrapper for Firebug console.* statements.

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/
var dbug = {
	logged: [],	
	timers: {},
	firebug: false, 
	enabled: false, 
	log: function() {
		dbug.logged.push(arguments);
	},
	nolog: function(msg) {
		dbug.logged.push(arguments);
	},
	time: function(name){
		dbug.timers[name] = new Date().getTime();
	},
	timeEnd: function(name){
		if (dbug.timers[name]) {
			var end = new Date().getTime() - dbug.timers[name];
			dbug.timers[name] = false;
			dbug.log('%s: %s', name, end);
		} else dbug.log('no such timer: %s', name);
	},
	enable: function(silent) { 
		if(dbug.firebug) {
			try {
				dbug.enabled = true;
				dbug.log = function(){
						(console.debug || console.log).apply(console, arguments);
				};
				dbug.time = function(){
					console.time.apply(console, arguments);
				};
				dbug.timeEnd = function(){
					console.timeEnd.apply(console, arguments);
				};
				if(!silent) dbug.log('enabling dbug');
				for(var i=0;i<dbug.logged.length;i++){ dbug.log.apply(console, dbug.logged[i]); }
				dbug.logged=[];
			} catch(e) {
				dbug.enable.delay(400);
			}
		}
	},
	disable: function(){ 
		if(dbug.firebug) dbug.enabled = false;
		dbug.log = dbug.nolog;
		dbug.time = function(){};
		dbug.timeEnd = function(){};
	},
	cookie: function(set){
		var value = document.cookie.match('(?:^|;)\\s*jsdebug=([^;]*)');
		var debugCookie = value ? unescape(value[1]) : false;
		if((!$defined(set) && debugCookie != 'true') || ($defined(set) && set)) {
			dbug.enable();
			dbug.log('setting debugging cookie');
			var date = new Date();
			date.setTime(date.getTime()+(24*60*60*1000));
			document.cookie = 'jsdebug=true;expires='+date.toGMTString()+';path=/;';
		} else dbug.disableCookie();
	},
	disableCookie: function(){
		dbug.log('disabling debugging cookie');
		document.cookie = 'jsdebug=false;path=/;';
	}
};

(function(){
	var fb = typeof console != "undefined";
	var debugMethods = ['debug','info','warn','error','assert','dir','dirxml'];
	var otherMethods = ['trace','group','groupEnd','profile','profileEnd','count'];
	function set(methodList, defaultFunction) {
		for(var i = 0; i < methodList.length; i++){
			dbug[methodList[i]] = (fb && console[methodList[i]])?console[methodList[i]]:defaultFunction;
		}
	};
	set(debugMethods, dbug.log);
	set(otherMethods, function(){});
})();
if (typeof console != "undefined" && console.warn){
	dbug.firebug = true;
	var value = document.cookie.match('(?:^|;)\\s*jsdebug=([^;]*)');
	var debugCookie = value ? unescape(value[1]) : false;
	if(window.location.href.indexOf("jsdebug=true")>0 || debugCookie=='true') dbug.enable();
	if(debugCookie=='true')dbug.log('debugging cookie enabled');
	if(window.location.href.indexOf("jsdebugCookie=true")>0){
		dbug.cookie();
		if(!dbug.enabled)dbug.enable();
	}
	if(window.location.href.indexOf("jsdebugCookie=false")>0)dbug.disableCookie();
}


/*
Script: IframeShim.js
	Defines IframeShim, a class for obscuring select lists and flash objects in IE.

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/	
var IframeShim = new Class({
	Implements: [Options, Events],
	options: {
		name: '',
		className:'iframeShim',
		display:false,
		zindex: null,
		margin: 0,
		offset: {
			x: 0,
			y: 0
		},
		browsers: (Browser.Engine.trident4 || (Browser.Engine.gecko && !Browser.Engine.gecko19 && Browser.Platform.mac))
	},
	initialize: function (element, options){
		this.setOptions(options);
		//legacy
		if(this.options.offset && this.options.offset.top) this.options.offset.y = this.options.offset.top;
		if(this.options.offset && this.options.offset.left) this.options.offset.x = this.options.offset.left;
		this.element = $(element);
		this.makeShim();
		return;
	},
	makeShim: function(){
		this.shim = new Element('iframe');
		this.id = this.options.name || new Date().getTime() + "_shim";
		if(this.element.getStyle('z-Index').toInt()<1 || isNaN(this.element.getStyle('z-Index').toInt()))
			this.element.setStyle('z-Index',5);
		var z = this.element.getStyle('z-Index')-1;
		
		if($chk(this.options.zindex) && 
			 this.element.getStyle('z-Index').toInt() > this.options.zindex)
			 z = this.options.zindex;
			
 		this.shim.setStyles({
			'position': 'absolute',
			'zIndex': z,
			'border': 'none',
			'filter': 'progid:DXImageTransform.Microsoft.Alpha(style=0,opacity=0)'
		}).setProperties({
			'src':'javascript:void(0);',
			'frameborder':'0',
			'scrolling':'no',
			'id':this.id
		}).addClass(this.options.className);
		
		this.element.store('shim', this);

		var inject = function(){
			this.shim.inject(this.element, 'after');
			if(this.options.display) this.show();
			else this.hide();
			this.fireEvent('onInject');
		};
		if(this.options.browsers){
			if(Browser.Engine.trident && !IframeShim.ready) {
				window.addEvent('load', inject.bind(this));
			} else {
				inject.run(null, this);
			}
		}
	},
	position: function(shim){
		if(!this.options.browsers || !IframeShim.ready) return this;
		var before = this.element.getStyles('display', 'visibility', 'position');
		this.element.setStyles({
			display: 'block',
			position: 'absolute',
			visibility: 'hidden'
		});
		var size = this.element.getSize();
		this.element.setStyles(before);
		if($type(this.options.margin)){
			size.x = size.x-(this.options.margin*2);
			size.y = size.y-(this.options.margin*2);
			this.options.offset.x += this.options.margin; 
			this.options.offset.y += this.options.margin;
		}
 		this.shim.setStyles({
			'width': size.x,
			'height': size.y
		}).setPosition({
			relativeTo: this.element,
			offset: this.options.offset
		});
		return this;
	},
	hide: function(){
		if(this.options.browsers) this.shim.setStyle('display','none');
		return this;
	},
	show: function(){
		if(!this.options.browsers) return this;
		this.shim.setStyle('display','block');
		return this.position();
	},
	dispose: function(){
		if(this.options.browsers) this.shim.dispose();
		return this;
	}
});
window.addEvent('load', function(){
	IframeShim.ready = true;
});


/*
Script: Hash.Extras.js
	Extends the Hash native object to include getFromPath which allows a path notation to child elements.

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/

Hash.implement({
	getFromPath: function(notation) {
		var source = this.getClean();
		notation.replace(/\[([^\]]+)\]|\.([^.[]+)|[^[.]+/g, function(match) {
			if (!source) return;
			var prop = arguments[2] || arguments[1] || arguments[0];
			source = (prop in source) ? source[prop] : null;
			return match;
		});
		return source;
	},
	cleanValues: function(method){
		method = method||$defined;
		this.each(function(v, k){
			if (!method(v)) this.erase(k);
		}, this);
		return this;
	}
});

/*
Script: String.Extras.js
	Extends the String native object to include methods useful in managing various kinds of strings (query strings, urls, html, etc).

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/
String.implement({
	stripTags: function() {
		return this.replace(/<\/?[^>]+>/gi, '');
  },
	parseQuery: function(encodeKeys, encodeValues) {
		encodeKeys = $pick(encodeKeys, true);
		encodeValues = $pick(encodeValues, true);
		var vars = this.split(/[&;]/);
		var rs = {};
		if (vars.length) vars.each(function(val) {
			var keys = val.split('=');
			if (keys.length && keys.length == 2) {
				rs[(encodeKeys)?encodeURIComponent(keys[0]):keys[0]] = (encodeValues)?encodeURIComponent(keys[1]):keys[1];
			}
		});
		return rs;
	},
	tidy: function() {
		var txt = this.toString();
		$each({
			"[\xa0\u2002\u2003\u2009]": " ",
			"\xb7": "*",
			"[\u2018\u2019]": "'",
			"[\u201c\u201d]": '"',
			"\u2026": "...",
			"\u2013": "-",
			"\u2014": "--",
			"\uFFFD": "&raquo;"
		}, function(value, key){
			txt = txt.replace(new RegExp(key, 'g'), value);
		});
		return txt;
	},
	cleanQueryString: function(method){
		return this.split("&").filter(method||function(set){
			return $chk(set.split("=")[1]);
		}).join("&");
	}
});


/*
Script: Element.Measure.js
	Extends the Element native object to include methods useful in measuring dimensions.

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/

Element.implement({

	expose: function(){
		if (this.getStyle('display') != 'none') return $empty;
		var before = {};
		var styles = { visibility: 'hidden', display: 'block', position:'absolute' };
		//use this method instead of getStyles 
		$each(styles, function(value, style){
			before[style] = this.style[style]||'';
		}, this);
		//this.getStyles('visibility', 'display', 'position');
		this.setStyles(styles);
		return (function(){ this.setStyles(before); }).bind(this);
	},
	
	getDimensions: function(options) {
		options = $merge({computeSize: false},options);
		var dim = {};
		function getSize(el, options){
			return (options.computeSize)?el.getComputedSize(options):el.getSize();
		};
		if(this.getStyle('display') == 'none'){
			var restore = this.expose();
			dim = getSize(this, options); //works now, because the display isn't none
			restore(); //put it back where it was
		} else {
			try { //safari sometimes crashes here, so catch it
				dim = getSize(this, options);
			}catch(e){}
		}
		return $chk(dim.x)?$extend(dim, {width: dim.x, height: dim.y}):$extend(dim, {x: dim.width, y: dim.height});
	},
	
	getComputedSize: function(options){
		options = $merge({
			styles: ['padding','border'],
			plains: {height: ['top','bottom'], width: ['left','right']},
			mode: 'both'
		}, options);
		var size = {width: 0,height: 0};
		switch (options.mode){
			case 'vertical':
				delete size.width;
				delete options.plains.width;
				break;
			case 'horizontal':
				delete size.height;
				delete options.plains.height;
				break;
		};
		var getStyles = [];
		//this function might be useful in other places; perhaps it should be outside this function?
		$each(options.plains, function(plain, key){
			plain.each(function(edge){
				options.styles.each(function(style){
					getStyles.push((style=="border")?style+'-'+edge+'-'+'width':style+'-'+edge);
				});
			});
		});
		var styles = this.getStyles.apply(this, getStyles);
		var subtracted = [];
		$each(options.plains, function(plain, key){ //keys: width, height, plains: ['left','right'], ['top','bottom']
			size['total'+key.capitalize()] = 0;
			size['computed'+key.capitalize()] = 0;
			plain.each(function(edge){ //top, left, right, bottom
				size['computed'+edge.capitalize()] = 0;
				getStyles.each(function(style,i){ //padding, border, etc.
					//'padding-left'.test('left') size['totalWidth'] = size['width']+[padding-left]
					if(style.test(edge)) {
						styles[style] = styles[style].toInt(); //styles['padding-left'] = 5;
						if(isNaN(styles[style]))styles[style]=0;
						size['total'+key.capitalize()] = size['total'+key.capitalize()]+styles[style];
						size['computed'+edge.capitalize()] = size['computed'+edge.capitalize()]+styles[style];
					}
					//if width != width (so, padding-left, for instance), then subtract that from the total
					if(style.test(edge) && key!=style && 
						(style.test('border') || style.test('padding')) && !subtracted.contains(style)) {
						subtracted.push(style);
						size['computed'+key.capitalize()] = size['computed'+key.capitalize()]-styles[style];
					}
				});
			});
		});
		if($chk(size.width)) {
			size.width = size.width+this.offsetWidth+size.computedWidth;
			size.totalWidth = size.width + size.totalWidth;
			delete size.computedWidth;
		}
		if($chk(size.height)) {
			size.height = size.height+this.offsetHeight+size.computedHeight;
			size.totalHeight = size.height + size.totalHeight;
			delete size.computedHeight;
		}
		return $extend(styles, size);
	}
});


/*
Script: Element.Pin.js
	Extends the Element native object to include the pin method useful for fixed positioning for elements.

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/

window.addEvent('domready', function(){
	var test = new Element('div').setStyles({
		position: 'fixed',
		top: 0,
		right: 0
	}).inject(document.body);
	var supported = (test.offsetTop === 0);
	test.dispose();
	Browser.set('supportsPositionFixed', supported);
});

Element.implement({
	pin: function(enable){
		if (this.getStyle('display') == 'none') {
			dbug.log('cannot pin ' + this + ' because it is hidden');
			return;
		}
		if(enable!==false) {
			var p = this.getPosition();
			if(!this.get('pinned')) {
				var pos = {
					top: (p.y - window.getScroll().y),
					left: (p.x - window.getScroll().x)
				};
				if(Browser.get('supportsPositionFixed')) {
					this.setStyle('position','fixed').setStyles(pos);
				} else {
					this.setStyles({
						position: 'absolute',
						top: p.y,
						left: p.x
					});
					window.addEvent('scroll', function(){
						if(this.get('pinned')) {
							var to = {
								top: (pos.top.toInt() + window.getScroll().y),
								left: (pos.left.toInt() + window.getScroll().x)
							};
							this.setStyles(to);
						}
					}.bind(this));
				}
				this.set('pinned', true);
			}
		} else {
			var op;
			if (!Browser.Engine.trident) {
				if (this.getParent().getComputedStyle('position') != 'static') op = this.getParent();
				else op = this.getParent().getOffsetParent();
			}
			var p = this.getPosition(op);
			this.set('pinned', false);
			var reposition = (Browser.get('supportsPositionFixed'))?
				{
					top: (p.y + window.getScroll().y),
					left: (p.x + window.getScroll().x)
				}:
				{
					top: (p.y),
					left: (p.x)
				};
			this.setStyles($merge(reposition, {position: 'absolute'}));
		}
		return this;
	},
	unpin: function(){
		return this.pin(false);
	},
	togglepin: function(){
		this.pin(!this.get('pinned'));
	}
});


/*
Script: Element.Position.js
	Extends the Element native object to include methods useful positioning elements relative to others.

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/

Element.implement({

	setPosition: function(options){
		$each(options||{}, function(v, k){ if (!$defined(v)) delete options[k]; });
		options = $merge({
			relativeTo: document.body,
			position: {
				x: 'center', //left, center, right
				y: 'center' //top, center, bottom
			},
			edge: false,
			offset: {x:0,y:0},
			returnPos: false,
			relFixedPosition: false,
			ignoreMargins: false
		}, options);
		//compute the offset of the parent positioned element if this element is in one
		var parentOffset = {x: 0, y: 0};
		var parentPositioned = false;
		var putItBack = this.expose();
		var offsetParent = this.getOffsetParent();
		putItBack();
		if(offsetParent && offsetParent != this.getDocument().body) {
			var putItBack = offsetParent.expose();
			parentOffset = offsetParent.getPosition();
			putItBack();
			parentPositioned = true;
			options.offset.x = options.offset.x - parentOffset.x;
			options.offset.y = options.offset.y - parentOffset.y;
		}
		//upperRight, bottomRight, centerRight, upperLeft, bottomLeft, centerLeft
		//topRight, topLeft, centerTop, centerBottom, center
		function fixValue(option) {
			if($type(option) != "string") return option;
			option = option.toLowerCase();
			var val = {};
			if(option.test('left')) val.x = 'left';
			else if(option.test('right')) val.x = 'right';
			else val.x = 'center';

			if(option.test('upper')||option.test('top')) val.y = 'top';
			else if (option.test('bottom')) val.y = 'bottom';
			else val.y = 'center';
			return val;
		};
		options.edge = fixValue(options.edge);
		options.position = fixValue(options.position);
		if(!options.edge) {
			if(options.position.x == 'center' && options.position.y == 'center') options.edge = {x:'center',y:'center'};
			else options.edge = {x:'left',y:'top'};
		}
		
		this.setStyle('position', 'absolute');
		var rel = $(options.relativeTo) || document.body;
    var top = (rel == document.body)?window.getScroll().y:rel.getPosition().y;
    var left = (rel == document.body)?window.getScroll().x:rel.getPosition().x;
		
		if (top < 0) top = 0;
    if (left < 0) left = 0;
		var dim = this.getDimensions({computeSize: true, styles:['padding', 'border','margin']});
		if (options.ignoreMargins) {
			options.offset.x = options.offset.x - parentOffset.x - offsetParent.getStyle('border-left-width').toInt()||0;
			options.offset.y = options.offset.y - parentOffset.y - offsetParent.getStyle('border-top-width').toInt()||0;
		}
		var pos = {};
		var prefY = options.offset.y.toInt();
		var prefX = options.offset.x.toInt();
		switch(options.position.x) {
			case 'left':
				pos.x = left + prefX;
				break;
			case 'right':
				pos.x = left + prefX + rel.offsetWidth;
				break;
			default: //center
				pos.x = left + (((rel == document.body)?window.getSize().x:rel.offsetWidth)/2) + prefX;
				break;
		};
		switch(options.position.y) {
			case 'top':
				pos.y = top + prefY;
				break;
			case 'bottom':
				pos.y = top + prefY + rel.offsetHeight;
				break;
			default: //center
				pos.y = top + (((rel == document.body)?window.getSize().y:rel.offsetHeight)/2) + prefY;
				break;
		};
		
		if(options.edge){
			var edgeOffset = {};
			
			switch(options.edge.x) {
				case 'left':
					edgeOffset.x = 0;
					break;
				case 'right':
					edgeOffset.x = -dim.x-dim.computedRight-dim.computedLeft;
					break;
				default: //center
					edgeOffset.x = -(dim.x/2);
					break;
			};
			switch(options.edge.y) {
				case 'top':
					edgeOffset.y = 0;
					break;
				case 'bottom':
					edgeOffset.y = -dim.y-dim.computedTop-dim.computedBottom;
					break;
				default: //center
					edgeOffset.y = -(dim.y/2);
					break;
			};
			pos.x = pos.x+edgeOffset.x;
			pos.y = pos.y+edgeOffset.y;
		}
		pos = {
			left: ((pos.x >= 0 || parentPositioned)?pos.x:0).toInt(),
			top: ((pos.y >= 0 || parentPositioned)?pos.y:0).toInt()
		};
		if(rel.getStyle('position') == "fixed"||options.relFixedPosition) {
			pos.top = pos.top.toInt() + window.getScroll().y;
			pos.left = pos.left.toInt() + window.getScroll().x;
		}

		if(options.returnPos) return pos;
		else this.setStyles(pos);
		return this;
	}
});

/*
Script: modalizer.js
	Defines Modalizer: functionality to overlay the window contents with a semi-transparent layer that prevents interaction with page content until it is removed

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/
var Modalizer = new Class({
	defaultModalStyle: {
		display:'block',
		position:'fixed',
		top:0,
		left:0,	
		'z-index':5000,
		'background-color':'#333',
		opacity:0.8
	},
	setModalOptions: function(options){
		this.modalOptions = $merge({
			width:(window.getScrollSize().x+300),
			height:(window.getScrollSize().y+300),
			elementsToHide: 'select',
			hideOnClick: true,
			modalStyle: {},
			updateOnResize: true,
			layerId: 'modalOverlay',
			onModalHide: $empty,
			onModalShow: $empty
		}, this.modalOptions, options);
		return this;
	},
	toElement: function(){
		if (!this.modalOptions.layerId) this.setModalOptions();
		return $(this.modalOptions.layerId) || new Element('div', {id: this.modalOptions.layerId}).inject(document.body);;
	},
	resize: function(){
		if($(this)) {
			$(this).setStyles({
				width:(window.getScrollSize().x+300),
				height:(window.getScrollSize().y+300)
			});
		}
	},
	setModalStyle: function (styleObject){
		this.modalOptions.modalStyle = styleObject;
		this.modalStyle = $merge(this.defaultModalStyle, {
			width:this.modalOptions.width,
			height:this.modalOptions.height
		}, styleObject);
		if($(this)) $(this).setStyles(this.modalStyle);
		return(this.modalStyle);
	},
	modalShow: function(options){
		this.setModalOptions(options);
		$(this).setStyles(this.setModalStyle(this.modalOptions.modalStyle));
		if(Browser.Engine.trident4) $(this).setStyle('position','absolute');
		$(this).removeEvents('click').addEvent('click', function(){
			this.modalHide(this.modalOptions.hideOnClick);
		}.bind(this));
		this.bound = this.bound||{};
		if(!this.bound.resize && this.modalOptions.updateOnResize) {
			this.bound.resize = this.resize.bind(this);
			window.addEvent('resize', this.bound.resize);
		}
		if ($type(this.modalOptions.onModalShow)  == "function") this.modalOptions.onModalShow();
		this.togglePopThroughElements(0);
		$(this).setStyle('display','block');
		return this;
	},
	modalHide: function(override){
		if(override === false) return false; //this is internal, you don't need to pass in an argument
		this.togglePopThroughElements(1);
		if ($type(this.modalOptions.onModalHide) == "function") this.modalOptions.onModalHide();
		$(this).setStyle('display','none');
		if(this.modalOptions.updateOnResize) {
			this.bound = this.bound||{};
			if(!this.bound.resize) this.bound.resize = this.resize.bind(this);
			window.removeEvent('resize', this.bound.resize);
		}
		return this;
	},
	togglePopThroughElements: function(opacity){
		if(Browser.Engine.trident4 || (Browser.Engine.gecko && Browser.Platform.mac)) {
			$$(this.modalOptions.elementsToHide).each(function(sel){
				sel.setStyle('opacity', opacity);
			});
		}
	}
});


/*
Script: StyleWriter.js

Provides a simple method for injecting a css style element into the DOM if it's not already present.

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/

var StyleWriter = new Class({
	createStyle: function(css, id) {
		window.addEvent('domready', function(){
			try {
				if($(id) && id) return;
				var style = new Element('style', {id: id||''}).inject($$('head')[0]);
				if (Browser.Engine.trident) style.styleSheet.cssText = css;
				else style.set('text', css);
			}catch(e){dbug.log('error: %s',e);}
		}.bind(this));
	}
});

/*
Script: StickyWin.js

Creates a div within the page with the specified contents at the location relative to the element you specify; basically an in-page popup maker.

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/

var StickyWin = new Class({
	Implements: [Options, Events, StyleWriter],
	options: {
//	onDisplay: $empty,
//	onClose: $empty,
		closeClassName: 'closeSticky',
		pinClassName: 'pinSticky',
		content: '',
		zIndex: 10000,
		className: '',
		//id: ... set above in initialize function
/*  these are the defaults for setPosition anyway
/************************************************
//		edge: false, //see Element.setPosition in element.cnet.js
//		position: 'center', //center, corner == upperLeft, upperRight, bottomLeft, bottomRight
//		offset: {x:0,y:0},
//	  relativeTo: document.body, */
		width: false,
		height: false,
		timeout: -1,
		allowMultipleByClass: false,
		allowMultiple: true,
		showNow: true,
		useIframeShim: true,
		iframeShimSelector: ''
	},
	css: '.SWclearfix:after {content: "."; display: block; height: 0; clear: both; visibility: hidden;}'+
			 '.SWclearfix {display: inline-table;}'+
			 '* html .SWclearfix {height: 1%;}'+
			 '.SWclearfix {display: block;}',
	initialize: function(options){
		this.options.inject = {
			target: document.body,
			where: 'bottom' 
		};
		this.setOptions(options);
		
		this.id = this.options.id || 'StickyWin_'+new Date().getTime();
		this.makeWindow();
		if(this.options.content) this.setContent(this.options.content);
		if(this.options.timeout > 0) {
			this.addEvent('onDisplay', function(){
				this.hide.delay(this.options.timeout, this)
			}.bind(this));
		}
		if(this.options.showNow) this.show();
		//add css for clearfix
		this.createStyle(this.css, 'StickyWinClearFix');
	},
	toElement: function() {
		return this.win;
	},
	makeWindow: function(){
		this.destroyOthers();
		if(!$(this.id)) {
			this.win = new Element('div', {
				id:		this.id
			}).addClass(this.options.className).addClass('StickyWinInstance').addClass('SWclearfix').setStyles({
			 	display:'none',
				position:'absolute',
				zIndex:this.options.zIndex
			}).inject(this.options.inject.target, this.options.inject.where).store('StickyWin', this);			
		} else this.win = $(this.id);
		if(this.options.width && $type(this.options.width.toInt())=="number") this.win.setStyle('width', this.options.width.toInt());
		if(this.options.height && $type(this.options.height.toInt())=="number") this.win.setStyle('height', this.options.height.toInt());
		return this;
	},
	show: function(){
		this.fireEvent('onDisplay');
		this.showWin();
		if(this.options.useIframeShim) this.showIframeShim();
		this.visible = true;
		return this;
	},
	showWin: function(){
		this.win.setStyle('display','block');
		if(!this.positioned) this.position();
	},
	hide: function(suppressEvent){
		if(!suppressEvent) this.fireEvent('onClose');
		this.hideWin();
		if(this.options.useIframeShim) this.hideIframeShim();
		this.visible = false;
		return this;
	},
	hideWin: function(){
		this.win.setStyle('display','none');
	},
	destroyOthers: function() {
		if(!this.options.allowMultipleByClass || !this.options.allowMultiple) {
			$$('div.StickyWinInstance').each(function(sw) {
				if(!this.options.allowMultiple || (!this.options.allowMultipleByClass && sw.hasClass(this.options.className))) 
					sw.dispose();
			}, this);
		}
	},
	setContent: function(html) {
		if(this.win.getChildren().length>0) this.win.empty();
		if($type(html) == "string") this.win.set('html', html);
		else if ($(html)) this.win.adopt(html);
		this.win.getElements('.'+this.options.closeClassName).each(function(el){
			el.addEvent('click', this.hide.bind(this));
		}, this);
		this.win.getElements('.'+this.options.pinClassName).each(function(el){
			el.addEvent('click', this.togglepin.bind(this));
		}, this);
		return this;
	},	
	position: function(){
		this.positioned = true;
		this.win.setPosition({
			relativeTo: this.options.relativeTo,
			position: this.options.position,
			offset: this.options.offset,
			edge: this.options.edge
		});
		if(this.shim) this.shim.position();
		return this;
	},
	pin: function(pin) {
		if(!this.win.pin) {
			dbug.log('you must include element.pin.js!');
			return this;
		}
		this.pinned = $pick(pin, true);
		this.win.pin(pin);
		return this;
	},
	unpin: function(){
		return this.pin(false);
	},
	togglepin: function(){
		return this.pin(!this.pinned);
	},
	makeIframeShim: function(){
		if(!this.shim){
			var el = (this.options.iframeShimSelector)?this.win.getElement(this.options.iframeShimSelector):this.win;
			this.shim = new IframeShim(el, {
				display: false,
				name: 'StickyWinShim'
			});
		}
	},
	showIframeShim: function(){
		if(this.options.useIframeShim) {
			this.makeIframeShim();
			this.shim.show();
		}
	},
	hideIframeShim: function(){
		if(this.options.useIframeShim)
			this.shim.hide();
	},
	destroy: function(){
		if (this.win) this.win.dispose();
		if(this.options.useIframeShim) this.shim.dispose();
		if($('modalOverlay'))$('modalOverlay').dispose();
	}
});


/*
Script: StickyWin.Modal.js

This script extends StickyWin and StickyWinFx classes to add Modalizer functionality.

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/
var StickyWinModal, StickyWinFxModal;
(function(){
var modalWinBase = function(extend){
	return {
		Extends: extend,
		initialize: function(options){
			options = options||{};
			this.setModalOptions($merge(options.modalOptions||{}, {
				onModalHide: function(){
						this.hide(false);
					}.bind(this)
				}));
			this.parent(options);
		},
		show: function(showModal){
			if($pick(showModal, true)) {
				this.modalShow();
				this.win.getElements(this.modalOptions.elementsToHide).setStyle('opacity', 1);
			}
			this.parent();
		},
		hide: function(hideModal){
			if($pick(hideModal, true)) this.modalHide();
			this.parent($pick(hideModal, true));
		}
	}
};
StickyWinModal = new Class(modalWinBase(StickyWin));
StickyWinModal.implement(new Modalizer);
StickyWinFxModal = (typeof StickyWinFx != "undefined")?new Class(modalWinBase(StickyWinFx)):$empty;
try { StickyWinFxModal.implement(new Modalizer()); }catch(e){}
})();

/*
Script: StickyWin.ui.js

Creates an html holder for in-page popups using a default style.

License:
	http://clientside.cnet.com/wiki/cnet-libraries#license
*/

StickyWin.ui = function(caption, body, options){
	options = $extend({
		width: 300,
		css: "div.DefaultStickyWin div.body{font-family:verdana; font-size:11px; line-height: 13px;}"+
			"div.DefaultStickyWin div.top_ul{background:url({%baseHref%}full.png) top left no-repeat; height:30px; width:15px; float:left}"+
			"div.DefaultStickyWin div.top_ur{position:relative; left:0px !important; left:-4px; background:url({%baseHref%}full.png) top right !important; height:30px; margin:0px 0px 0px 15px !important; margin-right:-4px; padding:0px}"+
			"div.DefaultStickyWin h1.caption{clear: none !important; margin:0px 5px 0px 0px !important; overflow: hidden; padding:0 !important; font-weight:bold; color:#555; font-size:14px !important; position:relative; top:8px !important; left:5px !important; float: left; height: 22px !important;}"+
			"div.DefaultStickyWin div.middle, div.DefaultStickyWin div.closeBody {background:url({%baseHref%}body.png) top left repeat-y; margin:0px 20px 0px 0px !important;	margin-bottom: -3px; position: relative;	top: 0px !important; top: -3px;}"+
			"div.DefaultStickyWin div.body{background:url({%baseHref%}body.png) top right repeat-y; padding:8px 30px 8px 0px !important; margin-left:5px !important; position:relative; right:-20px !important;}"+
			"div.DefaultStickyWin div.bottom{clear:both}"+
			"div.DefaultStickyWin div.bottom_ll{background:url({%baseHref%}full.png) bottom left no-repeat; width:15px; height:15px; float:left}"+
			"div.DefaultStickyWin div.bottom_lr{background:url({%baseHref%}full.png) bottom right; position:relative; left:0px !important; left:-4px; margin:0px 0px 0px 15px !important; margin-right:-4px; height:15px}"+
			"div.DefaultStickyWin div.closeButtons{text-align: center; background:url({%baseHref%}body.png) top right repeat-y; padding: 0px 30px 8px 0px; margin-left:5px; position:relative; right:-20px}"+
			"div.DefaultStickyWin a.button:hover{background:url({%baseHref%}big_button_over.gif) repeat-x}"+
			"div.DefaultStickyWin a.button {background:url({%baseHref%}big_button.gif) repeat-x; margin: 2px 8px 2px 8px; padding: 2px 12px; cursor:pointer; border: 1px solid #999 !important; text-decoration:none; color: #000 !important;}"+
			"div.DefaultStickyWin div.closeButton{width:13px; height:13px; background:url({%baseHref%}closebtn.gif) no-repeat; position: absolute; right: 0px; margin:10px 15px 0px 0px !important; cursor:pointer}"+
			"div.DefaultStickyWin div.dragHandle {	width: 11px;	height: 25px;	position: relative;	top: 5px;	left: -3px;	cursor: move;	background: url({%baseHref%}drag_corner.gif); float: left;}",
		cornerHandle: false,
		cssClass: '',
		baseHref: 'http://www.cnet.com/html/rb/assets/global/stickyWinHTML/',
		buttons: []
/*	These options are deprecated:		
		closeTxt: false,
		onClose: $empty,
		confirmTxt: false,
		onConfirm: $empty	*/
	}, options);
	//legacy support
	if(options.confirmTxt) options.buttons.push({text: options.confirmTxt, onClick: options.onConfirm || $empty});
	if(options.closeTxt) options.buttons.push({text: options.closeTxt, onClick: options.onClose || $empty});

	new StyleWriter().createStyle(options.css.substitute({baseHref: options.baseHref}, /\\?\{%([^}]+)%\}/g), 'defaultStickyWinStyle');
	caption = $pick(caption, '%caption%');
	body = $pick(body, '%body%');
	var container = new Element('div').setStyle('width', options.width).addClass('DefaultStickyWin');
	if(options.cssClass) container.addClass(options.cssClass);
	//header
	var h1Caption = new Element('h1').addClass('caption').setStyle('width', (options.width.toInt()-(options.cornerHandle?70:60)));

	if($(caption)) h1Caption.adopt(caption);
	else h1Caption.set('html', caption);
	
	var bodyDiv = new Element('div').addClass('body');
	if($(body)) bodyDiv.adopt(body);
	else bodyDiv.set('html', body);
	
	var top_ur = new Element('div').addClass('top_ur').adopt(
			new Element('div').addClass('closeButton').addClass('closeSticky')
		).adopt(h1Caption);
	if(options.cornerHandle) new Element('div').addClass('dragHandle').inject(top_ur, 'top');
	else h1Caption.addClass('dragHandle');
	container.adopt(
		new Element('div').addClass('top').adopt(
				new Element('div').addClass('top_ul')
			).adopt(top_ur)
	);
	//body
	container.adopt(new Element('div').addClass('middle').adopt(bodyDiv));
	//close buttons
	if(options.buttons.length > 0){
		var closeButtons = new Element('div').addClass('closeButtons');
		options.buttons.each(function(button){
			if(button.properties && button.properties.className){
				button.properties['class'] = button.properties.className;
				delete button.properties.className;
			}
			var properties = $merge({'class': 'closeSticky'}, button.properties);
			new Element('a').addEvent('click',
				button.onClick || $empty).appendText(
				button.text).inject(closeButtons).setProperties(properties).addClass('button');
		});
		container.adopt(new Element('div').addClass('closeBody').adopt(closeButtons));
	}
	//footer
	container.adopt(
		new Element('div').addClass('bottom').adopt(
				new Element('div').addClass('bottom_ll')
			).adopt(
				new Element('div').addClass('bottom_lr')
		)
	);
	return container;
};
