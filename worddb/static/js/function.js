

if (typeof(String.prototype.trim) === "undefined") {
	String.prototype.trim = function() {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
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

// of global usage
var flash_message_html = "<li class='flash-message'></li>";
var no_tags_message_html = '<h4 id="no-tags-message" style="margin: 10px 10px; color: #666; font-size: 14px;"></h4>';

function show_flash_message(message, customcss, delay) { // implement callback?
	var customcss = customcss || {};
	var delay = delay || 8000;
	var obj = $(flash_message_html).css(customcss).html(message);
	
	if (!$('#flash-messages-wrapper')[0]) // if wrapper not found, create
		$(document.body).append('<ul id="flash-messages-wrapper"></ul>');

	obj.click(function () { $(this).stop().slideUp(); });
	obj.hide().appendTo('#flash-messages-wrapper').fadeIn().delay(delay).slideUp();
}

function show_flash_error(message, customcss, delay) {
	var customcss = $.extend({'background':'url(/static/images/bg-grain-red.png)'}, customcss);
	show_flash_message(message, customcss, delay);
}


function goto_list(listname) { window.location.href = '/lists/'+encodeURI(listname); }

function open_link(link) { window.open(link); return false; }

function show_blackout() {
	$('#blackout').stop().show();
}

function hide_blackout() {
	$('#blackout').stop().fadeOut('fast');
}

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

var box_field_info_html = '<div class="field-info"></div>';

function show_meaning_info_box(textarea, html) {
	
	var field = $(textarea).parent(),
		word = $(textarea).val(),
		box = field.find('.field-info')[0],
		html = html || 'find meaning of \'${word}\' <a href="javascript:void(0);" \
						onClick="open_link(\'http://www.wordreference.com/enpt/${word}\')">here</a> \
						(wordreference.com).';

	if (!box) {
		if (!word) return;
		box = $(box_field_info_html).hide().appendTo(field).fadeIn();
	} else 
		if (!word)
			$(box).fadeOut( function() { $(box).remove() });

	$(box).html($.tmpl(html, {'word': word}));
}

// Add-Word Box functions
function make_add_word_box(word) { // creates the Add-Word box	
	var html = $(add_word_box_html);
	html.find(".edit-field[data-field=word] textarea").bind('keyup paste',
		function () { show_meaning_info_box(this); });

	show_blackout();
	html.hide().appendTo('body').fadeIn();
	$('#edit-wrapper textarea').autoResize({'extraSpace': 10});
	$("#edit-wrapper [data-field=word] .edit-field-value").focus();
}

function remove_add_word_box() { // removes the Add-Word box
	remove_editwrapper()
}


// Edit-Word Box functions
function make_edit_word_box(word) { // creates the Edit-Word Box
	show_blackout();
	w = word;
	$.tmpl(edit_word_box_html, word.dataset).hide().appendTo('body').fadeIn();

	if (word.dataset['meaning'] === '') // if meaning not set, show info_meaning box
		show_meaning_info_box($("#edit-wrapper [data-field=word] textarea")[0]);

	$('#edit-wrapper textarea').autoResize({'extraSpace': 10});
	$("#edit-wrapper [data-field=word] .edit-field-value").focus();
}

function remove_edit_word_box() { // removes the Edit-Word box
	remove_editwrapper()
}

function remove_editwrapper() {
	$("#edit-wrapper").fadeOut('fast', function() {
		$("#edit-wrapper").remove()
		hide_blackout();
	});
}

/****************************/
/* AJAX DATABASE ACCESS API */
/****************************/

function add_word_db(edit_wrapper, parentid, csrf_token) { // adds a word to the database based on Add-Word Box
	
	var form = {};
	$(['word', 'meaning', 'origin']).each(function (index, item) {
		form[item] = edit_wrapper.querySelector("[data-field="+item+"] .edit-field-value").value;
	});
	form['listid'] = parentid;
	console.log("oi");

	$.ajax({
		url: window.location.href+'/words', // gambiarra?
		context: this,
		data: form,
		type: 'PUT',
		dataType: 'json',
		beforeSend: function (xhr) {
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		},
		success: function (data, status) {
			if (data['success']) {
				show_flash_message(data['text']);
				add_word_tag($.extend(form, { 'wordid': data['wordid'] }));
				remove_add_word_box();
			} else {
				for (var i=0; i<data['errors'].length; i++)
					show_flash_error(data['errors'][i], {'background': "#ff7373"});
			}
		},
		error: function (obj, status) {
			// wtf?
		} });
}

function update_word_db(edit_wrapper, parentid, csrf_token) { // updates the word in the database based on the Edit-Word box
	
	form = {};
	$(['word', 'meaning', 'origin']).each(function (index, item) {
		form[item] = edit_wrapper.querySelector("[data-field="+item+"] .edit-field-value").value;
	});
	form['wordid'] = edit_wrapper.dataset['wordid'];
	form['listid'] = parentid;
	form['csrfmiddlewaretoken'] = csrf_token;

	$.ajax({
		url: window.location.href+'/words/'+form['wordid'], 
		context: this,
		data: form,
		type: 'post',
		dataType: 'json',
		beforeSend: function (xhr) {
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		},
		success: function (data, status) {
			if (data['success']) {
				show_flash_message(data['text']);
				update_word_tag(form);
				remove_edit_word_box();
			} else {
				for (var i=0; i<data['errors'].length; i++)
					show_flash_message(data['errors'][i], {'background': "#F60018"});
			}
		},
		error: function (obj, status) {
			// wtf?
		} });
}

function remove_word_db(edit_wrapper, parentid, csrf_token) { // removes the word being edited at the Edit-Word box from the database

	var form = {};
	form['wordid'] = edit_wrapper.dataset['wordid'];
	form['listid'] = parentid;
	form['csrfmiddlewaretoken'] = csrf_token;

	$.ajax({
		url: window.location.href+'/words/'+form['wordid'], 
		context: this, 
		data: form,
		type: 'DELETE',
		dataType: 'json',
		beforeSend: function (xhr) {
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		},
		success: function (data, status) {
			if (data['success']) {
				show_flash_message(data['text']);
				remove_word_tag(form);
				remove_edit_word_box();
			} else {
				for (var i=0; i<data['errors'].length; i++)
					show_flash_message(data['errors'][i], {'background': "#F60018"});
			}
		},
		error: function (obj, status) {
			// wtf?
		} });
}



/**********************************************/
/**********************************************/
/*********** LISTS RELATED FUNCTIONS ***********/
/**********/
/**********/

/**************************************/
/* ADD-LIST/EDIT-LIST BOXES functions */
/**************************************/

// Add-List Box functions
function make_add_list_box() { 
	show_blackout();
	$(add_list_box_html).hide().appendTo('body').fadeIn();
	$('#edit-wrapper textarea').autoResize({'extraSpace': 10});
	$("#edit-wrapper [data-field=label] .edit-field-value").focus();
}

function remove_add_list_box() { 
	remove_edit_list_box();
}


// Edit-List Box functions
function make_edit_list_box(list) {
	show_blackout();
	$.tmpl(edit_list_box_html, list.dataset).hide().appendTo('body').fadeIn();

	$("#edit-wrapper textarea").autoResize({'extraSpace':10});
	$("#edit-wrapper [data-field=label] .edit-field-value").focus();
}


function remove_edit_list_box() {
	$("#edit-wrapper").fadeOut('fast', function() {
		$("#edit-wrapper").remove();
		hide_blackout();
	});
}

/****************************/
/* AJAX DATABASE ACCESS API */
/****************************/

function add_list_db(wrapper, csrf_token) { // adds a list to the database based on Add-List Box
	var form = {};
	$(['label', 'description']).each(function (index, item) {
		form[item] = wrapper.querySelector("[data-field="+item+"] .edit-field-value").value;
	});

	$.ajax({
		url: '/lists/',
		context: this,
		data: form,
		type: 'PUT',
		dataType: 'json',
		beforeSend: function (xhr) {
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		},
		success: function (data, status) {
			if (data['success']) {
				show_flash_message(data['text']);	
				add_list_tag($.extend(form, {'listid': data['listid']}));
				remove_add_list_box();
			} else {
				for (var i=0; i<data['errors'].length; i++)
					show_flash_message(data['errors'][i], {'background': "#ff7373", 'border-color': 'red', 'color': 'black'});
			}
		},
		error: function (jqXHR, textStatus, errorThrown) {
			// wtf?
		} });
}

function update_list_db(edit_wrapper, csrf_token) { // updates the list in the database based on the Edit-List box

	var form = {
		description: edit_wrapper.querySelector("[data-field='description'] .edit-field-value").value,
		label: edit_wrapper.querySelector("[data-field='label'] .edit-field-value").value,
		listid: edit_wrapper.dataset['listid'],
	};
	
	$.ajax({
		url: '/lists/'+form['listid'],
		context: this,
		data: form,
		dataType: 'json',
		type: 'POST',
		beforeSend: function (xhr) {
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		},
		success: function (data, status) {
			if (data['success']) {
				show_flash_message(data['text']);
				update_list_tag(form);
				remove_edit_list_box();
			} else {
				for (var i=0; i<data['errors'].length; i++)
					show_flash_message(data['errors'][i], {'background': "#ff7373", 'border-color': 'red'});
			}
		},
		error: function (obj, status) {
			// wtf?
		} });
}

function remove_list_db(edit_wrapper, csrf_token) { // removes the list being edited at the Edit-List from the database
	
	var form = {};
	form['listid'] = edit_wrapper.dataset['listid'];
	form['csrfmiddlewaretoken'] = csrf_token;

	$.ajax({
		url: '/lists/'+form['listid'],
		context: this, 
		data: form,
		type: 'DELETE',
		dataType: 'json',
		beforeSend: function (xhr) {
			xhr.setRequestHeader("X-CSRFToken", csrf_token);
		},		
		success: function (data, status) {
			if (data['success']) {
				show_flash_message(data['text']);
				remove_list_tag(form);
				remove_edit_word_box();
			} else {
				for (var i=0; i<data['errors'].length; i++)
					show_flash_message(data['errors'][i], {'background': "#ff7373", 'border-color': 'red'});
			}
		},
		error: function (obj, status) {
			// wtf?
		} });
}