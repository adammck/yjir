var dh = $(document.html);

/* we're obviously running javascript, so
 * add a css hook to the root element */
dh.addClass("js");

/* if we have css (check for the token
 * from base.css), add another hook */
if (dh.getStyle ("z-index") == 1234)
	dh.addClass("css");

/* if we are being loaded in a
 * frame, then add another hook */
if (window.frameElement)
	dh.addClass("framed");




/* ====  HIJACK ADD + EDIT LINKS, OPEN IN IFRAME  ==== */


window.addEvent ("domready", function () {
	$$("div.add a, a.edit, #actions a, div.notice a").addEvent ("click", function(ev) {
		ev.stop();
		
		/* create a dialog box (iframe), and open it
		 * in a "stickywin" (via the cnet extensions) */
		new StickyWinModal({
			content: '<iframe class="dialog loading" src="' + this.href + '" frameborder="0"></iframe>',
			relativeTo: document.body,
			
			/* make the overlay light, rather
			 * than dark (the default) */
			modalOptions: {
				modalStyle: {
					"background-color": "#fff",
					"opacity": 0.8
				}
			}
		});
	});
});




/* ====  WHEN LOADING IN AN IFRAME...  ==== */


if (window.frameElement) {
	(function () {
		var frame = $(window.frameElement);
		
		/* measure the contents of this document, and
		 * auto-size the iframe we are contained by */
		var autosize = function () {
			var size = $("wrapper").getSize();
			frame.setStyles ({
				"height": size.y + "px"//,
				//"margin-top": -(size.y/2) + "px"
			});
		};
		
		/* re-size every time the document *could have*
		 * changed size. todo: should this poll regularly? */
		window.addEvent ("domready", autosize);
		window.addEvent ("resize", autosize);
		
		
		/* when the document has finished loading,
		 * remove the class from the frame, which
		 * makes it visible (see base.css) */
		window.addEvent ("load", function () {
			frame.removeClass("loading");
			
			/* since this frame is mocking a modal
			 * dialog, give focus to the first field
			 * as soon as it is made visible */
			(function () {
				var fields = $$("input, textarea, select");
				if (fields.length) fields[0].select();
			}).delay(100);
		});


		window.addEvent ("domready", function() {
		
			/* hijack the "cancel" button to
			 * simply close the lightbox */
			$$("input[value=Cancel]").each(function(el) {
				el.addEvent ("click", function(ev) {
					ev.stop();
				
					/* destroy both the modal overlay
					 * and the "dialog" iframe */
					var sel = "#modalOverlay, .StickyWinInstance";
					frameElement.ownerDocument.getElements(sel).destroy();
				});
			});
		});
	})();
}




















window.addEvent ("domreadyxx", function() {
	$$(".column.scopes ul axxxx").addEvent ("click", function(ev) {
		var t = ev.target;
		
		/* cancel the click event, but store the
		 * href that we would have navigated to,
		 * in case the ajax fails */
		var href = t.href;
		ev.stop();
		
		new Request({
			"url": "/json/"+ t.get ("text"),
			"onSuccess": function (text) {
				var data = JSON.decode (text);
				
				var dest = $$(".column.keywords .col-hack")[0];
				
				/* remove any existing lists or hints from the dom
				 * (there won't be any if this is first load) */
				dest.getElements ("ul,div.pick").dispose();
				
				/* create a new list, and populate it by
				 * iterating the data returned by JSON */
				var ul = new Element ("ul").inject(dest);
				data["keywords"].each(function(kw,index) {
					
					// each item is a new LI + A
					new Element("li").adopt(
						new Element("a", {
							"href": href + "/" + kw["name"],
							"html": kw["name"],
							"class": (index==0) ? "first" : ""
						})
					).inject(ul);
				});
				
				/* if an fix is needed (looking at YOU,
				 * internet explorer) then apply it now
				 * that the contents have changed */
				var fit = window.columns_fit_fix;
				if(fit) fit();
				
				/* de-active the current "active" element,
				 * and active the one we just clicked */
				t.getParent().getParent().getElements("li.active").removeClass("active");
				t.getParent().addClass("active");
			},
			
			/* fall back to full-page reloading
			 * if the fancy-schmancy ajax fails */
			"onFailure": function() {
				location.assign(href); }
		}).get();
	});
});

