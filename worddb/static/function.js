
function makeApiCall (customArgs) {
	// Arguments that NEED to be passed in customArgs: url, form, success
	var error = function (jqXHR, status, error) {
			try {
				data = JSON.parse(jqXHR.responseText);
			} catch (error) {
				console.warn('Received data is not serializable. Aborting messaging process.');
				return
			}
			show_errors(data.errors);
		},
		beforeSend = function (xhr) {
			xhr.setRequestHeader("X-CSRFToken", window._csrf_token);
		},
		success = function (data, textStatus, jqXHR) {
			//! This is for debuging purposes only.
			// Make direct connection in live code.
			console.log('Data received', data, textStatus, jqXHR)
			d = data;
			if (data.success) {
				if (customArgs._success)
					customArgs._success.apply(this, arguments);
			} else
				error(jqXHR, textStatus, data.errors);
		}
	customArgs._success = customArgs.success
	delete customArgs.success
	ajaxArgs = {
		context: this,
		dataType: 'JSON',
		type: 'POST',
		beforeSend: beforeSend,
		error: error,
		success: success
	}
	$.ajax($.extend(ajaxArgs, customArgs));
}

function makeSortFuncGetter (obj, fallback) {
	return function () {
		function getURLParameter (name) {
			return decodeURI((RegExp("" + name + "=(.+?)(&|$)").exec(location.search) || [null, null])[1]);
		};
		var ordering = getURLParameter('order_by');
		console.log('ordering:', ordering);
		for (value in obj) {
			if (obj.hasOwnProperty(value)) {
				if (value == ordering)
					return function (a, b) {
						if (obj[value](a) > obj[value](b))
							return 1;
						return -1;
					}
			}
		}
		console.warn("No ordering was catched. Trying fallback.")
		return function (a, b) {
			if (fallback(a) > fallback(b))
				return 1;
			return -1;
		}
	}
}


if (typeof(String.prototype.trim) === "undefined") {
	String.prototype.trim = function() {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

if (typeof(String.prototype.capitalize) === "undefined") {
	String.prototype.capitalize = function() {
		return String(this).replace(/\w\S*/g, function(t){return t.charAt(0).toUpperCase()+t.substr(1);})
	}
}

$.ctrl = function(key, callback, args) {
	$(document).keydown(function(e) {
		if(!args) args=[]; // IE barks when args is null
		if(e.keyCode == key.charCodeAt(0) && e.ctrlKey) {
			callback.apply(this, args);
			return false;
		}
	});
};

$.fn.serializeObject = function () {
	var obj = {};
	$.each($(this).serializeArray(), function (index, item) {
		obj[item.name] = item.value;
	})
	return obj;
}

// of global usage
var flash_message_html = "<li class='flash-message'></li>";
var no_tags_message_html = '<h4 id="no-tags-message" style="margin: 10px 10px; color: #666; font-size: 14px;"></h4>';

function show_errors (messages) {
	console.warn(messages);
	for (var i=0; i<messages.length; i++)
		flash_message(messages[i], {'background': "#F60018", color: 'white'});
}

function show_info (messages) {
	for (var i=0; i<messages.length; i++)
		flash_message(messages[i], {'background': "#F60018", color: 'white'});
}

function flash_message(message, customcss, delay) { // implement callback?
	var customcss = customcss || {};
	var delay = delay || 8000;
	var obj = $(flash_message_html).css(customcss).html(message);
	
	if (!$('#flash-messages-wrapper')[0]) // if wrapper not found, create
		$(document.body).append('<ul id="flash-messages-wrapper"></ul>');

	obj.click(function () { $(this).stop().slideUp(); });
	obj.hide().appendTo('#flash-messages-wrapper').fadeIn().delay(delay).slideUp(function(){ obj.remove() });
}

function flash_error(message, customcss, delay) {
	var customcss = $.extend({background:'url(/static/images/bg-grain-red.png)', color: 'white'}, customcss);
	flash_message(message, customcss, delay);
}


function goto_list(listname) { window.location.href = '/lists/'+encodeURI(listname); }

function open_link(link) { window.open(link); return false; }


function show_no_tags_message(message) {
	$(no_tags_message_html)
		.html(message)
			.hide()
				.appendTo('ul.tags-wrapper')
					.fadeIn();
}




/**********************************************/
/**********************************************/
/*********** WORDS RELATED FUNCTIONS ***********/
/**********/
/**********/

/**************************************/
/* ADD-WORD/EDIT-WORD BOXES functions */
/**************************************/


function showMeaning (textarea) {
	function _is_valid (word) {
		return word?true:false;
	}
	var	word = $(textarea).val(),
		elm = textarea.parentElement.querySelector('.field-meaning'),
		MEANING_HTML = "You can find the meaning for '[[word]]' <a href='javascript:void(0);'\
		 onClick='location.href=\'http://www.wordreference.com/enpt/${word}\''>here</a> (<a href='http://wordreference.com'>wordreference.com</a>).";
	if (!_is_valid(word))
		return $(elm).fadeOut();
	$(elm).html(Mustache.render(MEANING_HTML, {'word': word})).fadeIn();
}

function hideEditWrapper () {
	$("#edit-wrapper").fadeOut('fast', function () {
		$("#edit-wrapper").remove();
	});
}

/////////////////////////


function makeEditWordWrapper (dict) {
	var elm = $(Mustache.render($('script#edit-box')[0].innerHTML, dict))
	elm.find("[name=word]").bind('keyup paste', function () { showMeaning(this); });
	$(elm).hide().appendTo('body').fadeIn();
	$('#edit-wrapper textarea').autoResize({'extraSpace': 10});
	$("#edit-wrapper [autofocus]").focus();
}

function makeEditListWrapper (dict) {
	var html = Mustache.render($('script#edit-box')[0].innerHTML, dict);
	$(html).hide().appendTo('body').fadeIn();
	$('#edit-wrapper textarea').autoResize({'extraSpace': 10});
	$("#edit-wrapper [autofocus]").focus();
}

/**********************************/
/* EditorWrapper caller creation */
/********************************/

function makeAddWrapperCreator (objname, renderer) {
	return function () {
		renderer({
			B1: { label: "Add", 	func: objname+'Db.create' },
			B2: { label: "Cancel",	func: "hideEditWrapper" },
		});
	}
}

function makeEditWrapperCreator (objname, func) {
	return function (elm) {
		func($.extend({
			B1: { label: "Save", 							func: objname+'Db.update' },
			B2: { label: "Remove "+objname.capitalize(),	func: objname+'Db.delete' },
		}, elm.dataset));
	}
}

actionMap = {
	create: 'PUT',
	update: 'POST',
	delete: 'DELETE'
}

function makeApiCaller (action, objname, url_template, callback) {
	return function (elm) {
		var form = $(elm).serializeObject();
		return makeApiCall({
			url: Mustache.render(url_template, form),
			data: form,
			type: actionMap[action],
			success: function (data, status) {
				flash_message(data['text']);
				callback(JSON.parse(data.object));
				hideEditWrapper();
			}
		});
	};
}


window.onload = function () {

	Mustache.tags = ['[[', ']]'];

	if (document.querySelector('body.lists')) {

		listPin = {
			create: objPinCreator('list', window.listpinHTML),
			update: objPinUpdater('list', window.listpinHTML),
			delete: objPinRemover('list')
		}

		listDb = {
			create: makeApiCaller('create', 'lists', '/lists/',			listPin.create),
			update: makeApiCaller('update', 'lists', '/lists/[[id]]', 	listPin.update),
			delete: makeApiCaller('delete', 'lists', '/lists/[[id]]', 	listPin.delete),
		}

		addList = makeAddWrapperCreator('list', makeEditListWrapper, listDb)
		editList = makeEditWrapperCreator('list', makeEditListWrapper, listDb)
		
		if (!lists[0]) 
			show_no_tags_message("» no lists found");
		else {
			lists = $(window.lists).sort(getSortFunc());
			for (var i=0; i<window.lists.length; i++) {
				listPin.create(lists[i]);
			}
		}

	} else if (document.querySelector('body.words')) {
		
		wordPin = {
			create: objPinCreator('word', wordpinHTML),
			update: objPinUpdater('word', wordpinHTML),
			delete: objPinRemover('word')
		}

		wordDb = {
			create: makeApiCaller('create', 'words', '/lists/[[list]]/words',		 objPinCreator('word', wordpinHTML)),
			update: makeApiCaller('update', 'words', '/lists/[[list]]/words/[[id]]', objPinUpdater('word', wordpinHTML)),
			delete: makeApiCaller('delete', 'words', '/lists/[[list]]/words/[[id]]', objPinRemover('word')),
		}
		
		addWord = makeAddWrapperCreator('word', makeEditWordWrapper, wordDb)
		editWord = makeEditWrapperCreator('word', makeEditWordWrapper, wordDb)

		if (!words[0])
			show_no_tags_message("» no words found");
		else {
			words = $(words).sort(getSortFunc());
			for (var i=0; i<words.length; i++)
				wordPin.create(words[i]);
		}
		
	}
}


/**********************************************/
/**********************************************/
/*********** LISTS RELATED FUNCTIONS ***********/


function objPinCreator (objname, html) {
	return function (data) {
		var pin = $(Mustache.render(html, data));
		for (p in data) {
			if (data.hasOwnProperty(p)) {
				pin[0].dataset[p] = data[p];
			}
		}
		pin.appendTo('.tags-wrapper');
	}
}

function objPinUpdater (objname, html) {
	return function (data) {	
		var pin = $("."+objname+"[data-id='"+data.id+"']");
		pa = pin;
		for (p in data) {
			if (data.hasOwnProperty(p)) {
				pin[0].dataset[p] = data[p];
			}
		}
		pin[0].innerHTML = $(Mustache.render(html, data))[0].innerHTML;
	} 
}

function objPinRemover (objname) {
	return function (data) {
		console.log('d', data)
		var pin = $(".list[data-id='"+data.id+"']");
		pin.fadeOut(function () {
			pin.remove();
		});
	}
}
