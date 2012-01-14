

if (typeof(String.prototype.trim) === "undefined") {
	String.prototype.trim = function() {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

// of global usage
flash_message_html = "<li class='flash-message'></li>"

function show_flash_message(message, customcss, delay) { // implement callback?
	if (!message) return; // if used with no message at all.

	var customcss = customcss || {};
	var delay = delay || 8000;
	var obj = $(flash_message_html).css(customcss).html(message);
	if (!$('#flash-messages-wrapper')[0])
		$(document.body).append('<div id="flash-messages-wrapper"></div>');
	obj.click(function () { $(this).stop().slideUp(); });
	obj.hide().appendTo('#flash-messages-wrapper').fadeIn().delay(delay).slideUp();
}

function goto_list(listname) {
	window.location.replace('/lists/'+encodeURI(listname))
}

function show_blackout() {
	$('#blackout').stop().show();
}

function hide_blackout() {
	$('#blackout').stop().fadeOut('fast');
}

/**************************************/
/* ADD-WORD/EDIT-WORD BOXES functions */
/**************************************/

// Add-Word Box functions
function make_add_word_box(word) { // creates the Add-Word box
	show_blackout();
	$(add_word_box_html).hide().appendTo('body').fadeIn();
	$('#edit-wrapper textarea').autoResize({'extraSpace': 10});
	$("#edit-wrapper [data-field=word] .edit-field-value").focus();
}

function remove_add_word_box() { // removes the Add-Word box
	remove_edit_word_box(); }


// Edit-Word Box functions
function make_edit_word_box(word) { // creates the Edit-Word Box
	show_blackout();
	$(edit_word_box_html).hide().appendTo('body').fadeIn();

	$(['word', 'meaning', 'origin']).each(function (index, item) {
		var value = $(word).find('input[name='+item+']').val();
		$("#edit-wrapper [data-field="+item+"] .edit-field-value").val(value);
	});

	var wordid = $(word).find('input[name=wordid]').val();
	$("#edit-wrapper input[name=wordid]").val(wordid);

	$('#edit-wrapper textarea').autoResize({'extraSpace': 10});
	$("#edit-wrapper [data-field=word] .edit-field-value").focus();
}

function remove_edit_word_box() { // removes the Edit-Word box
	$("#edit-wrapper").fadeOut('fast', function() {
		$("#edit-wrapper").remove()
		hide_blackout();
	});
}


/****************************/
/* AJAX DATABASE ACCESS API */
/****************************/

function add_word_db(parentid, csrf_token) { // adds a word to the database based on Add-Word Box
	var form = {};
	$(['word', 'meaning', 'origin']).each(function (index, item) {
		form[item] = $("#edit-wrapper [data-field="+item+"] .edit-field-value").val();
	});
	form['listid'] = parentid;
	form['csrfmiddlewaretoken'] = csrf_token;

	$.ajax({
		url: '/lists/api/add_word', 
		context: this,
		data: form,
		type: 'post',
		dataType: 'json',
		success: function (data, status) {
			if (data['success']) {
				show_flash_message(data['text']);
				add_word_tag($.extend(form, { 'wordid': data['wordid'] }));
				remove_add_word_box();
			} else {
				show_flash_message(data['text'], {'background': "#F60018"});
			}
		},
		error: function (obj, status) {
			// wtf?
		} });
}

function update_word_db(parentid, csrf_token) { // updates the word in the database based on the Edit-Word box
	var form = {};
	$(['word', 'meaning', 'origin']).each(function (index, item) {
		form[item] = $("#edit-wrapper [data-field="+item+"] .edit-field-value").val();
	});
	form['wordid'] = $("#edit-wrapper input[name=wordid]").val();
	form['listid'] = parentid;
	form['csrfmiddlewaretoken'] = csrf_token;

	$.ajax({
		url: '/lists/api/change_word', 
		context: this,
		data: form,
		type: 'post',
		dataType: 'json',
		success: function (data, status) {
			if (data['success']) {
				show_flash_message(data['text']);
				update_word_tag(form);
				remove_edit_word_box();
			} else {
				show_flash_message(data['text'], {'background': "#F60018"});
			}
		},
		error: function (obj, status) {
			// wtf?
		} });
}

function remove_word_db(parentid, csrf_token) { // removes the word being edited at the Edit-Word box from the database
	var form = {};
	form['wordid'] = $("#edit-wrapper input[name=wordid]").val();
	form['listid'] = parentid;
	form['csrfmiddlewaretoken'] = csrf_token;

	$.ajax({
		url: '/lists/api/remove_word',
		context: this, 
		data: form,
		type: 'post',
		dataType: 'json',
		success: function (data, status) {
			if (data['success']) {
				show_flash_message(data['text']);
				remove_word_tag(form);
				remove_edit_word_box();
			} else {
				show_flash_message(data['text'], {'background': "#F60018"});
			}
		},
		error: function (obj, status) {
			// wtf?
		} });
}
